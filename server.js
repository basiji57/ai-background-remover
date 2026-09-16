import express from "express";
import multer from "multer";
import dotenv from "dotenv";
import { File } from "node:buffer";
import { fal } from "@fal-ai/client";

dotenv.config();

const app = express();
const port = process.env.PORT || 3000;

if (!process.env.FAL_KEY) {
  console.warn("FAL_KEY تنظیم نشده است. قبل از استفاده آن را در .env قرار بده.");
}

fal.config({ credentials: process.env.FAL_KEY });

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 15 * 1024 * 1024 }
});

app.use(express.static("public"));

app.post("/api/remove-background", upload.single("image"), async (req, res) => {
  try {
    if (!process.env.FAL_KEY) {
      return res.status(500).json({
        error: "کلید سرویس روی سرور تنظیم نشده است."
      });
    }

    if (!req.file) {
      return res.status(400).json({ error: "عکسی ارسال نشده است." });
    }

    const file = new File(
      [req.file.buffer],
      req.file.originalname || "image.png",
      { type: req.file.mimetype || "image/png" }
    );

    // آپلود فایل از سمت سرور؛ کلید هیچ‌وقت به مرورگر فرستاده نمی‌شود.
    const imageUrl = await fal.storage.upload(file);

    // subscribe خودش وضعیت صف را مدیریت می‌کند و نتیجه نهایی را برمی‌گرداند.
    const result = await fal.subscribe("fal-ai/bria/background/remove", {
      input: { image_url: imageUrl },
      logs: false
    });

    const outputUrl = result?.data?.image?.url;

    if (!outputUrl) {
      console.error("Unexpected Fal response:", result);
      return res.status(502).json({
        error: "سرویس تصویر خروجی معتبری برنگرداند."
      });
    }

    return res.json({ imageUrl: outputUrl });
  } catch (error) {
    console.error(error);
    return res.status(500).json({
      error: error?.message || "پردازش تصویر ناموفق بود."
    });
  }
});

app.listen(port, () => {
  console.log(`Background remover running on port ${port}`);
});
