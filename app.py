from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session
from PIL import Image
from io import BytesIO
import os

app = FastAPI(title="AI Background Remover")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET","POST"], allow_headers=["*"])

session = new_session("u2netp")
MAX_BYTES = 12 * 1024 * 1024

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def home():
    return FileResponse("public/index.html")

@app.post("/api/remove-background")
async def remove_background(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Please upload an image.")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Image is too large. Maximum size is 12 MB.")
    try:
        Image.open(BytesIO(data)).verify()
        result = remove(data, session=session)
    except Exception as exc:
        raise HTTPException(500, f"Could not process image: {exc}")
    return Response(content=result, media_type="image/png",
                    headers={"Content-Disposition": 'inline; filename="background-removed.png"'})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
