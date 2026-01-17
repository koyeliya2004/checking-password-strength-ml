# 🚀 Deployment Guide - Flask Password Assistant

This guide provides step-by-step instructions for deploying the Flask Password Assistant application to various platforms.

## 📋 Prerequisites

- Git installed
- GitHub account
- Account on your chosen deployment platform (Render, Railway, Heroku, or Docker host)

## 🎯 Recommended Deployment Platform

**Render** is the recommended platform for this Flask application because:
- ✅ Free tier available
- ✅ Native Python/Flask support
- ✅ Automatic deployments from GitHub
- ✅ Easy environment variable management
- ✅ Built-in health checks and monitoring
- ✅ No credit card required for free tier

## 🔧 Deployment Options

### Option 1: Render (Recommended)

#### Step 1: Prepare Your Repository
1. Ensure all changes are committed and pushed to GitHub
2. Verify `requirements-consolidated.txt` and `Procfile` are in the repository root

#### Step 2: Create Render Account
1. Go to [https://render.com](https://render.com)
2. Sign up using your GitHub account

#### Step 3: Deploy Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the `checking-password-strength-ml` repository
4. Configure the service:
   - **Name**: `password-assistant` (or your preferred name)
   - **Region**: Choose closest to your users
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave blank
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements-consolidated.txt`
   - **Start Command**: `cd password-ml-app && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app`
5. Select the **Free** instance type
6. Click "Create Web Service"

#### Step 4: Configure Environment Variables (Optional)
- In the Render dashboard, go to "Environment" tab
- Add any required environment variables:
  - `PYTHON_VERSION=3.12` (if needed)
  - `PORT` is automatically set by Render

#### Step 5: Verify Deployment
1. Wait for the build to complete (5-10 minutes)
2. Click on the provided URL (e.g., `https://password-assistant.onrender.com`)
3. Test the health endpoint: `https://your-app.onrender.com/health`
4. Test the UI by visiting the root URL

#### Step 6: Set Up Auto-Deploy (Optional)
- By default, Render auto-deploys on every push to the selected branch
- You can configure this in the "Settings" tab

---

### Option 2: Railway

#### Step 1: Prepare Your Repository
Same as Render - ensure all files are committed and pushed.

#### Step 2: Create Railway Account
1. Go to [https://railway.app](https://railway.app)
2. Sign up with GitHub

#### Step 3: Deploy
1. Click "New Project" → "Deploy from GitHub repo"
2. Select your repository
3. Railway will auto-detect Python and use the Procfile
4. Configure:
   - **Root Directory**: Leave blank
   - **Custom Start Command**: Already defined in Procfile
5. Click "Deploy"

#### Step 4: Configure Domain
1. Go to "Settings" → "Networking"
2. Click "Generate Domain"
3. Your app will be available at the generated URL

#### Step 5: Verify Deployment
Test the health endpoint and UI as described in the Render section.

---

### Option 3: Heroku

#### Step 1: Install Heroku CLI
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login to Heroku
heroku login
```

#### Step 2: Create Heroku App
```bash
# Navigate to your repository
cd /path/to/checking-password-strength-ml

# Create a new Heroku app
heroku create your-app-name

# Or use auto-generated name
heroku create
```

#### Step 3: Deploy
```bash
# Deploy to Heroku
git push heroku main

# If you're on a different branch
git push heroku your-branch:main
```

#### Step 4: Scale the Application
```bash
# Ensure at least one web dyno is running
heroku ps:scale web=1
```

#### Step 5: View Logs and Test
```bash
# View logs
heroku logs --tail

# Open the app in browser
heroku open
```

---

### Option 4: Docker (Self-Hosted or Cloud)

#### Step 1: Build Docker Image
```bash
# Navigate to repository root
cd /path/to/checking-password-strength-ml

# Build the Docker image
docker build -t password-assistant:latest .
```

#### Step 2: Test Locally
```bash
# Run the container
docker run -d -p 5000:5000 --name password-app password-assistant:latest

# Test health endpoint
curl http://localhost:5000/health

# View logs
docker logs password-app

# Stop the container
docker stop password-app
docker rm password-app
```

#### Step 3: Deploy to Docker Host

##### Option A: AWS ECS/Fargate
1. Push image to Amazon ECR
2. Create ECS task definition
3. Create ECS service
4. Configure load balancer

##### Option B: Google Cloud Run
```bash
# Tag image for GCR
docker tag password-assistant:latest gcr.io/YOUR-PROJECT-ID/password-assistant:latest

# Push to GCR
docker push gcr.io/YOUR-PROJECT-ID/password-assistant:latest

# Deploy to Cloud Run
gcloud run deploy password-assistant \
  --image gcr.io/YOUR-PROJECT-ID/password-assistant:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

##### Option C: DigitalOcean App Platform
1. Connect your GitHub repository
2. Select "Docker" as the source
3. Configure auto-deploy
4. Set port to 5000

---

### Option 5: Vercel (Serverless - Advanced)

⚠️ **Note**: Vercel is optimized for serverless/edge functions. For a traditional Flask app, Render or Railway is recommended. However, if you prefer Vercel:

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Configure Vercel
The `vercel.json` file is already configured in the repository.

#### Step 3: Deploy
```bash
# Navigate to repository root
cd /path/to/checking-password-strength-ml

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Known Limitations with Vercel:
- Function timeout limits (10s on free tier)
- Cold start delays
- Model files may need to be stored externally (large file size)
- Stateless functions require models to be loaded on each request

---

## 🔍 Post-Deployment Verification Checklist

After deploying to any platform, verify the following:

- [ ] Health endpoint responds: `GET /health` returns `{"status": "healthy"}`
- [ ] Home page loads: `GET /` shows the UI
- [ ] API endpoint works: `POST /api/analyze` with JSON body returns analysis
- [ ] Logs show model initialization messages
- [ ] No error messages in deployment logs
- [ ] Response times are acceptable (< 5 seconds)

### Test Commands
```bash
# Health check
curl https://your-app-url.com/health

# API test
curl -X POST https://your-app-url.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"password": "Test123!@#"}'
```

---

## 🔧 Environment Variables

No environment variables are required for basic deployment. The app uses sensible defaults.

Optional environment variables:
- `PORT` - Port to run the server (default: 5000, auto-set by most platforms)
- `PYTHON_VERSION` - Python version (default: 3.12)

---

## 📊 Monitoring and Logging

### Render
- View logs in the Render dashboard under "Logs" tab
- Metrics available in "Metrics" tab

### Railway
- View logs in the Railway dashboard under your deployment
- Real-time log streaming available

### Heroku
```bash
# View logs
heroku logs --tail --app your-app-name

# View metrics
heroku ps --app your-app-name
```

### Docker
```bash
# View logs
docker logs -f password-app

# View resource usage
docker stats password-app
```

---

## 🔄 Updating the Application

### For Render/Railway (Auto-Deploy)
1. Make changes locally
2. Commit and push to GitHub
3. Platform automatically rebuilds and redeploys

### For Heroku
```bash
git push heroku main
```

### For Docker
```bash
# Rebuild image
docker build -t password-assistant:latest .

# Stop old container
docker stop password-app
docker rm password-app

# Run new container
docker run -d -p 5000:5000 --name password-app password-assistant:latest
```

---

## 🆘 Troubleshooting

### Issue: Application won't start
**Solution**: Check logs for model loading errors. Ensure all required .pkl files are present.

### Issue: 404 errors on all routes
**Solution**: Verify the start command points to the correct app file (`app:app`)

### Issue: Timeout on model loading
**Solution**: Increase timeout in gunicorn command: `--timeout 300`

### Issue: Out of memory
**Solution**: 
- Upgrade to a paid tier with more RAM
- Reduce number of gunicorn workers: `--workers 1`

### Issue: Models not found
**Solution**: Verify model files are in the repository and check `ml_engine.py` paths

---

## 📞 Support

For deployment issues:
1. Check the platform's documentation
2. Review application logs
3. Verify all files are committed to Git
4. Ensure the Procfile/Dockerfile is correctly configured

---

## 🎯 Production Recommendations

1. **Use a CDN** for static assets
2. **Enable HTTPS** (automatic on most platforms)
3. **Set up monitoring** and alerts
4. **Configure auto-scaling** if available
5. **Regular backups** of model files
6. **Set up staging environment** for testing

---

**Last Updated**: January 2026  
**Tested Platforms**: Render ✅ | Railway ✅ | Heroku ✅ | Docker ✅ | Vercel ⚠️
