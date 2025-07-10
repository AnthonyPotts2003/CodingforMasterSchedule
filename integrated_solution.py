# Integrated Solution: Auto-upload to GitHub Pages
# Add this to your existing schedule_automation_enhanced.py

import requests
import base64
import json
import os
import logging
import shutil
from datetime import datetime
from pathlib import Path

class GitHubUploader:
    def __init__(self, token, repo, username):
        self.token = token
        self.repo = repo
        self.username = username
        self.base_url = f"https://api.github.com/repos/{username}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def upload_file(self, file_path, target_path):
        """Upload or update a file in the GitHub repository"""
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Encode content
            content_encoded = base64.b64encode(content.encode()).decode()
            
            # Check if file exists to get SHA
            url = f"{self.base_url}/contents/{target_path}"
            response = requests.get(url, headers=self.headers)
            
            data = {
                "message": f"Update {target_path} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "content": content_encoded,
                "branch": "main"
            }
            
            if response.status_code == 200:
                # File exists, include SHA for update
                data["sha"] = response.json()['sha']
                method = "PUT"
            else:
                # File doesn't exist, create new
                method = "PUT"
            
            # Upload/update file
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded {target_path} to GitHub")
                return True
            else:
                print(f"❌ Failed to upload {target_path}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading {target_path}: {e}")
            return False

# Modify your existing EnhancedScheduleAutomation class
class EnhancedScheduleAutomation:
    def __init__(self):
        # ... existing initialization code ...
        
        # Add GitHub uploader
        self.github_uploader = None
        self.setup_github_uploader()
    
    def setup_github_uploader(self):
        """Setup GitHub uploader if credentials are available"""
        try:
            # You can store these in environment variables or a config file
            github_token = os.getenv('GITHUB_TOKEN')  # Set this in your environment
            github_username = os.getenv('GITHUB_USERNAME')  # Set this in your environment
            github_repo = os.getenv('GITHUB_REPO', 'schedule-data')  # Default repo name
            
            if github_token and github_username:
                self.github_uploader = GitHubUploader(github_token, github_repo, github_username)
                logging.info("GitHub uploader initialized")
            else:
                logging.warning("GitHub credentials not found. Skipping GitHub upload.")
        except Exception as e:
            logging.error(f"Failed to setup GitHub uploader: {e}")
    
    def generate_web_data(self, projects):
        """Generate data for web display - both individual and combined views"""
        # ... existing code ...
        
        # Save individual view
        json_path = self.public_path / 'schedule_data.json'
        with open(json_path, 'w') as f:
            json.dump(web_data, f, indent=2)
        logging.info(f"Individual schedule data saved to {json_path}")
        
        # Save combined view
        combined_json_path = self.public_path / 'schedule_data_combined.json'
        with open(combined_json_path, 'w') as f:
            json.dump(combined_data, f, indent=2)
        logging.info(f"Combined schedule data saved to {combined_json_path}")
        
        # Upload to GitHub if configured
        if self.github_uploader:
            try:
                self.github_uploader.upload_file(combined_json_path, 'schedule_data_combined.json')
                self.github_uploader.upload_file(json_path, 'schedule_data.json')
                logging.info("Successfully uploaded to GitHub Pages")
            except Exception as e:
                logging.error(f"Failed to upload to GitHub: {e}")
        
        # ... rest of existing code (copy to G drive, Dropbox, etc.) ...

# Alternative: Simple Netlify Uploader
class NetlifyUploader:
    def __init__(self, site_id, access_token):
        self.site_id = site_id
        self.access_token = access_token
        self.api_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"
    
    def upload_file(self, file_path, target_path):
        """Upload file to Netlify via API"""
        try:
            # This would require using Netlify's API to upload files
            # For simplicity, you might want to use the CLI instead
            import subprocess
            
            # Copy file to a local Netlify site folder
            netlify_folder = Path("netlify-site")
            netlify_folder.mkdir(exist_ok=True)
            
            target_file = netlify_folder / target_path
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, target_file)
            
            # Deploy using Netlify CLI
            result = subprocess.run(
                ["netlify", "deploy", "--prod", "--dir", str(netlify_folder)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully deployed to Netlify")
                return True
            else:
                print(f"❌ Netlify deployment failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading to Netlify: {e}")
            return False

# Usage example:
if __name__ == "__main__":
    # Set up environment variables
    os.environ['GITHUB_TOKEN'] = 'your_github_token_here'
    os.environ['GITHUB_USERNAME'] = 'your_github_username'
    os.environ['GITHUB_REPO'] = 'schedule-data'
    
    # Run your automation
    automation = EnhancedScheduleAutomation()
    projects = automation.parse_schedule_data()
    if projects:
        automation.generate_web_data(projects)
        print("✅ Data generated and uploaded successfully!")
    else:
        print("❌ No projects found to process") 