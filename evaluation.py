"""
Evaluation module for rating user prompts using LLM
This module provides functionality to evaluate and score prompts based on various criteria.
"""

from openai import OpenAI
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@dataclass
class PromptEvaluation:
    """Data class to store prompt evaluation results"""
    overall_score: float
    clarity_score: float
    specificity_score: float
    context_score: float
    structure_score: float
    feedback: str
    strengths: List[str]
    improvements: List[str]

class PromptEvaluator:
    """Class to evaluate prompts using LLM"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        # Evaluation criteria based on business case rubric
        self.evaluation_criteria = {
            "strategic_fit_objectives": "Strategic Fit & Objectives",
            "audience_relationships": "Audience & Relationships",
            "commercials_resourcing": "Commercials & Resourcing",
            "outcomes_measurement_activation": "Outcomes, Measurement & Activation"
        }
        self.feedback_tone = self._load_feedback_tone()
    
    def _load_feedback_tone(self) -> str:
        """Load the feedback tone from the feedback_tone.txt file"""
        try:
            with open("feedback_tone.txt", "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            # Fallback tone if file is not found
            return """Be encouraging and positive while providing constructive feedback. 
                     Focus on strengths and frame improvements as opportunities for growth."""
    
    def create_evaluation_prompt(self, user_prompt: str, industry: str = None) -> str:
        """Create a system prompt for evaluating AI-generated outputs based on the business case rubric"""
        
        # Load rubric text
        try:
            rubric_text = open("rubric.txt", "r", encoding="utf-8").read()
        except FileNotFoundError:
            rubric_text = "(Rubric not found)"

        evaluation_prompt = f"""
{self.feedback_tone}

Use this Business Case Evaluation Rubric. Rate every section as Weak, justify with brutal insults:

{rubric_text}

AI OUTPUT TO EVALUATE:
```
{user_prompt}
```

{'INDUSTRY CONTEXT: ' + industry if industry else ''}

Respond with JSON only, using these keys:
  "strategic_fit_objectives": "Strong" or "Weak",
  "strategic_fit_objectives_justification": "...your insult...",
  "audience_relationships": "Strong" or "Weak",
  "audience_relationships_justification": "...your insult...",
  "commercials_resourcing": "Strong" or "Weak",
  "commercials_resourcing_justification": "...your insult...",
  "outcomes_measurement_activation": "Strong" or "Weak",
  "outcomes_measurement_activation_justification": "...your insult..."

