"""
CivicFlow Backend — Image Processing Service
============================================
Handles image compression and Base64 encoding for the zero-cost architecture.
Instead of using Firebase Storage, we aggressively compress incoming images
and store them directly in Firestore as Base64 data URIs.
"""

import io
import base64
import logging
from PIL import Image

logger = logging.getLogger(__name__)

def compress_to_base64(image_bytes: bytes, max_width: int = 800, quality: int = 60) -> str:
    """
    Compresses an image and returns it as a Base64 data URI.
    
    - Resizes the image so its width doesn't exceed `max_width` (maintains aspect ratio).
    - Converts the image to JPEG.
    - Compresses it with the specified `quality` (1-100).
    - Returns a string prefixed with `data:image/jpeg;base64,`.

    Args:
        image_bytes: The raw image file bytes.
        max_width: The maximum allowed width of the image.
        quality: JPEG compression quality.

    Returns:
        A Base64 string suitable for Firestore storage and frontend rendering.
    """
    try:
        # Open the image using Pillow
        image = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB (in case of PNG with transparency/alpha channel)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Resize if width exceeds max_width while maintaining aspect ratio
        if image.width > max_width:
            ratio = max_width / float(image.width)
            new_height = int(float(image.height) * float(ratio))
            # Use LANCZOS for high-quality downsampling
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

        # Save to an in-memory byte buffer as JPEG
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
        compressed_bytes = buffer.getvalue()

        logger.info(
            f"🖼️  Image compressed: original size ~{len(image_bytes) // 1024}KB, "
            f"new size ~{len(compressed_bytes) // 1024}KB"
        )

        # Encode to Base64
        b64_string = base64.b64encode(compressed_bytes).decode("utf-8")
        
        # Return as a complete Data URI
        return f"data:image/jpeg;base64,{b64_string}"

    except Exception as e:
        logger.error(f"Failed to compress image: {e}")
        raise ValueError(f"Image processing failed: {str(e)}")
