#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple

# Colors for output (works on all platforms)
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

# Get repo root
REPO_ROOT = Path(__file__).parent.absolute()

def print_header():
    """Display script header"""
    print(f"\n{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}         VesselVerse Dataset User Manager          {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")

def print_menu():
    """Display user menu"""
    print(f"{Colors.CYAN}What would you like to do?{Colors.NC}\n")
    print("  [1] Initial Setup     - First time setup (configure credentials & download)")
    print("  [2] Update Dataset    - Sync latest changes from remote")
    print("  [3] Upload Data       - Upload your modifications to the shared folder")
    print("  [4] Switch Dataset    - Change to a different dataset")
    print("  [5] Exit\n")

def run_command(cmd: List[str], description: str = "", cwd: Path = None) -> Tuple[bool, str]:
    """
    Run a shell command and return success status
    
    Args:
        cmd: Command as list (e.g., ['git', 'pull'])
        description: Description for logging
        cwd: Working directory
        
    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        if cwd is None:
            cwd = REPO_ROOT
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_prerequisites() -> bool:
    """Check if all prerequisites are installed"""
    print(f"{Colors.YELLOW}[1/6] Checking prerequisites...{Colors.NC}")
    
    # Check Python
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Error: Python 3.8+ is required{Colors.NC}")
        return False
    
    # Check Git
    success, _ = run_command(['git', '--version'])
    if not success:
        print(f"{Colors.RED}❌ Error: Git is not installed{Colors.NC}")
        return False
    
    # Check DVC
    success, _ = run_command(['dvc', '--version'])
    if not success:
        print(f"{Colors.YELLOW}⚠️  DVC is not installed. Installing now...{Colors.NC}")
        success, _ = run_command([sys.executable, '-m', 'pip', 'install', 'dvc[gdrive]'])
        if not success:
            print(f"{Colors.RED}❌ Failed to install DVC{Colors.NC}")
            return False
    
    print(f"{Colors.GREEN}✅ All prerequisites met{Colors.NC}\n")
    return True

def configure_credentials() -> bool:
    """Configure user credentials"""
    print(f"{Colors.YELLOW}[2/6] Configuring user credentials...{Colors.NC}")
    
    config_path = REPO_ROOT / 'config.sh'
    if not config_path.exists():
        print(f"{Colors.RED}❌ Error: config.sh not found{Colors.NC}")
        return False
    
    # Find credential files
    creds_dir = REPO_ROOT / 'credentials'
    if not creds_dir.exists():
        print(f"{Colors.RED}❌ Error: credentials directory not found{Colors.NC}")
        return False
    
    cred_files = list(creds_dir.glob('*.json'))
    if not cred_files:
        print(f"{Colors.RED}❌ Error: No credential files found in credentials/{Colors.NC}")
        print("Please contact dataset maintainers to obtain credentials")
        return False
    
    print("Available credential files:")
    for i, cred_file in enumerate(cred_files):
        print(f"  [{i}] {cred_file.name}")
    
    print()
    choice_str = input(f"Select credential file number [0]: ").strip() or "0"
    
    try:
        choice = int(choice_str)
        if choice < 0 or choice >= len(cred_files):
            print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
            return False
    except ValueError:
        print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
        return False
    
    selected_cred = cred_files[choice]
    print(f"{Colors.GREEN}✅ Using credentials: {selected_cred.name}{Colors.NC}\n")
    
    # Update config.sh
    try:
        with open(config_path, 'r') as f:
            config_content = f.read()
        
        # Replace user_auth_path
        import re
        config_content = re.sub(
            r'user_auth_path="[^"]*"',
            f'user_auth_path="{selected_cred.absolute()}"',
            config_content
        )
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"{Colors.GREEN}✅ config.sh updated{Colors.NC}\n")
        return True
    except Exception as e:
        print(f"{Colors.RED}❌ Error updating config.sh: {e}{Colors.NC}")
        return False

def configure_dvc_remotes() -> bool:
    """Configure DVC remotes for user"""
    print(f"{Colors.YELLOW}[3/6] Configuring DVC remotes...{Colors.NC}")
    
    # Load config.sh
    config_path = REPO_ROOT / 'config.sh'
    try:
        config_vars = {}
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith(('database_ID=', 'user_upload_ID=', 'user_auth_path=')):
                    key, value = line.split('=', 1)
                    config_vars[key] = value.strip('"\'')
        
        database_id = config_vars.get('database_ID')
        user_upload_id = config_vars.get('user_upload_ID')
        user_auth_path = config_vars.get('user_auth_path')
        
        if not all([database_id, user_upload_id, user_auth_path]):
            print(f"{Colors.RED}❌ Error: Missing configuration variables{Colors.NC}")
            return False
        
    except Exception as e:
        print(f"{Colors.RED}❌ Error reading config.sh: {e}{Colors.NC}")
        return False
    
    # Remove existing remotes if they exist
    run_command(['dvc', 'remote', 'remove', 'storage'], cwd=REPO_ROOT)
    run_command(['dvc', 'remote', 'remove', 'uploads'], cwd=REPO_ROOT)
    
    # Add storage remote (read-only for users)
    print(f"Setting up 'storage' remote (Database ID: {database_id[:20]}...)")
    success, output = run_command(
        ['dvc', 'remote', 'add', '-d', 'storage', f'gdrive://{database_id}'],
        cwd=REPO_ROOT
    )
    if not success:
        print(f"{Colors.RED}❌ Failed to add storage remote{Colors.NC}")
        return False
    
    run_command(
        ['dvc', 'remote', 'modify', 'storage', 'gdrive_service_account_json_file_path', user_auth_path],
        cwd=REPO_ROOT
    )
    run_command(
        ['dvc', 'remote', 'modify', 'storage', 'gdrive_use_service_account', 'true'],
        cwd=REPO_ROOT
    )
    
    # Add uploads remote
    print(f"Setting up 'uploads' remote (Upload ID: {user_upload_id[:20]}...)")
    success, output = run_command(
        ['dvc', 'remote', 'add', 'uploads', f'gdrive://{user_upload_id}'],
        cwd=REPO_ROOT
    )
    if not success:
        print(f"{Colors.RED}❌ Failed to add uploads remote{Colors.NC}")
        return False
    
    run_command(
        ['dvc', 'remote', 'modify', 'uploads', 'gdrive_service_account_json_file_path', user_auth_path],
        cwd=REPO_ROOT
    )
    run_command(
        ['dvc', 'remote', 'modify', 'uploads', 'gdrive_use_service_account', 'true'],
        cwd=REPO_ROOT
    )
    
    # Enable autostage
    run_command(['dvc', 'config', 'core.autostage', 'true'], cwd=REPO_ROOT)
    
    print(f"{Colors.GREEN}✅ DVC remotes configured{Colors.NC}\n")
    return True

def user_initial_setup():
    """Function 1: Initial Setup"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Initial Setup - First Time Configuration        {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    if not check_prerequisites():
        return
    
    if not configure_credentials():
        return
    
    if not configure_dvc_remotes():
        return
    
    # Verify setup
    print(f"{Colors.YELLOW}[4/6] Verifying remote setup...{Colors.NC}")
    success, output = run_command(['dvc', 'remote', 'list'], cwd=REPO_ROOT)
    
    if 'storage' in output and 'uploads' in output:
        print(f"{Colors.GREEN}✅ User Mode Activated{Colors.NC}\n")
    else:
        print(f"{Colors.RED}❌ Error: Remote configuration failed{Colors.NC}")
        return
    
    # Summary
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.GREEN}          Setup Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    print("You can now:")
    print("  [2] Update Dataset  - Download approved data")
    print("  [3] Upload Data     - Share your work\n")

