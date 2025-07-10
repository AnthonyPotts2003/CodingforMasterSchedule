# GitHub Pages Setup for JSON Hosting

## Step 1: Create a GitHub Repository
1. Go to GitHub.com and create a new repository
2. Name it something like `schedule-data` or `construction-dashboard-data`
3. Make it public (required for GitHub Pages)

## Step 2: Upload Your JSON Files
1. In your new repository, click "Add file" → "Upload files"
2. Upload your `schedule_data_combined.json` file
3. Commit the file

## Step 3: Enable GitHub Pages
1. Go to repository Settings → Pages
2. Under "Source", select "Deploy from a branch"
3. Choose "main" branch and "/ (root)" folder
4. Click "Save"

## Step 4: Update Your HTML
Replace the fetch URL in your Dashboard.html:

```javascript
// Replace this line in loadData() function:
const response = await fetch('https://corsproxy.io/?https://www.dropbox.com/scl/fi/osj8mpndudzz705pwjsxx/schedule_data_combined.json?rlkey=zx9s7kiyd2yhwqcsrjb3ozmv7&st=sysxua2t&raw=1');

// With this:
const response = await fetch('https://YOUR_USERNAME.github.io/schedule-data/schedule_data_combined.json');
```

## Step 5: Automated Updates
Create a script to automatically update the GitHub repository when your data changes:

```python
# update_github_data.py
import requests
import json
import os
from pathlib import Path

def update_github_data():
    # Read your local JSON file
    json_path = Path("schedule_data_combined.json")
    
    if not json_path.exists():
        print("JSON file not found")
        return
    
    # GitHub API setup
    token = "YOUR_GITHUB_TOKEN"  # Create a personal access token
    repo = "YOUR_USERNAME/schedule-data"
    
    # Read file content
    with open(json_path, 'r') as f:
        content = f.read()
    
    # Update file via GitHub API
    url = f"https://api.github.com/repos/{repo}/contents/schedule_data_combined.json"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Get current file to get SHA
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()['sha']
    else:
        sha = None
    
    data = {
        "message": f"Update schedule data - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": content.encode('base64').decode(),
        "branch": "main"
    }
    
    if sha:
        data["sha"] = sha
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code in [200, 201]:
        print("Successfully updated GitHub repository")
    else:
        print(f"Failed to update: {response.status_code}")

if __name__ == "__main__":
    update_github_data()
```

## Benefits:
- ✅ Free hosting
- ✅ No CORS issues
- ✅ Reliable and fast
- ✅ Version control
- ✅ Can be automated
- ✅ Works with Squarespace

## Alternative URLs:
Your JSON will be available at:
- `https://YOUR_USERNAME.github.io/schedule-data/schedule_data_combined.json`
- `https://YOUR_USERNAME.github.io/schedule-data/schedule_data.json` 