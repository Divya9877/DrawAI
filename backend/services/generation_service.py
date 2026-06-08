from services.gemini_service import \
    generate_prompt

from services.tripo_service import \
    generate_3d_model

# ==========================================
# FULL AI PIPELINE
# ==========================================

def process_image(image_path):

    # STEP 1
    # GEMINI PROMPT

    prompt = generate_prompt(
        image_path
    )

    print("\nGEMINI PROMPT:\n")

    print(prompt)

    # STEP 2
    # TRIPO GENERATION

    model_file = generate_3d_model(
        prompt
    )

    return model_file