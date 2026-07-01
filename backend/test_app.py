import pytest
from io import BytesIO
from PIL import Image
import json


@pytest.fixture
def client():
    """Create test client for Flask application"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test health check endpoint returns healthy status"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {"status": "healthy"}


def test_allowed_file_extension():
    """Test file extension validation"""
    from app import allowed_file

    # Test allowed extensions
    allowed = {'png', 'jpg', 'jpeg', 'gif'}

    # Valid extensions
    assert allowed_file('image.png', allowed) == True
    assert allowed_file('image.jpg', allowed) == True
    assert allowed_file('image.jpeg', allowed) == True
    assert allowed_file('image.gif', allowed) == True
    assert allowed_file('IMAGE.PNG', allowed) == True  # Case insensitive

    # Invalid extensions
    assert allowed_file('document.pdf', allowed) == False
    assert allowed_file('video.mp4', allowed) == False
    assert allowed_file('noextension', allowed) == False
    assert allowed_file('', allowed) == False


def create_test_image():
    """Helper function to create a test image"""
    img = Image.new('RGB', (800, 600), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


def test_process_resize(client):
    """Test image processing endpoint with resize operation"""
    # Create test image
    test_image = create_test_image()

    # Prepare form data
    data = {
        'file': (test_image, 'test.png'),
        'operations': json.dumps([
            {"operation": "resize", "params": {"width": 400, "height": 300}}
        ])
    }

    # Send request
    response = client.post(
        '/process',
        data=data,
        content_type='multipart/form-data'
    )

    # Check response
    assert response.status_code == 200
    result = json.loads(response.data)

    # Verify response structure
    assert 'processed_image' in result
    assert 'metadata' in result
    assert result['metadata']['original_dimensions'] == [800, 600]
    assert result['metadata']['processed_dimensions'] == [400, 300]
    assert result['processed_image'].startswith('data:image/png;base64,')


def test_process_missing_resize_params(client):
    """Test /process with resize but missing parameters"""
    test_image = create_test_image()

    data = {
        'file': (test_image, 'test.png'),
        'operations': json.dumps([
            {"operation": "resize", "params": {}}  # Missing width/height
        ])
    }

    response = client.post(
        '/process',
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result
    assert 'width' in result['error'].lower() and 'height' in result['error'].lower()


def test_process_invalid_resize_params(client):
    """Test /process with invalid resize parameters"""
    test_image = create_test_image()

    # Test negative dimensions
    data = {
        'file': (test_image, 'test.png'),
        'operations': json.dumps([
            {"operation": "resize", "params": {"width": -100, "height": 500}}
        ])
    }

    response = client.post(
        '/process',
        data=data,
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    result = json.loads(response.data)
    assert 'error' in result
    assert 'positive' in result['error'].lower()
