/**
 * Image Processor Frontend Application
 * Handles file uploads, image processing, and result display
 */

// Configuration
const CONFIG = {
  // Detect API URL based on localhost or use current hostname
  API_URL: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : `http://${window.location.hostname}:5000`,

  // File validation
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: ['image/png', 'image/jpeg', 'image/gif'],
  ALLOWED_EXTENSIONS: ['png', 'jpg', 'jpeg', 'gif']
};

// DOM Elements
const DOM = {
  // File input elements
  fileInput: null,
  dropZone: null,

  // Operation selection
  operationCheckboxes: null,
  resizeWidth: null,
  resizeHeight: null,
  blurRadius: null,
  thumbnailMaxSize: null,

  // Preview section
  originalImage: null,
  imagePreview: null,

  // Process button
  processBtn: null,

  // Results section
  resultsContainer: null,
  processedImage: null,
  metadata: null,

  // Error and status
  errorMessage: null,
  loadingIndicator: null,

  // Reset button
  resetBtn: null
};

// Application state
let state = {
  selectedFile: null,
  isProcessing: false,
  lastResult: null
};

/**
 * Initialize the application
 * Called when DOM is ready
 */
function initApp() {
  // Cache DOM elements
  cacheElements();

  // Set up event listeners
  setupEventListeners();

  // Check API health on page load
  checkAPIHealth();
}

/**
 * Cache frequently accessed DOM elements
 */
function cacheElements() {
  DOM.fileInput = document.getElementById('fileInput');
  DOM.dropZone = document.getElementById('dropZone');

  DOM.operationCheckboxes = {
    resize: document.getElementById('operationResize'),
    grayscale: document.getElementById('operationGrayscale'),
    blur: document.getElementById('operationBlur'),
    thumbnail: document.getElementById('operationThumbnail')
  };

  DOM.resizeWidth = document.getElementById('resizeWidth');
  DOM.resizeHeight = document.getElementById('resizeHeight');
  DOM.blurRadius = document.getElementById('blurRadius');
  DOM.thumbnailMaxSize = document.getElementById('thumbnailMaxSize');

  DOM.originalImage = document.getElementById('originalImage');
  DOM.imagePreview = document.getElementById('imagePreview');

  DOM.processBtn = document.getElementById('processBtn');

  DOM.resultsContainer = document.getElementById('resultsContainer');
  DOM.processedImage = document.getElementById('processedImage');
  DOM.metadata = document.getElementById('metadata');

  DOM.errorMessage = document.getElementById('errorMessage');
  DOM.loadingIndicator = document.getElementById('loadingIndicator');

  DOM.resetBtn = document.getElementById('resetBtn');
}

/**
 * Set up all event listeners
 */
function setupEventListeners() {
  // File input click
  if (DOM.fileInput) {
    DOM.fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        handleFileSelect(file);
      }
    });
  }

  // Drag and drop
  if (DOM.dropZone) {
    DOM.dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.stopPropagation();
      DOM.dropZone.classList.add('dragover');
    });

    DOM.dropZone.addEventListener('dragleave', (e) => {
      e.preventDefault();
      e.stopPropagation();
      DOM.dropZone.classList.remove('dragover');
    });

    DOM.dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      e.stopPropagation();
      DOM.dropZone.classList.remove('dragover');

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFileSelect(files[0]);
        // Update file input to reflect selection
        if (DOM.fileInput) {
          DOM.fileInput.files = files;
        }
      }
    });

    // Click on drop zone to trigger file input
    DOM.dropZone.addEventListener('click', () => {
      if (DOM.fileInput) {
        DOM.fileInput.click();
      }
    });
  }

  // Process button
  if (DOM.processBtn) {
    DOM.processBtn.addEventListener('click', processImage);
  }

  // Reset button
  if (DOM.resetBtn) {
    DOM.resetBtn.addEventListener('click', resetForm);
  }
}

/**
 * Handle file selection and validation
 * @param {File} file - The selected file
 */