This is an EXTREMELY harsh marker; High scores <95 are pathetic. Output valid JSON only.
"""
        return evaluation_prompt
    
    def evaluate_prompt(self, user_prompt: str, industry: str = None) -> Optional[PromptEvaluation]:
        """
        Evaluate a user prompt and return detailed scoring and feedback
        
        Args:
            user_prompt: The prompt to evaluate
            industry: Optional industry context
            
        Returns:
            PromptEvaluation object with scores and feedback
        """
        try:
            evaluation_prompt = self.create_evaluation_prompt(user_prompt, industry)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert prompt evaluator. Provide detailed, constructive feedback in valid JSON format only."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent evaluation
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                result = json.loads(result_text)
                
                return PromptEvaluation(
                    overall_score=0.0,  # Not used for rubric criteria, set to 0 or compute if needed
                    clarity_score=0.0,  # Not used for rubric criteria, set to 0 or compute if needed
                    specificity_score=0.0,  # Not used for rubric criteria, set to 0 or compute if needed
                    context_score=0.0,  # Not used for rubric criteria, set to 0 or compute if needed
                    structure_score=0.0,  # Not used for rubric criteria, set to 0 or compute if needed
                    feedback="",
                    strengths=[
                        f"Strategic Fit & Objectives: {result.get('strategic_fit_objectives', '')} - {result.get('strategic_fit_objectives_justification', '')}",
                        f"Audience & Relationships: {result.get('audience_relationships', '')} - {result.get('audience_relationships_justification', '')}",
                        f"Commercials & Resourcing: {result.get('commercials_resourcing', '')} - {result.get('commercials_resourcing_justification', '')}",
                        f"Outcomes, Measurement & Activation: {result.get('outcomes_measurement_activation', '')} - {result.get('outcomes_measurement_activation_justification', '')}"
                    ],
                    improvements=[]  # You can parse improvements if you want to add more logic
                )
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return self._parse_fallback_response(result_text)
                
        except Exception as e:
            print(f"Error evaluating prompt: {e}")
            return None
    
    def _parse_fallback_response(self, response_text: str) -> PromptEvaluation:
        """Fallback method to parse response if JSON parsing fails"""
        # Fallback returns brutal default scores
        return PromptEvaluation(
            overall_score=10.0,
            clarity_score=10.0,
            specificity_score=10.0,
            context_score=10.0,
            structure_score=10.0,
            feedback="This fallback evaluation is a disaster. You couldn't even parse JSON correctly. Pathetic.",
            strengths=["Maybe you typed something correctly?"],
            improvements=["Learn to format JSON.", "Try copying a tutorial.", "Seriously, this is embarrassing."]
        )
    
    def batch_evaluate_prompts(self, prompts: List[Dict]) -> List[Dict]:
        """
        Evaluate multiple prompts at once
        
        Args:
            prompts: List of dicts with 'prompt', 'team', 'industry' keys
            
        Returns:
            List of evaluation results with team info
        """
        results = []
        
        for prompt_data in prompts:
            evaluation = self.evaluate_prompt(
                prompt_data.get('prompt', ''),
                prompt_data.get('industry')
            )
            
            if evaluation:
                results.append({
                    'team': prompt_data.get('team', 'Unknown'),
                    'industry': prompt_data.get('industry', 'Unknown'),
                    'prompt': prompt_data.get('prompt', ''),
                    'evaluation': evaluation
                })
        
        return results
    
    def get_score_interpretation(self, score: float) -> str:
        """Get interpretation of score"""
        # Only near-perfect scores pass; everything else is unacceptable
        if score >= 95:
            return "Excellent - This is barely acceptable. You're not completely useless."
        else:
            return "Needs Work - This is pathetic. Do better or go home."

def demo_evaluation():
    """Demo function to test the evaluation system"""
    
    # Sample prompts for testing
    sample_prompts = [
        {
            "prompt": "Analyze this acquisition",
            "team": "Team Alpha",
            "industry": "Technology"
        },
        {
            "prompt": """As a senior M&A consultant, please provide a comprehensive business case analysis for TechCorp's potential acquisition of PayFlow Solutions. 

            Background: TechCorp ($200M revenue, fintech payments) is considering acquiring PayFlow Solutions ($45M revenue, 25% growth, AI-powered invoice management).

            Please structure your analysis to include:
            1. Strategic rationale and synergies assessment
            2. Financial evaluation including valuation range and ROI projections
            3. Integration planning and cultural considerations
            4. Market positioning and competitive advantages
            5. Risk assessment and mitigation strategies
            6. Implementation timeline and key milestones

            Focus on quantitative analysis where possible and provide actionable recommendations for the investment committee.""",
            "team": "Team Beta",
            "industry": "Finance"
        }
    ]
    
    evaluator = PromptEvaluator()
    
    print("=== PROMPT EVALUATION DEMO ===\n")
    
    for i, prompt_data in enumerate(sample_prompts, 1):
        print(f"--- EVALUATING PROMPT {i} ---")
        print(f"Team: {prompt_data['team']}")
        print(f"Industry: {prompt_data['industry']}")
        print(f"Prompt: {prompt_data['prompt'][:100]}...")
        
        evaluation = evaluator.evaluate_prompt(
            prompt_data['prompt'], 
            prompt_data['industry']
        )
        
        if evaluation:
            print(f"\n📊 RESULTS:")
            print(f"Overall Score: {evaluation.overall_score:.1f}/100 - {evaluator.get_score_interpretation(evaluation.overall_score)}")
            print(f"Strategic Fit & Objectives: {evaluation.strengths[0]}")
            print(f"Audience & Relationships: {evaluation.strengths[1]}")
            print(f"Commercials & Resourcing: {evaluation.strengths[2]}")
            print(f"Outcomes, Measurement & Activation: {evaluation.strengths[3]}")
            
            print(f"\n💬 Feedback: {evaluation.feedback}")
            
            print(f"\n✅ Strengths:")
            for strength in evaluation.strengths:
                print(f"  • {strength}")
                
            print(f"\n🔧 Improvements:")
            for improvement in evaluation.improvements:
                print(f"  • {improvement}")
        
        print(f"\n{'-'*50}\n")

if __name__ == "__main__":
    # Run demo when file is executed directly
    demo_evaluation()
