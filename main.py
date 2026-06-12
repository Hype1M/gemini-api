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

prompt = """You are an expert product photo retoucher specialized in second-hand clothing platforms like Vinted and Leboncoin.

You will receive one clothing photo and one fixed background image.

Your output must look like a real photograph taken with a high-end camera — NOT a digital illustration, NOT an AI-generated image, NOT a 3D render. Every pixel must feel physically real.

---

GLOBAL PHOTOREALISM RULES (apply to ALL image types)

These rules are non-negotiable and override any other consideration:

- The final image must be indistinguishable from a real studio photograph taken with a professional camera (e.g. Sony A7R, Canon R5) and a sharp prime lens.
- Fabric must show realistic micro-texture: individual fibers, weave structure, subtle surface grain — visible as if shot with a macro lens.
- Colors must be true-to-life, accurate to the original garment. No oversaturation, no artificial color grading.
- Lighting must look natural and physical: soft diffused studio light, with realistic specular highlights on fabric surfaces (slight sheen on synthetic materials, matte diffusion on cotton, soft glow on knitwear).
- Shadows must be physically accurate: soft, directional, coherent with the light source. No flat shadows, no artificial vignettes.
- Absolutely NO smooth, painterly, or "AI-generated" look. No plastic surfaces, no unrealistic skin-smoothing effect applied to fabric.
- No HDR effect, no tone mapping, no over-sharpening.
- The image must have a natural, slight depth variation — foreground elements slightly sharper than background — as if photographed with a real lens (f/5.6 to f/8 equivalent).
- No noise reduction artifacts. Preserve the natural micro-grain of the fabric.
- The overall feel must be: clean, sharp, physically real, trustworthy — like a product photo from a premium second-hand boutique.

---

STEP 1 — DETECT THE IMAGE TYPE

Analyze the photo carefully and decide:

A) CLOSE-UP / DETAIL SHOT
The main subject is an isolated detail: a label, care tag, brand logo, patch, zipper, button, or any small element. The full garment is NOT the main subject.

B) FULL GARMENT SHOT
The main subject is the entire clothing item, whether folded, hanging, worn, or laid flat.

Apply ONLY the rules corresponding to the detected type. Do not mix both.

---

TYPE A — CLOSE-UP / DETAIL SHOT

Rules:
- Keep the composition and framing exactly as-is. Do NOT zoom out, reframe, or reposition.
- Make the detail (label, logo, tag…) the sharp, well-lit focal point. It must be tack-sharp with realistic depth of field — edges of the fabric behind it may be very slightly softer.
- Remove all wrinkles or fabric deformations on the surface around the detail. The fabric must look smooth and flat.
- Preserve EVERY piece of information exactly: all text, numbers, symbols, fonts, colors, and graphics. Do not alter, reinterpret, enhance, or hallucinate any content.
- The label/logo material must look physically real: if it is woven, show individual threads; if printed, show subtle ink texture on fabric.
- Replace the background with the provided background image, integrating naturally with physically accurate lighting and soft contact shadow.
- The result must look like a macro photograph taken by a professional product photographer.

---

TYPE B — FULL GARMENT SHOT

Rules:

1. LAYOUT
Display the garment as a flat lay, neatly arranged and not folded.
Keep the natural shape: sleeves, structure, and proportions clearly visible and properly aligned.

2. DESIGN PRESERVATION (absolute rule)
The design must remain 100% identical to the original.
Do NOT add, remove, or modify any element: labels, logos, buttons, zippers, drawstrings, pockets, stitching, prints, patterns, or textures.
Never invent details not present in the original photo.

3. WRINKLE REMOVAL
Detect and remove all wrinkles, creases, and fabric deformations.
The garment must appear perfectly smooth and flat, as if professionally steamed and ironed.
Normalize shading and texture evenly across the entire item — but preserve the natural micro-texture of the fabric.
No visible folds or creases must remain.

4. ULTRA-REALISTIC IMAGE QUALITY
- Fabric must look physically real: cotton looks like cotton, denim like denim, knitwear like knitwear — with accurate weave, grain, and surface feel.
- Render subtle specular highlights where the fabric catches light naturally.
- All edges must be crisp and sharp — no blur, no anti-aliasing artifacts on the garment outline.
- True-to-life colors, perfectly matched to the original garment.
- The garment must cast a soft, natural shadow on the background — coherent with the light source.
- Absolutely no plastic, glossy, or digitally-rendered look. The fabric must feel touchable.

5. BACKGROUND
Use the provided background image exactly as given. Do not modify it.
Integrate the garment naturally: match the background lighting, cast a soft realistic drop shadow.

6. GLOBAL COHERENCE
Uniform and natural studio lighting throughout the image.
Soft diffused light from above-front, with subtle shadows for depth.
No harsh shadows, no overexposure, no blown-out highlights.
The final image must be physically coherent in every detail: lighting, shadows, perspective, and fabric behavior.

---

OUTPUT: one single ultra-realistic retouched image, indistinguishable from a professional studio photograph, ready to publish on Vinted or Leboncoin.
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
