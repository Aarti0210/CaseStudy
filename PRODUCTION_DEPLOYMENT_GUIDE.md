# Production Deployment Guide

## 🚀 Quick Start Production Deployment

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Redis server (for rate limiting and caching)
- Domain name with SSL certificate
- Environment variables configured

### Step 1: Environment Setup
```bash
# Clone and navigate to project
git clone <repository-url>
cd judicial_supreme_backend_v3

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Generate secure keys
python fix_security_keys.py
```

### Step 2: Database Setup
```bash
# Set database URL in .env
export DATABASE_URL="postgresql://user:password@localhost:5432/judicial_supreme"

# Run migrations
flask db upgrade

# Create initial roles (optional)
python -c "
from app import create_app
from app.models import Role
app = create_app()
with app.app_context():
    roles = ['admin', 'lawyer', 'judge', 'citizen']
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=f'{role_name.capitalize()} role')
            app.db.session.add(role)
    app.db.session.commit()
    print('Roles created successfully')
"
```

### Step 3: Redis Setup
```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

### Step 4: Environment Configuration
Update `.env` file with production values:
```bash
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-key
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Step 5: Start Production Server
```bash
# Using Gunicorn (recommended)
gunicorn -k eventlet -w 2 --bind 0.0.0.0:5000 run:app

# Or with systemd service
sudo systemctl start judicial-backend
```

## 🔧 System Configuration

### Systemd Service
Create `/etc/systemd/system/judicial-backend.service`:
```ini
[Unit]
Description=Judicial Backend API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/judicial_supreme_backend_v3
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/gunicorn -k eventlet -w 2 --bind 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable judicial-backend
sudo systemctl start judicial-backend
```

### Nginx Reverse Proxy
Create `/etc/nginx/sites-available/judicial-backend`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/judicial-backend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📊 Monitoring and Logging

### Log Configuration
Logs are automatically written to:
- Application logs: `logs/judicial_backend.log`
- Access logs: Nginx access logs
- Error logs: Nginx error logs

### Health Monitoring
```bash
# Check application health
curl https://your-domain.com/health

# Expected response
{
  "status": "ok",
  "service": "judicial-backend",
  "timestamp": "2024-01-01T00:00:00Z",
  "checks": {
    "db": true
  }
}
```

### Monitoring Setup (Optional)
```bash
# Install Prometheus and Grafana for monitoring
# Add metrics endpoint to application
# Monitor database connections, request rates, error rates
```

## 🔒 Security Hardening

### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### SSL Certificate
```bash
# Use Let's Encrypt for free SSL
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Database Security
```bash
# Create dedicated database user
CREATE USER judicial_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE judicial_supreme TO judicial_user;

# Restrict connections in postgresql.conf
listen_addresses = 'localhost'
```

## 🚀 Deployment Commands

### Pre-Deployment Checklist
```bash
# 1. Test application locally
python run.py

# 2. Run health check
curl http://localhost:5000/health

# 3. Test database connection
python test_db_connection.py

# 4. Validate security
python test_security_validation.py

# 5. Run API tests
python test_api_endpoints.py
```

### Production Deployment Sequence
```bash
# 1. Backup current deployment
sudo cp -r /path/to/current /path/to/backup/$(date +%Y%m%d_%H%M%S)

# 2. Update code
git pull origin main
pip install -r requirements.txt

# 3. Run migrations
flask db upgrade

# 4. Restart services
sudo systemctl restart judicial-backend
sudo systemctl restart nginx

# 5. Verify deployment
curl https://your-domain.com/health
```

### Rollback Procedure
```bash
# If deployment fails, rollback:
sudo systemctl stop judicial-backend
sudo cp -r /path/to/backup/<timestamp>/* /path/to/current/
sudo systemctl start judicial-backend
```

## 📈 Performance Optimization

### Database Optimization
```sql
-- Create additional indexes for performance
CREATE INDEX CONCURRENTLY idx_case_status_created ON case(status, created_at);
CREATE INDEX CONCURRENTLY idx_audit_user_timestamp ON audit_log(user_id, timestamp);
```

### Caching Strategy
```python
# Add Redis caching for frequently accessed data
# Cache user sessions, case lists, and AI responses
```

### Load Balancing
```nginx
# Multiple backend instances behind load balancer
upstream judicial_backend {
    server 127.0.0.1:5000;
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
}
```

## 🔍 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U judicial_user -d judicial_supreme

# Check connection string
echo $DATABASE_URL
```

#### Redis Connection Failed
```bash
# Check Redis status
sudo systemctl status redis-server

# Test connection
redis-cli ping

# Check Redis URL
echo $REDIS_URL
```

#### Application Not Starting
```bash
# Check logs
sudo journalctl -u judicial-backend -f

# Check configuration
python -c "from app import create_app; print(create_app().config)"
```

#### High Memory Usage
```bash
# Monitor memory usage
top -p $(pgrep -f gunicorn)

# Adjust worker count
gunicorn -k eventlet -w 1 --max-requests 1000 run:app
```

### Performance Monitoring
```bash
# Monitor system resources
htop
iotop
netstat -tulpn | grep :5000

# Monitor database
sudo -u postgres psql -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks
```bash
# Weekly: Update dependencies
pip list --outdated
pip install --upgrade package_name

# Monthly: Database maintenance
vacuumdb judicial_supreme
reindexdb judicial_supreme

# Quarterly: Security updates
sudo apt-get update && sudo apt-get upgrade
```

### Backup Strategy
```bash
# Database backup
pg_dump judicial_supreme > backup_$(date +%Y%m%d).sql

# File backup
tar -czf files_backup_$(date +%Y%m%d).tar.gz uploads/

# Configuration backup
cp .env .env.backup.$(date +%Y%m%d)
```

### Monitoring Alerts
Set up alerts for:
- Application downtime (health check failures)
- High error rates (>5%)
- Database connection issues
- High memory usage (>80%)
- Disk space usage (>90%)

---

## 🎯 Success Metrics

After deployment, monitor these metrics:
- **Uptime**: >99.9%
- **Response Time**: <200ms average
- **Error Rate**: <1%
- **Database Response**: <50ms average
- **Memory Usage**: <80% of available

## 📞 Emergency Contacts

- **Application Issues**: Check logs and restart services
- **Database Issues**: Contact database administrator
- **Security Issues**: Immediate security team notification
- **Infrastructure Issues**: Contact DevOps team

---

*Deployment Guide v1.0 - Last Updated: 2026-03-17*
