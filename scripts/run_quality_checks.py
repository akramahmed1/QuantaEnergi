import subprocess
import sys

def run_command(cmd: list, description: str):
    print(f"Running {description}")
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(f"{description} PASSED")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"{description} FAILED")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_command(["ruff", "check", "."], "Ruff Linter")
    run_command(["ruff", "format", "--check", "."], "Ruff Formatter")
    print("Checks passed!")