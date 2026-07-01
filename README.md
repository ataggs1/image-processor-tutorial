# Image Processor Tutorial

A beginner-friendly tutorial for learning Docker, Kubernetes, and Knative through building an image processing application.

## Phase 1: Docker Containerization

Two-service application:
- **Backend API** (Python/Flask): Processes images (resize, grayscale, blur, thumbnail)
- **Frontend** (HTML/JS/Nginx): Upload interface and results display

### Prerequisites

- Docker Desktop installed
- Python 3.11+ (for local testing)
- Git

### Quick Start

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000/health
```

## Project Structure

```
image-processor-tutorial/
├── backend/          # Python Flask API
├── frontend/         # HTML/JS frontend
└── docker-compose.yml
```

## Learning Goals

- Writing Dockerfiles
- Building Docker images
- Container networking
- Volume mounts for persistent storage
- Multi-container orchestration with Docker Compose
