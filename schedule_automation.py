import os
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(r'G:\My Drive\Project Dashboard\Schedule System\Automation\logs\automation.log'),
        logging.StreamHandler()
    ]
)

class MasterScheduleAutomation:
    def __init__(self):
        """Initialize the automation system"""
        self.base_path = r"G:\My Drive\Project Dashboard"
        self.temp_path = os.path.join(self.base_path, "Schedule System", "Temp")
        self.public_path = os.path.join(self.base_path, "Public", "Master Schedule")
        self.projects_path = os.path.join(self.base_path, "Projects", "Active")
        self.portals_path = os.path.join(self.base_path, "Customer Portals")
        
        # Initialize Google Drive service
        self.drive_service = self._init_google_drive()
        
        logging.info("Master Schedule Automation initialized")
    
    def _init_google_drive(self):
        """Initialize Google Drive API service"""
        try:
            creds_path = os.path.join(self.base_path, "Schedule System", "Automation", "config", "service-account-key.json")
            
            if not os.path.exists(creds_path):
                logging.error(f"Service account key not found at: {creds_path}")
                return None
            
            credentials = service_account.Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            service = build('drive', 'v3', credentials=credentials)
            logging.info("Google Drive service initialized successfully")
            return service
            
        except Exception as e:
            logging.error(f"Failed to initialize Google Drive: {e}")
            return None
    
    def check_trigger_file(self):
        """Check if Excel has triggered the automation"""
        trigger_file = os.path.join(self.temp_path, "trigger.txt")
        
        if os.path.exists(trigger_file):
            logging.info("Trigger file found - processing...")
            
            # Read trigger file
            with open(trigger_file, 'r') as f:
                lines = f.readlines()
            
            # Parse trigger data
            trigger_data = {}
            for line in lines:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    trigger_data[key] = value
            
            # Delete trigger file
            os.remove(trigger_file)
            
            return trigger_data
        
        return None
    
    def parse_pdf_schedule(self):
        """Parse the PDF schedule and extract project data"""
        # For now, we'll create sample data
        # In production, you'd use a PDF parsing library like PyPDF2 or pdfplumber
        
        logging.info("Parsing schedule data...")
        
        # Sample project data - replace with actual PDF parsing
        projects = [
            {
                "project_id": "346-354",
                "customer_name": "Smith",
                "customer_email": "smith@example.com",
                "address": "346 Stockton Street",
                "community": "Sunrise Estates",
                "lots": "81/82",
                "sqft": "1163",
                "current_phase": "Interior Finishing",
                "schedule": [
                    {"date": "2024-06-10", "task": "Final Inspection", "phase": "final"},
                    {"date": "2024-06-11", "task": "Detail Work", "phase": "finishing"},
                    {"date": "2024-06-16", "task": "Clean/Move In", "phase": "final"}
                ]
            }
        ]
        
        return projects
    
    def create_project_folders(self, project):
        """Create folder structure for a project"""
        project_folder = f"{project['project_id']} - {project['customer_name']} Residence"
        
        # Create internal project folders
        internal_path = os.path.join(self.projects_path, project_folder)
        folders = [
            "Internal",
            "Customer_Data/Schedule",
            "Customer_Data/Documents",
            "Customer_Data/Selections",
            "Customer_Data/Photos"
        ]
        
        for folder in folders:
            Path(os.path.join(internal_path, folder)).mkdir(parents=True, exist_ok=True)
        
        # Create customer portal folders
        portal_path = os.path.join(self.portals_path, project['customer_email'], f"{project['customer_name']} Residence")
        portal_folders = ["Schedule", "Documents", "Selections", "Photos"]
        
        for folder in portal_folders:
            Path(os.path.join(portal_path, folder)).mkdir(parents=True, exist_ok=True)
        
        logging.info(f"Created folders for project: {project_folder}")
        
        return internal_path, portal_path
    
    def save_project_schedule(self, project, internal_path, portal_path):
        """Save project schedule data"""
        # Save to internal project folder
        schedule_file = os.path.join(internal_path, "Customer_Data", "Schedule", "project_schedule.json")
        with open(schedule_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Create customer-friendly version
        customer_data = {
            "project_name": f"{project['customer_name']} Residence",
            "address": project['address'],
            "community": project['community'],
            "sqft": project['sqft'],
            "current_phase": project['current_phase'],
            "schedule": project['schedule'],
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save to customer portal
        customer_file = os.path.join(portal_path, "Schedule", "my_schedule.json")
        with open(customer_file, 'w') as f:
            json.dump(customer_data, f, indent=2)
        
        logging.info(f"Saved schedule for: {project['customer_name']}")
    
    def upload_to_drive(self, file_path):
        """Upload file to Google Drive"""
        if not self.drive_service:
            logging.error("Google Drive service not available")
            return None
        
        try:
            file_metadata = {'name': os.path.basename(file_path)}
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            logging.info(f"Uploaded to Drive: {file_path}")
            return file.get('id')
            
        except Exception as e:
            logging.error(f"Failed to upload to Drive: {e}")
            return None
    
    def send_notifications(self, trigger_data, projects):
        """Send email notifications"""
        # This is a placeholder - you'll need to set up email configuration
        
        if trigger_data.get('TRADE_EMAIL') == 'True':
            logging.info("Sending trade partner emails...")
            # Add email sending logic here
        
        if trigger_data.get('CUSTOMER_EMAIL') == 'True':
            logging.info("Sending customer emails...")
            # Add email sending logic here
    
    def run(self):
        """Main automation process"""
        logging.info("=" * 50)
        logging.info("Starting Master Schedule Automation")
        
        # Check for trigger
        trigger_data = self.check_trigger_file()
        if not trigger_data:
            logging.info("No trigger file found - waiting...")
            return
        
        # Process the schedule
        try:
            # Parse schedule data
            projects = self.parse_pdf_schedule()
            
            # Process each project
            for project in projects:
                internal_path, portal_path = self.create_project_folders(project)
                self.save_project_schedule(project, internal_path, portal_path)
            
            # Upload to Google Drive
            pdf_path = os.path.join(self.public_path, "Master Schedule.pdf")
            if os.path.exists(pdf_path):
                self.upload_to_drive(pdf_path)
            
            # Send notifications
            self.send_notifications(trigger_data, projects)
            
            logging.info("Automation completed successfully!")
            
        except Exception as e:
            logging.error(f"Automation failed: {e}")

def main():
    """Run the automation"""
    automation = MasterScheduleAutomation()
    
    # For testing - run once
    automation.run()
    
    # For production - monitor for triggers
    # while True:
    #     automation.run()
    #     time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()