import torch
from transformers import AutoProcessor, AutoModel

# Note: Use HF_TOKEN environment variable instead of hardcoding tokens
# Set: export HF_TOKEN="your_token" or create ~/.huggingface/token file

print("Loading MedGemma 4B model...")
medgemma_model_id = "google/medgemma-4b-it"  # Using 4B for faster responses
model_kwargs = dict(
    attn_implementation="eager",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
medgemma_model = AutoModel.from_pretrained(medgemma_model_id, **model_kwargs)
medgemma_processor = AutoProcessor.from_pretrained(medgemma_model_id)
medgemma_processor.tokenizer.padding_side = "right"
print("MedGemma loaded successfully.\n")


class ValidationAgent:
    """
    Evaluates if we have enough information for diagnosis
    Uses simple rule-based + AI hybrid approach for reliability
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
    
    def evaluate_completeness(self, conversation_history):
        """
        Check if we have sufficient information.
        Returns: (should_continue_asking: bool, missing_category: str)
        """
        combined = " ".join(conversation_history).lower()
        num_exchanges = len(conversation_history)
        
        # Rule-based checks for core information
        has_symptom = any(word in combined for word in [
            'pain', 'ache', 'fever', 'sick', 'hurt', 'rash', 'cough', 
            'tired', 'dizzy', 'nausea', 'vomit', 'swell', 'bleed'
        ])
        
        has_duration = any(word in combined for word in [
            'day', 'week', 'month', 'hour', 'yesterday', 'today', 
            'ago', 'started', 'began', 'since'
        ])
        
        has_location = any(word in combined for word in [
            'chest', 'head', 'back', 'leg', 'arm', 'stomach', 'throat',
            'left', 'right', 'upper', 'lower', 'side'
        ])
        
        # Minimum 3 exchanges required
        if num_exchanges < 3:
            return True, "basic symptom details"
        
        # Check what's missing
        if not has_symptom:
            return True, "clear description of symptoms"
        
        if num_exchanges == 3:
            if not has_duration:
                return True, "duration of symptoms"
            if not has_location and 'pain' in combined:
                return True, "location of pain"
        
        if num_exchanges == 4:
            # Check for severity or intensity
            has_severity = any(word in combined for word in [
                'severe', 'mild', 'intense', 'bad', 'worse', 'better',
                'scale', 'level', 'sharp', 'dull'
            ])
            if not has_severity:
                return True, "severity or intensity"
        
        if num_exchanges == 5:
            # Check for medical history
            has_history = any(word in combined for word in [
                'history', 'before', 'previous', 'past', 'medication',
                'condition', 'allergies', 'surgery'
            ])
            if not has_history:
                return True, "medical history"
        
        # After 5+ exchanges with core info, ready for report
        if num_exchanges >= 5 and has_symptom and has_duration:
            return False, ""
        
        # If we have 6+ exchanges, proceed regardless
        if num_exchanges >= 6:
            return False, ""
        
        return True, "additional details"


class QuestionGeneratorAgent:
    """
    Generates natural follow-up questions using MedGemma
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
    
    def generate_question(self, conversation_history, missing_category):
        """
        Generate a contextual medical question
        """
        recent_context = "\n".join(conversation_history[-3:])  # Last 3 exchanges
        
        prompt = f"""You are a doctor talking to a patient. Based on the conversation, ask ONE brief follow-up question.

Recent conversation:
Patient: {recent_context}

The patient needs to provide: {missing_category}

Generate ONE natural question a doctor would ask. Be brief and empathetic.
Do not explain, just ask the question.

Doctor:"""

        inputs = self.processor(
            text=prompt,
            images=None,
            return_tensors="pt",
            padding=True
        ).to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=60,
                temperature=0.8,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.4,
                pad_token_id=self.processor.tokenizer.eos_token_id
            )
        
        response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up response
        if "Doctor:" in response:
            response = response.split("Doctor:")[-1].strip()
        
        # Get first sentence with question mark
        sentences = response.split('.')
        for sent in sentences:
            if '?' in sent:
                question = sent[:sent.index('?')+1].strip()
                question = question.strip('"\'')
                return question
        
        # Fallback - just take first line
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        if lines:
            question = lines[0].strip('"\'')
            if not question.endswith('?'):
                question += '?'
            return question
        
        return "Can you tell me more about your symptoms?"


