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
        self.evaluation_criteria = {
            "clarity": "How clear and understandable is the prompt?",
            "specificity": "How specific and detailed are the requirements?",
            "context": "How well does the prompt provide necessary context?",
            "structure": "How well-structured and organized is the prompt?"
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
        """Create a system prompt for evaluating user prompts"""
        
        evaluation_prompt = f"""
{self.feedback_tone}

You are an expert prompt engineer and business consultant evaluating prompts for M&A and business strategy analysis. Use the cheerful, encouraging tone described above in all your feedback.

Please evaluate the following user prompt based on these criteria:

1. **Clarity (25%)**: How clear and understandable is the prompt? Is it easy to follow?
2. **Specificity (25%)**: How specific and detailed are the requirements? Does it ask for concrete deliverables?
3. **Context (25%)**: How well does the prompt provide necessary background and context for analysis?
4. **Structure (25%)**: How well-organized is the prompt? Does it follow a logical flow?

USER PROMPT TO EVALUATE:
```
{user_prompt}
```

{f"INDUSTRY CONTEXT: {industry}" if industry else ""}

Please provide your evaluation in the following JSON format, using the enthusiastic and encouraging tone throughout:
{{
    "overall_score": <float 0-100>,
    "clarity_score": <float 0-100>,
    "specificity_score": <float 0-100>, 
    "context_score": <float 0-100>,
    "structure_score": <float 0-100>,
    "feedback": "<encouraging overall feedback paragraph using the cheerful tone>",
    "strengths": ["<positive strength 1>", "<positive strength 2>", "<positive strength 3>"],
    "improvements": ["<encouraging improvement 1>", "<encouraging improvement 2>", "<encouraging improvement 3>"]
}}

Remember: Frame all feedback positively and encouragingly! Focus on business consulting and M&A context while maintaining an upbeat, supportive tone that makes the user excited to improve their prompting skills.
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
                    overall_score=float(result.get("overall_score", 0)),
                    clarity_score=float(result.get("clarity_score", 0)),
                    specificity_score=float(result.get("specificity_score", 0)),
                    context_score=float(result.get("context_score", 0)),
                    structure_score=float(result.get("structure_score", 0)),
                    feedback=result.get("feedback", ""),
                    strengths=result.get("strengths", []),
                    improvements=result.get("improvements", [])
                )
            except json.JSONDecodeError:
                # Fallback parsing if JSON is malformed
                return self._parse_fallback_response(result_text)
                
        except Exception as e:
            print(f"Error evaluating prompt: {e}")
            return None
    
    def _parse_fallback_response(self, response_text: str) -> PromptEvaluation:
        """Fallback method to parse response if JSON parsing fails"""
        return PromptEvaluation(
            overall_score=70.0,  # Default score
            clarity_score=70.0,
            specificity_score=70.0,
            context_score=70.0,
            structure_score=70.0,
            feedback="Evaluation completed with limited parsing. Please check prompt formatting.",
            strengths=["Prompt submitted successfully"],
            improvements=["Consider more specific requirements", "Add more context", "Improve structure"]
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
        if score >= 90:
            return "Excellent - Professional quality prompt"
        elif score >= 80:
            return "Very Good - Strong prompt with minor improvements needed"
        elif score >= 70:
            return "Good - Solid prompt, some enhancements would help"
        elif score >= 60:
            return "Fair - Decent foundation, needs significant improvement"
        else:
            return "Needs Work - Major improvements required"

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
            print(f"Clarity: {evaluation.clarity_score:.1f}")
            print(f"Specificity: {evaluation.specificity_score:.1f}")
            print(f"Context: {evaluation.context_score:.1f}")
            print(f"Structure: {evaluation.structure_score:.1f}")
            
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