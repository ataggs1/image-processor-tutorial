# Phase 1: Docker Containerization

Learn Docker basics by containerizing a two-service image processing application.

## Learning Objectives

By completing this phase, you will understand:

- **Docker fundamentals**: Images, containers, layers
- **Writing Dockerfiles**: Multi-stage builds, optimization
- **Container networking**: How services communicate
- **Volumes**: Persistent data storage
- **Docker Compose**: Multi-container orchestration

## Prerequisites

- Docker Desktop installed and running
- Git
- Text editor or IDE

## Architecture

```
┌─────────────┐     ┌─────────────┐
│  Frontend   │────>│   Backend   │
│  (Nginx)    │     │  (Python)   │
│  Port 3000  │     │  Port 5000  │
└─────────────┘     └─────────────┘
                          │
                          v
                    ┌──────────┐
                    │  Volume  │
                    │  /data   │
                    └──────────┘
```

## Step-by-Step Guide

### Step 1: Clone or Navigate to Project

```bash
cd image-processor-tutorial
```

### Step 2: Understand the Dockerfiles

#### Backend Dockerfile

The backend Dockerfile (`backend/Dockerfile`) uses a Python base image:

```dockerfile
FROM python:3.11-slim
```

**Key concepts:**
- **Base image**: Starting point with Python pre-installed
- **Layer caching**: Dependencies installed before code (changes less frequently)
- **Production server**: Uses Gunicorn instead of Flask's dev server

**Why Gunicorn?**
Flask's built-in server is for development only. Gunicorn is a production WSGI server that can handle multiple concurrent requests.

**Dockerfile breakdown:**
1. **Base image** - Python 3.11 slim (minimal size)
2. **Working directory** - Sets `/app` as the working directory
3. **System dependencies** - Installs gcc (needed for Pillow)
4. **Python dependencies** - Copies requirements.txt first (layer caching!)
5. **Application code** - Copies app.py and processor.py
6. **Data directories** - Creates folders for uploads/processed images
7. **Environment variables** - Configures Flask app settings
8. **Startup command** - Runs Gunicorn with 2 workers

#### Frontend Dockerfile

The frontend Dockerfile (`frontend/Dockerfile`) uses Nginx Alpine:

```dockerfile
FROM nginx:1.25-alpine
```

**Key concepts:**
- **Alpine Linux**: Minimal Linux distribution (5MB vs 100MB+)
- **Static file serving**: Nginx excels at serving HTML/CSS/JS
- **Custom configuration**: We replace default Nginx config

**Why Nginx?**
- High-performance web server
- Excellent at serving static files
- Built-in gzip compression
- Proper caching headers

### Step 3: Build Images

Build each service separately to understand the process:

```bash
# Build backend
docker build -t image-processor-backend:v1 ./backend

# Build frontend  
docker build -t image-processor-frontend:v1 ./frontend
```

**Watch the output:**
- Each line represents a layer
- Layers are cached (second build is faster)
- Final image size is shown

**Inspect images:**

```bash
docker images | grep image-processor
```

### Step 4: Run Backend Manually

Before using Docker Compose, run containers manually to understand networking:

```bash
# Create a network
docker network create image-processor-net

# Create a volume
docker volume create image-data

# Run backend
docker run -d \
  --name backend \
  --network image-processor-net \
  -p 5000:5000 \
  -v image-data:/data \
  image-processor-backend:v1
```

**Test it:**

```bash
curl http://localhost:5000/health
```

Expected: `{"status":"healthy"}`

### Step 5: Run Frontend Manually

```bash
# Run frontend
docker run -d \
  --name frontend \
  --network image-processor-net \
  -p 3000:80 \
  image-processor-frontend:v1
```

**Test it:**

Open browser to `http://localhost:3000`

**Note:** The frontend JavaScript uses `localhost:5000` to reach the backend. This works because we're accessing from the host browser. In Kubernetes (Phase 2), we'll use proper service discovery.

### Step 6: Clean Up Manual Containers

```bash
docker stop frontend backend
docker rm frontend backend
docker network rm image-processor-net
docker volume rm image-data
```

### Step 7: Use Docker Compose

Docker Compose defines the entire stack in one file:

```bash
# Build and start
docker-compose up --build -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**What Docker Compose does:**
- Creates network automatically
- Creates volume automatically
- Starts services in dependency order (`depends_on`)
- Handles container naming
- Provides service discovery (containers can reach each other by service name)

### Step 8: Test the Application

1. **Open** `http://localhost:3000`
2. **Upload** an image (JPEG, PNG, etc.)
3. **Select** operations: Resize (800x600) + Grayscale
4. **Click** "Process Image"
5. **Verify** results appear

