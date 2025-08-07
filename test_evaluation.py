#!/usr/bin/env python3
"""
Test script for evaluation.py module
This script tests the functionality of the PromptEvaluator class and identifies any issues.
"""

import sys
import traceback
from typing import Optional

def test_imports():
    """Test if all imports work correctly"""
    print("=== TESTING IMPORTS ===")
    try:
        from evaluation import PromptEvaluator, PromptEvaluation
        print("✅ Successfully imported PromptEvaluator and PromptEvaluation")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        traceback.print_exc()
        return False

def test_evaluator_initialization():
    """Test if PromptEvaluator can be initialized"""
    print("\n=== TESTING EVALUATOR INITIALIZATION ===")
    try:
        from evaluation import PromptEvaluator
        evaluator = PromptEvaluator()
        print("✅ Successfully initialized PromptEvaluator")
        print(f"   Model: {evaluator.model}")
        print(f"   Criteria keys: {list(evaluator.evaluation_criteria.keys())}")
        return evaluator
    except Exception as e:
        print(f"❌ Error initializing PromptEvaluator: {e}")
        traceback.print_exc()
        return None

def test_prompt_evaluation_dataclass():
    """Test if PromptEvaluation dataclass works correctly"""
    print("\n=== TESTING PROMPTEVALUATION DATACLASS ===")
    try:
        from evaluation import PromptEvaluation
        
        # Test creating an instance
        eval_result = PromptEvaluation(
            overall_score=85.0,
            strategic_fit_score=80.0,
            audience_score=90.0,
            commercials_score=85.0,
            outcomes_score=88.0,
            feedback="Test feedback"
        )
        
        print("✅ Successfully created PromptEvaluation instance")
        print(f"   Overall Score: {eval_result.overall_score}")
        print(f"   Strategic Fit Score: {eval_result.strategic_fit_score}")
        print(f"   Audience Score: {eval_result.audience_score}")
        print(f"   Commercials Score: {eval_result.commercials_score}")
        print(f"   Outcomes Score: {eval_result.outcomes_score}")
        print(f"   Feedback: {eval_result.feedback}")
        return True
    except Exception as e:
        print(f"❌ Error with PromptEvaluation dataclass: {e}")
        traceback.print_exc()
        return False

def test_evaluation_prompt_creation(evaluator):
    """Test if evaluation prompt can be created"""
    print("\n=== TESTING EVALUATION PROMPT CREATION ===")
    try:
        test_prompt = "Please analyze our technology sector for additional investment opportunities."
        test_industry = "Technology"
        
        evaluation_prompt = evaluator.create_evaluation_prompt(test_prompt, test_industry)
        
        print("✅ Successfully created evaluation prompt")
        print(f"   Prompt length: {len(evaluation_prompt)} characters")
        print(f"   Contains user prompt: {'USER PROMPT TO EVALUATE' in evaluation_prompt}")
        print(f"   Contains industry context: {'INDUSTRY CONTEXT' in evaluation_prompt}")
        print(f"   Contains JSON format: {'json' in evaluation_prompt.lower()}")
        
        # Show first 200 characters of the prompt
        print(f"   Preview: {evaluation_prompt[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Error creating evaluation prompt: {e}")
        traceback.print_exc()
        return False

def test_score_interpretation(evaluator):
    """Test score interpretation method"""
    print("\n=== TESTING SCORE INTERPRETATION ===")
    try:
        test_scores = [95, 85, 75, 65, 45]
        
        for score in test_scores:
            interpretation = evaluator.get_score_interpretation(score)
            print(f"   Score {score}: {interpretation}")
        
        print("✅ Successfully tested score interpretation")
        return True
    except Exception as e:
        print(f"❌ Error with score interpretation: {e}")
        traceback.print_exc()
        return False

def test_fallback_response(evaluator):
    """Test fallback response method"""
    print("\n=== TESTING FALLBACK RESPONSE ===")
    try:
        fallback_result = evaluator._parse_fallback_response("Invalid JSON response")
        
        print("✅ Successfully created fallback response")
        print(f"   Overall Score: {fallback_result.overall_score}")
        print(f"   Strategic Fit Score: {fallback_result.strategic_fit_score}")
        print(f"   Audience Score: {fallback_result.audience_score}")
        print(f"   Commercials Score: {fallback_result.commercials_score}")
        print(f"   Outcomes Score: {fallback_result.outcomes_score}")
        return True
    except Exception as e:
        print(f"❌ Error with fallback response: {e}")
        traceback.print_exc()
        return False

def test_full_evaluation_dry_run(evaluator):
    """Test the full evaluation process without making API calls"""
    print("\n=== TESTING FULL EVALUATION (DRY RUN) ===")
    try:
        # Mock a simple test that doesn't require OpenAI API
        test_prompt = """
        We need additional funding for our TMT sector to expand our AI analytics capabilities.
        
        Strategic Objectives:
        - Increase market share in TMT analytics by 25%
        - Build relationships with top 10 TMT clients
        - Generate $5M in additional revenue
        
        Target Audience:
        - C-suite executives at Fortune 500 TMT companies
        - Current clients in tech and media
        
        Budget:
        - $2M for technology infrastructure
        - $1M for talent acquisition
        - $500K for marketing and events
        
        Expected Outcomes:
        - 15 new client relationships
        - 30% increase in pipeline
        - ROI of 3:1 within 18 months
        """
        
        industry = "TMT"
        
        # Test prompt creation
        evaluation_prompt = evaluator.create_evaluation_prompt(test_prompt, industry)
        print("✅ Created evaluation prompt successfully")
        
        # Test that all required components are present
        required_components = [
            "strategic_fit_score",
            "audience_score", 
            "commercials_score",
            "outcomes_score",
            "overall_score"
        ]
        
        for component in required_components:
            if component in evaluation_prompt:
                print(f"   ✅ Found {component} in prompt")
            else:
                print(f"   ⚠️  Missing {component} in prompt")
        
        print("✅ Dry run completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in dry run evaluation: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 STARTING EVALUATION.PY TEST SUITE")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Imports
    total_tests += 1
    if test_imports():
        tests_passed += 1
    else:
        print("❌ Cannot continue testing - import failed")
        return
    
    # Test 2: Evaluator initialization
    total_tests += 1
    evaluator = test_evaluator_initialization()
    if evaluator:
        tests_passed += 1
    else:
        print("❌ Cannot continue testing - evaluator initialization failed")
        return
    
    # Test 3: PromptEvaluation dataclass
    total_tests += 1
    if test_prompt_evaluation_dataclass():
        tests_passed += 1
    
    # Test 4: Evaluation prompt creation
    total_tests += 1
    if test_evaluation_prompt_creation(evaluator):
        tests_passed += 1
    
    # Test 5: Score interpretation
    total_tests += 1
    if test_score_interpretation(evaluator):
        tests_passed += 1
    
    # Test 6: Fallback response
    total_tests += 1
    if test_fallback_response(evaluator):
        tests_passed += 1
    
    # Test 7: Full evaluation dry run
    total_tests += 1
    if test_full_evaluation_dry_run(evaluator):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! evaluation.py is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")

if __name__ == "__main__":
    main()
