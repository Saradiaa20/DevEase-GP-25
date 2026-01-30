"""
Configuration settings for the backend API
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
API_RELOAD = os.getenv("API_RELOAD", "true").lower() == "true"

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# File Upload Configuration
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 10 * 1024 * 1024))  # 10MB
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads"))
ALLOWED_EXTENSIONS = ['.py', '.java', '.js', '.cpp', '.cs', '.php']

# Model Configuration
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "complexity_model.pkl"))
DATASET_PATH = os.getenv("DATASET_PATH", str(BASE_DIR / "dataset1.csv"))

# Storage Configuration
STORAGE_FOLDER = os.getenv("STORAGE_FOLDER", str(BASE_DIR / "project_files"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(BASE_DIR / "logs" / "app.log"))

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STORAGE_FOLDER, exist_ok=True)
os.makedirs(Path(LOG_FILE).parent, exist_ok=True)
