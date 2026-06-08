import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

import numpy as np
from PIL import Image

import io
import base64
import tensorflow as tf
import cv2
import sqlite3
import time

from dotenv import load_dotenv
load_dotenv()

from rag_engine import query_rag

import torch
import clip

from google import genai

# ==========================================
# NEW AI PIPELINE IMPORT
# ==========================================

from services.generation_service import \
    process_image

# ==========================================
# GEMINI API
# ==========================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

# ==========================================
# FLASK
# ==========================================

app = Flask(__name__)

CORS(app)

# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL1_PATH = os.path.join(
    BASE_DIR,
    "final_model"
)

LABEL1_PATH = os.path.join(
    BASE_DIR,
    "labels.npy"
)

MODEL2_PATH = os.path.join(
    BASE_DIR,
    "doodle_model"
)

LABEL2_PATH = os.path.join(
    BASE_DIR,
    "doodle_labels.npy"
)

GENERATED_3D_DIR = os.path.join(
    BASE_DIR,
    "generated_3d"
)

UPLOADS_DIR = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    GENERATED_3D_DIR,
    exist_ok=True
)

os.makedirs(
    UPLOADS_DIR,
    exist_ok=True
)

DB_PATH = os.path.join(
    BASE_DIR,
    "app.db"
)

# ==========================================
# DATABASE
# ==========================================

def init_db():

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        name TEXT,

        email TEXT UNIQUE,

        password TEXT
    )

    """)

    cur.execute("""

    CREATE TABLE IF NOT EXISTS sessions (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        session_id TEXT,

        user_id INTEGER,

        title TEXT,

        summary TEXT,

        full_chat TEXT,

        flashcards TEXT,

        doodle_image TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )

    """)

    cur.execute("""

    CREATE TABLE IF NOT EXISTS doodles (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        label TEXT,

        image TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )

    """)

    conn.commit()

    conn.close()

init_db()

# ==========================================
# LOAD MODELS
# ==========================================

model1 = tf.saved_model.load(
    MODEL1_PATH
)

infer1 = model1.signatures[
    "serving_default"
]

labels1 = np.load(
    LABEL1_PATH,
    allow_pickle=True
)

model2 = tf.saved_model.load(
    MODEL2_PATH
)

infer2 = model2.signatures[
    "serve"
]

labels2 = np.load(
    LABEL2_PATH,
    allow_pickle=True
)

print("✅ Models loaded")

# ==========================================
# CLIP
# ==========================================

device = \
    "cuda" if torch.cuda.is_available() \
    else "cpu"

clip_model, preprocess = clip.load(
    "ViT-B/32",
    device=device
)

clip_labels = [

    "a drawing of a cat",
    "a drawing of a dog",
    "a drawing of a car",
    "a drawing of a tree",
    "a drawing of a fish",
    "a drawing of a sun",
    "a drawing of a face",
    "a drawing of a phone",
    "a drawing of a book",
    "a drawing of a heart",
    "a drawing of a house",
    "a drawing of a flower"
]

# ==========================================
# GEMINI EXPLANATION
# ==========================================

def get_explanation(label):

    try:

        prompt = f"""
You are an educational AI assistant.

The user drew: {label}

Explain:

- what it is
- important characteristics
- real-world uses
- interesting facts

Requirements:

- beginner friendly
- educational
- engaging
- simple language
- maximum 80 words
- use bullet points
- maximum 5 bullet points
- each bullet should be short

Use this format:

• Point 1
• Point 2
• Point 3
• Point 4
• Point 5
"""
        
        response = gemini_client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        explanation = response.text.strip()

        return explanation

    except Exception as e:

        print("\nGEMINI EXPLANATION ERROR:\n")

        print(e)

        return f"""
Unable to generate explanation for {label}.
"""

# ==========================================
# GEMINI CHAT SUMMARY
# ==========================================

def summarize_chat(text):

    try:

        prompt = f"""
Summarize this educational conversation.

Conversation:
{text}

Requirements:

- concise
- educational
- clear
- easy to understand
- around 80-120 words

