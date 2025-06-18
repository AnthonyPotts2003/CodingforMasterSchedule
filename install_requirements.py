import subprocess
import sys

def install_packages():
    """Install required packages for the Master Schedule automation"""
    
    packages = [
        'google-api-python-client',
        'google-auth-httplib2',
        'google-auth-oauthlib',
        'pandas',
        'openpyxl',
        'python-dotenv',
        'schedule',
        'pywin32',  # For Excel automation on Windows
    ]
    
    print("Master Schedule Automation - Package Installer")
    print("=" * 50)
    print("This will install the following packages:")
    for pkg in packages:
        print(f"  - {pkg}")
    
    response = input("\nContinue with installation? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        for package in packages:
            print(f"\nInstalling {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} installed successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Error installing {package}")
        
        print("\n" + "="*50)
        print("Installation complete!")
        
        # Create requirements.txt for future reference
        with open('requirements.txt', 'w') as f:
            for pkg in packages:
                f.write(f"{pkg}\n")
        print("✓ Created requirements.txt file")
        
    else:
        print("Installation cancelled.")

if __name__ == "__main__":
    install_packages()