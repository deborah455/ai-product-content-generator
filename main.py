from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
import pandas as pd
import os
import traceback

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize OpenAI client (may be missing in mock mode)
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
try:
    client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None
except Exception:
    client = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, file: UploadFile = File(...)):
    try:
        # attempt to read the uploaded CSV
        df = pd.read_csv(file.file)
    except Exception as e:
        error_html = f"<h2>Error reading CSV:</h2><pre>{str(e)}</pre>"
        return HTMLResponse(content=error_html, status_code=400)

    # required headers check
    expected = {"Product Name", "Features"}
    if not expected.issubset(set(df.columns)):
        return HTMLResponse(
            content=f"<h2>CSV header error</h2><p>Required columns: Product Name, Features</p><p>Your columns: {list(df.columns)}</p>",
            status_code=400,
        )

    results = []
    for _, row in df.iterrows():
        try:
            product_name = str(row["Product Name"])
            features = str(row["Features"])
            prompt = f"Write a vibrant, persuasive, 70-word product description for '{product_name}' that highlights these features: {features}. Make it sound premium and human-like."

            if client:
                # use OpenAI if available
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=140,
                )
                desc = resp.choices[0].message.content.strip()
            else:
                # mock fallback content
                desc = f"{product_name} — crafted for modern life. {features}. Upgrade your world with a single touch."

        except Exception as e:
            # catch per-row errors and continue
            desc = f"[Error generating for {product_name}] {str(e)}"
        results.append({"product": product_name, "description": desc})

    return templates.TemplateResponse("results.html", {"request": request, "results": results})

# Simple health endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}
