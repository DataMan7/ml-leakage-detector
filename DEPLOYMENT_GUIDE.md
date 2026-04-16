# 🚀 ML Leakage Detector - Deployment Guide

This guide covers deploying the ML Leakage Detector for both local development and AWS EC2 production.

---

## 🖥️ Part 1: Local Development

### System Requirements (Local Running)

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| **RAM** | 4 GB | 8 GB+ |
| **Storage** | 5 GB free | 20 GB SSD |
| **OS** | Ubuntu 20.04+ / macOS | Ubuntu 22.04 LTS |

### AI Features (NVIDIA NIM)

**Can it run on t3.medium? YES!** 🟢

The AI features use NVIDIA's cloud API, not local GPU:

- **API calls** go to `api.nvidia.com`
- **Your server** just needs internet connection
- **RAM needed**: ~500MB for the Python process
- **Storage**: 2-3 GB for dependencies

### Setup Local

```bash
# Clone and setup
git clone https://github.com/DataMan7/ml-leakage-detector.git
cd ml-leakage-detector

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Setup API key
cp .env.example .env
nano .env  # Add NVIDIA_API_KEY

# Test basic (no AI)
python -m src.detector examples/buggy_pipelines/pipeline_1_imputation_leak.py

# Test AI features
python -m src.ai_detector examples/buggy_pipelines/pipeline_1_imputation_leak.py --ai-fix
```

---

## ☁️ Part 2: AWS EC2 Deployment

### Instance Comparison

| Instance | vCPU | Memory | Best For | On-Demand Cost |
|----------|------|--------|----------|----------------|
| **t3.medium** | 2 | 4 GB | Dev / Small API | $0.042/hr |
| **t3.large** | 2 | 8 GB | Production API | $0.083/hr |
| **m5.large** | 2 | 8 GB | High traffic API | $0.10/hr |
| **g4dn.xlarge** | 4 | 16 GB + GPU | Local AI inference | $0.526/hr |

**Recommendation: t3.medium for MVP** ($30/month)

---

### Step-by-Step EC2 Deployment

#### 1. Launch Instance

```
# In AWS Console:
# 1. EC2 → Launch Instance
# 2. Name: ml-leakage-detector
# 3. Ubuntu Server 22.04 LTS (Free tier eligible)
# 4. t3.medium (or t3.large for more RAM)
# 5. Key pair: (create or use existing)
# 6. Security Group: 
#    - SSH (port 22) - Your IP
#    - HTTP (port 80) - 0.0.0.0/0
#    - HTTPS (port 443) - 0.0.0.0/0
#    - Custom TCP (port 8000) - 0.0.0.0/0 (for API)
# 7. Launch
```

#### 2. Connect to Instance

```bash
# From your terminal
ssh -i your-key.pem ubuntu@<YOUR-EC2-IP>
```

#### 3. Setup Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Docker
sudo apt install python3-pip docker.io docker-compose -y

# Clone your project
git clone https://github.com/DataMan7/ml-leakage-detector.git
cd ml-leakage-detector

# Create .env file
cp .env.example .env
sudo nano .env
# Add: NVIDIA_API_KEY=your_key_here

# Install Python deps
pip install -r requirements.txt
```

#### 4. Run as API Service (Optional)

Create a simple API using Flask/FastAPI:

```bash
# Install FastAPI
pip install fastapi uvicorn

# Create api.py
cat > api.py << 'EOF'
from fastapi import FastAPI
from src.detector import LeakageDetector
from src.ai_detector import AICodeDoctor
import json

app = FastAPI(title="ML Leakage Detector API")
detector = LeakageDetector()
ai_doctor = AICodeDoctor()

@app.get("/analyze")
def analyze(code: str):
    result = detector.detect(code)
    return result.to_dict()

@app.get("/analyze-ai")
def analyze_ai(code: str):
    result = detector.detect(code)
    fixes = []
    if result.has_leakage:
        for leak in result.leaks:
            fix = ai_doctor.generate_fix(leak.name, code)
            fixes.append({"type": leak.name, "fix": fix.fixed_code})
    return {"has_leakage": result.has_leakage, "ai_fixes": fixes}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Run API
python api.py
```

#### 5. Setup systemd Service (Production)

```bash
# Create service file
sudo nano /etc/systemd/system/ml-leakage.service

# Paste this:
[Unit]
Description=ML Leakage Detector API
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ml-leakage-detector
ExecStart=/usr/bin/python3 /home/ubuntu/ml-leakage-detector/api.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable ml-leakage
sudo systemctl start ml-leakage

# Check status
sudo systemctl status ml-leakage
```

#### 6. Access Your API

```
# Your API is now live!
curl "http://<EC2-IP>:8000/analyze?code=X.fillna(X.mean())"

# Or use AI features
curl "http://<EC2-IP>:8000/analyze-ai?code=X.fillna(X.mean())"
```

---

## 🐳 Part 3: Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create .env (will be overridden at runtime)
RUN cp .env.example .env

EXPOSE 8000

CMD ["python", "api.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  leakage-detector:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
    restart: unless-stopped
```

### Build & Run

```bash
# Build
docker build -t ml-leakage-detector .

# Run
docker run -d -p 8000:8000 \
  -e NVIDIA_API_KEY=your_key \
  ml-leakage-detector
```

---

## 💰 Monetization Setup

### Option 1: Simple API (Stripe Integration)

Add payment to your API:

```python
# In api.py
from fastapi import FastAPI, Header
from stripe import StripeClient

stripe = StripeClient("sk_live_...")

@app.get("/analyze-ai")
def analyze_ai(
    code: str, 
    authorization: str = Header(None)
):
    # Check API key (implement auth)
    if not valid_api_key(authorization):
        return {"error": "Invalid API key", "subscribe": "https://your-site.com"}
    
    # Your analysis logic
    ...
```

### Option 2: GitHub Marketplace

1. Package as GitHub App
2. List in GitHub Marketplace ($9.99/mo)
3. Auto-install on user repos

---

## 📊 Cost Breakdown

### Running Locally

| Item | Cost |
|------|------|
| Your laptop | Already owned |
| Internet | Already owned |
| NVIDIA API | Free (your NGC credits) |
| **Total** | **$0** |

### Running on t3.medium

| Item | Cost |
|------|------|
| EC2 t3.medium | $30/month |
| Data transfer | ~$5/month |
| Domain (optional) | $12/year |
| **Total** | **~$45/month** |

### Break-even Analysis

| Users | Revenue (Pro $19/mo) | Profit |
|-------|---------------------|--------|
| 3 | $57 | $12 |
| 10 | $190 | $145 |
| 100 | $1,900 | $1,855 |

---

## 🔒 Security Checklist

- [ ] Use IAM roles, not access keys
- [ ] Restrict security group to your IP only (SSH)
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Store API keys in AWS Secrets Manager
- [ ] Regular security updates: `sudo apt update`

---

## 📤 Push to GitHub & Deploy

```bash
# Push all changes
git add .
git commit -m "feat: Complete deployment setup - Docker, API, AWS guide"
git push origin main

# On EC2:
git pull origin main
sudo systemctl restart ml-leakage
```

---

## 🎯 Quick Start Commands

```bash
# Local
python -m src.detector examples/

# Local with AI
python -m src.ai_detector examples/ --ai-fix

# EC2 API
curl "http://localhost:8000/analyze?code=X.fillna(X.mean())"

# Docker
docker-compose up -d
```

**You're ready to deploy and monetize!** 🚀
