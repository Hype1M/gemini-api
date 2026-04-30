from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import os
from google import genai

app = FastAPI()

# Initialisation client (NOUVEAU SDK)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """"Recreate this image in an ultra-realistic style. The clothing item must be displayed flat (not folded), arranged neatly in a clean flat lay. Keep the shape natural, with sleeves and structure clearly visible and properly aligned.

Pay extreme attention to details: preserve the exact design of the item and do not add or modify any elements under any circumstances. Do not invent, generate, or alter any features that are not present in the original image. This includes labels, tags, logos, buttons, zippers, drawstrings, pockets, stitching, or textures. The item must remain 100% identical to the original in every detail.

Carefully detect all wrinkles, creases, and fabric deformations, and completely remove them. The clothing item must appear perfectly ironed, smooth, and flat, as if professionally pressed. There must be absolutely no visible wrinkles or folds remaining.

To ensure this, evenly smooth and normalize the fabric texture and color across the entire garment, removing any shading inconsistencies caused by wrinkles, while keeping a natural and realistic fabric look.

The fabric should look realistic with accurate texture, sharp details, and true-to-life colors.

The final image must be in high resolution, extremely sharp, with no blur, no pixelation, and no noise. Ensure crisp edges and fine details, like a professional studio photo.

Place the item on a very light-colored parquet wooden floor (light oak or pale wood), clean and minimal, similar to what a private seller could have at home. The parquet floor background will be provided separately by the user and must be used as-is, without modification.

Ensure the entire image is coherent and physically realistic: consistent lighting, shadows, perspective, and proportions. Use soft natural lighting with subtle shadows to create depth while keeping a clean and professional look. Avoid harsh lighting or overexposure.

The final image should look like a high-quality, realistic product photo suitable for resale on platforms like Vinted: clean, trustworthy, and visually appealing."""



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
