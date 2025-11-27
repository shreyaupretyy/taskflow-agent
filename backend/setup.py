#!/usr/bin/env python
"""Setup script for TaskFlow Agent backend."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command: list, description: str):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return False


def main():
    """Main setup function."""
    print("TaskFlow Agent - Backend Setup")
    print("="*60)
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        print("\nCreating virtual environment...")
        if not run_command([sys.executable, "-m", "venv", "venv"], "Creating virtual environment"):
            sys.exit(1)
    else:
        print("\nVirtual environment already exists")
    
    # Determine pip path
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip.exe"
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip
    run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip")
    
    # Install requirements
    if not run_command([str(pip_path), "install", "-r", "requirements.txt"], "Installing requirements"):
        print("\nWarning: Some packages failed to install. You may need to install them manually.")
    
    # Copy environment file
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("\nCopying .env.example to .env...")
        env_file.write_text(env_example.read_text())
        print("Please edit .env file with your configuration")
    
    print("\n" + "="*60)
    print("Setup completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Activate the virtual environment:")
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Edit .env file with your configuration")
    print("3. Start PostgreSQL and Redis")
    print("4. Run database migrations:")
    print("   alembic upgrade head")
    print("5. Start the application:")
    print("   python -m uvicorn app.main:app --reload")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
