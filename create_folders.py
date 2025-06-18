import os
from pathlib import Path

def create_folder_structure():
    """
    Creates the complete folder structure for the Master Schedule system
    """
    # Your Google Drive path
    base_path = r"G:\My Drive\Project Dashboard"
    
    # Define all folders to create
    folders = [
        # Public folder for website
        "Public/Master Schedule",
        
        # Schedule System folders
        "Schedule System/Master Files/Archive",
        "Schedule System/Automation/vba_macros",
        "Schedule System/Automation/email_templates",
        "Schedule System/Automation/config",
        "Schedule System/Automation/logs",
        "Schedule System/Temp",
        
        # Project folders
        "Projects/Active",
        "Projects/Completed/2024",
        "Projects/Completed/2025",
        
        # Customer Portal base
        "Customer Portals"
    ]
    
    # Create each folder
    created_folders = []
    existing_folders = []
    
    for folder in folders:
        full_path = os.path.join(base_path, folder)
        try:
            Path(full_path).mkdir(parents=True, exist_ok=True)
            if os.path.exists(full_path):
                if full_path not in existing_folders:
                    created_folders.append(folder)
            print(f"✓ Created: {folder}")
        except Exception as e:
            print(f"✗ Error creating {folder}: {e}")
    
    print("\n" + "="*50)
    print(f"Folder creation complete!")
    print(f"Created {len(created_folders)} folders")
    print(f"Base path: {base_path}")
    
    # Create a README file to document the structure
    readme_content = """# Master Schedule Automation Folder Structure

## Folder Purposes:

### Public/
- Contains ONLY the Master Schedule.pdf for website display
- This is the only publicly accessible folder

### Schedule System/
- Master Files: Contains the Excel file and archived PDFs
- Automation: All scripts and configuration files
- Temp: Temporary files during processing

### Projects/
- Active: Current construction projects
- Completed: Archived projects by year

### Customer Portals/
- Individual folders for each customer
- Contains their specific schedule and documents

## Important Notes:
- Never put sensitive data in the Public folder
- All automation scripts run from Schedule System/Automation/
- Customer data syncs from Projects to Customer Portals
"""
    
    readme_path = os.path.join(base_path, "README.md")
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"\n✓ Created README.md in {base_path}")

if __name__ == "__main__":
    print("Master Schedule Folder Structure Creator")
    print("="*50)
    
    # Confirm before creating
    response = input("This will create folders in G:\\My Drive\\Project Dashboard\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        create_folder_structure()
    else:
        print("Folder creation cancelled.")