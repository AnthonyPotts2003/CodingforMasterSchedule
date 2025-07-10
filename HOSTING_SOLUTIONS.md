# Schedule Data Hosting Solutions

## 🚨 Problem
Your HTML dashboard currently uses an unreliable CORS proxy to access JSON data from Dropbox. This causes:
- ❌ Intermittent failures
- ❌ Slow loading times
- ❌ Dependency on third-party services
- ❌ Poor user experience

## 🎯 Solutions Overview

### 1. **GitHub Pages** (Recommended - Free & Reliable)
- ✅ **Best for**: Long-term, reliable hosting
- ✅ **Cost**: Free
- ✅ **Setup**: 10 minutes
- ✅ **Reliability**: Very high
- ✅ **Integration**: Works with your existing Python automation

### 2. **Netlify** (Alternative - Also Free)
- ✅ **Best for**: Quick deployment, global CDN
- ✅ **Cost**: Free
- ✅ **Setup**: 5 minutes
- ✅ **Reliability**: Very high
- ✅ **Integration**: Easy drag-and-drop

### 3. **JSONBin.io** (Simple JSON Hosting)
- ✅ **Best for**: Simple JSON storage
- ✅ **Cost**: Free tier available
- ✅ **Setup**: 2 minutes
- ✅ **Reliability**: Good
- ⚠️ **Limitations**: Request limits on free tier

## 🚀 Quick Start: GitHub Pages (Recommended)

### Step 1: Create GitHub Account & Repository
1. Go to [GitHub.com](https://github.com) and create an account
2. Create a new repository named `schedule-data`
3. Make it **public** (required for GitHub Pages)

### Step 2: Get GitHub Token
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a name like "Schedule Data Upload"
4. Select scopes: `repo` (full control of private repositories)
5. Copy the token (you'll only see it once!)

### Step 3: Run Setup Script
```bash
python setup_hosting.py
```

This script will:
- Ask for your GitHub credentials
- Create the repository if needed
- Enable GitHub Pages
- Test the upload
- Update your Dashboard.html automatically

### Step 4: Test Your Dashboard
Your JSON will be available at:
```
https://YOUR_USERNAME.github.io/schedule-data/schedule_data_combined.json
```

## 🔧 Integration with Your Python Automation

Add this to your `schedule_automation_enhanced.py`:

```python
# Add to imports
from simple_github_uploader import SimpleGitHubUploader

# Add to your generate_web_data method after saving JSON files:
def generate_web_data(self, projects):
    # ... existing code ...
    
    # Save combined view
    combined_json_path = self.public_path / 'schedule_data_combined.json'
    with open(combined_json_path, 'w') as f:
        json.dump(combined_data, f, indent=2)
    
    # Upload to GitHub Pages
    uploader = SimpleGitHubUploader()
    if uploader.upload_schedule_data(combined_json_path):
        logging.info("✅ Data uploaded to GitHub Pages successfully!")
    else:
        logging.warning("❌ Failed to upload to GitHub Pages")
    
    # ... rest of existing code ...
```

## 🌐 Alternative Solutions

### Netlify (Quick Setup)
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag your `schedule_data_combined.json` file
3. Get instant URL like: `https://amazing-name-123456.netlify.app/schedule_data_combined.json`
4. Update your Dashboard.html with the new URL

### JSONBin.io (API-based)
1. Sign up at [jsonbin.io](https://jsonbin.io)
2. Get your API key
3. Use the provided Python script to upload
4. Get URL like: `https://api.jsonbin.io/v3/b/YOUR_BIN_ID`

## 📊 Dashboard Integration

### Update Your Dashboard.html
Replace this line in your `loadData()` function:

```javascript
// OLD (unreliable):
const response = await fetch('https://corsproxy.io/?https://www.dropbox.com/scl/fi/osj8mpndudzz705pwjsxx/schedule_data_combined.json?rlkey=zx9s7kiyd2yhwqcsrjb3ozmv7&st=sysxua2t&raw=1');

// NEW (reliable):
const response = await fetch('https://YOUR_USERNAME.github.io/schedule-data/schedule_data_combined.json');
```

### Squarespace Integration
1. Upload your updated `Dashboard.html` to Squarespace
2. The dashboard will now load data from your reliable hosting
3. No more CORS issues or proxy failures

## 🔄 Automated Updates

### Option 1: GitHub Actions (Recommended)
Create `.github/workflows/update-data.yml`:

```yaml
name: Update Schedule Data
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install requests
      - name: Update data
        run: python update_schedule_data.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Option 2: Local Automation
Add to your existing Python automation:

```python
# After generating JSON data
if upload_to_github(json_path):
    print("✅ Data uploaded to GitHub Pages")
    print(f"📊 Dashboard updated: https://{username}.github.io/{repo}/")
```

## 🧪 Testing Your Setup

### Test JSON Access
```bash
curl https://YOUR_USERNAME.github.io/schedule-data/schedule_data_combined.json
```

### Test Dashboard
1. Open your Dashboard.html in a browser
2. Check browser console for errors
3. Verify data loads correctly

## 🛠️ Troubleshooting

### Common Issues

**"Repository not found"**
- Make sure repository is public
- Check repository name spelling
- Verify GitHub token has correct permissions

**"Upload failed"**
- Check GitHub token is valid
- Ensure repository exists
- Verify file paths are correct

**"CORS error"**
- GitHub Pages serves files with correct CORS headers
- If still getting CORS errors, check your fetch URL

**"Dashboard not loading"**
- Verify JSON URL is accessible
- Check browser console for errors
- Ensure JSON format is valid

## 📈 Performance Comparison

| Solution | Speed | Reliability | Setup Time | Cost |
|----------|-------|-------------|------------|------|
| CORS Proxy | Slow | Poor | 0 min | Free |
| GitHub Pages | Fast | Excellent | 10 min | Free |
| Netlify | Very Fast | Excellent | 5 min | Free |
| JSONBin.io | Fast | Good | 2 min | Free* |

*With request limits

## 🎯 Recommendation

**Use GitHub Pages** because:
1. ✅ Completely free and reliable
2. ✅ Integrates with your existing automation
3. ✅ No request limits
4. ✅ Version control for your data
5. ✅ Works perfectly with Squarespace
6. ✅ Can be fully automated

## 🚀 Next Steps

1. **Run the setup script**: `python setup_hosting.py`
2. **Test the upload**: Verify your JSON is accessible
3. **Update your automation**: Add GitHub upload to your Python script
4. **Deploy to Squarespace**: Upload the updated Dashboard.html
5. **Monitor**: Check that updates work automatically

Your dashboard will now be fast, reliable, and professional! 🎉 