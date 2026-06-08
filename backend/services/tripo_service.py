import requests
import time
import os
import json

from dotenv import load_dotenv

# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

TRIPO_API_KEY = os.getenv(
    "TRIPO_API_KEY"
)

print("\nTRIPO KEY LOADED:\n")

print(TRIPO_API_KEY)

# ==========================================
# BASE DIRECTORY
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(__file__)
)

GENERATED_DIR = os.path.join(
    BASE_DIR,
    "generated_3d"
)

os.makedirs(
    GENERATED_DIR,
    exist_ok=True
)

# ==========================================
# GENERATE 3D MODEL
# ==========================================

def generate_3d_model(prompt):

    headers = {

        "Authorization":
        f"Bearer {TRIPO_API_KEY}",

        "Content-Type":
        "application/json"
    }

    # ======================================
    # PAYLOAD
    # ======================================

    payload = {

        "type": "text_to_model",

        "prompt": prompt,

        # HIGH QUALITY

        "texture": True,

        "pbr": True
    }

    print("\n========== TRIPO PAYLOAD ==========\n")

    print(json.dumps(payload, indent=2))

    # ======================================
    # CREATE TASK
    # ======================================

    response = requests.post(

        "https://api.tripo3d.ai/v2/openapi/task",

        headers=headers,

        json=payload
    )

    print("\n========== TRIPO RESPONSE ==========\n")

    print(response.text)

    # ======================================
    # JSON PARSE
    # ======================================

    try:

        data = response.json()

    except Exception as e:

        print("\nJSON ERROR:\n")

        print(e)

        return None

    # ======================================
    # FAILED RESPONSE
    # ======================================

    if "data" not in data:

        print("\nTRIPO FAILED:\n")

        print(data)

        return None

    # ======================================
    # TASK ID
    # ======================================

    task_id = data["data"]["task_id"]

    print("\nTASK ID:\n")

    print(task_id)

    # ======================================
    # STATUS URL
    # ======================================

    status_url = \
        f"https://api.tripo3d.ai/v2/openapi/task/{task_id}"

    # ======================================
    # WAIT LOOP
    # ======================================

    while True:

        status_response = requests.get(

            status_url,

            headers=headers
        )

        try:

            status_data = \
                status_response.json()

        except Exception as e:

            print("\nSTATUS JSON ERROR:\n")

            print(e)

            return None

        print("\n========== STATUS ==========\n")

        print(json.dumps(status_data, indent=2))

        # ==================================
        # SAFETY CHECK
        # ==================================

        if "data" not in status_data:

            print("\nINVALID STATUS RESPONSE\n")

            print(status_data)

            return None

        status = status_data["data"]["status"]

        # ==================================
        # SUCCESS
        # ==================================

        if status == "success":

            result = \
                status_data["data"]["result"]

            print("\n========== RESULT ==========\n")

            print(json.dumps(result, indent=2))

            model_url = None

            # ==================================
            # FIND MODEL URL
            # ==================================

            if "pbr_model" in result:

                model_url = \
                    result["pbr_model"]["url"]

            elif "model" in result:

                model_url = \
                    result["model"]["url"]

            elif "base_model" in result:

                model_url = \
                    result["base_model"]["url"]

            # ==================================
            # MODEL URL MISSING
            # ==================================

            if not model_url:

                print("\nNO MODEL URL FOUND\n")

                print(result)

                return None

            print("\nMODEL URL:\n")

            print(model_url)

            # ==================================
            # DOWNLOAD MODEL
            # ==================================

            filename = \
                f"model_{int(time.time())}.glb"

            save_path = os.path.join(

                GENERATED_DIR,

                filename
            )

            print("\nDOWNLOADING MODEL...\n")

            model_response = requests.get(
                model_url
            )

            with open(save_path, "wb") as f:

                f.write(model_response.content)

            print("\nMODEL SAVED SUCCESSFULLY\n")

            print("FILENAME:")

            print(filename)

            print("\nFULL PATH:")

            print(save_path)

            return filename

        # ==================================
        # FAILED
        # ==================================

        elif status == "failed":

            print("\nTRIPO GENERATION FAILED\n")

            print(status_data)

            return None

        # ==================================
        # STILL GENERATING
        # ==================================

        else:

            progress = \
                status_data["data"].get(
                    "progress",
                    0
                )

            print(
                f"\nGenerating... {progress}%"
            )

            time.sleep(5)