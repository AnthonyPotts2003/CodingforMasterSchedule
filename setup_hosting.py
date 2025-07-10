#!/usr/bin/env python3
"""
Setup script for hosting schedule data
This script helps you set up GitHub Pages hosting for your JSON data
"""

import os
import json
import requests
from pathlib import Path
from simple_github_uploader import SimpleGitHubUploader

def setup_environment():
    """Setup environment variables for GitHub hosting"""
    print("🚀 Setting up GitHub Pages hosting for your schedule data...")
    print()
    
    # Get GitHub credentials
    token = input("Enter your GitHub Personal Access Token: ").strip()
    username = input("Enter your GitHub username: ").strip()
    repo_name = input("Enter repository name (default: schedule-data): ").strip() or "schedule-data"
    
    # Save to environment file
    env_content = f"""# GitHub Pages Configuration
GITHUB_TOKEN={token}
GITHUB_USERNAME={username}
GITHUB_REPO={repo_name}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"✅ Environment variables saved to .env file")
    print()
    
    return token, username, repo_name

def create_repository(username, repo_name):
    """Create GitHub repository if it doesn't exist"""
    print(f"📦 Creating GitHub repository: {username}/{repo_name}")
    
    # Check if repository exists
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print(f"✅ Repository {username}/{repo_name} already exists")
        return True
    elif response.status_code == 404:
        print(f"❌ Repository {username}/{repo_name} does not exist")
        print("Please create it manually on GitHub.com:")
        print(f"  1. Go to https://github.com/new")
        print(f"  2. Repository name: {repo_name}")
        print(f"  3. Make it Public (required for GitHub Pages)")
        print(f"  4. Click 'Create repository'")
        print()
        input("Press Enter after creating the repository...")
        return True
    else:
        print(f"❌ Error checking repository: {response.status_code}")
        return False

def enable_github_pages(username, repo_name):
    """Enable GitHub Pages for the repository"""
    print("🌐 Enabling GitHub Pages...")
    print(f"  1. Go to https://github.com/{username}/{repo_name}/settings/pages")
    print(f"  2. Under 'Source', select 'Deploy from a branch'")
    print(f"  3. Choose 'main' branch and '/ (root)' folder")
    print(f"  4. Click 'Save'")
    print()
    input("Press Enter after enabling GitHub Pages...")

def test_upload():
    """Test uploading data to GitHub"""
    print("🧪 Testing upload to GitHub...")
    
    # Check if JSON file exists
    json_path = Path("schedule_data_combined.json")
    if not json_path.exists():
        print("❌ schedule_data_combined.json not found")
        print("Please run your automation first to generate the JSON file")
        return False
    
    # Load environment variables
    if Path('.env').exists():
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Test upload
    uploader = SimpleGitHubUploader()
    if not uploader.enabled:
        print("❌ GitHub uploader is disabled. Check your credentials.")
        return False
    
    success = uploader.upload_schedule_data(json_path)
    
    if success:
        print("✅ Upload test successful!")
        username = os.getenv('GITHUB_USERNAME')
        repo = os.getenv('GITHUB_REPO')
        print(f"📊 Your data is now available at:")
        print(f"   https://{username}.github.io/{repo}/schedule_data_combined.json")
        return True
    else:
        print("❌ Upload test failed")
        return False

def update_dashboard_html():
    """Update the Dashboard.html file with the new URL"""
    print("📝 Updating Dashboard.html with new URL...")
    
    username = os.getenv('GITHUB_USERNAME')
    repo = os.getenv('GITHUB_REPO')
    
    if not username or not repo:
        print("❌ GitHub credentials not found")
        return False
    
    new_url = f"https://{username}.github.io/{repo}/schedule_data_combined.json"
    
    # Read current Dashboard.html
    dashboard_path = Path("Dashboard.html")
    if not dashboard_path.exists():
        print("❌ Dashboard.html not found")
        return False
    
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the old URL
    old_url = "https://corsproxy.io/?https://www.dropbox.com/scl/fi/osj8mpndudzz705pwjsxx/schedule_data_combined.json?rlkey=zx9s7kiyd2yhwqcsrjb3ozmv7&st=sysxua2t&raw=1"
    
    if old_url in content:
        content = content.replace(old_url, new_url)
        
        # Write back to file
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Dashboard.html updated with new URL: {new_url}")
        return True
    else:
        print("❌ Could not find the old URL in Dashboard.html")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🏗️  Schedule Data Hosting Setup")
    print("=" * 60)
    print()
    
    # Step 1: Setup environment
    token, username, repo_name = setup_environment()
    
    # Step 2: Create repository
    if not create_repository(username, repo_name):
        print("❌ Failed to setup repository")
        return
    
    # Step 3: Enable GitHub Pages
    enable_github_pages(username, repo_name)
    
    # Step 4: Test upload
    if test_upload():
        print()
        print("🎉 Setup completed successfully!")
        
        # Step 5: Update Dashboard.html
        if update_dashboard_html():
            print()
            print("📊 Your dashboard is now ready!")
            print(f"   Dashboard URL: https://{username}.github.io/{repo_name}/")
            print()
            print("Next steps:")
            print("1. Upload your Dashboard.html to your Squarespace site")
            print("2. Test the dashboard to make sure it loads correctly")
            print("3. Set up automatic updates in your Python automation")
        else:
            print("⚠️  Setup completed but Dashboard.html update failed")
    else:
        print("❌ Setup failed during upload test")

if __name__ == "__main__":
    main() 