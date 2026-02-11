import torch
from transformers import AutoProcessor, AutoModelForCausalLM

import torch
from transformers import AutoProcessor, AutoModelForCausalLM

print("Loading MedGemma 4B model...")
medgemma_model_id = "google/medgemma-4b-it"

model_kwargs = dict(
    attn_implementation="eager",
    dtype=torch.bfloat16,  # ← Changed from torch_dtype
    device_map="auto"
)

medgemma_model = AutoModelForCausalLM.from_pretrained(medgemma_model_id, **model_kwargs)
medgemma_processor = AutoProcessor.from_pretrained(medgemma_model_id)
medgemma_processor.tokenizer.padding_side = "right"
print("MedGemma loaded successfully.\n")


class ValidationAgent:
    """
    Evaluates if we have enough information for diagnosis.
    Uses strict rule-based checks to ensure minimum conversation depth.
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
        self.min_patient_responses = 4  # Minimum patient responses before allowing report
    
    def evaluate_completeness(self, patient_responses_only):
        """
        Check if we have sufficient information.
        Only counts PATIENT responses, not doctor questions.
        Returns: (should_continue_asking: bool, missing_category: str)
        """
        num_responses = len(patient_responses_only)
        combined = " ".join(patient_responses_only).lower()
        
        # CRITICAL: Need minimum 4 patient responses
        if num_responses < self.min_patient_responses:
            return True, self._determine_missing_category(num_responses, combined)
        
        # Check for essential information
        has_symptom = any(word in combined for word in [
            'pain', 'ache', 'fever', 'sick', 'hurt', 'rash', 'cough', 
            'tired', 'dizzy', 'nausea', 'vomit', 'swell', 'bleed', 'headache'
        ])
        
        has_duration = any(word in combined for word in [
            'day', 'week', 'month', 'hour', 'yesterday', 'today', 
            'ago', 'started', 'began', 'since', 'morning', 'evening'
        ])
        
        has_severity = any(word in combined for word in [
            'severe', 'mild', 'intense', 'bad', 'worse', 'better',
            'scale', 'level', 'sharp', 'dull', 'terrible', 'moderate'
        ])
        
        has_location = any(word in combined for word in [
            'chest', 'head', 'back', 'leg', 'arm', 'stomach', 'throat',
            'left', 'right', 'upper', 'lower', 'side', 'neck', 'shoulder'
        ])
        
        # Need at least: symptom + duration + (severity OR location)
        if not has_symptom:
            return True, "symptoms"
        if not has_duration:
            return True, "duration"
        if not has_severity and not has_location:
            return True, "severity or location"
        
        # If we have 4+ responses with all essential info, we're ready
        if num_responses >= self.min_patient_responses:
            return False, "none"
        
        return True, "additional details"
    
    def _determine_missing_category(self, num_responses, combined_text):
        """Determine what to ask for based on conversation stage"""
        if num_responses == 1:
            return "duration and timeline"
        elif num_responses == 2:
            if 'pain' in combined_text or 'ache' in combined_text:
                return "severity and location"
            return "symptom details"
        elif num_responses == 3:
            return "medical history or additional symptoms"
        else:
            return "additional information"


class QuestionGeneratorAgent:
    """
    Generates natural follow-up questions using MedGemma.
    Maintains history to avoid repetition.
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
        self.asked_questions = []  # Track questions we've asked
    
    def generate_question(self, full_conversation, missing_category):
        """
        Generate a contextual medical question.
        full_conversation: list alternating between patient and doctor messages
        """
        # Build conversation with roles for context
        conversation_text = ""
        for i, msg in enumerate(full_conversation):
            role = "Patient" if i % 2 == 0 else "Doctor"
            conversation_text += f"{role}: {msg}\n"
        
        # Build context about what we've already asked
        prev_questions_text = ""
        if self.asked_questions:
            prev_questions_text = "\nQuestions already asked (DO NOT repeat):\n" + "\n".join([f"- {q}" for q in self.asked_questions[-5:]])
        
        prompt = f"""You are a doctor in a consultation. Here is the conversation so far:

{conversation_text}
You need to ask about: {missing_category}
{prev_questions_text}

Generate ONE brief, natural follow-up question that builds on the conversation. Be empathetic and direct.
Output ONLY the question, nothing else.

Question:"""

        inputs = self.processor(
            text=prompt,
            images=None,
            return_tensors="pt",
            padding=True
        ).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.85,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.4,
                pad_token_id=self.processor.tokenizer.eos_token_id
            )
        
        response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up response
        if "Question:" in response:
            response = response.split("Question:")[-1].strip()
        
        # Extract first question
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        question = None
        
        for line in lines:
            if '?' in line:
                question = line[:line.index('?')+1].strip()
                break
        
        if not question and lines:
            question = lines[0].strip()
            if not question.endswith('?'):
                question += '?'
        
        if not question:
            question = self._get_fallback_question(missing_category)
        
        # Remove quotes if present
        question = question.strip('"\'')
        
        # Store this question
        self.asked_questions.append(question)
        
        return question
    
    def _get_fallback_question(self, missing_category):
        """Fallback questions based on category"""
        fallbacks = {
            "duration": "When did these symptoms start?",
            "duration and timeline": "How long have you been experiencing these symptoms?",
            "severity": "How severe is the pain on a scale of 1-10?",
            "severity and location": "Can you describe where exactly you feel this and how intense it is?",
            "severity or location": "Where exactly do you feel this, and how severe is it?",
            "location": "Where exactly are you feeling this?",
            "medical history": "Do you have any pre-existing conditions or take any medications?",
            "medical history or additional symptoms": "Have you noticed any other symptoms, or do you have any relevant medical history?",
            "symptoms": "What symptoms are you experiencing?",
            "symptom details": "Can you describe your symptoms in more detail?",
            "additional information": "Is there anything else about your condition I should know?",
            "additional details": "Can you tell me more about how this is affecting you?"
        }
        return fallbacks.get(missing_category, "Can you provide more details about your symptoms?")


