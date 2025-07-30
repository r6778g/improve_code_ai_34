from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import os
import requests

app = FastAPI()

# Set Hugging Face API key
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
                "content": f"You are an expert software engineer. Improve and fix bugs in the given code in any programming language:\n{text}"
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
