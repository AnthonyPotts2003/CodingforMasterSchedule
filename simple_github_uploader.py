# Simple GitHub Uploader for Schedule Data
# This can be integrated into your existing schedule_automation_enhanced.py

import requests
import base64
import json
import os
import logging
from datetime import datetime
from pathlib import Path

class SimpleGitHubUploader:
    """Simple class to upload JSON files to GitHub Pages"""
    
    def __init__(self, token=None, username=None, repo=None):
        """
        Initialize the uploader
        
        Args:
            token: GitHub personal access token
            username: GitHub username
            repo: Repository name (without username)
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.username = username or os.getenv('GITHUB_USERNAME')
        self.repo = repo or os.getenv('GITHUB_REPO', 'schedule-data')
        
        if not all([self.token, self.username]):
            logging.warning("GitHub credentials not provided. Uploader disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.base_url = f"https://api.github.com/repos/{self.username}/{self.repo}"
            self.headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
    
    def upload_file(self, local_file_path, remote_file_path):
        """
        Upload or update a file in the GitHub repository
        
        Args:
            local_file_path: Path to the local file
            remote_file_path: Path in the repository (e.g., 'data/schedule.json')
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled:
            logging.warning("GitHub uploader is disabled")
            return False
        
        try:
            # Check if file exists
            file_path = Path(local_file_path)
            if not file_path.exists():
                logging.error(f"Local file not found: {local_file_path}")
                return False
            
            # Read and encode file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            content_encoded = base64.b64encode(content.encode()).decode()
            
            # Check if file exists in repository
            url = f"{self.base_url}/contents/{remote_file_path}"
            response = requests.get(url, headers=self.headers)
            
            data = {
                "message": f"Update {remote_file_path} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "content": content_encoded,
                "branch": "main"
            }
            
            if response.status_code == 200:
                # File exists, include SHA for update
                data["sha"] = response.json()['sha']
                logging.info(f"Updating existing file: {remote_file_path}")
            else:
                logging.info(f"Creating new file: {remote_file_path}")
            
            # Upload/update file
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                logging.info(f"✅ Successfully uploaded {remote_file_path} to GitHub")
                return True
            else:
                logging.error(f"❌ Failed to upload {remote_file_path}: {response.status_code}")
                if response.text:
                    logging.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error uploading {remote_file_path}: {e}")
            return False
    
    def upload_schedule_data(self, json_file_path):
        """
        Upload schedule data files to GitHub
        
        Args:
            json_file_path: Path to the schedule_data_combined.json file
        """
        if not self.enabled:
            return False
        
        success = True
        
        # Upload the combined data file
        if self.upload_file(json_file_path, 'schedule_data_combined.json'):
            logging.info("✅ Combined schedule data uploaded successfully")
        else:
            success = False
        
        # Also upload individual data if it exists
        individual_path = json_file_path.parent / 'schedule_data.json'
        if individual_path.exists():
            if self.upload_file(individual_path, 'schedule_data.json'):
                logging.info("✅ Individual schedule data uploaded successfully")
            else:
                success = False
        
        return success

# Example usage and integration
def setup_github_uploader():
    """Setup GitHub uploader with environment variables"""
    return SimpleGitHubUploader()

def upload_to_github(json_file_path):
    """Simple function to upload schedule data to GitHub"""
    uploader = setup_github_uploader()
    return uploader.upload_schedule_data(json_file_path)

# Integration example for your existing automation
def integrate_with_automation():
    """
    Add this to your schedule_automation_enhanced.py generate_web_data method:
    
    # After saving the JSON files locally, add:
    if upload_to_github(combined_json_path):
        print("✅ Data uploaded to GitHub Pages successfully!")
        print(f"📊 Dashboard URL: https://{os.getenv('GITHUB_USERNAME')}.github.io/{os.getenv('GITHUB_REPO', 'schedule-data')}/")
    else:
        print("❌ Failed to upload to GitHub Pages")
    """
    pass

# Test the uploader
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Test upload
    json_path = Path("schedule_data_combined.json")
    if json_path.exists():
        success = upload_to_github(json_path)
        if success:
            print("🎉 Upload successful! Your data is now available on GitHub Pages.")
            username = os.getenv('GITHUB_USERNAME', 'your-username')
            repo = os.getenv('GITHUB_REPO', 'schedule-data')
            print(f"📊 Dashboard URL: https://{username}.github.io/{repo}/")
        else:
            print("❌ Upload failed. Check your GitHub credentials and repository setup.")
    else:
        print("❌ schedule_data_combined.json not found in current directory") 