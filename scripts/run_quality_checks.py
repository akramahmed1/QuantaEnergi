import subprocess

def run_command(cmd):
    subprocess.run(cmd, check=True)

run_command(["ruff", "check", "."])
run_command(["black", "--check", "."])
run_command(["mypy", "."])