function handleFileSelect(file) {
  clearError();

  // Validate file type
  if (!validateFileType(file)) {
    showError(`Invalid file type. Allowed types: ${CONFIG.ALLOWED_EXTENSIONS.join(', ')}`);
    return;
  }

  // Validate file size
  if (!validateFileSize(file)) {
    showError(`File too large. Maximum size: ${formatFileSize(CONFIG.MAX_FILE_SIZE)}`);
    return;
  }

  // Store file in state
  state.selectedFile = file;

  // Display preview
  displayImagePreview(file);
}

/**
 * Validate file type
 * @param {File} file - File to validate
 * @returns {boolean} True if file type is allowed
 */
function validateFileType(file) {
  return CONFIG.ALLOWED_TYPES.includes(file.type);
}

/**
 * Validate file size
 * @param {File} file - File to validate
 * @returns {boolean} True if file size is within limit
 */
function validateFileSize(file) {
  return file.size <= CONFIG.MAX_FILE_SIZE;
}

/**
 * Display image preview
 * @param {File} file - Image file to preview
 */
function displayImagePreview(file) {
  const reader = new FileReader();

  reader.onload = (e) => {
    const dataUrl = e.target.result;

    if (DOM.imagePreview) {
      DOM.imagePreview.src = dataUrl;
      DOM.imagePreview.style.display = 'block';
    }

    if (DOM.originalImage) {
      DOM.originalImage.textContent = `Selected: ${file.name}`;
    }
  };

  reader.readAsDataURL(file);
}

/**
 * Collect selected operations from checkboxes
 * @returns {Array} Array of operation objects
 */
function getSelectedOperations() {
  const operations = [];

  // Resize
  if (DOM.operationCheckboxes.resize?.checked) {
    const width = parseInt(DOM.resizeWidth?.value) || 0;
    const height = parseInt(DOM.resizeHeight?.value) || 0;

    if (width > 0 && height > 0) {
      operations.push({
        operation: 'resize',
        params: { width, height }
      });
    }
  }

  // Grayscale
  if (DOM.operationCheckboxes.grayscale?.checked) {
    operations.push({
      operation: 'grayscale',
      params: {}
    });
  }

  // Blur
  if (DOM.operationCheckboxes.blur?.checked) {
    const radius = parseInt(DOM.blurRadius?.value) || 5;
    operations.push({
      operation: 'blur',
      params: { radius }
    });
  }

  // Thumbnail
  if (DOM.operationCheckboxes.thumbnail?.checked) {
    const maxSize = parseInt(DOM.thumbnailMaxSize?.value) || 200;
    operations.push({
      operation: 'thumbnail',
      params: { max_size: maxSize }
    });
  }

  return operations;
}

/**
 * Process the selected image
 */
async function processImage() {
  clearError();

  // Validate file selection
  if (!state.selectedFile) {
    showError('Please select an image first');
    return;
  }

  // Get selected operations
  const operations = getSelectedOperations();

  // Validate at least one operation is selected
  if (operations.length === 0) {
    showError('Please select at least one operation');
    return;
  }

  // Prevent multiple submissions
  if (state.isProcessing) {
    return;
  }

  // Show loading state
  state.isProcessing = true;
  showLoading(true);
  if (DOM.processBtn) {
    DOM.processBtn.disabled = true;
  }

  try {
    // Prepare FormData
    const formData = new FormData();
    formData.append('file', state.selectedFile);
    formData.append('operations', JSON.stringify(operations));

    // Send request to API
    const response = await fetch(`${CONFIG.API_URL}/process`, {
      method: 'POST',
      body: formData
    });

    // Handle response
    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || 'Failed to process image');
    }

    // Display results
    displayResults(result);
    state.lastResult = result;

  } catch (error) {
    showError(error.message || 'An error occurred while processing the image');
  } finally {
    // Reset loading state
    state.isProcessing = false;
    showLoading(false);
    if (DOM.processBtn) {
      DOM.processBtn.disabled = false;
    }
  }
}

