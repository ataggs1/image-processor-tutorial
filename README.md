# Image Processor Tutorial

A beginner-friendly tutorial for learning Docker, Kubernetes, and Knative through building an image processing application.

## Progress

- [x] **Phase 1: Docker Containerization** - Complete! ✅
- [ ] **Phase 2: Kubernetes Deployment** - Coming soon
- [ ] **Phase 3: Knative Integration** - Coming soon

## Current Phase: Docker Containerization

Two-service application fully containerized with Docker:
- **Backend API** (Python/Flask): Processes images (resize, grayscale, blur, thumbnail)
- **Frontend** (HTML/JS/Nginx): Upload interface and results display

### Prerequisites

- Docker Desktop installed and running
- Python 3.11+ (for local testing only)
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/ataggs1/image-processor-tutorial.git
cd image-processor-tutorial

# Build and run with Docker Compose
docker-compose up --build -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/health

# Stop services
docker-compose down
```

### Detailed Tutorial

See [docs/PHASE-1-DOCKER.md](docs/PHASE-1-DOCKER.md) for step-by-step instructions and explanations.

## Project Structure

```
image-processor-tutorial/
├── backend/
│   ├── app.py                 # Flask API
│   ├── processor.py           # Image processing module
│   ├── test_app.py            # API tests (5 tests)
│   ├── test_processor.py      # Processor tests (7 tests)
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container definition
│   └── .dockerignore
├── frontend/
│   ├── public/
│   │   ├── index.html         # Upload interface
│   │   ├── style.css          # Responsive styling
│   │   └── app.js             # Application logic
│   ├── nginx.conf             # Nginx configuration
│   ├── Dockerfile             # Frontend container definition
│   └── .dockerignore
├── docs/
│   └── PHASE-1-DOCKER.md      # Detailed Phase 1 tutorial
├── docker-compose.yml         # Multi-container orchestration
├── README.md                  # This file
└── .gitignore
```

## Features

- **Image Upload**: Drag-and-drop or file selection
- **Processing Operations**:
  - Resize to custom dimensions
  - Convert to grayscale
  - Apply blur effect
  - Generate thumbnail
- **Results Display**: Side-by-side comparison of original and processed images
- **Persistent Storage**: Images saved to Docker volume
- **Production Ready**: Gunicorn + Nginx, health checks, proper error handling

## Learning Goals

### Phase 1 (Current) ✅
- Writing production-ready Dockerfiles
- Building and optimizing Docker images
- Container networking and communication
- Persistent data with Docker volumes
- Multi-container orchestration with Docker Compose
- Health checks and monitoring

### Phase 2 (Coming Soon)
- Setting up local Kubernetes cluster (Minikube/Kind)
- Writing Kubernetes manifests (Deployments, Services)
- Service discovery and networking
- Persistent volumes and claims
- ConfigMaps and Secrets
- Health checks and readiness probes

### Phase 3 (Coming Soon)
- Installing Knative Serving
- Converting to serverless functions
- Auto-scaling and scale-to-zero
- Request-driven compute
- Traffic splitting and canary deployments

## Testing

### Run Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest -v

# Expected: 12/12 tests PASSED
```

### Test with Docker Compose

```bash
# Start services
docker-compose up -d

# Test backend health
curl http://localhost:5000/health

# Test in browser
# Open http://localhost:3000 and upload an image

# View logs
docker-compose logs -f

# Cleanup
docker-compose down
```

## Development

### Local Development (without Docker)

```bash
# Backend
cd backend
pip install -r requirements.txt
export UPLOAD_FOLDER=../data/uploads
export PROCESSED_FOLDER=../data/processed
mkdir -p ../data/uploads ../data/processed
python app.py

# Frontend
# Open frontend/public/index.html in browser
# Note: CORS will prevent API calls unless backend is also running
```

## Docker Commands Reference

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build -d

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec backend sh
```

## Contributing

This is a learning project. Feel free to fork and experiment!

## License

MIT License - See LICENSE file for details

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
