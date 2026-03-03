# AWS EC2 + Docker + Nginx Deployment Guide

## 📚 Architecture Overview

```
Internet Request
    ↓
EC2 Instance (your virtual server in the cloud)
    ↓
Nginx (port 80) - Web server
    ├── Serves static files (CSS, JS)
    ├── Serves media files (student uploads)
    └── Forwards API requests to Django
            ↓
    Gunicorn (port 8000) - WSGI server
            ↓
    Django Application
            ├── PostgreSQL (Docker container on EC2 OR RDS)
            └── S3 Bucket (media files in production)
```

---

## 🎓 Component Breakdown (What Each Does & Why)

### 1. **Docker** 
- **What:** Packages your app + dependencies into a container
- **Why:** Same environment everywhere (dev, staging, production)
- **How:** Multi-stage build - Poetry in build stage, only runtime dependencies in final image
- **Analogy:** Like shipping a fully-furnished house instead of just furniture
- **Docs:** https://docs.docker.com/get-started/

### 2. **Nginx**
- **What:** High-performance web server and reverse proxy
- **Why:** 
  - Handles static files faster than Django
  - SSL termination (HTTPS)
  - Load balancing
  - Security (shields Django from direct internet access)
- **Analogy:** Like a receptionist filtering requests before they reach your office
- **Docs:** https://nginx.org/en/docs/beginners_guide.html

### 3. **Gunicorn**
- **What:** Python WSGI HTTP server
- **Why:** Production-ready app server (Django dev server is not safe for production)
- **Analogy:** Like a professional waiter vs. your friend serving food
- **Docs:** https://docs.gunicorn.org/

### 4. **EC2**
- **What:** Virtual server in AWS cloud
- **Why:** Full control, scalable, industry standard
- **Cost:** t2.micro free tier (1 CPU, 1GB RAM, 750 hours/month)
- **Docs:** https://docs.aws.amazon.com/ec2/

### 5. **S3**
- **What:** Object storage service
- **Why:** 
  - EC2 disk is ephemeral (can be wiped)
  - Scalable (handles millions of files)
  - CDN integration (fast downloads worldwide)
- **Cost:** 5GB free tier
- **Docs:** https://docs.aws.amazon.com/s3/

### 6. **RDS (Optional)**
- **What:** Managed PostgreSQL database
- **Why:** 
  - Automatic backups
  - High availability
  - No database admin needed
- **Cost:** db.t2.micro free tier (20GB storage)
- **Docs:** https://docs.aws.amazon.com/rds/

---

## 🚀 Step-by-Step Deployment

### **Phase 1: Local Docker Testing**

1. **Copy .env.example to .env**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env with your settings**
   ```env
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=school_db
   DB_USER=postgres
   DB_PASSWORD=testpassword123
   DB_HOST=db
   USE_S3=False
   ```

3. **Build and run Docker containers**
   ```bash
   docker-compose up --build
   ```
   
   **What happens:**
   - Downloads Python, PostgreSQL, Nginx images
   - Builds your Django app into a container
   - Starts 3 containers: web (Django), db (PostgreSQL), nginx
   - Runs migrations automatically

4. **Test locally**
   - Open browser: http://localhost
   - Admin: http://localhost/admin
   - API: http://localhost/api/

5. **Stop containers**
   ```bash
   docker-compose down
   ```

---

### **Phase 2: AWS EC2 Setup**

#### **Step 1: Launch EC2 Instance**

