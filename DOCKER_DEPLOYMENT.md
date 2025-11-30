# Saving Server - Docker Deployment Guide

## Quick Start for Users

### Prerequisites
- Docker installed
- Docker Compose installed

### Deployment Steps

1. **Clone or download this repository**

2. **Create a `.env` file** (optional, for custom configuration):
```env
DATABASE_URL=postgresql://admin:password@db:5432/savingdb
INTERNAL_API_KEY=your-custom-api-key-here
SECRET_KEY=your-super-secret-key-here
DEBUG=false
```

3. **Start the services**:
```bash
docker-compose up -d
```

4. **Initialize the database** (first time only):
```bash
# Copy SQL file to database container
docker cp create_database.sql $(docker-compose ps -q db):/tmp/

# Execute SQL script
docker-compose exec db psql -U admin -d savingdb -f /tmp/create_database.sql
```

5. **Verify it's running**:
```bash
curl http://localhost:5001/health
```

### Using Pre-built Image from Docker Hub

If the image is available on Docker Hub, update `docker-compose.yml`:

```yaml
services:
  app:
    image: yassine4555/saving-server:latest  # Replace with your Docker Hub username
    # Remove the 'build: .' line
```

Then run:
```bash
docker-compose pull
docker-compose up -d
```

### API Access

The server will be available at: `http://localhost:5001`

**Authentication**: All requests require the `X-Internal-Key` header:
```bash
curl -H "X-Internal-Key: nexus-internal-secret-key-123" http://localhost:5001/users/
```

### Configuration

You can customize the following environment variables in `docker-compose.yml`:

- `INTERNAL_API_KEY`: Your internal API key for service authentication
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: PostgreSQL connection string
- `DEBUG`: Set to `true` for development mode

### Storage

Uploaded files and meeting logs are stored in `./storage/` directory.

### Stopping the Services

```bash
docker-compose down

# To remove volumes (database data):
docker-compose down -v
```

### Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f app
docker-compose logs -f db
```

### Troubleshooting

**Database connection failed:**
```bash
docker-compose restart db
docker-compose logs db
```

**App won't start:**
```bash
docker-compose logs app
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up --build -d
```