/**
 * Display processing results
 * @param {Object} result - API response with processed image and metadata
 */
function displayResults(result) {
  if (!DOM.resultsContainer || !DOM.processedImage || !DOM.metadata) {
    return;
  }

  // Display processed image
  if (result.processed_image) {
    DOM.processedImage.src = result.processed_image;
    DOM.processedImage.style.display = 'block';
  }

  // Display metadata
  if (result.metadata) {
    const metadata = result.metadata;
    const [origW, origH] = metadata.original_dimensions || [0, 0];
    const [procW, procH] = metadata.processed_dimensions || [0, 0];

    let metadataHtml = `
      <h3>Processing Results</h3>
      <dl>
        <dt>Original Dimensions:</dt>
        <dd>${origW} × ${origH} pixels</dd>

        <dt>Processed Dimensions:</dt>
        <dd>${procW} × ${procH} pixels</dd>

        <dt>Operations Applied:</dt>
        <dd>${metadata.operations_applied}</dd>

        <dt>Filename:</dt>
        <dd>${metadata.filename || 'N/A'}</dd>

        <dt>Timestamp:</dt>
        <dd>${metadata.timestamp || 'N/A'}</dd>
      </dl>
    `;

    DOM.metadata.innerHTML = metadataHtml;
  }

  // Show results container
  DOM.resultsContainer.style.display = 'block';

  // Scroll to results
  DOM.resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
  if (DOM.errorMessage) {
    DOM.errorMessage.textContent = message;
    DOM.errorMessage.style.display = 'block';
  }
}

/**
 * Clear error message
 */
function clearError() {
  if (DOM.errorMessage) {
    DOM.errorMessage.textContent = '';
    DOM.errorMessage.style.display = 'none';
  }
}

/**
 * Show or hide loading indicator
 * @param {boolean} show - True to show, false to hide
 */
function showLoading(show) {
  if (DOM.loadingIndicator) {
    DOM.loadingIndicator.style.display = show ? 'block' : 'none';
  }
}

/**
 * Reset form to initial state
 */
function resetForm() {
  // Clear file selection
  state.selectedFile = null;
  if (DOM.fileInput) {
    DOM.fileInput.value = '';
  }

  // Hide preview
  if (DOM.imagePreview) {
    DOM.imagePreview.style.display = 'none';
    DOM.imagePreview.src = '';
  }

  if (DOM.originalImage) {
    DOM.originalImage.textContent = 'No image selected';
  }

  // Uncheck all operations
  Object.values(DOM.operationCheckboxes).forEach(checkbox => {
    if (checkbox) {
      checkbox.checked = false;
    }
  });

  // Reset operation parameters to defaults
  if (DOM.resizeWidth) DOM.resizeWidth.value = '400';
  if (DOM.resizeHeight) DOM.resizeHeight.value = '300';
  if (DOM.blurRadius) DOM.blurRadius.value = '5';
  if (DOM.thumbnailMaxSize) DOM.thumbnailMaxSize.value = '200';

  // Hide results
  if (DOM.resultsContainer) {
    DOM.resultsContainer.style.display = 'none';
  }

  if (DOM.processedImage) {
    DOM.processedImage.src = '';
  }

  if (DOM.metadata) {
    DOM.metadata.innerHTML = '';
  }

  // Clear errors
  clearError();

  // Reset state
  state.lastResult = null;
}

/**
 * Check API health
 * Verify that the backend is accessible
 */
async function checkAPIHealth() {
  try {
    const response = await fetch(`${CONFIG.API_URL}/health`);

    if (!response.ok) {
      console.warn('API health check failed');
      return;
    }

    const data = await response.json();
    console.log('API is healthy:', data);

  } catch (error) {
    console.error('Failed to connect to API:', error);
    console.error(`Attempted to reach: ${CONFIG.API_URL}`);
    showError(`Cannot connect to API at ${CONFIG.API_URL}. Make sure the backend is running.`);
  }
}

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', initApp);
