import base64

import filetype

base64_identifier = "base64,"


def decode_base64_image(data: str) -> bytes:
    """Decode a base64 image from a base64 data string."""
    return base64.b64decode(data.split(base64_identifier)[1])


def encode_base64_image(image: bytes) -> str:
    """Encode image data bytes to a base64 data string."""
    kind = filetype.guess(image)
    mime_type = kind.mime if kind else "octet-stream"
    return f"data:{mime_type};{base64_identifier}{base64.b64encode(image).decode()}"