Do not use markdown.
"""

        response = gemini_client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        summary = response.text.strip()

        return summary

    except Exception as e:

        print("\nGEMINI SUMMARY ERROR:\n")

        print(e)

        return text

# ==========================================
# GEMINI FLASHCARDS
# ==========================================

def make_flashcards(summary):

    try:

        prompt = f"""
Convert this educational content into flashcards.

Content:
{summary}

Requirements:

- short flashcards
- question-answer style
- easy to study
- concise
- educational

Do not use markdown.
"""

        response = gemini_client.models.generate_content(

            model="gemini-3-flash-preview",

            contents=prompt
        )

        flashcards = response.text.strip()

        return flashcards

    except Exception as e:

        print("\nGEMINI FLASHCARD ERROR:\n")

        print(e)

        return "Unable to generate flashcards."

# ==========================================
# IMAGE PROCESSING
# ==========================================

def process_canvas_image(data_url):

    image_data = base64.b64decode(
        data_url.split(',')[1]
    )

    image = Image.open(
        io.BytesIO(image_data)
    ).convert('L')

    image = image.resize((128,128))

    img = np.array(image) / 255.0

    if np.mean(img) > 0.5:

        img = 1 - img

    img = cv2.GaussianBlur(
        img,
        (3,3),
        0
    )

    img = (
        img > np.mean(img)
    ).astype(np.float32)

    coords = np.argwhere(img > 0)

    if coords.size > 0:

        y_min, x_min = coords.min(axis=0)

        y_max, x_max = coords.max(axis=0)

        img = img[
            y_min:y_max,
            x_min:x_max
        ]

    img = (img * 255).astype(np.uint8)

    img = Image.fromarray(img)

    img = img.resize((28,28))

    img = np.array(img) / 255.0

    img = img.reshape(
        1,
        28,
        28,
        1
    ).astype(np.float32)

    return img

def predict_from_models(img):

    input_tensor = tf.convert_to_tensor(img)

    preds1 = list(

        infer1(
            keras_tensor=input_tensor
        ).values()

    )[0].numpy()[0]

    preds2 = list(

        infer2(
            keras_tensor=input_tensor
        ).values()

    )[0].numpy()[0]

    idx1 = np.argmax(preds1)

    idx2 = np.argmax(preds2)

    conf1 = preds1[idx1]

    conf2 = preds2[idx2]

    label1 = labels1[idx1]

    label2 = labels2[idx2]

    return (

        (label1, conf1 * 100)

        if conf1 > conf2

        else

        (label2, conf2 * 100)
    )

def clip_predict(pil_img):

    image = preprocess(
        pil_img
    ).unsqueeze(0).to(device)

    text = clip.tokenize(
        clip_labels
    ).to(device)

    with torch.no_grad():

        logits_per_image, _ = \
            clip_model(image,text)

        probs = logits_per_image \
            .softmax(dim=-1) \
            .cpu().numpy()[0]

    idx = probs.argmax()

    label = clip_labels[idx] \
        .replace("a drawing of ","")

    return label, probs[idx] * 100

def smart_predict(img, base64_img):

    try:

        image_data = base64.b64decode(
            base64_img.split(',')[1]
        )

        pil_img = Image.open(
            io.BytesIO(image_data)
        ).convert("RGB")

        # CNN

        label, confidence = \
            predict_from_models(img)
        print("CNN:", label, confidence)

        if confidence > 95:

            return str(label), \
                   float(confidence)

        # CLIP

        clip_label, clip_conf = \
            clip_predict(pil_img)
        print("CLIP:", clip_label, clip_conf)

        if clip_conf > 90:

            return str(clip_label), \
                   float(clip_conf)

        # GEMINI FALLBACK

        response = gemini_client.models.generate_content(

            model="gemini-2.5-flash",

            contents=[

                """
                Identify this hand drawn doodle.

                Return ONLY ONE WORD.

                Examples:

                tree
                flower
                elephant
                eye
                sun
                car
                cat

                No explanation.
                """,

                pil_img
            ]
        )

        gemini_label = \
            response.text.strip()
        print("GEMINI:", gemini_label)

        return gemini_label, 100

    except Exception as e:

        print(e)

        return "Unknown", 0
    
# ==========================================
# AUTH
# ==========================================


@app.route(
    '/signup',
    methods=['POST']
)

def signup():

    data = request.json

    try:

        conn = sqlite3.connect(DB_PATH)

        cur = conn.cursor()

        cur.execute(

            """
            INSERT INTO users
            (name,email,password)

            VALUES(?,?,?)
            """,

            (
                data.get("name"),
                data.get("email"),
                data.get("password")
            )
        )

        conn.commit()

        conn.close()

        return jsonify({
            "message":"User created"
        })

    except:

        return jsonify({
            "message":"Email already exists"
        })
    
    
@app.route(
    '/login',
    methods=['POST']
)

def login():

    try:

        data = request.json

        email = data.get("email")
        password = data.get("password")

        print("\n===== LOGIN ATTEMPT =====")
        print("EMAIL:", email)
        print("PASSWORD:", password)

        conn = sqlite3.connect(DB_PATH)

        cur = conn.cursor()

        cur.execute(

            """
            SELECT id,name
            FROM users
            WHERE email=? AND password=?
            """,

            (email, password)
        )

        user = cur.fetchone()

        print("USER FOUND:", user)

        conn.close()

        if user:

            return jsonify({

                "success": True,

                "user_id": user[0],

                "name": user[1]
            })

        return jsonify({

            "success": False,

            "message": "Invalid email or password"
        })

    except Exception as e:

        print("\nLOGIN ERROR:\n")
        print(e)

        return jsonify({

            "success": False,

            "message": str(e)
        })
    
# ==========================================
# PREDICT
# ==========================================

@app.route(
    '/predict',
    methods=['POST']
)

def predict():

    data = request.json

    img = process_canvas_image(
        data['image']
    )

    label, confidence = smart_predict(

        img,

        data['image']
    )

    # SAVE DOODLE

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute(

        """
        INSERT INTO doodles
        (label,image)

        VALUES(?,?)
        """,

        (
            str(label),
            data['image']
        )
    )

    conn.commit()

    conn.close()

    return jsonify({

        "label":label,

        "confidence":
        round(confidence,2)
    })

# ==========================================
# AI 3D GENERATION
# ==========================================

@app.route(
    '/generate_3d',
    methods=['POST']
)

def generate_3d():

    try:

        data = request.json

        image_data = data['image']

        image_bytes = base64.b64decode(
            image_data.split(',')[1]
        )

        filename = \
            f"{int(time.time())}.png"

        image_path = os.path.join(
            UPLOADS_DIR,
            filename
        )

        with open(image_path, "wb") as f:

            f.write(image_bytes)

        print("\nIMAGE SAVED:")
        print(image_path)

        model_file = process_image(
            image_path
        )

        if not model_file:

            return jsonify({

                "success": False,

                "message":
                "3D generation failed"
            })

        return jsonify({

            "success": True,

            "model":
            model_file
        })

    except Exception as e:

        print("\n3D ERROR:\n")

        print(e)

        return jsonify({

            "success": False,

            "message": str(e)
        })

# ==========================================
# SERVE GENERATED MODELS
# ==========================================

@app.route(
    '/generated_3d/<path:filename>'
)

def serve_generated_3d(filename):

    return send_from_directory(
        GENERATED_3D_DIR,
        filename
    )

# ==========================================
# CONFIRM
# ==========================================

@app.route(
    '/confirm',
    methods=['POST']
)

def confirm():

    data = request.json

    label = data['label']

    info = (

        get_explanation(label)

        or

        query_rag(label)

        or

        f"This looks like {label}"
    )

    return jsonify({
        "info":info
    })

@app.route(
    '/flashcards',
    methods=['POST']
)

def flashcards():

    data = request.json

    label = data.get(
        "label",
        ""
    )

    prompt = f"""
