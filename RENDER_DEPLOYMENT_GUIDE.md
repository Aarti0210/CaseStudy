# 🚀 Render Deployment Guide

## 📋 **Quick Start - Deploy to Render in 10 Minutes**

### **Step 1: Prepare Your Repository**
```bash
# Make sure all changes are committed
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### **Step 2: Deploy to Render**

#### **Option A: Web Dashboard (Easiest)**
1. Go to [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure as shown below

#### **Option B: Render CLI (Advanced)**
```bash
# Install Render CLI
npm install -g @render/cli

# Login
render login

# Deploy
render deploy
```

---

## 🔧 **Render Web Service Configuration**

### **Basic Settings**
```
Name: judicial-supreme-backend
Environment: Docker
Region: Oregon (or closest to users)
Branch: main
Root Directory: . (leave empty)
```

### **Build Settings**
```
Dockerfile Path: ./Dockerfile
Docker Context: .
```

### **Runtime Settings**
```
Instance Type: Free (upgrade to Standard for production)
Command: gunicorn -k eventlet -w 1 run:app
Health Check Path: /health
Port: 8000
```

---

## 🗄️ **Database Setup**

### **Create PostgreSQL Service**
1. In Render dashboard: **"New +"** → **"PostgreSQL"**
2. Configure:
   ```
   Name: judicial-supreme-db
   Database Name: judicial_supreme
   User: judicial_user
   Plan: Free (upgrade for production)
   ```
3. **Important**: Copy the **Internal Database URL**

### **Connect Database to Backend**
1. Go to your **Web Service** settings
2. Add **Environment Variables**:
   ```
   DATABASE_URL = [paste Internal Database URL from PostgreSQL service]
   ```

---

## 🔐 **Environment Variables Configuration**

Add these in your Web Service → **Environment** section:

### **Required Variables**
```bash
# Core Configuration
FLASK_ENV=production
SECRET_KEY=Ab234h12iihjik39jkl21lala90sjdke
JWT_SECRET_KEY=hjk234hsiut8wok213dnxufia9w0ekwn

# Database (from PostgreSQL service)
DATABASE_URL=postgresql://case_database_user:oYqxCbvitwwpscTeRKdGretEIW0fuzHO@dpg-d6o09rfkijhs739uq5sg-a.oregon-postgres.render.com/case_database

# Performance
GUNICORN_WORKERS=1
LOG_LEVEL=INFO
```

### **Optional Variables**
```bash
# AI Services (if using)
OPENAI_API_KEY=your-openai-api-key

# Email Services (if using OTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=no-reply@judicial.local
```

---

## 🚀 **Deployment Process**

### **Automatic Deployment**
1. **Push to GitHub** → Render automatically builds and deploys
2. **Monitor Logs** in Render dashboard
3. **Health Check** at `https://your-app.onrender.com/health`

### **Manual Deployment**
1. In Render dashboard: **"Manual Deploy"** → **"Deploy Latest Commit"**
2. Wait for build to complete (2-3 minutes)
3. Check deployment logs

---

## 📊 **Post-Deployment Verification**

### **Health Check**
```bash
curl https://your-app-name.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "judicial-backend",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "db": true
  }
}
```

### **API Test**
```bash
# Test signup
curl -X POST https://your-app-name.onrender.com/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test User","email":"test@example.com","password":"SecurePass123!","role":"citizen"}'
```

---

## 🔧 **Troubleshooting Common Issues**

### **Issue 1: Database Connection Failed**
**Solution:**
1. Check DATABASE_URL format
2. Verify PostgreSQL service is running
3. Ensure database user has correct permissions

### **Issue 2: Health Check Failing**
**Solution:**
1. Check application logs in Render dashboard
2. Verify all environment variables are set
3. Ensure port 8000 is exposed in Dockerfile

### **Issue 3: Build Fails**
**Solution:**
1. Check requirements.txt for correct versions
2. Verify Dockerfile syntax
3. Check for missing files in repository

