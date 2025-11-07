# Railway Deployment Guide for Automated-Attendance

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)
- Your repository: https://github.com/vishalharkal15/A.git

## Configuration Files Updated

I've configured the following files for Railway deployment:

1. **Procfile** - Tells Railway how to start your app
2. **railway.json** - Railway-specific configuration
3. **nixpacks.toml** - Build configuration for Nixpacks
4. **startup.sh** - Alternative startup script
5. **app.py** - Updated to:
   - Serve React frontend from `/dist` folder
   - Use Railway's PORT environment variable
6. **.railwayignore** - Excludes unnecessary files from deployment

## Deployment Steps

### Step 1: Push Your Changes to GitHub

First, commit and push all the configuration changes:

```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

### Step 2: Deploy on Railway

1. **Go to Railway**: Visit https://railway.app
2. **Sign In**: Log in with your GitHub account
3. **Create New Project**: 
   - Click "New Project"
   - Select "Deploy from GitHub repo"
4. **Select Repository**:
   - Choose `vishalharkal15/A` repository
   - Click "Deploy Now"

### Step 3: Configure Environment Variables (if needed)

If your app uses environment variables:

1. Go to your project in Railway
2. Click on your service
3. Go to "Variables" tab
4. Add any required environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<your-secret-key>`
   - Add any database URLs or API keys

### Step 4: Monitor Deployment

1. Railway will automatically:
   - Install Node.js dependencies
   - Build the React frontend (Vite)
   - Install Python dependencies
   - Start the Flask backend with Gunicorn

2. Check the deployment logs for any errors
3. Once deployed, Railway will provide a URL like: `https://your-app.up.railway.app`

## Application Architecture

Your application is configured as a **monolithic deployment**:
- **Frontend**: React (Vite) - built to `/dist` folder
- **Backend**: Flask API - serves both API endpoints and static frontend
- **Server**: Gunicorn (production WSGI server)

## Important Notes

### Port Configuration
Railway automatically assigns a PORT environment variable. The app is configured to use it:
```python
port = int(os.environ.get("PORT", 5000))
```

### Static Files
Flask serves the React build from the `/dist` folder:
- API routes: `/api/*`
- Frontend: All other routes serve `index.html` (SPA routing)

### Dependencies
- **Python**: TensorFlow, Keras, MTCNN, Flask, Gunicorn
- **Node.js**: React, Vite, Axios

### Database
Your app uses SQLAlchemy. For production:
- Consider using Railway's PostgreSQL plugin
- Update database URL in environment variables

## Troubleshooting

### Build Fails
- Check Railway build logs
- Ensure all dependencies are in `requirements.txt` and `package.json`
- Verify Python version compatibility (Python 3.11)

### Application Won't Start
- Check if Gunicorn is installed: `pip install gunicorn`
- Verify PORT environment variable is being used
- Check startup logs for errors

### Frontend Not Loading
- Ensure `npm run build` completed successfully
- Check that `/dist` folder contains built files
- Verify Flask routes are serving static files correctly

### Memory Issues
- TensorFlow and Keras models are memory-intensive
- Consider upgrading Railway plan if needed
- Monitor memory usage in Railway dashboard

## Alternative Deployment Methods

### Using Separate Services
For better performance, consider splitting frontend and backend:

1. **Frontend** (Vercel/Netlify):
   - Deploy React app separately
   - Update API base URL in React app

2. **Backend** (Railway):
   - Keep only Flask API
   - Enable CORS for frontend domain

## Useful Commands

### Local Testing
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Build frontend
npm run build

# Test production setup
gunicorn app:app
```

### Update Deployment
```bash
git add .
git commit -m "Update message"
git push origin main
# Railway will auto-deploy on push
```

## Resources

- Railway Documentation: https://docs.railway.app
- Your Repository: https://github.com/vishalharkal15/A.git
- Railway Dashboard: https://railway.app/dashboard

## Support

If you encounter issues:
1. Check Railway build logs
2. Review this guide
3. Check Railway's documentation
4. Contact Railway support (for platform issues)

---

**Note**: Make sure to push all these configuration files to your GitHub repository before deploying on Railway!
