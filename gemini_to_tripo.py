from google import genai
from PIL import Image

import requests
import time
import json

# =====================================================
# API KEYS
# =====================================================

GEMINI_API_KEY = "Your_api_key"

TRIPO_API_KEY = "Your_api_key"

# =====================================================
# GEMINI CLIENT
# =====================================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# =====================================================
# LOAD IMAGE
# =====================================================

image = Image.open("test.png")

# =====================================================
# GEMINI PROMPT
# =====================================================

vision_prompt = """
You are an expert AI prompt engineer for 3D generation.

Your job is to analyze rough hand-drawn sketches
and convert them into PROFESSIONAL, DETAILED,
HIGH-QUALITY 3D generation prompts.

The user drawings may be:
- childish
- incomplete
- rough
- simple doodles

But your output must ALWAYS create:
- realistic
- visually appealing
- professional
- educational-quality
3D models.

IMPORTANT RULES:

1. Understand the REAL object/concept.
2. Infer missing details intelligently.
3. Enhance the object professionally.
4. Add realistic structure and appearance.
5. Make prompts visually rich.
6. Keep object identity correct.
7. Add educational realism where appropriate.
8. Output ONLY the final prompt.
9. Do NOT explain anything.
10. Do NOT use bullet points.
11. Do NOT use markdown.

GOOD EXAMPLES:

Input:
rough tree doodle

Output:
Highly detailed realistic broadleaf tree with
dense green foliage, textured natural bark,
realistic branching structure, botanical accuracy,
clean proportions, educational 3D model

Input:
rough airplane sketch

Output:
Highly detailed realistic commercial passenger jet
aircraft with aerodynamic wings, twin turbofan
engines, clean fuselage, realistic aviation design,
professional 3D model

Input:
rough Christmas tree

Output:
Highly detailed realistic Christmas tree with
lush green pine branches, glowing decorative
lights, colorful ornaments, golden star topper,
gift boxes underneath, cinematic realistic 3D model

Now analyze the uploaded sketch carefully
and generate ONLY the final professional 3D prompt.
"""

# =====================================================
# SEND TO GEMINI
# =====================================================

vision_response = client.models.generate_content(

    model="gemini-3-flash-preview",

    contents=[
        vision_prompt,
        image
    ]
)

generated_prompt = vision_response.text.strip()

print("\n========== GENERATED PROMPT ==========\n")

print(generated_prompt)

# =====================================================
# TRIPO HEADERS
# =====================================================

headers = {
    "Authorization": f"Bearer {TRIPO_API_KEY}",
    "Content-Type": "application/json"
}

# =====================================================
# CREATE TRIPO TASK
# =====================================================

generate_url = \
    "https://api.tripo3d.ai/v2/openapi/task"

payload = {

    "type": "text_to_model",

    "prompt": generated_prompt,

    # =============================================
    # DEVELOPMENT SETTINGS
    # =============================================

    "texture": True,
    "pbr": True
}

response = requests.post(
    generate_url,
    headers=headers,
    json=payload
)

data = response.json()

print("\n========== TRIPO TASK RESPONSE ==========\n")

print(json.dumps(data, indent=2))

# =====================================================
# GET TASK ID
# =====================================================

task_id = data["data"]["task_id"]

print("\nTASK ID:")
print(task_id)

# =====================================================
# CHECK STATUS
# =====================================================

status_url = \
    f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"

while True:

    status_response = requests.get(
        status_url,
        headers=headers
    )

    status_data = status_response.json()

    print("\n========== STATUS ==========\n")

    print(json.dumps(status_data, indent=2))

    status = status_data["data"]["status"]

    # =================================================
    # SUCCESS
    # =================================================

    if status == "success":

        print("\n✅ 3D MODEL GENERATED SUCCESSFULLY!\n")

        result = status_data["data"]["result"]

        print("\n========== RESULT ==========\n")

        print(json.dumps(result, indent=2))

        # =============================================
        # FIND MODEL URL SAFELY
        # =============================================

        model_url = None

        # CASE 1 → PBR MODEL

        if "pbr_model" in result:

            model_url = \
                result["pbr_model"]["url"]

        # CASE 2 → BASE MODEL

        elif "model" in result:

            model_url = \
                result["model"]["url"]

        # CASE 3 → BASE MODEL

        elif "base_model" in result:

            model_url = \
                result["base_model"]["url"]

        # =============================================
        # IF STILL NONE
        # =============================================

        if not model_url:

            print(
                "\n❌ Could not find model URL."
            )

            break

        print("\n========== MODEL URL ==========\n")

        print(model_url)

        # =============================================
        # DOWNLOAD MODEL
        # =============================================

        print("\nDownloading model...\n")

        model_response = requests.get(model_url)

        output_file = "generated_model.glb"

        with open(output_file, "wb") as f:

            f.write(model_response.content)

        print(
            f"\n✅ Model saved as: {output_file}"
        )

        break

    # =================================================
    # FAILED
    # =================================================

    elif status == "failed":

        print("\n❌ 3D generation failed.")

        break

    # =================================================
    # STILL PROCESSING
    # =================================================

    else:

        progress = \
            status_data["data"].get(
                "progress",
                0
            )

        print(
            f"\n⏳ Generating... {progress}%"
        )

        time.sleep(5)