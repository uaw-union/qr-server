# qr-server

Serve QR codes via `.png` URLs.

## Usage

If you have this deployed at `https://qrserver.myorganization.org`, you can generate a QR code by visiting `https://qrserver.myorganization.org/<qrdatahere>.png`.

This works anywhere that a URL to an image works, like as a src= value, a media URL when
sending an MMS, etc.

If you want your QR code to point to a URL, just put that in the URL with careful attention to URL encoding.

For the UAW, this is deployed at `qrcode.uaw.tech` (click [here](https://qrcode.uaw.tech/https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ.png) or scan the below QR code to see it in action).

You can see if you inspect this markdown that this image is generated and not stored.

![Alt text](https://qrcode.uaw.tech/https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DdQw4w9WgXcQ.png)

## Logo 

This server accepts a `LOGO_URL` environment variable. If provided, it will be downloaded and overlaid on the QR code for a minimal but present branding.

If LOGO_URL is present but you want to disable the logo for an individual request, you can pass `?hide_logo=true` in the URL.

The image at `LOGO_URL` is downloaded once per server start and cached.

## URL Encoding

When using this in new contexts, pay careful attention to URL encoding. Almost everything
that you'll want to encode will have URL unsafe characters.

## Contributions

Many services (Instagram, Cash App, etc.) have engines for much cooler QR code generation.
If you're interested in contributing features along those lines, please get in touch or open a PR!
