---
title: Public Access Setup Guide
type: note
permalink: docs-deployment-public-access-setup-guide
---

# VeoGen Public Access Setup Guide

## 🎯 Quick Setup for Public Demo Access

This guide helps you enable public access to your VeoGen instance for demos and friend access.

## 📋 Prerequisites

- VeoGen running locally on development machine
- Router with port forwarding capabilities
- Public IP address (static or dynamic)

## 🚀 5-Minute Setup

### Step 1: Get Your Public IP
```bash
curl ifconfig.me
# Note this IP address
```

### Step 2: Configure Port Forwarding
In your router admin panel, forward:
- **Port 4710** → Your PC's local IP:4710 (Frontend)
- **Port 4700** → Your PC's local IP:4700 (Backend API)

### Step 3: Update CORS Configuration
Apply the CORS patches from: `docs/troubleshooting/CORS Configuration Patches for Multi-Origin Access.md`

**Quick version:**
1. Add your public IP to `.env`:
   ```bash
   PUBLIC_IP=your.public.ip.here
   ```

2. Restart backend:
   ```bash
   docker-compose restart backend
   ```

### Step 4: Test Access
- **Local**: http://localhost:4710
- **Tailscale**: http://goliath:4710  
- **Public**: http://your-public-ip:4710

## 🔐 Security Checklist

✅ **Authentication**: All users must create accounts  
✅ **API Keys**: Protected in user settings  
✅ **Rate Limiting**: Consider adding for public endpoints  
✅ **Monitoring**: Check logs for unusual activity  
✅ **Firewall**: Only ports 4710/4700 open  

## 📱 Mobile Access

### Tailscale Users (Dev Team)
- URL: `http://goliath:4710`
- Works on iPhone/iPad after CORS patches

### Public Users (Friends)
- URL: `http://your-public-ip:4710`
- Works from any device with internet access

## 🧪 Testing Checklist

### Before Sharing with Friends:
- [ ] Can access frontend at public IP
- [ ] Can create new user account
- [ ] Can login successfully  
- [ ] Video generation works
- [ ] Movie maker accessible
- [ ] API endpoints respond correctly

### Test Commands:
```bash
# Test frontend
curl http://your-public-ip:4710

# Test backend health
curl http://your-public-ip:4700/health

# Test API docs
curl http://your-public-ip:4700/docs
```

## 🆘 Troubleshooting

### Can't Access from Outside
1. **Check port forwarding**: Verify router configuration
2. **Check firewall**: Ensure Windows Firewall allows ports
3. **Check CORS**: Apply patches from troubleshooting guide
4. **Check public IP**: May have changed if dynamic

### Login Fails on Mobile
1. **Apply CORS patches**: See troubleshooting guide
2. **Clear browser cache**: Hard refresh on mobile
3. **Check backend logs**: `docker-compose logs backend`

### Performance Issues
1. **Check bandwidth**: Video generation uses significant data
2. **Monitor resources**: Check system usage during demos
3. **Limit concurrent users**: Consider user limits for demos

## 📞 Demo Instructions for Friends

Send this to friends:

---

**🎬 Try VeoGen AI Video Generator!**

1. **Visit**: http://your-public-ip:4710
2. **Create Account**: Click "Sign Up" and create account
3. **Login**: Use your new credentials
4. **Generate Video**: 
   - Enter text description
   - Choose style and duration
   - Click "Generate Video"
5. **Try Movie Maker**: Click "Movie Maker" for multi-scene videos

**Note**: Video generation takes 2-5 minutes. Be patient! 🎥✨

---

## 🔄 Reverting to Private

To disable public access:
1. **Remove port forwarding** from router
2. **Revert CORS configuration** to localhost only
3. **Restart backend** with new config

## 📊 Monitoring Public Usage

### Check User Activity:
```bash
# View recent users
docker-compose exec postgres psql -U veogen -d veogen -c "SELECT email, created_at FROM users ORDER BY created_at DESC LIMIT 10;"

# Check video generation stats
docker-compose logs backend | grep "video_generation"
```

### Grafana Dashboards:
- **System Overview**: http://localhost:4725/d/veogen-overview
- **Video Analytics**: http://localhost:4725/d/veogen-video
- **Infrastructure**: http://localhost:4725/d/veogen-infrastructure

---

**Last Updated**: July 11, 2025  
**Related**: CORS Configuration Patches, Authentication System, Security Guide