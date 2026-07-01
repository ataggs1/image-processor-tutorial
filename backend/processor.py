from PIL import Image, ImageFilter


class ImageProcessor:
    """Handles image processing operations"""

    def resize(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """
        Resize image to exact dimensions.

        Args:
            image: PIL Image object to resize
            width: Target width in pixels
            height: Target height in pixels

        Returns:
            Resized PIL Image object

        Raises:
            ValueError: If width or height is not positive
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"Width and height must be positive integers, got {width}x{height}")
        return image.resize((width, height), Image.Resampling.LANCZOS)

    def convert_grayscale(self, image: Image.Image) -> Image.Image:
        """
        Convert image to grayscale.

        Args:
            image: PIL Image object to convert

        Returns:
            Grayscale PIL Image object (mode 'L')
        """
        return image.convert('L')

    def apply_blur(self, image: Image.Image, radius: int = 5) -> Image.Image:
        """
        Apply Gaussian blur to image.

        Args:
            image: PIL Image object to blur
            radius: Blur radius (default: 5)

        Returns:
            Blurred PIL Image object

        Raises:
            ValueError: If radius is negative
        """
        if radius < 0:
            raise ValueError(f"Radius must be non-negative, got {radius}")
        return image.filter(ImageFilter.GaussianBlur(radius))

    def create_thumbnail(self, image: Image.Image, max_size: int = 200) -> Image.Image:
        """
        Create thumbnail maintaining aspect ratio.

        Args:
            image: PIL Image object to thumbnail
            max_size: Maximum size for width and height (default: 200)

        Returns:
            Thumbnail PIL Image object

        Raises:
            ValueError: If max_size is not positive
        """
        if max_size <= 0:
            raise ValueError(f"Max size must be positive, got {max_size}")
        thumb = image.copy()
        thumb.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return thumb
