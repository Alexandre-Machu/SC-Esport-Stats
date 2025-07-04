import base64

def get_image_as_base64(image_path: str) -> str:
    """Convert an image file to base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return ""