def user_update_dataset():
    """Function 2: Update Dataset"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Update Dataset - User Mode                     {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    # Step 1: Git pull
    print(f"{Colors.YELLOW}[1/3] Updating Git repository...{Colors.NC}")
    success, output = run_command(['git', 'pull'], cwd=REPO_ROOT)
    if success:
        print(f"{Colors.GREEN}✅ Git repository updated{Colors.NC}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Git pull had issues{Colors.NC}\n")
    
    # Step 2: DVC pull
    print(f"{Colors.YELLOW}[2/3] Pulling data from remote...{Colors.NC}")
    success, output = run_command(['dvc', 'pull'], cwd=REPO_ROOT)
    
    if success:
        print(f"{Colors.GREEN}✅ Data updated{Colors.NC}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Some files may have failed to download{Colors.NC}\n")
    
    # Summary
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.GREEN}          Update Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    print("Your data is ready to work with!")
    print(f"Location: {REPO_ROOT / 'VESSELVERSE_DATA_IXI' / 'data'}\n")

def user_upload_data():
    """Function 3: Upload Data"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Upload Data - User Mode                        {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    data_dir = REPO_ROOT / 'VESSELVERSE_DATA_IXI' / 'data'
    
    if not data_dir.exists():
        print(f"{Colors.RED}❌ Error: Data directory not found{Colors.NC}")
        return
    
    # Step 1: List folders to track
    print(f"{Colors.YELLOW}[1/5] Scanning for modified folders...{Colors.NC}")
    
    folders = sorted([d.name for d in data_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
    
    if not folders:
        print(f"{Colors.RED}❌ No folders found{Colors.NC}")
        return
    
    print("Available folders:")
    for i, folder in enumerate(folders):
        dvc_file = data_dir / f"{folder}.dvc"
        status = "already tracked" if dvc_file.exists() else "not tracked"
        print(f"  [{i}] {folder} ({status})")
    
    print(f"  [a] All folders\n")
    
    choice_str = input("Select folder(s) to upload (comma-separated or 'a' for all): ").strip().lower()
    
    selected_folders = []
    if choice_str == 'a':
        selected_folders = folders
    else:
        try:
            for choice in choice_str.split(','):
                idx = int(choice.strip())
                if 0 <= idx < len(folders):
                    selected_folders.append(folders[idx])
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
            return
    
    if not selected_folders:
        print(f"{Colors.RED}❌ No valid folders selected{Colors.NC}")
        return
    
    print(f"{Colors.GREEN}✅ Selected {len(selected_folders)} folder(s){Colors.NC}\n")
    
    # Step 2: Track with DVC
    print(f"{Colors.YELLOW}[2/5] Adding folders to DVC...{Colors.NC}")
    tracked_folders = []
    
    for folder in selected_folders:
        print(f"{Colors.CYAN}Processing: {folder}{Colors.NC}")
        success, output = run_command(['dvc', 'add', folder], cwd=data_dir)
        
        if success:
            print(f"  {Colors.GREEN}✅ Added {folder} to DVC{Colors.NC}")
            tracked_folders.append(folder)
        else:
            print(f"  {Colors.RED}❌ Failed to add {folder}{Colors.NC}")
    
    if not tracked_folders:
        print(f"{Colors.RED}❌ No folders were tracked{Colors.NC}")
        return
    
    print()
    
    # Step 3: Commit to Git
    print(f"{Colors.YELLOW}[3/5] Committing to Git...{Colors.NC}")
    
    # Stage files
    for folder in tracked_folders:
        run_command(['git', 'add', f'{folder}.dvc'], cwd=data_dir)
    
    run_command(['git', 'add', '.gitignore'], cwd=data_dir)
    
    commit_msg = input("Enter commit message [Updated data]: ").strip() or "Updated data"
    success, _ = run_command(['git', 'commit', '-m', commit_msg], cwd=REPO_ROOT)
    
    if success:
        print(f"{Colors.GREEN}✅ Changes committed{Colors.NC}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  No changes to commit or commit failed{Colors.NC}\n")
    
    # Step 4: Push to DVC
    print(f"{Colors.YELLOW}[4/5] Pushing to DVC uploads remote...{Colors.NC}")
    
    for folder in tracked_folders:
        dvc_file = data_dir / f"{folder}.dvc"
        print(f"{Colors.CYAN}Pushing: {folder}{Colors.NC}")
        success, _ = run_command(['dvc', 'push', '-r', 'uploads', str(dvc_file)], cwd=REPO_ROOT)
        
        if success:
            print(f"  {Colors.GREEN}✅ Pushed{Colors.NC}")
        else:
            print(f"  {Colors.RED}❌ Failed to push{Colors.NC}")
    
    print()
    
    # Step 5: Push to Git
    print(f"{Colors.YELLOW}[5/5] Pushing to Git...{Colors.NC}")
    success, _ = run_command(['git', 'push'], cwd=REPO_ROOT)
    
    if success:
        print(f"{Colors.GREEN}✅ Pushed to Git{Colors.NC}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Git push failed{Colors.NC}\n")
    
    # Summary
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.GREEN}          Upload Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    print(f"Your modifications are ready for owner review!")
    print(f"Owner will review and approve via: [4] Review Uploads\n")

def user_switch_dataset():
    """Function 4: Switch Dataset"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Switch Dataset - User Mode                     {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}This feature allows you to work with different datasets.{Colors.NC}\n")
    
    datasets_dir = REPO_ROOT / 'VesselVerse-Dataset' / 'datasets'
    
    if not datasets_dir.exists():
        print(f"{Colors.RED}❌ Error: Datasets directory not found{Colors.NC}")
        return
    
    datasets = sorted([d.name for d in datasets_dir.iterdir() if d.is_dir() and d.name.startswith('D-')])
    
    if not datasets:
        print(f"{Colors.RED}❌ No datasets found{Colors.NC}")
        return
    
    print("Available datasets:")
    for i, dataset in enumerate(datasets):
        print(f"  [{i}] {dataset}")
    
    print()
    choice_str = input("Select dataset to switch to: ").strip()
    
    try:
        choice = int(choice_str)
        if 0 <= choice < len(datasets):
            selected = datasets[choice]
            print(f"{Colors.GREEN}✅ Switched to: {selected}{Colors.NC}")
            print(f"\nNext steps:")
            print(f"  1. Run [2] Update Dataset to download data")
            print(f"  2. Work with the data")
            print(f"  3. Run [3] Upload Data to share your work\n")
        else:
            print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
    except ValueError:
        print(f"{Colors.RED}❌ Invalid input{Colors.NC}")

def main():
    """Main execution loop"""
    print_header()
    
    while True:
        print_menu()
        choice = input(f"Enter your choice [1-5]: ").strip()
        
        if choice == '1':
            user_initial_setup()
        elif choice == '2':
            user_update_dataset()
        elif choice == '3':
            user_upload_data()
        elif choice == '4':
            user_switch_dataset()
        elif choice == '5':
            print(f"{Colors.BLUE}Goodbye!{Colors.NC}\n")
            sys.exit(0)
        else:
            print(f"{Colors.RED}Invalid option. Please select 1-5{Colors.NC}\n")
        
        input(f"Press Enter to continue...")
        print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Script interrupted by user{Colors.NC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.NC}\n")
        sys.exit(1)
