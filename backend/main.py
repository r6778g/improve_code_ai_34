from fastapi import FastAPI, Form, HTTPException

import os
import requests

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.environ["HF_API_KEY"] = "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"

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {os.environ['HF_API_KEY']}",
    "Content-Type": "application/json"
}

def query_huggingface(text: str):
    payload = {
        "messages": [
            {
                "role": "system",
                "content": f"Review this code and give feedback on:  Bugs or logical issues  Readability and performance  Security and best practices  Test coverage and maintainability Also, Suggested code fixes where relevant.\n{text}"
            }
        ],
        "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct:novita"
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


@app.post("/process/")
async def process_input(text: str = Form(None)):
    if not text:
        raise HTTPException(status_code=400, detail="No input provided. Submit either text or a file.")

    try:
        hf_response = query_huggingface(text)
        assistant_reply = hf_response["choices"][0]["message"]["content"]
        return {
            "input_type": "text",
            "input": text,
            "model_response": assistant_reply
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Hugging Face API error: {str(e)}")
