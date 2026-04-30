from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image
import google.generativeai as genai
import io
import os

app = FastAPI()

# API KEY (Render environment variable)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
Recreate this image in an ultra-realistic professional product photo style.

The clothing item must be displayed flat (flat lay), not folded, with a clean and perfectly aligned shape. Sleeves, edges, and structure must look natural and physically correct.

EXTREME CONSTRAINTS:
- Do NOT modify, invent, or remove any design elements of the garment.
- Preserve EXACTLY all details: logos, labels, tags, stitching, buttons, zippers, drawstrings, textures.
- The item must remain 100% identical to the original design.

FABRIC QUALITY:
- Remove ALL wrinkles, folds, and creases completely.
- The garment must look perfectly ironed and smooth.
- Maintain realistic fabric texture while removing deformation artifacts.
- Normalize lighting and shading caused by wrinkles while preserving realism.

BACKGROUND:
- Place the item on a light-colored wooden parquet floor (light oak / pale wood).
- The background must remain natural, clean, minimal, and realistic.

LIGHTING:
- Soft natural lighting
- Subtle realistic shadows
- No harsh light, no overexposure

QUALITY:
- Ultra high resolution
- Extremely sharp details
- No blur, no noise, no pixelation
- Professional e-commerce product photography style (like Vinted / Shopify listing)

The final result must look like a high-end studio product photo.
"""

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/generate")
async def generate(image1: UploadFile = File(...), image2: UploadFile = File(...)):

    # Load images
    img1 = Image.open(io.BytesIO(await image1.read()))
    img2 = Image.open(io.BytesIO(await image2.read()))

    # CALL GEMINI IMAGE MODEL
    model = genai.GenerativeModel("gemini-3.1-flash-image-preview")

    response = model.generate_content([prompt, img1, img2])

    # Extract image result
    for part in response.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            img = Image.open(io.BytesIO(part.inline_data.data))

            output = io.BytesIO()
            img.save(output, format="PNG")
            output.seek(0)

            return StreamingResponse(output, media_type="image/png")

    return {"error": "no image generated"}
