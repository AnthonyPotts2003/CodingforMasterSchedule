# JSONBin.io Setup for JSON Hosting

## Step 1: Create Account
1. Go to [jsonbin.io](https://jsonbin.io) and sign up
2. Get your API key from the dashboard

## Step 2: Upload Your JSON
Using the JSONBin API:

```python
# upload_to_jsonbin.py
import requests
import json
from pathlib import Path

def upload_to_jsonbin():
    # Your JSONBin API key
    api_key = "YOUR_JSONBIN_API_KEY"
    
    # Read your JSON file
    json_path = Path("schedule_data_combined.json")
    
    if not json_path.exists():
        print("JSON file not found")
        return
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Upload to JSONBin
    url = "https://api.jsonbin.io/v3/b"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        bin_id = response.json()['metadata']['id']
        print(f"Successfully uploaded! Bin ID: {bin_id}")
        print(f"URL: https://api.jsonbin.io/v3/b/{bin_id}")
        return bin_id
    else:
        print(f"Failed to upload: {response.status_code}")
        return None

if __name__ == "__main__":
    upload_to_jsonbin()
```

## Step 3: Update Your HTML
Replace the fetch URL in your Dashboard.html:

```javascript
// Replace this line in loadData() function:
const response = await fetch('https://corsproxy.io/?https://www.dropbox.com/scl/fi/osj8mpndudzz705pwjsxx/schedule_data_combined.json?rlkey=zx9s7kiyd2yhwqcsrjb3ozmv7&st=sysxua2t&raw=1');

// With this:
const response = await fetch('https://api.jsonbin.io/v3/b/YOUR_BIN_ID');
```

## Step 4: Update Existing Bin
To update an existing bin instead of creating new ones:

```python
# update_jsonbin.py
import requests
import json
from pathlib import Path

def update_jsonbin(bin_id):
    api_key = "YOUR_JSONBIN_API_KEY"
    
    json_path = Path("schedule_data_combined.json")
    
    if not json_path.exists():
        print("JSON file not found")
        return
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    url = f"https://api.jsonbin.io/v3/b/{bin_id}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Successfully updated JSONBin")
    else:
        print(f"Failed to update: {response.status_code}")

if __name__ == "__main__":
    update_jsonbin("YOUR_BIN_ID")
```

## Benefits:
- ✅ Purpose-built for JSON hosting
- ✅ Simple API
- ✅ Version history
- ✅ No CORS issues
- ✅ Works with Squarespace
- ✅ Free tier available

## Limitations:
- ❌ Free tier has limits (10,000 requests/month)
- ❌ Requires API key management 