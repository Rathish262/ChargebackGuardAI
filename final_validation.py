import subprocess
import sys


TESTS = [
    "adversarial_tests.py",
    "edge_case_tests.py",
    "evaluate_pipeline.py",
    "pipeline_audit.py"
]


print("==========================================")
print("CHARGEBACKGUARD AI")
print("FINAL VALIDATION")
print("==========================================")
print()


failed = []


for test_file in TESTS:

    print()
    print("==========================================")
    print("RUNNING:", test_file)
    print("==========================================")
    print()

    result = subprocess.run(
        [sys.executable, test_file],
        capture_output=False
    )

    if result.returncode != 0:

        failed.append(test_file)

        print()
        print("STATUS:", test_file, "FAILED")

    else:

        print()
        print("STATUS:", test_file, "PASSED")


print()
print("==========================================")
print("FINAL VALIDATION SUMMARY")
print("==========================================")
print()

if failed:

    print("FINAL STATUS: FAIL")
    print()
    print("Failed tests:")

    for test in failed:
        print(" -", test)

else:

    print("FINAL STATUS: PASS")
    print()
    print("All validation stages completed successfully.")
    print()
    print("Decision engine tests: PASS")
    print("Edge-case tests: PASS")
    print("Pipeline evaluation: PASS")
    print("Pipeline audit: PASS")

print()
print("==========================================")
print("FINAL VALIDATION COMPLETED")
print("==========================================")