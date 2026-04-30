from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import os
from google import genai

app = FastAPI()

# Initialisation client (NOUVEAU SDK)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """Recreate this image in an ultra-realistic professional product photo style..."""

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/generate")
async def generate(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    try:
        img1 = Image.open(io.BytesIO(await image1.read()))
        img2 = Image.open(io.BytesIO(await image2.read()))

        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt, img1, img2],
        )

        for part in response.parts:
            if part.inline_data:
                img = Image.open(io.BytesIO(part.inline_data.data))
                output = io.BytesIO()
                img.save(output, format="PNG")
                output.seek(0)

                return StreamingResponse(output, media_type="image/png")

        return {"error": "no image generated"}

    except Exception as e:
        return {"error": str(e)}


# 🔥 Render PORT fix
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
