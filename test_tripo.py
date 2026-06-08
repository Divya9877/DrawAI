import requests
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("TRIPO_API_KEY")

r = requests.get(
    "https://api.tripo3d.ai/v2/openapi/user/balance",
    headers={
        "Authorization": f"Bearer tsk_HfD8mINroagKqRPMQ_edUv9lqTjaK0tFkllRo9rfQiT"
    }
)

print(r.text)