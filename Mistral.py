import torch
import json
import re
import warnings
import os
import logging
from transformers import (
    AutoProcessor,
    AutoModel,
    AutoModelForCausalLM,
    AutoTokenizer
)

# Suppress transformers verbosity and warnings
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
logging.getLogger('transformers').setLevel(logging.ERROR)
logging.getLogger('transformers.generation.utils').setLevel(logging.ERROR)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*temperature.*')
warnings.filterwarnings('ignore', message='.*pad_token_id.*')
warnings.filterwarnings('ignore', message='.*Setting.*pad_token_id.*')


# ========================================================================
# Load MedGemma Model for Question Generation and Diagnosis
# ========================================================================
print("Loading MedGemma 4B model...")
medgemma_model_id = "google/medgemma-4b-it"  # Efficient yet powerful
model_kwargs = dict(
    attn_implementation="eager",
    dtype=torch.bfloat16,
    device_map="auto"
)
medgemma_model = AutoModel.from_pretrained(medgemma_model_id, **model_kwargs)
medgemma_processor = AutoProcessor.from_pretrained(medgemma_model_id)
medgemma_processor.tokenizer.padding_side = "right"
print("MedGemma loaded successfully.\n")


# ========================================================================
# Load Mistral 7B Instruct Model for Validation Agent
# ========================================================================
print("Loading Mistral 7B Instruct model for Validation Agent...")
validation_model_id = "mistralai/Mistral-7B-Instruct-v0.3"
val_tokenizer = AutoTokenizer.from_pretrained(validation_model_id)
val_model = AutoModelForCausalLM.from_pretrained(
    validation_model_id,
    dtype=torch.bfloat16,
    device_map="auto"
)
print("Mistral Validation Agent loaded successfully.\n")


# ========================================================================
# Transformer-Based Validation Agent
# ========================================================================
class TransformerValidationAgent:
    """
    Uses Mistral-7B to evaluate conversation completeness.
    Tracks progress to avoid repetition.
    """

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.last_category = None

    def evaluate_completeness(self, conversation_history):
        num_exchanges = len(conversation_history)
        conversation = "\n".join([f"Patient: {msg}" for msg in conversation_history[-5:]])

        prompt = f"""Evaluate patient info. JSON only.
{{
  "should_continue_asking": true or false,
  "missing_category": "symptoms / duration / severity / location / medical history / none",
  "reasoning": "brief"
}}
"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                do_sample=False
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                if isinstance(result, dict) and result.get("missing_category") == "unclear":
                    result["missing_category"] = "additional symptoms information"
                # Force progression
                if result.get("missing_category") == self.last_category and num_exchanges > 2:
                    categories = ["symptom details", "duration and severity", "medical history", "none"]
                    if self.last_category in categories:
                        idx = categories.index(self.last_category)
                        result["missing_category"] = categories[min(idx + 1, len(categories) - 1)]
                self.last_category = result.get("missing_category")
                return result
            except json.JSONDecodeError:
                pass

        # Rule-based progression
        progression = {
            1: "symptom details", 2: "symptom details",
            3: "duration and severity", 4: "duration and severity",
            5: "medical history", 6: "medical history", 7: "none"
        }
        missing = progression.get(num_exchanges, "none")
        
        # Force progression if stuck
        if missing == self.last_category and num_exchanges > 2:
            categories = ["symptom details", "duration and severity", "medical history", "none"]
            idx = categories.index(missing) if missing in categories else 0
            missing = categories[min(idx + 1, len(categories) - 1)]
        
        self.last_category = missing
        return {
            "should_continue_asking": missing != "none",
            "missing_category": missing,
            "reasoning": "Using rule-based progression."
        }


# ========================================================================
# Question Generator Agent (MedGemma)
# ========================================================================
class QuestionGeneratorAgent:
    """
    Generates natural follow-up questions using MedGemma with smart fallback.
    Optimized for speed with caching.
    """
    
    # Smart fallback questions - rotating to avoid repetition
    SMART_FALLBACKS = {
        "symptom details": [
            "Can you describe your symptoms in more detail?",
            "What exactly are you experiencing?",
            "Tell me more about what you feel."
        ],
        "duration and severity": [
            "How long have you had this, and on a scale of 1-10, how severe?",
            "When did this start, and is it getting worse?",
            "How many days has this been going on?"
        ],
        "medical history": [
            "Do you have any medical conditions or take medications?",
            "Have you experienced this before?",
            "Are you allergic to anything?"
        ],
        "additional symptoms information": [
            "Are there any other symptoms?",
            "Anything else bothering you?",
            "Any other changes you've noticed?"
        ],
        "none": ["Is there anything else you'd like to tell me?"]
    }

    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
        self.fallback_index = {}  # Rotate through fallbacks

    def generate_question(self, conversation_history, missing_category):
        # Use smart fallback first (fast)
        if missing_category in self.SMART_FALLBACKS:
            fallback_list = self.SMART_FALLBACKS[missing_category]
            idx = self.fallback_index.get(missing_category, 0)
            question = fallback_list[idx % len(fallback_list)]
            self.fallback_index[missing_category] = idx + 1
            return question
        
        # Attempt generation if needed (slower)
        try:
            recent_context = " ".join(conversation_history[-2:])
            prompt = f"Ask one brief doctor question about: {missing_category}. Context: {recent_context}\nQuestion:"

            inputs = self.processor(
                text=prompt,
                images=None,
                return_tensors="pt",
                padding=True
            ).to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=25,
                    do_sample=False,  # Deterministic generation
                    pad_token_id=self.processor.tokenizer.eos_token_id,
                    use_cache=True
                )

            response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            if "?" in response:
                question = response.split("?")[0].split("\n")[-1].strip() + "?"
                if len(question) > 5:
                    return question
        except Exception:
            pass
        
        # Fall back to smart fallback
        return self.SMART_FALLBACKS.get(missing_category, ["Can you tell me more?"])[0]


# ========================================================================
# Doctor Agent - Uses Mistral for Report Generation
# ========================================================================
class DoctorAgent:
    """
    Generates comprehensive medical assessment reports using Mistral-7B
    """

    def __init__(self, val_model, val_tokenizer):
        """Uses Mistral model for medical report generation"""
        self.model = val_model
        self.tokenizer = val_tokenizer

    def generate_report(self, conversation_history):
        """Generate medical assessment using Mistral"""
        full_conversation = "\n".join([f"Patient: {msg}" for msg in conversation_history[-6:]])  # Last 6 exchanges

        prompt = f"""Based on this patient consultation, provide a brief medical assessment.

