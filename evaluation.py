"""
Evaluation module for rating user prompts using LLM
This module provides functionality to evaluate and score prompts based on various criteria.
"""
import streamlit as st
from openai import OpenAI
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()

# Initialize OpenAI client - try multiple sources for API key
def get_openai_api_key():
    """Get OpenAI API key from multiple sources"""
    try:
        # Try Streamlit secrets first
        if hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    
    # Fallback to environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # If no key found, raise a clear error
    raise ValueError("No OpenAI API key found. Please set OPENAI_API_KEY in environment variables or Streamlit secrets.")

# Get the API key safely
OPENAI_API_KEY = get_openai_api_key()
client = OpenAI(api_key=OPENAI_API_KEY)

@dataclass
class PromptEvaluation:
    """Data class to store prompt evaluation results"""
    overall_score: float
    clarity_score: float
    specificity_score: float
    context_score: float
    structure_score: float

class PromptEvaluator:
    """Class to evaluate prompts using LLM"""
    
    def __init__(self, model: str = "gpt-4.1-mini-2025-04-14"):
        self.model = model
        self.evaluation_criteria = {
            "clarity": "How clear and understandable is the prompt?",
            "specificity": "How specific and detailed are the requirements?",
            "context": "How well does the prompt provide necessary context?",
            "structure": "How well-structured and organized is the prompt?"
        }
    
    def create_evaluation_prompt(self, user_prompt: str, industry: str = None) -> str:
        """Create a system prompt for evaluating user prompts"""
        
        evaluation_prompt = f"""
You are an expert prompt engineer and business consultant evaluating prompts for M&A and business strategy analysis.

*YOU WILL EVALUATE ALL BUSINESS CASES WITH HIGH SCRUTINY AND CRITICALLY HARSH MARKING*

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

Please provide your evaluation in the following JSON format:
{{
    "overall_score": <float 0-100>,
    "clarity_score": <float 0-100>,
    "specificity_score": <float 0-100>, 
    "context_score": <float 0-100>,
    "structure_score": <float 0-100>
}}

Focus on providing accurate numerical scores for business consulting and M&A context evaluation.
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
                temperature=0.3 # Lower temperature for more consistent evaluation

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
                    structure_score=float(result.get("structure_score", 0))
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
            structure_score=70.0
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
        
        print(f"\n{'-'*50}\n")

if __name__ == "__main__":
    # Run demo when file is executed directly
    demo_evaluation()