Create 5 educational flashcards about {label}.

Format:

Q:
A:

Keep answers short.
"""

    response = gemini_client.models.generate_content(

        model="gemini-2.5-flash",

        contents=prompt
    )

    return jsonify({

        "cards":
        response.text
    })
@app.route(
    "/flashcard_explanation",
    methods=["POST"]
)
def flashcard_explanation():

    try:

        label = request.json["label"]

        prompt = f"""
Give 4 short educational revision points about {label}.

Rules:
- Student friendly
- One point per line
- Maximum 15 words per point
- No introduction
- No markdown headings
"""

        response = gemini_client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        return jsonify({

            "explanation":
            response.text.strip()

        })

    except Exception as e:

        print(e)

        return jsonify({

            "explanation":
            f"""• {label} is an interesting object.

• Learning about {label} improves knowledge.

• It can be identified from doodles.

• This flashcard helps revision."""

        })

# ==========================================
# CHAT
# ==========================================

@app.route(
    '/chat',
    methods=['POST']
)

def chat():

    data = request.json

    msg = data.get(
        "message",
        ""
    )

    label = data.get(
        "label",
        ""
    )

    try:

        prompt = f"""
Object detected: {label}

User question: {msg}

Answer clearly, educationally and simply.

Keep response:
- beginner friendly
- concise
- intelligent
- engaging