Patient Information:
{full_conversation}

Provide assessment with:
1. SUMMARY: Patient's main condition
2. LIKELY CAUSES: Potential causes
3. RECOMMENDATIONS: Suggested actions

Assessment:"""

        try:
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=400,
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            report = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the assessment part
            if "Assessment:" in report:
                report = report.split("Assessment:")[-1].strip()
            
            # Clean up the report
            report = report[:500]  # Limit length
            return report.strip()
        
        except Exception as e:
            # Fallback heuristic report if generation fails
            return self._generate_heuristic_report(conversation_history)
    
    def _generate_heuristic_report(self, conversation_history):
        """Generate a heuristic-based report when AI generation fails"""
        text = " ".join(conversation_history).lower()
        
        # Comprehensive symptom-cause mappings
        condition_keywords = {
            "indigestion|stomach|gastric|reflux|acid|heartburn": {
                "name": "Gastrointestinal Issues",
                "symptoms": ["Indigestion"],
                "causes": ["Dietary issues", "Acid reflux", "Functional dyspepsia"],
                "recommendations": ["Dietary modifications", "Antacids", "Regular meals", "Limit spicy foods"]
            },
            "cough|respiratory|throat|bronch|pneumonia|flu": {
                "name": "Respiratory Infection",
                "symptoms": ["Cough", "Throat discomfort"],
                "causes": ["Viral infection", "Bacterial infection", "Common cold"],
                "recommendations": ["Rest", "Hydration", "Honey tea", "Throat lozenges"]
            },
            "headache|migraine|tension": {
                "name": "Headache",
                "symptoms": ["Head pain"],
                "causes": ["Stress", "Dehydration", "Poor sleep", "Tension"],
                "recommendations": ["Rest", "Analgesics", "Hydration", "Stress management"]
            },
            "fever|temperature|infection|viral": {
                "name": "Fever",
                "symptoms": ["Elevated temperature"],
                "causes": ["Viral infection", "Bacterial infection", "Inflammatory response"],
                "recommendations": ["Rest", "Antipyretics", "Hydration", "Monitor symptoms"]
            },
            "pain|ache|soreness": {
                "name": "Pain/Discomfort",
                "symptoms": ["Pain present"],
                "causes": ["Muscle strain", "Inflammation", "Underlying condition"],
                "recommendations": ["Rest", "Pain management", "Physical rest", "Monitor severity"]
            },
            "dizziness|dizzy|vertigo|spinning": {
                "name": "Dizziness",
                "symptoms": ["Dizziness"],
                "causes": ["Dehydration", "Low blood pressure", "Inner ear issues", "Anemia"],
                "recommendations": ["Rest", "Hydration", "Gradual movement", "Monitor blood pressure"]
            },
            "fatigue|tired|weakness|weak|drowsy|drowsiness": {
                "name": "Fatigue",
                "symptoms": ["Fatigue/weakness"],
                "causes": ["Sleep deprivation", "Anemia", "Infection", "Metabolic issues"],
                "recommendations": ["Rest and sleep", "Nutrition", "Gradual activity", "B vitamins"]
            },
            "nausea|vomit|nauseous": {
                "name": "Nausea",
                "symptoms": ["Nausea/Vomiting"],
                "causes": ["Gastrointestinal issue", "Infection", "Medication side effect"],
                "recommendations": ["Anti-nausea medication", "Hydration", "Clear liquids", "Ginger tea"]
            }
        }
        
        # Find matching conditions
        matched_conditions = []
        for keywords, condition_info in condition_keywords.items():
            for keyword in keywords.split("|"):
                if keyword in text:
                    matched_conditions.append(condition_info)
                    break
        
        # Build report
        report = "\n" + "="*60 + "\n"
        report += "CLINICAL ASSESSMENT REPORT\n"
        report += "="*60 + "\n\n"
        
        report += "1. SUMMARY:\n"
        if matched_conditions:
            main_condition = matched_conditions[0]["name"]
            report += f"Patient presents with {main_condition.lower()}.\n"
        else:
            report += f"Patient reported {len(conversation_history)} health-related items.\n"
        
        report += "\n2. IDENTIFIED SYMPTOMS:\n"
        all_symptoms = set()
        for condition in matched_conditions:
            for symptom in condition["symptoms"]:
                all_symptoms.add(f"• {symptom}")
        if all_symptoms:
            report += "\n".join(sorted(all_symptoms))
        else:
            report += "• Multiple reported symptoms\n"
        
        report += "\n\n3. LIKELY CAUSES:\n"
        all_causes = []
        for condition in matched_conditions:
            all_causes.extend(condition["causes"])
        if all_causes:
            for cause in all_causes[:4]:  # Limit to 4 causes
                report += f"• {cause}\n"
        else:
            report += "• Functional or structural issue\n"
        
        report += "\n4. RECOMMENDED ACTIONS:\n"
        all_recommendations = []
        for condition in matched_conditions:
            all_recommendations.extend(condition["recommendations"])
        if all_recommendations:
            # Remove duplicates and limit to 5
            unique_recommendations = list(set(all_recommendations))[:5]
            for rec in unique_recommendations:
                report += f"• {rec}\n"
        else:
            report += "• Consult healthcare provider\n"
            report += "• Monitor symptoms\n"
            report += "• Maintain rest and hydration\n"
        
        report += "\n" + "="*60 + "\n"
        return report


# ========================================================================
# Main Consultation Loop
# ========================================================================
def interactive_consultation():
    print("=" * 75)
    print("INTERACTIVE MEDICAL CONSULTATION SYSTEM")
    print("Multi-Agent Architecture: Transformer Validation + MedGemma QA + Diagnosis")
    print("=" * 75)

    print("\n[Initializing AI agents...]")
    validation_agent = TransformerValidationAgent(val_model, val_tokenizer)
    question_agent = QuestionGeneratorAgent(medgemma_model, medgemma_processor)
    doctor_agent = DoctorAgent(val_model, val_tokenizer)
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

        conversation_history.append(user_input)

        # TRANSFORMER VALIDATION AGENT
        validation_output = validation_agent.evaluate_completeness(conversation_history)
        should_continue = validation_output.get("should_continue_asking", True)
        missing_category = validation_output.get("missing_category", "unclear")

        if not should_continue:
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

        try:
            question = question_agent.generate_question(conversation_history, missing_category)
            print(f"\nDoctor: {question}\n")
        except Exception as e:
            print(f"\nDoctor: Could you tell me more about {missing_category}?\n")

    if len(conversation_history) >= max_exchanges:
        print("\nDoctor: Thank you for sharing. I recommend consulting with a")
        print("        healthcare professional in person. Take care!\n")


# ========================================================================
# Entry Point
# ========================================================================
if __name__ == "__main__":
    try:
        interactive_consultation()
    except Exception as e:
        print(f"\nSystem error: {str(e)}")
        print("Please restart the consultation.")