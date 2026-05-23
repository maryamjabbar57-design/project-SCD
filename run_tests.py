import unittest
import sys

def run_all_tests():
    """
    Automated test runner that discovers and executes all unit tests
    in the 'tests' directory and generates a clean console report.
    """
    print("==================================================")
    print("   ONLINE QUIZ GAME - AUTOMATED TEST RUNNER       ")
    print("==================================================")
    
    # Discover and load all tests from the tests directory
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir="tests")
    
    # Run the tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print custom summary block
    print("\n==================================================")
    print("                TEST RESULTS SUMMARY              ")
    print("==================================================")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("==================================================")
    
    if not result.wasSuccessful():
        print("[FAIL] SOME TESTS FAILED!")
        sys.exit(1)
    else:
        print("[SUCCESS] ALL TESTS PASSED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    run_all_tests()
