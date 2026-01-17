# 🚀 Quick Start Guide

Get the Flask Password Assistant running in under 5 minutes!

## Option 1: Local Development (Fastest)

```bash
# Clone the repository
git clone https://github.com/koyeliya2004/checking-password-strength-ml.git
cd checking-password-strength-ml

# Install dependencies
pip install -r requirements-consolidated.txt

# Run the app
cd password-ml-app
python app.py
```

Visit: http://localhost:5000

---

## Option 2: Docker (Recommended for Testing)

```bash
# Build the image
docker build -t password-assistant .

# Run the container
docker run -p 5000:5000 password-assistant
```

Visit: http://localhost:5000

---

## Option 3: Deploy to Render (Recommended for Production)

1. **Create Account**: Go to [render.com](https://render.com) and sign up
2. **New Web Service**: Click "New +" → "Web Service"
3. **Connect Repo**: Select your GitHub repository
4. **Configure**:
   - Name: `password-assistant`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements-consolidated.txt`
   - Start Command: `cd password-ml-app && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
5. **Deploy**: Click "Create Web Service"
6. **Wait**: Build takes 5-10 minutes
7. **Visit**: Your app at `https://password-assistant.onrender.com`

---

## Testing Your Deployment

### Health Check
```bash
curl https://your-app-url.com/health
```

Expected: `{"status": "healthy", "service": "password-assistant"}`

### API Test
```bash
curl -X POST https://your-app-url.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "Test123!@#"}'
```

Expected: JSON with `predicted_strength`, `issues_found`, `suggestions`, `estimated_crack_time`

---

## Need Help?

- **Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for all platforms
- **Issues**: [GitHub Issues](https://github.com/koyeliya2004/checking-password-strength-ml/issues)
- **Production Checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

---

**Ready to deploy? Pick your platform and follow the guide in DEPLOYMENT.md!**
