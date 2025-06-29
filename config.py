# config.py
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# GCP Configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_LOCATION = "us-central1"
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
DEFAULT_REFERENCE_IMAGE_GCS_URI = "Reference_Image.png"

# Gradio UI Configuration (optional, but good for consistency)
CUSTOM_CSS = """
body { font-family: 'Roboto', sans-serif; background-color: #f8f8f8; color: #333; }
h1 { color: #4CAF50; text-align: center; font-size: 2.5em; margin-bottom: 20px; }
.gr-button { background-color: #4CAF50 !important; color: white !important; border-radius: 8px !important; padding: 12px 20px !important; font-size: 1.1em !important; border: none !important; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
.gr-button:hover { background-color: #45a049 !important; box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15); }
.gradio-container { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important; border-radius: 12px !important; background-color: black !important; padding: 30px !important; max-width: 1200px; margin: 30px auto; }
.gr-textbox, .gr-image { border-radius: 8px !important; border: 1px solid #ddd !important; }
.gr-label { font-weight: bold; color: #555; }
.gr-row, .gr-column { gap: 20px; }
.gr-markdown h3 { color: #666; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
"""

# Base prompts
SYSTEM_INSTRUCTION_FOR_GEMINI = "You are an expert in creating impactful product advertisements. Your goal is to generate precise and effective visuals for advertising campaigns."
BASE_USER_IMAGE_PROMPT = '''Generate an ad featuring the smoothened silhouette of a product, filled with a word cloud of its key attributes from the provided text. The brand name should be prominent. The word cloud should be clear, not crowded, and use color-coding for different attribute categories. Only the product silhouette should be visible.'''
