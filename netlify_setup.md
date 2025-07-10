# Netlify Setup for JSON Hosting

## Step 1: Create a Simple Site Structure
Create a folder structure like this:
```
schedule-data-site/
├── index.html (optional)
└── data/
    ├── schedule_data_combined.json
    └── schedule_data.json
```

## Step 2: Deploy to Netlify
1. Go to [netlify.com](https://netlify.com) and sign up
2. Click "New site from Git" or drag your folder to deploy
3. If using Git: Connect your GitHub/GitLab repository
4. If dragging: Just drag your folder to the deploy area

## Step 3: Update Your HTML
Replace the fetch URL in your Dashboard.html:

```javascript
// Replace this line in loadData() function:
const response = await fetch('https://corsproxy.io/?https://www.dropbox.com/scl/fi/osj8mpndudzz705pwjsxx/schedule_data_combined.json?rlkey=zx9s7kiyd2yhwqcsrjb3ozmv7&st=sysxua2t&raw=1');

// With this:
const response = await fetch('https://YOUR_SITE_NAME.netlify.app/data/schedule_data_combined.json');
```

## Step 4: Automated Updates with Netlify CLI
Install Netlify CLI and set up automatic deployments:

```bash
npm install -g netlify-cli
netlify login
netlify init
```

Then create a script to update your data:

```python
# update_netlify_data.py
import shutil
import os
from pathlib import Path

def update_netlify_data():
    # Copy your JSON files to the Netlify site folder
    source_path = Path("schedule_data_combined.json")
    target_path = Path("schedule-data-site/data/schedule_data_combined.json")
    
    if source_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        print("Copied data to Netlify site folder")
        
        # If you have Netlify CLI installed, you can auto-deploy:
        # os.system("cd schedule-data-site && netlify deploy --prod")
    else:
        print("Source JSON file not found")

if __name__ == "__main__":
    update_netlify_data()
```

## Benefits:
- ✅ Free hosting
- ✅ No CORS issues
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Easy deployment
- ✅ Works with Squarespace

## Alternative: Netlify Drop
For quick testing, you can use Netlify Drop:
1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag your JSON file directly
3. Get an instant URL like: `https://amazing-name-123456.netlify.app/schedule_data_combined.json` 