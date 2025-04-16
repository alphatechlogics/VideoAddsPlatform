# Quick Start Guide: Video Ads API

## 1. Install Python

1. Go to https://www.python.org/downloads/
2. Python for Window, Mac, Linux 
3. Click "Download Python 3.12" (latest version)
4. Run the installer
5. **IMPORTANT**: Check "Add Python to PATH" during installation
6. Click "Install Now"


## 2. Verify Python Installation

Open Terminal/Command Prompt and type:
```bash
python --version
```
for MacOS
```bash
python3 --version
```

You should see something like: `Python 3.12`

## 3. Open the Project Directory

1. Create a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate  or venv/scripts/activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

4. Install required packages:
```bash
pip install -r requirements.txt
```

1. Create a `.env` file:
```bash
# change the Keys with actual keys
YOUTUBE_API_KEY=your_youtube_api_key
JWT_SECRET_KEY=your_secret_key

```

## 4. Run the API

1. Make sure you're in the project folder and virtual environment is activated
2. Start the API:
```bash
uvicorn app.main:app --reload
```

3. The API is now running! Open your web browser and go to:
   - API Documentation: http://localhost:8000/docs
   - API Status: http://localhost:8000/

## 5. Test the API

1. Get an access token:
```bash
curl -X POST "http://localhost:8000/api/auth/token" \
```
The above Endpoint create the Token then save that token in env file with `JWT_SECRET_KEY`

1. Use the token to search videos:
```bash
curl -X GET "http://localhost:8000/api/videos/search?keyword=cats" \
  -H "Authorization: Bearer your_access_token"
```

## 6. Stop the API

Press `Ctrl+C` in the terminal where the API is running.

## 7. Restart the API

1. Open Terminal/Command Prompt
2. Navigate to the project folder:


1. Start the API:
```bash
uvicorn app.main:app --reload
```

## Troubleshooting

### If Python is not found:
- Windows: Make sure you checked "Add Python to PATH" during installation
- Mac/Linux: Try `python3` instead of `python`

### If pip is not found:
```bash
# Windows
python -m pip install --upgrade pip

# Mac/Linux
python3 -m pip install --upgrade pip
```

### If port 8000 is in use:
```bash
# Change the port number
uvicorn app.main:app --reload --port 8001
```

### If you get permission errors:
- Windows: Run Command Prompt as Administrator
- Mac/Linux: Use `sudo` before the command

## Need Help?

1. Check the terminal for error messages
2. Make sure Python is installed correctly
3. Verify the virtual environment is activated
4. Check if all packages are installed
5. Contact support if issues persist 