Do not use markdown.
"""

        response = gemini_client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt
        )

        reply = response.text.strip()

        return jsonify({
            "reply": reply
        })

    except Exception as e:

        print("\nGEMINI CHAT ERROR:\n")

        print(e)

        return jsonify({
            "reply":
            "⚠️ AI not responding"
        })
    

# ==========================================
# GET FLASHCARDS
# ==========================================

@app.route(
    '/get_flashcards',
    methods=['GET']
)

def get_flashcards():

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute(

        """
        SELECT id,label,image
        FROM doodles

        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    conn.close()

    cards = []

    for row in rows:

        cards.append({

            "id": row[0],

            "label": row[1],

            "image": row[2]
        })

    return jsonify(cards)

@app.route(
    "/dashboard",
    methods=["GET"]
)
def dashboard():

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM doodles"
    )

    total = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(
            DISTINCT label
        )
        FROM doodles
        """
    )

    unique_objects = cur.fetchone()[0]

    cur.execute(
        """
        SELECT label,
               COUNT(*)

        FROM doodles

        GROUP BY label

        ORDER BY COUNT(*) DESC

        LIMIT 1
        """
    )

    top = cur.fetchone()

    top_object = (
        top[0]
        if top
        else "-"
    )

    cur.execute(
        """
        SELECT label

        FROM doodles

        ORDER BY id DESC

        LIMIT 10
        """
    )

    recent = [

        row[0]

        for row in cur.fetchall()
    ]
    flashcard_count = total

    chat_count = total * 2

    learning_streak = 7

    top_topic = top_object

    conn.close()

    return jsonify({

        "total": total,

        "unique": unique_objects,

        "top": top_object,

        "recent": recent,

        "flashcards": flashcard_count,

        "chats": chat_count,

        "streak": learning_streak,

        "topic": top_topic
    })
@app.route(
    "/chart_data",
    methods=["GET"]
)
def chart_data():

    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""

        SELECT label,
               COUNT(*)

        FROM doodles

        GROUP BY label

    """)

    rows = cur.fetchall()

    conn.close()

    return jsonify({

        "labels":[
            r[0]
            for r in rows
        ],

        "counts":[
            r[1]
            for r in rows
        ]
    })
@app.route(
    "/quiz",
    methods=["POST"]
)
def generate_quiz():

    label = request.json["label"]

    prompt = f"""
Create one MCQ about {label}.

Format exactly:

Question: ...

A) ...
B) ...
C) ...
D) ...

Correct: A
"""

    response = gemini_client.models.generate_content(

        model="gemini-2.5-flash",

        contents=prompt
    )

    quiz_text = response.text

    lines = quiz_text.split("\n")

    correct_answer = ""

    for line in lines:

        if line.startswith("Correct:"):

            correct_answer = line.replace(
                "Correct:",
                ""
            ).strip()

    question_text = quiz_text.replace(

        f"Correct: {correct_answer}",

        ""

    )

    return jsonify({

        "quiz": question_text,

        "answer": correct_answer

    })
# ==========================================
# RUN
# ==========================================

if __name__ == '__main__':

    app.run(debug=False)