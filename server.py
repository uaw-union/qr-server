import requests
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError, ImageDraw, ImageFont
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
    text = request.query_params.get("text", "")
    print(f"Generating QR code for {url} with label: {text}")
    # Ensure the URL is reasonable to avoid malicious content generation
    if len(url) > 2048:
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
        border=1.5,  # Halfway between 1 and 2
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create QR code image
    qr_color = "black"  # Color of the QR code
    img_qr = qr.make_image(fill_color=qr_color, back_color="white").convert(
        "RGBA"
    )

    # Get the size of the QR code image
    qr_size = img_qr.size[0]

    # Create a new image with reduced size
    new_size = (
        qr_size - 10
    )  # Reduce 5 pixels on each side (halfway between 0 and 10)
    new_img = Image.new("RGBA", (new_size, new_size), "white")

    # Paste the QR code onto the new image, effectively cropping it
    new_img.paste(img_qr, (-5, -5))  # Offset by -5 instead of -10

    # Use new_img instead of img_qr for the rest of the processing
    img_qr = new_img

    # Place logo in the middle
    pos = (
        (img_qr.size[0] - _logo.size[0]) // 2,
        (img_qr.size[1] - _logo.size[1]) // 2,
    )
    img_qr.paste(_logo, pos, _logo)

    # Add text at the bottom if present
    if text:
        # Create a drawing object
        draw = ImageDraw.Draw(img_qr)
        # Use a default font
        font = ImageFont.load_default().font_variant(size=18)

        # Calculate text size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Define padding and border width
        padding = 8
        border_width = 2

        # Calculate rectangle size and position
        rect_width = text_width + 2 * padding
        rect_height = text_height + 2 * padding
        rect_position = (
            (img_qr.width - rect_width) // 2,
            img_qr.height - rect_height - 10,
        )

        # Draw white rectangle with black border
        draw.rectangle(
            [
                rect_position,
                (
                    rect_position[0] + rect_width,
                    rect_position[1] + rect_height,
                ),
            ],
            fill=(255, 255, 255, 200),  # White with some transparency
            outline=(0, 0, 0),  # Black border
            width=border_width,
        )

        # Calculate text position within the rectangle
        text_position = (
            rect_position[0] + padding,
            rect_position[1] + padding,
        )

        # Draw the text
        draw.text(text_position, text, font=font, fill=(0, 0, 0, 255))

    # Save to a stream
    img_byte_arr = io.BytesIO()
    img_qr.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return StreamingResponse(img_byte_arr, media_type="image/png")
