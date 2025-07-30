from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse


app = FastAPI()

@app.post("/process/")
async def process_input(
    text: str = Form(None)
):
    if text:
        return {"input_type": "text", "content": text}
    else:
        raise HTTPException(status_code=400, detail="No input provided. Submit either text or a file.")
