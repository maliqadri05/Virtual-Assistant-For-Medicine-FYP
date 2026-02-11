"""
MedAI Assistant - Optimized Medical Diagnostic System
Combines best practices from all 4 approaches
Features: Efficient rule-based validation + MedGemma intelligence + safety checks
"""

import torch
import json
import re
from typing import Tuple, List, Dict
from transformers import AutoProcessor, AutoModel
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 75)
print("Loading MedAI Assistant - Optimized Multi-Agent System")
print("=" * 75)

# ========================================================================
# Model Loading with Error Handling
# ========================================================================

def load_medgemma_model():
    """Load MedGemma 4B model with proper error handling"""
    try:
        print("\n[1/2] Loading MedGemma 4B model...")
        medgemma_model_id = "google/medgemma-4b-it"
        
        model_kwargs = dict(
            attn_implementation="eager",
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        
        model = AutoModel.from_pretrained(medgemma_model_id, **model_kwargs)
        processor = AutoProcessor.from_pretrained(medgemma_model_id)
        processor.tokenizer.padding_side = "right"
        
        print("✓ MedGemma loaded successfully")
        return model, processor
        
    except Exception as e:
        logger.error(f"Failed to load MedGemma: {str(e)}")
        print(f"✗ Error loading model: {str(e)}")
        raise

try:
    medgemma_model, medgemma_processor = load_medgemma_model()
except Exception as e:
    print(f"\nFatal error: Could not load required model")
    print(f"Error: {str(e)}")
    print("\nTroubleshooting steps:")
    print("1. Ensure you have internet connection for Hugging Face download")
    print("2. Check that you have at least 8GB free disk space")
    print("3. Try: huggingface-cli login")
    print("4. Verify GPU has at least 4GB VRAM available")
    exit(1)

print("[2/2] System initialization complete\n")

# ========================================================================
# Agent 1: Intelligent Validation Agent (Hybrid)
# ========================================================================

class ValidationAgent:
    """
    Intelligent validation combining rule-based checks with context awareness.
    Determines when enough medical information has been gathered.
    """
    
    MEDICAL_KEYWORDS = {
        'symptoms': {
            'pain', 'ache', 'fever', 'sick', 'hurt', 'rash', 'cough', 
            'tired', 'dizzy', 'nausea', 'vomit', 'swell', 'bleed', 'headache',
            'sweat', 'itch', 'burn', 'cramp', 'stiff', 'short breath', 'wheezing'
        },
        'duration': {
            'day', 'week', 'month', 'hour', 'yesterday', 'today', 
            'ago', 'started', 'began', 'since', 'morning', 'evening',
            'night', 'minutes', 'hours', 'days', 'weeks', 'months', 'year', 'years'
        },
        'severity': {
            'severe', 'mild', 'intense', 'bad', 'worse', 'better',
            'scale', 'level', 'sharp', 'dull', 'terrible', 'moderate',
            'extreme', 'slight', 'unbearable', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'
        },
        'location': {
            'chest', 'head', 'back', 'leg', 'arm', 'stomach', 'throat',
            'left', 'right', 'upper', 'lower', 'side', 'neck', 'shoulder',
            'abdomen', 'hip', 'knee', 'foot', 'hand', 'jaw', 'ear', 'eye'
        },
        'history': {
            'history', 'before', 'previous', 'past', 'medication',
            'condition', 'allergies', 'surgery', 'disease', 'treatment',
            'chronic', 'diabetes', 'hypertension', 'asthma', 'cancer'
        }
    }
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
        self.min_exchanges = 3  # Minimum conversation exchanges
        self.info_threshold = 0.6  # What % of info we need (0-1)
        
    def evaluate_completeness(self, conversation_history: List[str]) -> Tuple[bool, str]:
        """
        Evaluate if we have enough information for diagnosis.
        
        Returns:
            (should_continue_asking: bool, missing_category: str)
        """
        if not conversation_history:
            return True, "initial symptoms"
        
        # Check exchange count
        num_exchanges = len(conversation_history)
        if num_exchanges < self.min_exchanges:
            return True, self._get_missing_category(num_exchanges, conversation_history)
        
        # Analyze content
        combined_text = " ".join(conversation_history).lower()
        found_info = self._analyze_content(combined_text)
        
        # Determine readiness
        if num_exchanges < 3:
            return True, "more symptom details"
        elif num_exchanges == 3:
            required = {'symptoms', 'duration'}
            if not required.issubset(set(found_info.keys())):
                missing = required - set(found_info.keys())
                return True, next(iter(missing))
        elif num_exchanges < 5:
            required = {'symptoms', 'duration', 'severity'} if 'pain' in combined_text else {'symptoms', 'duration'}
            missing = required - set(found_info.keys())
            if missing:
                return True, next(iter(missing))
        
        # Check if we have sufficient information
        required_fields = {'symptoms', 'duration'}
        if required_fields.issubset(set(found_info.keys())):
            if num_exchanges >= 5 or (num_exchanges >= 4 and 'severity' in found_info):
                return False, ""
        
        if num_exchanges >= 7:  # Max out at 7 exchanges
            return False, ""
        
        return True, self._get_missing_category(num_exchanges, conversation_history)
    
    def _analyze_content(self, text: str) -> Dict[str, bool]:
        """Analyze what medical information is present"""
        found = {}
        for category, keywords in self.MEDICAL_KEYWORDS.items():
            found[category] = any(keyword in text for keyword in keywords)
        return found
    
    def _get_missing_category(self, num_exchanges: int, history: List[str]) -> str:
        """Intelligently determine what information is still missing"""
        combined = " ".join(history).lower()
        found = self._analyze_content(combined)
        
        # Progressive questioning strategy
        if num_exchanges == 1:
            return "symptom duration"
        elif num_exchanges == 2:
            if 'pain' in combined:
                return "pain severity and location"
            return "symptom details"
        elif num_exchanges == 3:
            if not found.get('duration'):
                return "how long it started"
            if not found.get('severity') and 'pain' in combined:
                return "pain severity"
            return "medical history"
        elif num_exchanges == 4:
            if not found.get('severity'):
                return "severity on scale 1-10"
            return "related medical conditions"
        else:
            return "additional relevant information"


# ========================================================================
# Agent 2: Context-Aware Question Generator
# ========================================================================

class QuestionGeneratorAgent:
    """
    Generates natural, contextual follow-up questions using MedGemma.
    Tracks conversation to avoid repetition and maintain coherence.
    """
    
    # Fallback questions by category for robustness
    FALLBACK_QUESTIONS = {
        'symptom duration': "When did these symptoms first start?",
        'symptom details': "Can you describe your symptoms in more detail?",
        'pain severity': "On a scale of 1-10, how severe is the pain?",
        'pain severity and location': "Where exactly do you feel the pain, and how severe is it?",
        'how long it started': "How long ago did this start?",
        'severity on scale 1-10': "Using a scale of 1-10, how would you rate the severity?",
        'related medical conditions': "Do you have any ongoing health conditions we should know about?",
        'medical history': "Have you had similar issues before, or do you take any medications?",
        'additional relevant information': "Is there anything else about your condition I should know?",
        'initial symptoms': "What symptoms are you experiencing?"
    }
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
        self.asked_questions = []  # Track to avoid repetition
        
    def generate_question(self, conversation_history: List[str], missing_category: str) -> str:
        """
        Generate contextual follow-up question.
        
        Args:
            conversation_history: List of patient responses
            missing_category: What information is needed
            
        Returns:
            Natural language question
        """
        try:
            # Build context from recent exchanges
            recent_context = "\n".join(conversation_history[-3:])
            
            prompt = f"""You are a caring, professional doctor. Generate ONE brief, natural follow-up question.

Recent conversation:
{recent_context}

Information needed: {missing_category}

Guidelines:
- Ask ONE question only
- Keep it brief and empathetic
- Sound natural, not robotic
- Avoid technical jargon

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
                    temperature=0.8,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.4,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            response = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
            question = self._extract_question(response)
            
            # Track to avoid repetition
            self.asked_questions.append(question)
            
            return question
            
        except Exception as e:
            logger.warning(f"Generation error: {str(e)}. Using fallback.")
            return self.FALLBACK_QUESTIONS.get(
                missing_category, 
                "Can you tell me more about your symptoms?"
            )
    
    def _extract_question(self, text: str) -> str:
        """Extract clean question from model output"""
        # Remove "Question:" prefix if present
        if "Question:" in text:
            text = text.split("Question:")[-1].strip()
        
        # Find first sentence with question mark
        sentences = text.split('.')
        for sent in sentences:
            if '?' in sent:
                question = sent[:sent.index('?')+1].strip()
                return question.strip('"\'')
        
        # Fallback: take first line
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            question = lines[0].strip('"\'')
            if not question.endswith('?'):
                question += '?'
            return question
        
        return "Can you tell me more?"


# ========================================================================
# Agent 3: Intelligent Medical Report Generator
# ========================================================================

class DoctorAgent:
    """
    Generates comprehensive medical assessment reports based on patient conversation.
    Provides structured, actionable medical guidance.
    """
    
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor
        
    def generate_report(self, conversation_history: List[str]) -> str:
        """
        Generate comprehensive medical assessment report.
        
        Args:
            conversation_history: Complete conversation history
            
        Returns:
            Structured medical report
        """
        try:
            # Create conversation narrative
            conversation_text = "\n".join([f"Patient: {msg}" for msg in conversation_history])
            
            prompt = f"""You are an experienced medical professional. Generate a comprehensive assessment based on this patient consultation.

PATIENT CONSULTATION:
{conversation_text}

Provide a structured assessment with these sections:

1. SUMMARY: Brief overview of patient's primary concern (2-3 sentences)

2. REPORTED SYMPTOMS: List main symptoms user reported

3. ASSESSMENT: Initial clinical impression based on reported symptoms

4. POSSIBLE CONDITIONS: Most likely condition(s) based on presentation

5. CONTRIBUTING FACTORS: Potential underlying causes or triggers

6. RECOMMENDATIONS:
   • Immediate steps (what to do now)
   • When to seek urgent care
   • Suggested medical tests/examinations
   • General care advice
   • Warning signs requiring immediate attention

Be professional, thorough, and evidence-based. Use clear language.

MEDICAL ASSESSMENT:"""

            inputs = self.processor(
                text=prompt,
                images=None,
                return_tensors="pt",
                padding=True
            ).to(self.model.device)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=600,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    pad_token_id=self.processor.tokenizer.eos_token_id
                )
            
            report = self.processor.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Clean up response
            if "MEDICAL ASSESSMENT:" in report:
                report = report.split("MEDICAL ASSESSMENT:")[-1].strip()
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return f"Error generating report: {str(e)}"


# ========================================================================
# Main Consultation System
# ========================================================================

def interactive_consultation():
    """
    Main interactive consultation loop combining all agents.
    Provides a natural doctor-patient interaction experience.
    """
    print("=" * 75)
    print("MedAI MEDICAL CONSULTATION SYSTEM")
    print("Intelligent Multi-Agent Medical Assistant")
    print("=" * 75)
    
    # Initialize agents
    print("\n[Initializing agents...]")
    validation_agent = ValidationAgent(medgemma_model, medgemma_processor)
    question_agent = QuestionGeneratorAgent(medgemma_model, medgemma_processor)
    doctor_agent = DoctorAgent(medgemma_model, medgemma_processor)
    print("[✓ All agents ready]\n")
    
    # Initial greeting
    print("Doctor: Good morning! I'm here to help you today.")
    print("        Please tell me about your symptoms or health concerns.\n")
    
    conversation_history = []
    max_exchanges = 10
    
    # Main loop
    while len(conversation_history) < max_exchanges:
        try:
            # Get patient input
            user_input = input("Patient: ").strip()
            
            # Handle empty input
            if not user_input:
                print("\nDoctor: I'm here to listen. Please describe what's bothering you.\n")
                continue
            
            # Handle exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye', 'stop', 'no thanks']:
                print("\n" + "=" * 75)
                print("Doctor: Take care of yourself! Seek professional medical attention if needed.")
                print("=" * 75 + "\n")
                break
            
            # Add to history
            conversation_history.append(user_input)
            
            # Validate completeness
            should_continue, missing_category = validation_agent.evaluate_completeness(
                conversation_history
            )
            
            if not should_continue:
                # Generate report
                print("\nDoctor: Thank you for all that information. Let me prepare")
                print("        a comprehensive assessment for you.\n")
                
                # Generate and display report
                print("=" * 75)
                print("MEDICAL ASSESSMENT REPORT")
                print("=" * 75 + "\n")
                
                try:
                    report = doctor_agent.generate_report(conversation_history)
                    print(report)
                except Exception as e:
                    print(f"I apologize, there was an error generating the report.")
                    print(f"Technical error: {str(e)}")
                
                # Disclaimer
                print("\n" + "=" * 75)
                print("\n⚠️  IMPORTANT MEDICAL DISCLAIMER:")
                print("-" * 75)
                print("This AI assessment is for INFORMATIONAL PURPOSES ONLY.")
                print("It is NOT a substitute for professional medical diagnosis or treatment.")
                print("\nPlease:")
                print("  • Consult a qualified healthcare provider for accurate diagnosis")
                print("  • Seek immediate emergency care for severe symptoms")
                print("  • Do not delay necessary medical treatment based on this assessment")
                print("  • Share this report with your healthcare provider\n")
                print("=" * 75 + "\n")
                
                print("Doctor: I hope you feel better soon. Please seek professional")
                print("        medical attention for proper diagnosis and treatment. Take care!\n")
                break
            
            # Generate follow-up question
            try:
                question = question_agent.generate_question(
                    conversation_history,
                    missing_category
                )
                print(f"\nDoctor: {question}\n")
                
            except Exception as e:
                logger.error(f"Question generation failed: {str(e)}")
                print(f"\nDoctor: {QuestionGeneratorAgent.FALLBACK_QUESTIONS.get(missing_category, 'Can you tell me more?')}\n")
                
        except KeyboardInterrupt:
            print("\n\nDoctor: Take care of yourself. Goodbye.\n")
            break
        except EOFError:
            print("\n\nDoctor: Thank you for visiting. Take care!\n")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            print(f"\nI encountered an unexpected error. Please try again.\n")
    
    # Final summary
    if len(conversation_history) >= max_exchanges:
        print("\nDoctor: We've gathered good information. I recommend consulting")
        print("        with a healthcare professional for proper diagnosis. Take care!\n")


# ========================================================================
# Entry Point
# ========================================================================

if __name__ == "__main__":
    try:
        print("\n")
        interactive_consultation()
        print("\n" + "=" * 75)
        print("Session ended. Thank you for using MedAI Assistant.")
        print("=" * 75 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user. Exiting gracefully.\n")
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        print(f"\nFatal error: {str(e)}")
        print("Please contact support or restart the application.\n")