class DoctorAgent:
    """
    Generates concise medical assessment with specific diagnosis
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
    
    def generate_report(self, full_conversation):
        """
        Generate concise medical report from full conversation context
        """
        # Build conversation with roles
        conversation_text = ""
        for i, msg in enumerate(full_conversation):
            role = "Patient" if i % 2 == 0 else "Doctor"
            conversation_text += f"{role}: {msg}\n"
        
        prompt = f"""You are a medical doctor. Based on this patient consultation, provide a CONCISE assessment.

CONSULTATION:
{conversation_text}

Provide a brief assessment in this structure:

SYMPTOMS: (2 sentences summarizing key symptoms)

DIAGNOSIS: (State ONE most likely specific condition clearly)

CAUSE: (1-2 sentences explaining likely cause)

RECOMMENDATIONS:
- Primary treatment action
- When to see a doctor
- One warning sign to watch for

Keep it concise and practical. Focus on ONE specific diagnosis.

ASSESSMENT:
"""

        inputs = self.processor(
            text=prompt,
            images=None,
            return_tensors="pt",
            padding=True
        ).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.6,
                do_sample=True,
                top_p=0.85,
                repetition_penalty=1.2,
                pad_token_id=self.processor.tokenizer.eos_token_id
            )
        
        report = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        if "ASSESSMENT:" in report:
            report = report.split("ASSESSMENT:")[-1].strip()
        
        return report


def interactive_consultation():
    """
    Main consultation loop - tracks BOTH patient and doctor messages for context,
    but validates based ONLY on patient responses
    """
    print("=" * 75)
    print("INTERACTIVE MEDICAL CONSULTATION SYSTEM")
    print("Multi-Agent: Validation + Question Generation + Diagnosis")
    print("=" * 75)
    
    # Initialize agents
    print("\n[Initializing AI agents...]")
    validation_agent = ValidationAgent(medgemma_model, medgemma_processor)
    question_agent = QuestionGeneratorAgent(medgemma_model, medgemma_processor)
    doctor_agent = DoctorAgent(medgemma_model, medgemma_processor)
    print("[Agents ready]\n")
    
    print("Doctor: Good morning! I'm here to help you today.")
    print("        Please tell me about your symptoms or health concerns.\n")
    
    patient_responses = []  # ONLY patient messages for validation
    full_conversation = []  # BOTH patient and doctor messages for context
    max_patient_responses = 8
    
    while len(patient_responses) < max_patient_responses:
        try:
            user_input = input("Patient: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nDoctor: Take care! Goodbye.\n")
            break
        
        if not user_input:
            print("\nDoctor: I'm here to listen. Please describe your symptoms.\n")
            continue
        
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye', 'stop']:
            print("\nDoctor: Take care of yourself. Seek medical attention if needed.\n")
            break
        
        # Add to BOTH lists
        patient_responses.append(user_input)
        full_conversation.append(user_input)
        
        # VALIDATION: Check based ONLY on patient responses
        should_continue, missing_category = validation_agent.evaluate_completeness(
            patient_responses
        )
        
        if not should_continue:
            # Ready to generate report
            print("\nDoctor: Thank you for all that information. Let me prepare")
            print("        a comprehensive assessment for you.\n")
            
            print("=" * 75)
            print("MEDICAL ASSESSMENT REPORT")
            print("=" * 75 + "\n")
            
            try:
                # Pass full conversation for context
                report = doctor_agent.generate_report(full_conversation)
                print(report)
            except Exception as e:
                print(f"I apologize, there was an error generating the report.")
                print(f"Error: {str(e)}")
            
            print("\n" + "=" * 75)
            print("\n⚠️  IMPORTANT DISCLAIMER:")
            print("   This is an AI-generated assessment for informational purposes.")
            print("   Please consult a qualified healthcare professional in person")
            print("   for accurate diagnosis and treatment.\n")
            print("Doctor: I hope you feel better soon. Take care!\n")
            break
        
        # QUESTION GENERATION: Pass full conversation for context
        try:
            question = question_agent.generate_question(
                full_conversation,
                missing_category
            )
            # Add doctor's question to full conversation
            full_conversation.append(question)
            print(f"\nDoctor: {question}\n")
        except Exception as e:
            fallback = f"Could you tell me more about {missing_category}?"
            full_conversation.append(fallback)
            print(f"\nDoctor: {fallback}\n")
    
    if len(patient_responses) >= max_patient_responses:
        print("\nDoctor: Thank you for sharing. I recommend consulting with a")
        print("        healthcare professional in person. Take care!\n")


if __name__ == "__main__":
    try:
        interactive_consultation()
    except Exception as e:
        print(f"\nSystem error: {str(e)}")
        print("Please restart the consultation.")