### Step 9: Inspect Container Internals

```bash
# Enter backend container
docker exec -it image-processor-backend sh

# Inside container:
ls /data/uploads     # See uploaded images
ls /data/processed   # See processed images
env                  # See environment variables
exit
```

### Step 10: Test Data Persistence

```bash
# Upload and process an image
# Then stop containers
docker-compose down

# Start again
docker-compose up -d

# Check if data persisted
docker exec image-processor-backend sh -c "ls /data/uploads"
```

**Key concept:** Volumes persist data even when containers are deleted.

### Step 11: Monitor Resource Usage

```bash
# See CPU/memory usage
docker stats

# See detailed container info
docker inspect image-processor-backend
```

## Key Concepts Explained

### Images vs Containers

- **Image**: Blueprint (like a class in programming)
- **Container**: Running instance (like an object)

```bash
# One image, multiple containers
docker run -d --name backend1 image-processor-backend:v1
docker run -d --name backend2 image-processor-backend:v1
```

### Layers and Caching

Each Dockerfile instruction creates a layer. Layers are cached and reused:

```dockerfile
COPY requirements.txt .      # Layer 1: Changes rarely
RUN pip install -r ...       # Layer 2: Changes rarely
COPY app.py processor.py .   # Layer 3: Changes often
```

**Best practice:** Order instructions from least to most frequently changing.

### Port Mapping

`-p 3000:80` means:
- Host port 3000 → Container port 80
- Traffic to `localhost:3000` on your machine goes to port 80 inside the container

### Volumes vs Bind Mounts

**Volumes** (what we use):
- Managed by Docker
- Stored in Docker's storage area
- Best for production

**Bind mounts**:
- Direct mapping to host filesystem
- Good for development (live code reload)

```bash
# Bind mount example (development)
docker run -v $(pwd)/backend:/app backend-image
```

### Networking

Docker Compose creates a default bridge network. Services can reach each other by name:

- Frontend can call `http://backend:5000` (won't work in our case due to browser)
- Backend can call `http://frontend:80`

## Common Issues

### "Cannot connect to Docker daemon"

**Solution:** Ensure Docker Desktop is running

### "Port already in use"

**Solution:** Another service is using that port

```bash
# Find process using port 5000 (Windows)
netstat -ano | findstr :5000

# Or use different port in docker-compose.yml
```

### "Network not found"

**Solution:** Recreate network

```bash
docker-compose down
docker-compose up
```

### Frontend can't reach backend

**Solution:** Check backend logs

```bash
docker-compose logs backend
```

Ensure backend is healthy:

```bash
curl http://localhost:5000/health
```

## Cleanup

```bash
# Stop and remove containers, networks
docker-compose down

# Remove volumes too (WARNING: deletes data)
docker-compose down -v

# Remove images
docker rmi image-processor-backend:v1
docker rmi image-processor-frontend:v1
```

## Docker Compose Commands Reference

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Rebuild images
docker-compose build [service-name]

# Scale a service
docker-compose up -d --scale backend=3

# View service status
docker-compose ps

# Execute command in container
docker-compose exec backend sh

# View resource usage
docker stats
```

## Next Steps

**Phase 2: Kubernetes** - Deploy to a Kubernetes cluster with service discovery, scaling, and health checks.

## Exercises

Try these to deepen your understanding:

1. **Modify the backend** to add a new image operation (rotate, crop)
2. **Optimize the Dockerfile** using multi-stage builds
3. **Add environment-specific configs** (dev vs production)
4. **Scale the backend** with multiple replicas
5. **Add logging** and log aggregation

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## Troubleshooting Tips

### Container exits immediately

```bash
# Check logs for errors
docker logs [container-name]

# Check if command in CMD/ENTRYPOINT is correct
docker inspect [image-name]
```

### Can't access application

```bash
# Verify ports are mapped correctly
docker ps

# Check if service is listening
docker exec [container-name] netstat -tuln
```

### Out of disk space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

## Summary

You've learned:
- ✅ How to write production-ready Dockerfiles
- ✅ Layer caching and optimization techniques
- ✅ Container networking and communication
- ✅ Persistent storage with volumes
- ✅ Multi-container orchestration with Docker Compose
- ✅ Debugging and troubleshooting containers

Your application is now fully containerized and ready for Kubernetes deployment in Phase 2!
