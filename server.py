import requests
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError
import qrcode
import io

app = FastAPI()

logo_url = os.environ["LOGO_URL"]
logo = None


async def get_logo():
    global logo

    if logo is None:
        try:
            response = requests.get(logo_url)
            response.raise_for_status()  # Raises HTTPError for bad responses
            logo = Image.open(io.BytesIO(response.content))
        except requests.exceptions.HTTPError:
            print("Error fetching the logo image")
        except UnidentifiedImageError:
            print("Fetched content is not a valid image")
        except Exception as e:
            print("Unknown error", e)

        return logo
    else:
        return logo


@app.get("/{url:path}.png")
async def generate_qr(url: str, request: Request):
    text = request.query_params.get("text", url)
    print(f"Generating QR code for {text}")
    # Ensure the URL is reasonable to avoid malicious content generation
    if len(text) > 2048:
        raise HTTPException(status_code=400, detail="URL is too long")

    _logo = await get_logo()
    if _logo is None:
        raise HTTPException(status_code=500, detail="Logo image not available")

    # Resize logo
    basewidth = 100
    wpercent = basewidth / float(logo.size[0])
    hsize = int((float(logo.size[1]) * float(wpercent)))
    _logo = _logo.resize((basewidth, hsize), Image.LANCZOS)

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=15,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    qr_color = "black"  # Color of the QR code
    img_qr = qr.make_image(fill_color=qr_color, back_color="white").convert(
        "RGBA"
    )

    # Place logo in the middle
    pos = (
        (img_qr.size[0] - _logo.size[0]) // 2,
        (img_qr.size[1] - _logo.size[1]) // 2,
    )
    img_qr.paste(_logo, pos, _logo)

    # Save to a stream
    img_byte_arr = io.BytesIO()
    img_qr.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")
