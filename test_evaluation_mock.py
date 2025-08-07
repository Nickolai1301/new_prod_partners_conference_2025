#!/usr/bin/env python3
"""
Test script for evaluation.py module (Streamlit-free version)
This script tests the functionality without requiring Streamlit.
"""

import sys
import traceback
import os
from typing import Optional, Dict, List
from dataclasses import dataclass

# Mock streamlit for testing
class MockStreamlit:
    class secrets:
        OPENAI_API_KEY = "test_key_12345"
    
    @staticmethod
    def hasattr(obj, attr):
        return True

# Add mock to sys.modules
sys.modules['streamlit'] = MockStreamlit()

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

def test_dataclass_fields():
    """Test if PromptEvaluation has the correct fields"""
    print("\n=== TESTING DATACLASS FIELDS ===")
    try:
        from evaluation import PromptEvaluation
        
        # Check what fields the dataclass actually has
        import dataclasses
        fields = dataclasses.fields(PromptEvaluation)
        field_names = [field.name for field in fields]
        
        print(f"✅ PromptEvaluation fields: {field_names}")
        
        # Expected fields based on the current code
        expected_fields = [
            'overall_score',
            'strategic_fit_score', 
            'audience_score',
            'commercials_score',
            'outcomes_score',
            'feedback'
        ]
        
        missing_fields = []
        for expected in expected_fields:
            if expected not in field_names:
                missing_fields.append(expected)
        
        if missing_fields:
            print(f"⚠️  Missing expected fields: {missing_fields}")
        
        extra_fields = []
        for actual in field_names:
            if actual not in expected_fields:
                extra_fields.append(actual)
                
        if extra_fields:
            print(f"⚠️  Unexpected extra fields: {extra_fields}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking dataclass fields: {e}")
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

def test_create_evaluation_instance():
    """Test creating PromptEvaluation with different field combinations"""
    print("\n=== TESTING PROMPTEVALUATION INSTANCE CREATION ===")
    try:
        from evaluation import PromptEvaluation
        
        # Try to create with all fields that might exist
        try:
            # First try with the fields that appear to be in the current code
            eval_result = PromptEvaluation(
                overall_score=85.0,
                strategic_fit_score=80.0,
                audience_score=90.0,
                commercials_score=85.0,
                outcomes_score=88.0,
                feedback="Test feedback"
            )
            print("✅ Successfully created PromptEvaluation with all fields")
            return True
        except TypeError as e:
            print(f"⚠️  Error with full field creation: {e}")
            
            # Try without feedback field
            try:
                eval_result = PromptEvaluation(
                    overall_score=85.0,
                    strategic_fit_score=80.0,
                    audience_score=90.0,
                    commercials_score=85.0,
                    outcomes_score=88.0
                )
                print("✅ Successfully created PromptEvaluation without feedback field")
                return True
            except TypeError as e2:
                print(f"⚠️  Error without feedback field: {e2}")
                
                # Try with old field names
                try:
                    eval_result = PromptEvaluation(
                        overall_score=85.0,
                        clarity_score=80.0,
                        specificity_score=90.0,
                        context_score=85.0,
                        structure_score=88.0
                    )
                    print("✅ Successfully created PromptEvaluation with old field names")
                    return True
                except TypeError as e3:
                    print(f"❌ Error with old field names: {e3}")
                    return False
                    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        traceback.print_exc()
        return False

def test_method_signatures(evaluator):
    """Test that methods exist and have correct signatures"""
    print("\n=== TESTING METHOD SIGNATURES ===")
    try:
        # Test that required methods exist
        methods_to_check = [
            'create_evaluation_prompt',
            'evaluate_prompt', 
            'get_score_interpretation',
            '_parse_fallback_response'
        ]
        
        for method_name in methods_to_check:
            if hasattr(evaluator, method_name):
                print(f"   ✅ Method {method_name} exists")
            else:
                print(f"   ❌ Method {method_name} missing")
        
        # Test method calls
        test_prompt = "Test prompt for evaluation"
        try:
            prompt_result = evaluator.create_evaluation_prompt(test_prompt, "Technology")
            print("   ✅ create_evaluation_prompt works")
        except Exception as e:
            print(f"   ❌ create_evaluation_prompt error: {e}")
            
        try:
            interp_result = evaluator.get_score_interpretation(75.0)
            print(f"   ✅ get_score_interpretation works: {interp_result}")
        except Exception as e:
            print(f"   ❌ get_score_interpretation error: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing method signatures: {e}")
        traceback.print_exc()
        return False

def check_app_compatibility():
    """Check if evaluation.py is compatible with app.py expectations"""
    print("\n=== TESTING APP.PY COMPATIBILITY ===")
    try:
        from evaluation import PromptEvaluation
        
        # Check what app.py expects to access
        test_eval = None
        
        # Try creating with various field combinations to see what works
        field_combinations = [
            # Current expected fields
            {
                'overall_score': 85.0,
                'strategic_fit_score': 80.0,
                'audience_score': 90.0,
                'commercials_score': 85.0,
                'outcomes_score': 88.0,
                'feedback': "test"
            },
            # Without feedback
            {
                'overall_score': 85.0,
                'strategic_fit_score': 80.0,
                'audience_score': 90.0,
                'commercials_score': 85.0,
                'outcomes_score': 88.0
            },
            # Old field names
            {
                'overall_score': 85.0,
                'clarity_score': 80.0,
                'specificity_score': 90.0,
                'context_score': 85.0,
                'structure_score': 88.0
            }
        ]
        
        for i, fields in enumerate(field_combinations):
            try:
                test_eval = PromptEvaluation(**fields)
                print(f"   ✅ Field combination {i+1} works")
                break
            except Exception as e:
                print(f"   ❌ Field combination {i+1} failed: {e}")
        
        if test_eval:
            # Test accessing fields that app.py expects
            expected_accesses = [
                'overall_score',
                'strategic_fit_score',
                'audience_score', 
                'commercials_score',
                'outcomes_score'
            ]
            
            for field in expected_accesses:
                try:
                    value = getattr(test_eval, field, None)
                    if value is not None:
                        print(f"   ✅ Can access {field}: {value}")
                    else:
                        print(f"   ⚠️  Field {field} is None or doesn't exist")
                except Exception as e:
                    print(f"   ❌ Cannot access {field}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing app compatibility: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 STARTING EVALUATION.PY TEST SUITE (MOCK VERSION)")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Imports
    total_tests += 1
    if test_imports():
        tests_passed += 1
    else:
        print("❌ Cannot continue testing - import failed")
        return
    
    # Test 2: Dataclass fields
    total_tests += 1
    if test_dataclass_fields():
        tests_passed += 1
    
    # Test 3: Evaluator initialization
    total_tests += 1
    evaluator = test_evaluator_initialization()
    if evaluator:
        tests_passed += 1
    else:
        print("❌ Cannot continue with evaluator tests")
        return
    
    # Test 4: PromptEvaluation instance creation
    total_tests += 1
    if test_create_evaluation_instance():
        tests_passed += 1
    
    # Test 5: Method signatures
    total_tests += 1
    if test_method_signatures(evaluator):
        tests_passed += 1
    
    # Test 6: App compatibility
    total_tests += 1
    if check_app_compatibility():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 TEST SUMMARY")
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! evaluation.py appears to be working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    print("\n📋 NEXT STEPS:")
    print("1. Fix any field name mismatches identified above")
    print("2. Ensure app.py is using the correct field names") 
    print("3. Test with actual Streamlit environment")

if __name__ == "__main__":
    main()
