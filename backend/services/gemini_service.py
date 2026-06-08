from google import genai
from PIL import Image
from dotenv import load_dotenv

import os

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# ==========================================
# GENERATE PROMPT
# ==========================================

def generate_prompt(image_path):

    image = Image.open(image_path)

    vision_prompt = """
You are an expert AI prompt engineer for 3D generation.

Analyze the sketch carefully.

The drawing may be:
- rough
- childish
- incomplete

But you must generate a PROFESSIONAL,
REALISTIC, DETAILED 3D prompt.

IMPORTANT:
Return ONLY the final prompt.
Do NOT explain anything.

Example:
Highly detailed realistic broadleaf tree
with dense green foliage, realistic bark,
natural branching structure, educational
3D model, centered composition
"""

    response = client.models.generate_content(

        model="gemini-3-flash-preview",

        contents=[
            vision_prompt,
            image
        ]
    )

    return response.text.strip()