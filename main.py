from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import os
from google import genai
from google.genai import types

app = FastAPI()

# Initialisation client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """Recreate this image in an ultra-realistic style.
— Image type detection (CRITICAL) —
First, analyze the image to determine its type:
If you are NOT 100% certain that the image shows a full garment as its main subject, do not apply any transformation. Simply place the item as-is on the provided background floor, integrating it naturally with consistent lighting and shadows. Do nothing else.
If and only if the image clearly shows a FULL GARMENT (whether folded, hanging, worn, or laid flat) with no ambiguity: apply all the full garment instructions below.
If the image is a CLOSE-UP / DETAIL SHOT (a label, tag, logo, care instructions, brand patch, zipper, button, or any isolated detail — meaning the full garment is NOT the main subject): Strict copy mode — zero interpretation allowed: 1. Framing: keep the exact composition, zoom, and angle. No reframing, no zoom out, no repositioning of any kind. 2. Text and graphics — absolute rule: every letter, number, symbol, color, font, and layout must be reproduced exactly as visible. Do not correct, complete, guess, or reinterpret anything. If a text is partially illegible, reproduce it as-is, including any blur or cutoff. Any hallucination of text or graphics is a critical error. 3. Fabric surface: remove wrinkles and deformations from the surrounding fabric so the surface appears smooth, flat, and clean, like a brand new label. 4. Photo quality: realistic macro rendering, sharp focus on the detail, soft and even lighting with no reflections, depth of field consistent with a close-up product shot. 5. Background: replace the background with the provided background image, integrating the subject naturally with consistent lighting and shadows.
— Full garment instructions —
The clothing item must be displayed flat (not folded), arranged neatly in a clean flat lay. Keep the shape natural, with sleeves and structure clearly visible and properly aligned.
Preservation of original design (ABSOLUTE RULE): Preserve the exact design of the item and do not add or modify any elements under any circumstances. Do not invent, generate, or alter any features that are not present in the original image. This includes labels, tags, logos, buttons, zippers, drawstrings, pockets, stitching, or textures. The item must remain 100% identical to the original in every detail.
Wrinkle removal: Carefully detect all wrinkles, creases, and fabric deformations, and completely remove them. The clothing item must appear perfectly ironed, smooth, and flat, as if professionally pressed. There must be absolutely no visible wrinkles or folds remaining. Evenly smooth and normalize the fabric texture and color across the entire garment, removing any shading inconsistencies caused by wrinkles, while keeping a natural and realistic fabric look.
Image quality: The fabric should look realistic with accurate texture, sharp details, and true-to-life colors. The final image must be in high resolution, extremely sharp, with no blur, no pixelation, and no noise. Ensure crisp edges and fine details, like a professional studio photo.
Background: Use the provided background image as-is, without any modification. The clothing item must be naturally integrated into this background with consistent lighting, perspective, and shadows.
Global coherence: Ensure the entire image is coherent and physically realistic: consistent lighting, shadows, perspective, and proportions. Use soft natural lighting with subtle shadows to create depth while keeping a clean and professional look. Avoid harsh lighting or overexposure.
The final image should look like a high-quality, realistic product photo suitable for resale on platforms like Vinted: clean, trustworthy, and visually appealing.
"""

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/generate")
async def generate(image1: UploadFile = File(...)):
    try:
        # Image utilisateur
        img1 = Image.open(io.BytesIO(await image1.read()))

        # Fond par défaut
        img2 = Image.open("fond.png")

        # 🔥 Appel Gemini avec ratio 3:4 uniquement
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt, img1, img2],
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio="3:4"
                )
            )
        )

        # Récupération image générée
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
