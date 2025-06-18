#!/usr/bin/env python3
"""
Enhanced Master Schedule Automation System
Includes PDF parsing, email notifications, and complete integration
"""

import os
import json
import time
import shutil
from datetime import datetime
from pathlib import Path
import pandas as pd
import openpyxl
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pdfplumber
import re
from datetime import timedelta

# Test mode - set to True for local testing without Google Drive
TEST_MODE = True

# Configuration
from dotenv import load_dotenv
load_dotenv()

CONFIG = {
    'BASE_PATH': r"G:\My Drive\Project Dashboard",
    'GMAIL_USER': os.getenv('GMAIL_USER'),
    'GMAIL_APP_PASSWORD': os.getenv('GMAIL_APP_PASSWORD'),
    'DRIVE_FOLDER_ID': os.getenv('DRIVE_FOLDER_ID')
}

# Set up logging
log_dir = os.path.join(CONFIG['BASE_PATH'], "Schedule System", "Automation", "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'automation_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)

class EnhancedScheduleAutomation:
    def __init__(self):
        """Initialize the enhanced automation system"""
        self.base_path = Path(CONFIG['BASE_PATH'])
        self.temp_path = self.base_path / "Schedule System" / "Temp"
        self.public_path = self.base_path / "Public" / "Master Schedule"
        self.projects_path = self.base_path / "Projects" / "Active"
        self.portals_path = self.base_path / "Customer Portals"
        self.master_files_path = self.base_path / "Schedule System" / "Master Files"
        
        # Initialize Google Drive service
        self.drive_service = self._init_google_drive()
        
        # Load customer data
        self.customer_data = self._load_customer_data()
        self.partner_data = self._load_partner_data()
        
        logging.info("Enhanced Master Schedule Automation initialized")
        
        # Define lot pairings
        self.lot_pairs = {
            # Sunrise Estates
            'Sunrise Estates': {
                'pairs': [
                    (81, 82),  # 346/354 Stockton
                    (73, 74),  # 282/290 Stockton
                    (65, 66),  # 224/230 Stockton
                    (15, 46),  # 276/268 Merrick
                    (16, 17),  # 284/292 Merrick
                ],
                'singles': [
                    # Add any single lots here
                ]
            },
            'Canal Landing': {
                'pairs': [
                    # West side lots
                    (1, 2),    # 1160/1156 N Yost St
                    (3, 4),    # 1152/1148 N Yost St

                    
                    # W Quinault Ave
                    (5, 6),    # 4792/4780 W Quinault Pl
                    (7, 8),    # 4774/4768 W Quinault Pl
                    (9, 10),   # 4762/4756 W Quinault Pl
                    (11, 12),  # 4750/4744 W Quinault Pl
                    (13, 14),  # 4738/4732 W Quinault Pl
                    (15, 16),  # 4726/1130 W Quinault/N Williams Pl
                    (21, 22),  # 1133/1129 W Quinault Pl/N Yost Pl
                    (25, 26),  # 4823/4817 W Quinault Pl
                    (27, 28),  # 4811/4805 W Quinault Pl
                    (29, 30),  # 4799/4793 W Quinault Pl           
                    (31, 32),  # 4787/4781 W Quinault Pl
                    (33, 34),  # 4775/4769 W Quinault Pl
                    (35, 36),  # 4763/4757 W Quinault Pl
                    (37, 38),  # 4751/4745 W Quinault Pl
                    (39, 40),  # 4739/4733 W Quinault Pl

                    # W Payette Pl
                    (41, 42),  # 4724/4730 W Quinault Pl
                    (43, 44),  # 4736/4742 W Quinault Pl
                    (45, 46),  # 4748/4754 W Quinault Pl
                    (47, 48),  # 4760/4766 W Quinault Pl
                    (49, 50),  # 4772/4778 W Quinault Pl
                    (51, 52),  # 4784/4790 W Quinault Pl
                    (53, 54),  # 4796/4802 W Quinault Pl
                    (55, 56),  # 4808/4814 W Quinault Pl
                    (57, 58),  # 4820/4838 W Quinault Pl

                    # N Williams Pl
                    (17, 18),  # 1126/1122 N Williams Pl
                    (93, 94),  # 1110/1114 N Williams Pl
                    (91, 92),  # 1102/1106 N Williams Pl

                    # N Yost Pl
                    (23, 24),  # 1125/1121 N Yost Pl
                    (59, 60),  # 1117/1113 N Yost Pl
                    (61, 62),  # 1109/1107 N Yost Pl             
                    
                    # W Payette Pl
                    (66, 67),  # 4845/4839 W Payette Pl
                    (68, 69),  # 4833/4827 W Payette Pl
                    (70, 71),  # 4821/4815 W Payette Pl
                    (72, 73),  # 4809/4803 W Payette Pl
                    (74, 75),  # 4797/4791 W Payette Pl
                    (76, 77),  # 4785/4779 W Payette Pl
                    (78, 79),  # 4773/4767 W Payette Pl
                    (80, 81),  # 4761/4755 W Payette Pl
                    (82, 83),  # 4749/4743 W Payette Pl
                    (84, 85),  # 4737/4731 W Payette Pl
                    (86, 87),  # 4725/4719 W Payette Pl
                    (88, 89),  # 4713/4707 W Payette Pl                 
                ],
                'singles': [
                    19,  # 4816 N Yost ST             
                    20,  # 4822 W Quinault Pl
                    95,  # 1118 N Williams Pl
                    63,  # 1101 N Yost Pl
                    64,  # 4857 W Payette Pl                    
                    65,  # 4851 W Payette Pl
                    90,  # 4701 W Payette Pl
                    ]
            }
        }

    def _load_customer_data(self):
        """Load customer data from Excel"""
        try:
            excel_path = self.master_files_path / "Master Schedule.xlsm"
            if excel_path.exists():
                # Try to read the Customers sheet
                try:
                    df = pd.read_excel(excel_path, sheet_name='Customers', engine='openpyxl')
                    return df.set_index('Address').to_dict('index')
                except:
                    logging.warning("Customers sheet not found in Excel")
                    return {}
            else:
                logging.warning("Master Schedule Excel file not found")
                return {}
        except Exception as e:
            logging.error(f"Error loading customer data: {e}")
            return {}
    
    def _load_partner_data(self):
        """Load partner data from Excel"""
        try:
            excel_path = self.master_files_path / "Master Schedule.xlsm"
            if excel_path.exists():
                # Try to read the Contacts sheet
                try:
                    df = pd.read_excel(excel_path, sheet_name='Contacts', engine='openpyxl')
                    return df.to_dict('records')
                except:
                    logging.warning("Contacts sheet not found in Excel")
                    return []
            else:
                logging.warning("Master Schedule Excel file not found")
                return []
        except Exception as e:
            logging.error(f"Error loading partner data: {e}")
            return []
    def _init_google_drive(self):
        """Initialize Google Drive API service"""
        if TEST_MODE:
            logging.info("Running in TEST MODE - Google Drive disabled")
            return None
                
        try:
            creds_path = self.base_path / "Schedule System" / "Automation" / "config" / "service-account-key.json"
                
            if not creds_path.exists():
                logging.warning(f"Service account key not found at: {creds_path}")
                return None
                
            credentials = service_account.Credentials.from_service_account_file(
                str(creds_path),
                scopes=['https://www.googleapis.com/auth/drive']
            )
                
            service = build('drive', 'v3', credentials=credentials)
            logging.info("Google Drive service initialized successfully")
            return service
                
        except Exception as e:
            logging.error(f"Failed to initialize Google Drive: {e}")
            return None
    
    def parse_schedule_data(self):
        """Parse the schedule data from JSON export"""
        json_path = self.temp_path / "schedule_data.json"
        
        if not json_path.exists():
            logging.warning(f"JSON data not found at: {json_path}")
            return []
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # VBA exports with 'projects' array
            projects = data.get('projects', [])
            enhanced_projects = []
            
            for project in projects:
                # Check if project has lots info
                lots = project.get('lots', '')
                
                # If lots contains a slash, it's a duplex - but VBA already split them
                # So we just process each unit as-is
                
                # Determine current phase from schedule
                if project.get('schedule'):
                    today = datetime.now().date()
                    current_phase = 'Planning'
                    for task in project['schedule']:
                        try:
                            task_date = datetime.strptime(task['date'], '%Y-%m-%d').date()
                            if task_date <= today:
                                current_phase = task.get('phase', 'other')
                        except:
                            pass
                    project['current_phase'] = current_phase
                else:
                    project['current_phase'] = 'Planning'
                
                # Look up customer info
                customer_info = self.customer_data.get(project.get('address', ''), {})
                project['customer_name'] = customer_info.get('Customer Name', 'Unknown')
                project['customer_email'] = customer_info.get('Email Address', '')
                
                enhanced_projects.append(project)
                logging.info(f"Parsed project: {project.get('address', 'Unknown')}")
            
            logging.info(f"Successfully parsed {len(enhanced_projects)} projects from JSON data")
            return enhanced_projects
            
        except Exception as e:
            logging.error(f"Error loading JSON data: {e}")
            return []
    
    def _determine_current_phase(self, text):
        """Determine current phase from schedule text"""
        phases = ["Foundation", "Framing", "Roofing", "Electrical", "Plumbing", 
                 "Insulation", "Drywall", "Flooring", "Painting", "Finishing", "Final"]
        
        # Simple logic - find the last mentioned phase
        current_phase = "Planning"
        for phase in phases:
            if phase.lower() in text.lower():
                current_phase = phase
        
        return current_phase
    
    def _categorize_task(self, task):
        """Categorize task into construction phase"""
        task_lower = task.lower()
        
        phase_keywords = {
            'foundation': ['foundation', 'concrete', 'slab', 'footing'],
            'framing': ['frame', 'framing', 'lumber', 'walls', 'roof deck'],
            'roofing': ['roof', 'shingle', 'roofing', 'gutters'],
            'electrical': ['electrical', 'wire', 'electric', 'panel'],
            'plumbing': ['plumb', 'pipe', 'water', 'sewer'],
            'insulation': ['insulation', 'insulate', 'vapor'],
            'drywall': ['drywall', 'sheetrock', 'mud', 'tape'],
            'flooring': ['floor', 'tile', 'carpet', 'hardwood'],
            'painting': ['paint', 'primer', 'stain'],
            'finishing': ['finish', 'trim', 'cabinet', 'countertop'],
            'final': ['final', 'inspection', 'walk', 'clean']
        }
        
        for phase, keywords in phase_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                return phase
        
        return 'other'
    
    def _get_sample_projects(self):
        """Return sample projects for testing"""
        return [
            {
                "project_id": "346",
                "customer_name": "Smith",
                "customer_email": "smith@example.com",
                "address": "346 Stockton Street",
                "community": "Sunrise Estates",
                "lots": "81",
                "sqft": "1163",
                "current_phase": "Interior Finishing",
                "schedule": [
                    {"date": "2024-06-10", "task": "Final Inspection", "phase": "final"},
                    {"date": "2024-06-11", "task": "Detail Work", "phase": "finishing"},
                    {"date": "2024-06-16", "task": "Clean/Move In", "phase": "final"}
                ]
            },
            {
                "project_id": "354",
                "customer_name": "Johnson",
                "customer_email": "johnson@example.com",
                "address": "354 Stockton Street",
                "community": "Sunrise Estates",
                "lots": "82",
                "sqft": "1163",
                "current_phase": "Framing",
                "schedule": [
                    {"date": "2024-06-12", "task": "Wall Framing", "phase": "framing"},
                    {"date": "2024-06-15", "task": "Roof Framing", "phase": "framing"},
                    {"date": "2024-06-20", "task": "Electrical Rough", "phase": "electrical"}
                ]
            }
        ]
    
    def create_project_folders(self, project):
        """Create folder structure for a project"""
        project_folder = f"{project['project_id']} - {project['customer_name']}"
        
        # Create internal project folders
        internal_path = self.projects_path / project_folder
        folders = [
            "Internal",
            "Customer_Data/Schedule",
            "Customer_Data/Documents",
            "Customer_Data/Selections",
            "Customer_Data/Photos"
        ]
        
        for folder in folders:
            (internal_path / folder).mkdir(parents=True, exist_ok=True)
        
        # Create customer portal folders
        if project['customer_email']:
            portal_path = self.portals_path / project['customer_email'] / project_folder
            portal_folders = ["Schedule", "Documents", "Selections", "Photos"]
            
            for folder in portal_folders:
                (portal_path / folder).mkdir(parents=True, exist_ok=True)
        else:
            portal_path = None
        
        logging.info(f"Created folders for project: {project_folder}")
        
        return internal_path, portal_path
    
    def save_project_schedule(self, project, internal_path, portal_path):
        """Save project schedule data and generate HTML views"""
        # Save to internal project folder
        schedule_file = internal_path / "Customer_Data" / "Schedule" / "project_schedule.json"
        with open(schedule_file, 'w') as f:
            json.dump(project, f, indent=2)
        
        # Generate HTML view
        html_content = self._generate_schedule_html(project)
        html_file = internal_path / "Customer_Data" / "Schedule" / "schedule_view.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Save to customer portal if email exists
        if portal_path:
            # Create customer-friendly version
            customer_data = {
                "project_name": f"{project['customer_name']} Residence",
                "address": project['address'],
                "community": project['community'],
                "sqft": project['sqft'],
                "current_phase": project['current_phase'],
                "schedule": project['schedule'],
                "completion_percentage": self._calculate_completion(project['schedule']),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Save to customer portal
            customer_file = portal_path / "Schedule" / "my_schedule.json"
            with open(customer_file, 'w') as f:
                json.dump(customer_data, f, indent=2)
            
            # Copy HTML to portal
            portal_html = portal_path / "Schedule" / "schedule_view.html"
            shutil.copy2(html_file, portal_html)
        
        logging.info(f"Saved schedule for: {project['customer_name']}")
    
    def _calculate_completion(self, schedule):
        """Calculate project completion percentage"""
        if not schedule:
            return 0
        
        today = datetime.now().date()
        completed = 0
        
        for item in schedule:
            try:
                task_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
                if task_date <= today:
                    completed += 1
            except:
                pass
        
        return round((completed / len(schedule)) * 100, 1)
    
    def _generate_schedule_html(self, project):
        """Generate HTML view for project schedule"""
        completion = self._calculate_completion(project['schedule'])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Schedule - {project['address']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 0;
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .info-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .info-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }}
        .label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .value {{
            font-size: 1.8em;
            font-weight: 600;
            color: #2c3e50;
        }}
        .progress-container {{
            margin-top: 15px;
        }}
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
            width: {completion}%;
            transition: width 0.5s ease;
        }}
        .schedule-section {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .schedule-section h2 {{
            margin-top: 0;
            color: #2c3e50;
            font-size: 1.8em;
        }}
        .schedule-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .schedule-table th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #555;
            border-bottom: 2px solid #e0e0e0;
        }}
        .schedule-table td {{
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .schedule-table tr:hover {{
            background: #f8f9fa;
        }}
        .phase-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 500;
        }}
        .phase-foundation {{ background: #e3f2fd; color: #1565c0; }}
        .phase-framing {{ background: #fff3e0; color: #e65100; }}
        .phase-roofing {{ background: #f3e5f5; color: #6a1b9a; }}
        .phase-electrical {{ background: #fff8e1; color: #f57f17; }}
        .phase-plumbing {{ background: #e8f5e9; color: #2e7d32; }}
        .phase-insulation {{ background: #fce4ec; color: #c2185b; }}
        .phase-drywall {{ background: #e0f2f1; color: #00695c; }}
        .phase-flooring {{ background: #efebe9; color: #4e342e; }}
        .phase-painting {{ background: #ede7f6; color: #512da8; }}
        .phase-finishing {{ background: #e8eaf6; color: #303f9f; }}
        .phase-final {{ background: #e1f5fe; color: #0277bd; }}
        .phase-other {{ background: #f5f5f5; color: #666; }}
        .status-completed {{
            color: #27ae60;
            font-weight: 500;
        }}
        .status-upcoming {{
            color: #3498db;
            font-weight: 500;
        }}
        .status-today {{
            color: #e67e22;
            font-weight: 600;
        }}
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .schedule-table {{
                font-size: 0.9em;
            }}
            .schedule-table th,
            .schedule-table td {{
                padding: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{project['address']}</h1>
            <p>{project['community']} • {project['customer_name']} Residence</p>
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="label">Square Footage</div>
                <div class="value">{project['sqft']} sq ft</div>
            </div>
            <div class="info-card">
                <div class="label">Current Phase</div>
                <div class="value">{project['current_phase']}</div>
            </div>
            <div class="info-card">
                <div class="label">Overall Progress</div>
                <div class="value">{completion}%</div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="schedule-section">
            <h2>Construction Schedule</h2>
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Task</th>
                        <th>Phase</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        today = datetime.now().date()
        
        for item in project['schedule']:
            task_date = datetime.strptime(item['date'], '%Y-%m-%d').date()
            
            # Determine status
            if task_date < today:
                status = '<span class="status-completed">✓ Completed</span>'
            elif task_date == today:
                status = '<span class="status-today">● In Progress</span>'
            else:
                status = '<span class="status-upcoming">◌ Upcoming</span>'
            
            # Format date
            formatted_date = task_date.strftime('%B %d, %Y')
            
            html += f"""
                    <tr>
                        <td>{formatted_date}</td>
                        <td>{item['task']}</td>
                        <td><span class="phase-badge phase-{item['phase']}">{item['phase'].title()}</span></td>
                        <td>{status}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def send_notifications(self, trigger_data, projects):
        """Send email notifications"""
        if trigger_data.get('TRADE_EMAIL') == 'True':
            self._send_trade_partner_emails(projects)
        
        if trigger_data.get('CUSTOMER_EMAIL') == 'True':
            self._send_customer_emails(projects)
    
    def _send_trade_partner_emails(self, projects):
        """Send email to trade partners"""
        if not self.partner_data:
            logging.warning("No partner email data available")
            return
        
        subject = f"Weekly Schedule Update - {datetime.now().strftime('%B %d, %Y')}"
        
        # Group projects by current phase
        phase_groups = {}
        for project in projects:
            phase = project['current_phase']
            if phase not in phase_groups:
                phase_groups[phase] = []
            phase_groups[phase].append(project)
        
        # Build email body
        body = """
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; color: #333; }
        h2 { color: #2c3e50; }
        .phase-section { margin: 20px 0; }
        .project-item { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>Weekly Construction Schedule Update</h2>
    <p>Dear Trade Partners,</p>
    <p>Please find below this week's schedule update:</p>
"""
        
        for phase, phase_projects in sorted(phase_groups.items()):
            body += f"""
    <div class="phase-section">
        <h3>{phase} Phase</h3>
"""
            for project in phase_projects:
                upcoming_tasks = [task for task in project['schedule'] 
                                if datetime.strptime(task['date'], '%Y-%m-%d').date() >= datetime.now().date()][:3]
                
                body += f"""
        <div class="project-item">
            <strong>{project['address']} - {project['community']}</strong><br>
            Upcoming work:
            <ul>
"""
                for task in upcoming_tasks:
                    body += f"<li>{task['date']}: {task['task']}</li>"
                
                body += """
            </ul>
        </div>
"""
            body += "</div>"
        
        body += """
    <p>Please review the attached master schedule for complete details.</p>
    <p>Best regards,<br>Ambience Homes Team</p>
</body>
</html>
"""
        
        # Send emails
        partner_emails = [p['Email Address'] for p in self.partner_data if 'Email Address' in p]
        
        if partner_emails:
            self._send_email(
                to_emails=partner_emails,
                subject=subject,
                body=body,
                is_html=True,
                use_bcc=True,
                attachment=str(self.public_path / "Master Schedule.pdf")
            )
    
    def _send_customer_emails(self, projects):
        """Send individual emails to customers"""
        for project in projects:
            if not project.get('customer_email'):
                continue
            
            subject = f"Your Home Progress Update - {project['address']}"
            
            completion = self._calculate_completion(project['schedule'])
            
            # Get upcoming tasks
            today = datetime.now().date()
            upcoming_tasks = []
            completed_this_week = []
            
            for task in project['schedule']:
                task_date = datetime.strptime(task['date'], '%Y-%m-%d').date()
                days_diff = (task_date - today).days
                
                if -7 <= days_diff < 0:
                    completed_this_week.append(task)
                elif 0 <= days_diff <= 14:
                    upcoming_tasks.append(task)
            
            body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; }}
        .progress-bar {{ background: #e0e0e0; height: 20px; border-radius: 10px; margin: 10px 0; }}
        .progress-fill {{ background: #27ae60; height: 100%; border-radius: 10px; width: {completion}%; }}
        .section {{ margin: 20px 0; }}
        .task-list {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h2>Progress Update for Your New Home</h2>
        <p>{project['address']} • {project['community']}</p>
    </div>
    
    <div class="section">
        <h3>Project Overview</h3>
        <p><strong>Current Phase:</strong> {project['current_phase']}</p>
        <p><strong>Overall Progress:</strong> {completion}%</p>
        <div class="progress-bar">
            <div class="progress-fill"></div>
        </div>
    </div>
"""
            
            if completed_this_week:
                body += """
    <div class="section">
        <h3>Completed This Week</h3>
        <div class="task-list">
            <ul>
"""
                for task in completed_this_week:
                    body += f"<li>{task['task']} ✓</li>"
                body += """
            </ul>
        </div>
    </div>
"""
            
            if upcoming_tasks:
                body += """
    <div class="section">
        <h3>Upcoming Work</h3>
        <div class="task-list">
            <ul>
"""
                for task in upcoming_tasks:
                    date_str = datetime.strptime(task['date'], '%Y-%m-%d').strftime('%B %d')
                    body += f"<li>{date_str}: {task['task']}</li>"
                body += """
            </ul>
        </div>
    </div>
"""
            
            # Add estimated completion dates
            if project['schedule']:
                last_task_date = max(task['date'] for task in project['schedule'])
                est_completion = datetime.strptime(last_task_date, '%Y-%m-%d')
                est_closing = est_completion + timedelta(days=7)
                est_signing = est_closing - timedelta(days=1)
                
                body += f"""
    <div class="section">
        <h3>Important Dates</h3>
        <p><strong>Estimated Completion:</strong> {est_completion.strftime('%B %d, %Y')}</p>
        <p><strong>Estimated Closing:</strong> {est_closing.strftime('%B %d, %Y')}</p>
        <p><strong>Estimated Signing:</strong> {est_signing.strftime('%B %d, %Y')}</p>
    </div>
"""
            
            body += """
    <p>Thank you for choosing Ambience Homes! If you have any questions, please don't hesitate to reach out.</p>
    <p>Best regards,<br>Your Ambience Homes Team</p>
</body>
</html>
"""
            
            self._send_email(
                to_emails=[project['customer_email']],
                subject=subject,
                body=body,
                is_html=True
            )
    
    def _send_email(self, to_emails, subject, body, is_html=False, use_bcc=False, attachment=None):
        """Send email using Gmail SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = CONFIG['GMAIL_USER']
            msg['Subject'] = subject
            
            if use_bcc:
                msg['To'] = CONFIG['GMAIL_USER']
                # BCC addresses are added in sendmail
            else:
                msg['To'] = ', '.join(to_emails)
            
            # Attach body
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            # Add attachment if provided
            if attachment and os.path.exists(attachment):
                with open(attachment, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment)}'
                    )
                    msg.attach(part)
            
            # Send email
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(CONFIG['GMAIL_USER'], CONFIG['GMAIL_APP_PASSWORD'])
                
                if use_bcc:
                    server.sendmail(CONFIG['GMAIL_USER'], [CONFIG['GMAIL_USER']] + to_emails, msg.as_string())
                else:
                    server.sendmail(CONFIG['GMAIL_USER'], to_emails, msg.as_string())
            
            logging.info(f"Email sent successfully to {len(to_emails)} recipients")
            
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
    
    def generate_web_data(self, projects):
        """Generate data for web display - both individual and combined views"""
        
        # Individual view for customers (keep as-is from VBA export)
        web_data = {
            'lastUpdated': datetime.now().isoformat(),
            'projects': {},
            'summary': {
                'totalProjects': len(projects),
                'phases': {}
            }
        }
        
        # Combined view for construction team
        combined_data = {
            'lastUpdated': datetime.now().isoformat(),
            'projects': {},
            'summary': {
                'totalProjects': 0,
                'phases': {}
            }
        }
        
        # Process individual projects first (for web_data)
        for project in projects:
            # Create key from community and address
            project_key = f"{project['community']}_{project['address']}".replace(' ', '_').replace('__', '_')
            
            # Individual view entry
            web_data['projects'][project_key] = {
                'community': project['community'],
                'address': project['address'],
                'customer_name': project.get('customer_name', 'Unknown'),
                'sqft': project.get('sqft', ''),
                'current_phase': project.get('current_phase', 'Planning'),
                'completion_percentage': self._calculate_completion(project.get('schedule', [])),
                'schedule': project.get('schedule', [])
            }
            
            # Count phases
            phase = project.get('current_phase', 'Planning')
            if phase not in web_data['summary']['phases']:
                web_data['summary']['phases'][phase] = 0
            web_data['summary']['phases'][phase] += 1
        
        # Create a mapping of community/lot to project for easy lookup
        lot_to_project = {}
        for project in projects:
            # Normalize community
            community = project['community'].strip()
            # Extract lot number (handle 'Lot 81', '81', etc.)
            lot_field = project.get('lots', '')
            match = re.search(r'\d+', lot_field)
            if match:
                lot_num = int(match.group())
                key = f"{community}_{lot_num}"
                lot_to_project[key] = project
        
        # Parse lot pairs with addresses from the configuration
        # This requires updating lot_pairs to include address info
        # For now, we'll create the mapping based on the structure
        lot_pairs_with_addresses = {
            'Sunrise Estates': {
                'pairs': [
                    {'lots': (81, 82), 'addresses': ('346 Stockton', '354 Stockton')},
                    {'lots': (73, 74), 'addresses': ('282 Stockton', '290 Stockton')},
                    {'lots': (65, 66), 'addresses': ('224 Stockton', '230 Stockton')},
                    {'lots': (15, 46), 'addresses': ('276 Merrick', '268 Merrick')},
                    {'lots': (16, 17), 'addresses': ('284 Merrick', '292 Merrick')},
                ]
            },
            'Canal Landing': {
                'pairs': [
                    {'lots': (1, 2), 'addresses': ('1160 N Yost St', '1156 N Yost St')},
                    {'lots': (3, 4), 'addresses': ('1152 N Yost St', '1148 N Yost St')},
                    {'lots': (5, 6), 'addresses': ('4792 W Quinault Pl', '4780 W Quinault Pl')},
                    {'lots': (7, 8), 'addresses': ('4774 W Quinault Pl', '4768 W Quinault Pl')},
                    {'lots': (9, 10), 'addresses': ('4762 W Quinault Pl', '4756 W Quinault Pl')},
                    {'lots': (11, 12), 'addresses': ('4750 W Quinault Pl', '4744 W Quinault Pl')},
                    {'lots': (13, 14), 'addresses': ('4738 W Quinault Pl', '4732 W Quinault Pl')},
                    {'lots': (15, 16), 'addresses': ('4726 W Quinault Pl', '1130 N Williams Pl')},
                    {'lots': (21, 22), 'addresses': ('1133 N Yost Pl', '1129 N Yost Pl')},
                    # ... continue for all pairs
                ],
                'singles': [
                    {'lot': 19, 'address': '4816 N Yost St'},
                    {'lot': 20, 'address': '4822 W Quinault Pl'},
                    {'lot': 95, 'address': '1118 N Williams Pl'},
                    {'lot': 63, 'address': '1101 N Yost Pl'},
                    {'lot': 64, 'address': '4857 W Payette Pl'},
                    {'lot': 65, 'address': '4851 W Payette Pl'},
                    {'lot': 90, 'address': '4701 W Payette Pl'},
                ]
            }
        }
        
        # Track which projects we've already processed
        processed_projects = set()
        
        # Process based on lot pairings with addresses
        for community, config in lot_pairs_with_addresses.items():
            # Process pairs
            for pair_info in config.get('pairs', []):
                lot1, lot2 = pair_info['lots']
                addr1, addr2 = pair_info['addresses']
                
                key1 = f"{community}_{lot1}"
                key2 = f"{community}_{lot2}"
                
                if key1 in lot_to_project and key2 in lot_to_project:
                    proj1 = lot_to_project[key1]
                    proj2 = lot_to_project[key2]
                    
                    # Mark as processed
                    processed_projects.add(id(proj1))
                    processed_projects.add(id(proj2))
                    
                    # Create combined entry with full addresses
                    combined_key = f"{community}_{lot1}_{lot2}".replace(' ', '_')
                    
                    combined_data['projects'][combined_key] = {
                        'community': community,
                        'address': f"{addr1} / {addr2}",
                        'customer_name': f"{proj1.get('customer_name', 'Unknown')} / {proj2.get('customer_name', 'Unknown')}",
                        'sqft': proj1.get('sqft', ''),
                        'lots': f"Lots {lot1}/{lot2}",
                        'current_phase': proj1.get('current_phase', 'Planning'),
                        'completion_percentage': self._calculate_completion(proj1.get('schedule', [])),
                        'schedule': proj1.get('schedule', []),
                        'is_duplex': True
                    }
            
            # Process singles with their addresses
            for single_info in config.get('singles', []):
                lot_num = single_info['lot']
                address = single_info['address']
                
                key = f"{community}_{lot_num}"
                if key in lot_to_project:
                    project = lot_to_project[key]
                    processed_projects.add(id(project))
                    
                    single_key = f"{community}_{lot_num}".replace(' ', '_')
                    combined_data['projects'][single_key] = {
                        'community': community,
                        'address': address,
                        'customer_name': project.get('customer_name', 'Unknown'),
                        'sqft': project.get('sqft', ''),
                        'lots': f"Lot {lot_num}",
                        'current_phase': project.get('current_phase', 'Planning'),
                        'completion_percentage': self._calculate_completion(project.get('schedule', [])),
                        'schedule': project.get('schedule', []),
                        'is_duplex': False
                    }
        
        # Process any remaining projects as singles (shouldn't be any if lot_pairs is complete)
        for project in projects:
            if id(project) not in processed_projects:
                single_key = f"{project['community']}_{project['address']}".replace(' ', '_')
                combined_data['projects'][single_key] = {
                    'community': project['community'],
                    'address': project['address'],
                    'customer_name': project.get('customer_name', 'Unknown'),
                    'sqft': project.get('sqft', ''),
                    'lots': f"Lot {project.get('lots', '')}" if project.get('lots') else "",
                    'current_phase': project.get('current_phase', 'Planning'),
                    'completion_percentage': self._calculate_completion(project.get('schedule', [])),
                    'schedule': project.get('schedule', []),
                    'is_duplex': False
                }
        
        # Update summary
        combined_data['summary']['totalProjects'] = len(combined_data['projects'])
        for project_data in combined_data['projects'].values():
            phase = project_data['current_phase']
            if phase not in combined_data['summary']['phases']:
                combined_data['summary']['phases'][phase] = 0
            combined_data['summary']['phases'][phase] += 1
        
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
        
        # Copy to project filing system (G drive)
        try:
            project_filing_path = Path("G:/My Drive/Project Dashboard/Schedule System")
            project_filing_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(json_path, project_filing_path / 'schedule_data.json')
            shutil.copy2(combined_json_path, project_filing_path / 'schedule_data_combined.json')
            logging.info("Copied both JSON files to project filing system (G drive)")
        except Exception as e:
            logging.error(f"Failed to copy to project filing system (G drive): {e}")

        # Copy to Dropbox folder (dynamic user path)
        try:
            home = Path.home()
            dropbox_path = home / 'Ambience Team Dropbox' / 'Onedrive files' / 'UNDER CONSTRUCTION' / 'NEW STUFF' / 'Master Schedules' / 'JsonScheduleData'
            dropbox_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(json_path, dropbox_path / 'schedule_data.json')
            shutil.copy2(combined_json_path, dropbox_path / 'schedule_data_combined.json')
            logging.info("Copied both JSON files to Dropbox folder (dynamic user path)")
        except Exception as e:
            logging.error(f"Failed to copy to Dropbox folder (dynamic user path): {e}")

def main():
    """Run the automation with monitoring"""
    automation = EnhancedScheduleAutomation()
    
    # For production - monitor for triggers
    logging.info("Monitoring for trigger files...")
    
    while True:
        try:
            projects = automation.parse_schedule_data()
            if projects:
                automation.generate_web_data(projects)
                logging.info("Web data generated and saved.")
                time.sleep(60)  # Wait a bit longer after processing
            else:
                logging.info("No projects found. Retrying soon.")
                time.sleep(30)  # Check again soon if nothing to process
        except KeyboardInterrupt:
            logging.info("Automation stopped by user")
            break
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # For testing, run once
    # automation = EnhancedScheduleAutomation()
    # automation.run()
    
    # For production, run monitoring loop
    main()