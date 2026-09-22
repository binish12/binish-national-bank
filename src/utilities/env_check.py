import sys
from dotenv import load_dotenv
import os

# 1. Python version
print(f"Python version : {sys.version.split()[0]}")

# 2. Virtual environment detection
venv_active = sys.prefix != sys.base_prefix
print(f"Virtual env    : {'ACTIVE' if venv_active else 'NOT ACTIVE'}")

# 3. Load .env and read values
load_dotenv()

project_name = os.getenv("PROJECT_NAME")
environment = os.getenv("ENVIRONMENT")

print(f"Project name   : {project_name if project_name else 'MISSING'}")
print(f"Environment    : {environment if environment else 'MISSING'}")