### **Issue 4: 502 Bad Gateway**
**Solution:**
1. Application might be starting slowly
2. Increase health check grace period to 120 seconds
3. Check application logs for startup errors

---

## 📈 **Production Optimizations**

### **Upgrade to Standard Plan**
```bash
# In Render dashboard:
# 1. Go to Web Service → Settings
# 2. Change Instance Type to "Standard"
# 3. Increase workers to 2-4
```

### **Add Redis for Rate Limiting**
```bash
# Create Redis Service:
# 1. "New +" → "Redis"
# 2. Add environment variable:
RATELIMIT_STORAGE_URI=redis://your-redis:6379/0
```

### **Enable Custom Domain**
```bash
# 1. Go to Web Service → Settings → Custom Domains
# 2. Add your domain (e.g., api.yourapp.com)
# 3. Configure DNS records
# 4. Enable SSL (automatic)
```

---

## 🔍 **Monitoring and Logging**

### **View Logs**
1. **Render Dashboard** → **Web Service** → **Logs**
2. **Real-time logs** during deployment
3. **Historical logs** for troubleshooting

### **Monitor Performance**
1. **Metrics** tab in Render dashboard
2. **Response times** and **error rates**
3. **Database performance** (PostgreSQL service)

### **Set Up Alerts**
1. **Settings** → **Alerts**
2. Configure email/Slack notifications
3. Monitor uptime and performance

---

## 🔄 **CI/CD Pipeline**

### **Automatic Deployments**
```yaml
# render.yaml (already in your repo)
service:
  name: judicial-supreme-backend
  type: web
  env: docker
  plan: free
  build:
    dockerfilePath: ./Dockerfile
  runtime:
    startCommand: gunicorn -k eventlet -w 1 run:app
    healthCheckPath: /health
```

### **Preview Deployments**
```bash
# Create pull request → Automatic preview deployment
# Test changes before merging to main
```

---

## 🛡️ **Security Best Practices**

### **Render Security**
- ✅ **HTTPS by default**
- ✅ **Isolated containers**
- ✅ **Managed database**
- ✅ **Automatic SSL**

### **Application Security**
- ✅ **Environment variables** for secrets
- ✅ **JWT tokens** for authentication
- ✅ **Rate limiting** configured
- ✅ **Input validation** in place

---

## 📱 **Testing Your Deployed API**

### **Base URL**
```
https://your-app-name.onrender.com
```

### **Test Endpoints**
```bash
# Health Check
curl https://your-app-name.onrender.com/health

# User Registration
curl -X POST https://your-app-name.onrender.com/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"name":"Test User","email":"test@example.com","password":"SecurePass123!","role":"citizen"}'

# User Login
curl -X POST https://your-app-name.onrender.com/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"SecurePass123!"}'
```

---

## 🆘 **Getting Help**

### **Render Documentation**
- [Render Docs](https://render.com/docs)
- [Docker Deployment](https://render.com/docs/docker-deployment)
- [PostgreSQL](https://render.com/docs/postgresql)

### **Common Issues**
1. **Build timeouts**: Increase build resources
2. **Memory issues**: Upgrade to Standard plan
3. **Database limits**: Monitor PostgreSQL usage

---

## 🎯 **Deployment Checklist**

### **Pre-Deployment**
- [ ] All code committed to GitHub
- [ ] Environment variables documented
- [ ] Database schema ready
- [ ] Health endpoint working

### **Deployment**
- [ ] Create Web Service on Render
- [ ] Create PostgreSQL service
- [ ] Configure environment variables
- [ ] Deploy and test

### **Post-Deployment**
- [ ] Verify health endpoint
- [ ] Test API endpoints
- [ ] Set up monitoring
- [ ] Configure custom domain (optional)

---

## 🚀 **You're Ready!**

Your **Judicial Supreme Backend** is now configured for **Render deployment** with:

- ✅ **Docker containerization**
- ✅ **PostgreSQL database**
- ✅ **Automatic deployments**
- ✅ **Health monitoring**
- ✅ **Production security**
- ✅ **Scalable architecture**

**Deploy now and start serving legal case management services!** 🎉
