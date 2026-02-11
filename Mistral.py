import torch
import json
import re
from transformers import (
    AutoProcessor,
    AutoModel,
    AutoModelForCausalLM,
    AutoTokenizer
)


# ========================================================================
# Load MedGemma Model for Question Generation and Diagnosis
# ========================================================================
import torch
from transformers import AutoProcessor, AutoModelForCausalLM

print("Loading MedGemma 4B model...")
medgemma_model_id = "google/medgemma-4b-it"

# ✅ FIXED: Use 'dtype' instead of 'torch_dtype'
model_kwargs = dict(
    attn_implementation="eager",
    dtype=torch.bfloat16,  # ← Changed from torch_dtype
    device_map="auto"
)

medgemma_model = AutoModelForCausalLM.from_pretrained(medgemma_model_id, **model_kwargs)
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
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
print("Mistral Validation Agent loaded successfully.\n")


# ========================================================================
# Transformer-Based Validation Agent
# ========================================================================
class TransformerValidationAgent:
    """
    Uses Mistral-7B-Instruct to evaluate if enough information
    has been gathered for a medical diagnosis.
    """

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def evaluate_completeness(self, conversation_history):
        conversation = "\n".join([f"Patient: {msg}" for msg in conversation_history])

        prompt = f"""
You are an intelligent medical validation assistant.
Your task is to evaluate whether the doctor has gathered enough information
from the patient to proceed with a medical diagnosis.

Conversation:
{conversation}

Respond ONLY in JSON format with the following keys:
{{
  "should_continue_asking": true or false,
  "missing_category": "symptoms / duration / severity / location / medical history / none",
  "reasoning": "brief explanation"
}}
"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=200,
                temperature=0.3,
                top_p=0.9
            )
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # Fallback if JSON extraction fails
        return {
            "should_continue_asking": True,
            "missing_category": "unclear",
            "reasoning": "Model output could not be parsed properly."
        }


# ========================================================================
# Question Generator Agent (MedGemma)
# ========================================================================
class QuestionGeneratorAgent:
    """
    Generates natural follow-up questions using MedGemma
    """

    def __init__(self, model, processor):
        self.model = model
        self.processor = processor

    def generate_question(self, conversation_history, missing_category):
        recent_context = "\n".join(conversation_history[-3:])

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
        if "Doctor:" in response:
            response = response.split("Doctor:")[-1].strip()

        sentences = response.split('.')
        for sent in sentences:
            if '?' in sent:
                question = sent[:sent.index('?') + 1].strip()
                question = question.strip('"\'')
                return question

        lines = [l.strip() for l in response.split('\n') if l.strip()]
        if lines:
            question = lines[0].strip('"\'')
            if not question.endswith('?'):
                question += '?'
            return question

        return "Can you tell me more about your symptoms?"


# ========================================================================
# Doctor Agent (MedGemma)
# ========================================================================
class DoctorAgent:
    """
    Generates comprehensive medical assessment reports
    """

    def __init__(self, model, processor):
        self.model = model
        self.processor = processor

    def generate_report(self, conversation_history):
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
        if "MEDICAL ASSESSMENT:" in report:
            report = report.split("MEDICAL ASSESSMENT:")[-1].strip()

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