class DoctorAgent:
    """
    Generates comprehensive medical assessment reports
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
    
    def generate_report(self, conversation_history):
        """
        Generate detailed medical assessment
        """
        full_conversation = "\n".join([f"Patient: {msg}" for msg in conversation_history])
        
        prompt = f"""You are an experienced medical doctor. Based on this patient consultation, provide a comprehensive medical assessment.

PATIENT CONSULTATION:
{full_conversation}

Provide a detailed assessment with these sections:

1. SUMMARY: Brief overview of patient's condition
2. ANALYSIS: Key symptoms and their significance
3. POSSIBLE DIAGNOSIS: Most likely condition(s) based on symptoms
4. CAUSES: Potential underlying causes
5. RECOMMENDATIONS: 
   - Immediate steps to take
   - Tests or examinations needed
   - Treatment suggestions
   - Warning signs to watch for

Be professional, thorough, and evidence-based.

MEDICAL ASSESSMENT:
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
                max_new_tokens=700,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.processor.tokenizer.eos_token_id
            )
        
        report = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the assessment
        if "MEDICAL ASSESSMENT:" in report:
            report = report.split("MEDICAL ASSESSMENT:")[-1].strip()
        
        return report


def interactive_consultation():
    """
    Main consultation loop with multi-agent system
    """
    print("=" * 75)
    print("INTERACTIVE MEDICAL CONSULTATION SYSTEM")
    print("Multi-Agent Architecture: Validation + Question Generation + Diagnosis")
    print("=" * 75)
    
    # Initialize agents
    print("\n[Initializing AI agents...]")
    validation_agent = ValidationAgent(medgemma_model, medgemma_processor)
    question_agent = QuestionGeneratorAgent(medgemma_model, medgemma_processor)
    doctor_agent = DoctorAgent(medgemma_model, medgemma_processor)
    print("[Agents ready]\n")
    
    print("Doctor: Good morning! I'm here to help you today.")
    print("        Please tell me about your symptoms or health concerns.\n")
    
    conversation_history = []
    max_exchanges = 10
    
    while len(conversation_history) < max_exchanges:
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
        
        # Add to conversation
        conversation_history.append(user_input)
        
        # VALIDATION AGENT: Check if we need more information
        should_continue, missing_category = validation_agent.evaluate_completeness(
            conversation_history
        )
        
        if not should_continue:
            # Ready to generate report
            print("\nDoctor: Thank you for all that information. Let me prepare")
            print("        a comprehensive assessment for you.\n")
            
            print("=" * 75)
            print("MEDICAL ASSESSMENT REPORT")
            print("=" * 75 + "\n")
            
            try:
                report = doctor_agent.generate_report(conversation_history)
                print(report)
            except Exception as e:
                print(f"I apologize, there was an error generating the report.")
                print(f"Error details: {str(e)}")
            
            print("\n" + "=" * 75)
            print("\n⚠️  IMPORTANT DISCLAIMER:")
            print("   This is an AI-generated assessment for informational purposes.")
            print("   Please consult a qualified healthcare professional in person")
            print("   for accurate diagnosis and treatment.\n")
            print("Doctor: I hope you feel better soon. Take care!\n")
            break
        
        # QUESTION GENERATOR AGENT: Ask follow-up question
        try:
            question = question_agent.generate_question(
                conversation_history, 
                missing_category
            )
            print(f"\nDoctor: {question}\n")
        except Exception as e:
            print(f"\nDoctor: Could you tell me more about {missing_category}?\n")
    
    if len(conversation_history) >= max_exchanges:
        print("\nDoctor: Thank you for sharing. I recommend consulting with a")
        print("        healthcare professional in person. Take care!\n")


if __name__ == "__main__":
    try:
        interactive_consultation()
    except Exception as e:
        print(f"\nSystem error: {str(e)}")
        print("Please restart the consultation.")