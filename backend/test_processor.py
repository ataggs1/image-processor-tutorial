import pytest
from PIL import Image
from processor import ImageProcessor


@pytest.fixture
def sample_image():
    """Create a test image"""
    img = Image.new('RGB', (1000, 1000), color='red')
    return img


def test_resize(sample_image):
    """Test that resize changes image to exact dimensions"""
    processor = ImageProcessor()
    resized = processor.resize(sample_image, 500, 300)

    assert resized.size == (500, 300), f"Expected size (500, 300), got {resized.size}"
    assert resized.mode == 'RGB', f"Expected mode RGB, got {resized.mode}"


def test_convert_grayscale(sample_image):
    """Test that convert_grayscale changes image to grayscale mode"""
    processor = ImageProcessor()
    grayscale = processor.convert_grayscale(sample_image)

    assert grayscale.mode == 'L', f"Expected mode L (grayscale), got {grayscale.mode}"
    assert grayscale.size == sample_image.size, "Image size should remain unchanged"


def test_apply_blur(sample_image):
    """Test that apply_blur applies Gaussian blur filter"""
    processor = ImageProcessor()
    blurred = processor.apply_blur(sample_image, radius=5)

    assert blurred.size == sample_image.size, "Image size should remain unchanged"
    assert blurred.mode == sample_image.mode, "Image mode should remain unchanged"

    # Test with default radius
    blurred_default = processor.apply_blur(sample_image)
    assert blurred_default.size == sample_image.size, "Default blur should work"


def test_create_thumbnail(sample_image):
    """Test that create_thumbnail generates thumbnail maintaining aspect ratio"""
    processor = ImageProcessor()
    thumbnail = processor.create_thumbnail(sample_image, max_size=200)

    # Check that thumbnail is smaller than or equal to max_size
    assert thumbnail.size[0] <= 200, f"Width {thumbnail.size[0]} exceeds max_size 200"
    assert thumbnail.size[1] <= 200, f"Height {thumbnail.size[1]} exceeds max_size 200"

    # Check aspect ratio maintained (for square image, should be 200x200)
    assert thumbnail.size == (200, 200), f"Expected (200, 200) for square image, got {thumbnail.size}"

    # Test with default max_size
    thumbnail_default = processor.create_thumbnail(sample_image)
    assert thumbnail_default.size[0] <= 200, "Default max_size should be 200"
    assert thumbnail_default.size[1] <= 200, "Default max_size should be 200"


def test_resize_invalid_dimensions(sample_image):
    """Test that resize raises ValueError for invalid dimensions"""
    processor = ImageProcessor()
    with pytest.raises(ValueError):
        processor.resize(sample_image, -100, 500)
    with pytest.raises(ValueError):
        processor.resize(sample_image, 500, 0)


def test_blur_negative_radius(sample_image):
    """Test that apply_blur raises ValueError for negative radius"""
    processor = ImageProcessor()
    with pytest.raises(ValueError):
        processor.apply_blur(sample_image, radius=-5)


def test_thumbnail_invalid_size(sample_image):
    """Test that create_thumbnail raises ValueError for invalid size"""
    processor = ImageProcessor()
    with pytest.raises(ValueError):
        processor.create_thumbnail(sample_image, max_size=0)
