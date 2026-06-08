from google import genai
from PIL import Image

# ==========================================
# GEMINI API KEY
# ==========================================

client = genai.Client(
    api_key="YOUR_API_KEY"
)

# ==========================================
# LOAD IMAGE
# ==========================================

image = Image.open("test.png")

# ==========================================
# PROMPT
# ==========================================

prompt = """
Analyze this drawing carefully.

Identify:
1. What object is drawn
2. Important characteristics
3. Whether it resembles:
   - normal tree
   - christmas tree
   - palm tree
   - coconut tree
   - etc.

Give a short semantic description.
"""

# ==========================================
# SEND TO GEMINI
# ==========================================

response = client.models.generate_content(
    model="gemini-2.5-flash",

    contents=[
        prompt,
        image
    ]
)

# ==========================================
# OUTPUT
# ==========================================

print("\n========== GEMINI RESPONSE ==========\n")

print(response.text)