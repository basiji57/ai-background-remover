from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove, new_session
import base64
import os

app = FastAPI(title="AI Background Remover")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MAX_BYTES = 12 * 1024 * 1024

# مدل حذف بک‌گراند
session = new_session("u2netp")


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def home():
    return FileResponse("public/index.html")


@app.post("/api/remove-background")
async def remove_background(file: UploadFile = File(...)):
    # بررسی نوع فایل
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "لطفاً یک عکس انتخاب کنید.")

    # خواندن عکس
    data = await file.read()

    # بررسی حجم
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "حجم عکس بیشتر از 12 مگابایت است.")

    try:
        # حذف بک‌گراند
        result = remove(data, session=session)

        # تبدیل خروجی به Base64
        encoded = base64.b64encode(result).decode("utf-8")

        # ساخت آدرس تصویر
        image_url = f"data:image/png;base64,{encoded}"

        return JSONResponse({
            "success": True,
            "imageUrl": image_url
        })

    except Exception as exc:
        raise HTTPException(
            500,
            f"خطا در پردازش تصویر: {exc}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000"))
    )