1. Go to AWS Console → EC2 → Launch Instance
2. **Choose:**
   - Name: `django-school-server`
   - AMI: Ubuntu 22.04 LTS (free tier)
   - Instance type: t2.micro (free tier)
   - Key pair: Create new → Download `.pem` file (you'll need this to SSH)
3. **Network settings:**
   - Allow SSH (port 22) from your IP
   - Allow HTTP (port 80) from anywhere
   - Allow HTTPS (port 443) from anywhere (for future SSL)
4. **Storage:** 20GB (free tier)
5. Click **Launch Instance**
6. Note your **Public IPv4 address** (e.g., 54.123.45.67)

**Docs:** https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html

---

#### **Step 2: Connect to EC2**

**On Windows (PowerShell):**
```powershell
# Set correct permissions
icacls your-key.pem /inheritance:r
icacls your-key.pem /grant:r "$($env:USERNAME):(R)"

# Connect
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**On Mac/Linux:**
```bash
chmod 400 your-key.pem
ssh -i your-key.pem ubuntu@your-ec2-ip
```

**Docs:** https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AccessingInstancesLinux.html

---

#### **Step 3: Install Docker on EC2**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (no need for sudo)
sudo usermod -aG docker ubuntu
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker --version
docker-compose --version
```

**Docs:** https://docs.docker.com/engine/install/ubuntu/

---

#### **Step 4: Deploy Your Code to EC2**

**Option A: Git (Recommended)**
```bash
# On EC2
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

**Option B: SCP (if not using Git)**
```bash
# On your local machine
scp -i your-key.pem -r . ubuntu@your-ec2-ip:~/app/
```

---

#### **Step 5: Configure Production Environment**

```bash
# On EC2, create .env file
nano .env
```

**Production .env:**
``env
DEBUG=False
SECRET_KEY=super-secret-production-key-change-this
ALLOWED_HOSTS=your-ec2-ip,your-domain.com

DB_NAME=school_db
DB_USER=postgres
DB_PASSWORD=strong-password-here
DB_HOST=db
DB_PORT=5432

USE_S3=False  # We'll enable later
```

**Save:** `Ctrl+X` → `Y` → `Enter`

---

#### **Step 6: Run Docker on EC2**

```bash
# Build and start
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Check running containers
docker ps
```

**Test:** Open browser → `http://your-ec2-ip`

---

### **Phase 3: AWS S3 Setup (Media Files)**

#### **Step 1: Create S3 Bucket**

1. AWS Console → S3 → Create bucket
2. **Bucket name:** `django-school-media` (must be globally unique)
3. **Region:** us-east-1 (or closest to you)
4. **Uncheck** "Block all public access" (we need public read for media files)
5. Create bucket

**Docs:** https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html

---

#### **Step 2: Create IAM User for S3 Access**

1. AWS Console → IAM → Users → Create user
2. **User name:** `django-s3-user`
3. **Attach policies:** `AmazonS3FullAccess`
4. Click **Create**
5. Go to user → Security credentials → Create access key
6. **Use case:** Application running outside AWS
7. **Download** or copy:
   - Access key ID
   - Secret access key

**Docs:** https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html

---

#### **Step 3: Update .env for S3**

```bash
# On EC2
nano .env
```

Add:
```env
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=django-school-media
AWS_S3_REGION_NAME=us-east-1
```

**Restart containers:**
```bash
docker-compose down
docker-compose up -d
```

**Test:** Upload a student submission → Check S3 bucket for file

---

### **Phase 4: RDS Setup (Optional - Managed Database)**

#### **Why RDS over Docker PostgreSQL?**
- Automatic backups
- High availability
- Separate compute from storage
- Easy scaling

#### **Setup:**

1. AWS Console → RDS → Create database
2. **Engine:** PostgreSQL 16
3. **Template:** Free tier
4. **DB instance:** db.t2.micro
5. **Credentials:**
   - Master username: `postgres`
   - Master password: (set strong password)
6. **Connectivity:** 
   - VPC: Same as EC2
   - Public access: No (EC2 connects privately)
   - Security group: Allow PostgreSQL (5432) from EC2 security group
7. Create database
8. Note **Endpoint** (e.g., `mydb.abc123.us-east-1.rds.amazonaws.com`)

**Update docker-compose.yml:**
```yaml
# Comment out db service, update web service env:
services:
  web:
    environment:
      DB_HOST: your-rds-endpoint.rds.amazonaws.com
      DB_NAME: school_db
      DB_USER: postgres
      DB_PASSWORD: your-rds-password
```

**Docs:** https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html

---

## 📖 Key Files Explained

### **Dockerfile**
```dockerfile
# Stage 1: Builder - Install dependencies with Poetry
FROM python:3.12-slim as builder
RUN pip install poetry
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --only main  # Only production deps

# Stage 2: Runtime - Copy only .venv, not Poetry
FROM python:3.12-slim as runtime
COPY --from=builder /app/.venv /app/.venv  # Copy installed packages
COPY . /app/                                # Copy all code
CMD ["gunicorn", ...]                       # Start app server
```

**Why multi-stage:** 
- Build stage has Poetry (~50MB), runtime stage doesn't
- Final image is smaller and more secure
- poetry.lock ensures reproducible builds
- **Why layers matter:** Docker caches each step. If code changes, only last layer rebuilds (fast).

---

### **docker-compose.yml**
```yaml
services:
  web:       # Django app
  db:        # PostgreSQL
  nginx:     # Web server

volumes:      # Persistent data storage
  postgres_data   # DB data survives container restarts
  static_volume   # Shared between web and nginx
  media_volume
```

**Why volumes:** Without volumes, data is lost when containers restart.

---

### **nginx.conf**
```nginx
location /static/ {
    alias /app/staticfiles/;  # Nginx serves directly (fast)
}

location / {
    proxy_pass http://django;  # Forward to Django (slow requests only)
}
```

**Why:** Nginx handles 10,000+ concurrent connections. Django handles complex logic.

---

## 🔧 Common Commands

```bash
# View logs
docker-compose logs -f web
docker-compose logs -f nginx

# Restart services
docker-compose restart

# Run Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Stop everything
docker-compose down

# Remove everything (including volumes)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build
```

---

## 📚 Learning Resources

### **Docker:**
- [Docker Official Tutorial](https://docs.docker.com/get-started/)
- [Docker for Beginners](https://docker-curriculum.com/)
- [Play with Docker](https://labs.play-with-docker.com/) - Free online playground

### **Nginx:**
- [Nginx Beginner's Guide](https://nginx.org/en/docs/beginners_guide.html)
- [Nginx + Django](https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html)

### **AWS:**
- [AWS Free Tier](https://aws.amazon.com/free/)
- [AWS EC2 User Guide](https://docs.aws.amazon.com/ec2/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

### **Django Deployment:**
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [12-Factor App](https://12factor.net/) - Industry best practices

---

## 🎯 Next Steps

1. ✅ Test locally with Docker
2. ✅ Deploy to EC2
3. ✅ Set up S3 for media files
4. 🔲 Add domain name (Route 53)
5. 🔲 Add SSL certificate (Let's Encrypt)
6. 🔲 Set up CI/CD (GitHub Actions auto-deploy)
7. 🔲 Add monitoring (CloudWatch)
8. 🔲 Add caching (Redis)

---

## ⚠️ Production Checklist

- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY`
- [ ] Specific `ALLOWED_HOSTS`
- [ ] HTTPS enabled
- [ ] Database backups configured
- [ ] Environment variables not in code
- [ ] Static files on CDN
- [ ] Error monitoring (Sentry)
- [ ] Log aggregation
- [ ] Rate limiting

---

## 💡 Pro Tips

1. **Always use volumes for data:** Don't store uploads on EC2 disk
2. **Separate secrets:** Use AWS Secrets Manager for production
3. **Monitor costs:** Set up billing alerts
4. **Automate backups:** Use RDS snapshots or pg_dump cron jobs
5. **Security groups:** Only open ports you need
6. **Use .dockerignore:** Faster builds, smaller images
7. **Multi-stage builds:** For even smaller production images

---

**If you get stuck, check logs first:**
```bash
docker-compose logs -f
```

**Need help?** Share the error and I'll guide you through it!
