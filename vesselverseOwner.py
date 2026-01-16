#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple, Optional
from config import VesselVerseConfig

# ANSI Color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def disable_on_windows():
        """Disable colors on Windows if not using ANSI support"""
        if sys.platform == 'win32':
            for attr in dir(Colors):
                if not attr.startswith('_') and attr != 'disable_on_windows':
                    setattr(Colors, attr, '')


REPO_ROOT = Path(__file__).parent.resolve()
DATASET_GIT_ROOT = REPO_ROOT / "VesselVerse-Dataset"
VENV_ROOT = DATASET_GIT_ROOT
VENV_PATH = VENV_ROOT / ".venv"


def setup_virtual_environment() -> bool:
    """
    Create and setup virtual environment if not exists
    Returns True if venv is ready, False otherwise
    """
    if not VENV_PATH.exists():
        print(f"{Colors.YELLOW}Creating virtual environment in VesselVerse-Dataset...{Colors.NC}")
        try:
            subprocess.run(
                [sys.executable, '-m', 'venv', str(VENV_PATH)],
                check=True,
                cwd=REPO_ROOT
            )
            print(f"{Colors.GREEN}✅ Virtual environment created{Colors.NC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Error: Failed to create virtual environment{Colors.NC}")
            return False
    
    # Get the python executable from venv
    if sys.platform == 'win32':
        venv_python = VENV_PATH / 'Scripts' / 'python.exe'
        venv_pip = VENV_PATH / 'Scripts' / 'pip.exe'
    else:
        venv_python = VENV_PATH / 'bin' / 'python'
        venv_pip = VENV_PATH / 'bin' / 'pip'
    
    if not venv_python.exists():
        print(f"{Colors.RED}❌ Error: Virtual environment is corrupted{Colors.NC}")
        return False
    
    return True


def get_venv_python() -> Path:
    """Get the Python executable from the virtual environment"""
    if sys.platform == 'win32':
        return VENV_PATH / 'Scripts' / 'python.exe'
    else:
        return VENV_PATH / 'bin' / 'python'


def run_command(cmd: str, cwd: Optional[Path] = None, capture_output: bool = False) -> Tuple[int, str]:
    """
    Execute a shell command and return exit code and output
    
    Args:
        cmd: Command to execute
        cwd: Working directory for command
        capture_output: Whether to capture output
    
    Returns:
        Tuple of (exit_code, output)
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or REPO_ROOT,
            capture_output=capture_output,
            text=True
        )
        # When capture_output=False, stdout/stderr are None; avoid concatenation errors
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode, out
    except Exception as e:
        print(f"{Colors.RED}❌ Error running command: {e}{Colors.NC}")
        return 1, str(e)


def check_prerequisites() -> bool:
    """Check if all required tools are installed"""
    print(f"{Colors.YELLOW}Checking prerequisites...{Colors.NC}")
    
    # Check Python 3
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Error: Python 3.8+ is required{Colors.NC}")
        return False
    
    # Check Git
    code, _ = run_command('git --version')
    if code != 0:
        print(f"{Colors.RED}❌ Error: Git is not installed{Colors.NC}")
        return False
    
    # Get venv python
    venv_python = get_venv_python()
    
    # Check DVC in venv
    code, _ = run_command(f'"{venv_python}" -c "import dvc.cli"')
    if code != 0:
        print(f"{Colors.YELLOW}⚠️  DVC is not installed in venv. Installing now...{Colors.NC}")
        code, _ = run_command(f'"{venv_python}" -m pip install "dvc[gdrive]"')
        if code != 0:
            print(f"{Colors.RED}❌ Failed to install DVC{Colors.NC}")
            return False
    
    # Check DVC gdrive support
    code, _ = run_command(f'"{venv_python}" -c "import dvc_gdrive"')
    if code != 0:
        print(f"{Colors.YELLOW}⚠️  DVC gdrive support not found. Installing...{Colors.NC}")
        code, _ = run_command(f'"{venv_python}" -m pip install "dvc[gdrive]"')
        if code != 0:
            print(f"{Colors.RED}❌ Failed to install DVC gdrive support{Colors.NC}")
            return False
    
    print(f"{Colors.GREEN}✅ All prerequisites met{Colors.NC}")
    return True


# Configuration is now loaded from config.py using VesselVerseConfig class


def display_header():
    """Display script header"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}         VesselVerse Dataset Owner Manager         {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()


def show_menu():
    """Display owner menu"""
    print(f"{Colors.CYAN}What would you like to do?{Colors.NC}")
    print()
    print("  [1] Initial Setup     - First time setup (configure credentials & download)")
    print("  [2] Update Dataset    - Sync latest changes from remote")
    print("  [3] Upload Dataset    - Push changes to the remote storage")
    print("  [4] Review Uploads    - Download user contributions for review")
    print("  [5] Exit")
    print()


######## Function 1: Initial Setup

def initial_owner_setup():
    """Initial setup - configure credentials and DVC remotes"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}   Initial Setup - First Time Configuration        {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()

    # Step 1: Check prerequisites
    print(f"{Colors.YELLOW}[1/4] Checking prerequisites...{Colors.NC}")
    if not check_prerequisites():
        return False
    print()

    # Step 2: Configure credentials
    print(f"{Colors.YELLOW}[2/4] Configuring owner credentials...{Colors.NC}")
    
    # Load config
    config = VesselVerseConfig()
    
    cred_dir = config.CREDENTIALS_DIR
    if not cred_dir.exists():
        print(f"{Colors.RED}❌ Error: credentials directory not found{Colors.NC}")
        return False
    
    # Find credential files
    cred_files = sorted([f for f in cred_dir.glob('*.json')])
    if not cred_files:
        print(f"{Colors.RED}❌ No credential files found in {cred_dir}{Colors.NC}")
        return False
    
    print("Available credential files:")
    for i, cred_file in enumerate(cred_files):
        print(f"  [{i}] {cred_file.name}")
    print()
    
    # Select credential
    try:
        choice = input("Select credential file number [0]: ").strip() or "0"
        choice = int(choice)
        if choice < 0 or choice >= len(cred_files):
            print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
            return False
        selected_cred = cred_files[choice]
    except ValueError:
        print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
        return False
    
    print(f"{Colors.GREEN}✅ Using credentials: {selected_cred.name}{Colors.NC}")
    
    # Update config with selected credentials
    config.owner_auth_path = selected_cred
    print()

    # Step 3: Initialize and configure DVC in each dataset
    print(f"{Colors.YELLOW}[3/6] Initializing all datasets...{Colors.NC}")
    datasets_dir = DATASET_GIT_ROOT / "datasets"
    if not datasets_dir.exists():
        print(f"{Colors.RED}❌ Error: Datasets directory not found: {datasets_dir}{Colors.NC}")
        return False

    all_datasets = sorted([d for d in datasets_dir.glob("D-*") if d.is_dir()])
    if not all_datasets:
        print(f"{Colors.RED}❌ No datasets found in {datasets_dir}{Colors.NC}")
        return False

    print(f"Found {len(all_datasets)} dataset(s):")
    for dataset in all_datasets:
        print(f"  • {dataset.name}")
    print()
    print("Configuring DVC for each dataset...")
    print()

    database_id = config.database_ID
    user_upload_id = config.user_upload_ID

    for dataset_path in all_datasets:
        print(f"{Colors.CYAN}► Processing: {dataset_path.name}{Colors.NC}")
        # Initialize DVC if not present
        dvc_dir = dataset_path / ".dvc"
        if not dvc_dir.exists():
            code, _ = run_command(f'"{get_venv_python()}" -m dvc init --no-scm', cwd=dataset_path)
            if code == 0:
                run_command(f'"{get_venv_python()}" -m dvc config core.autostage true', cwd=dataset_path)
                print("  ✓ DVC initialized")
            else:
                print(f"  {Colors.RED}❌ Failed to initialize DVC{Colors.NC}")
                continue
        else:
            print("  ✓ DVC already initialized")

        # Remove existing remotes
        ## add try and catch
        run_command(f'"{get_venv_python()}" -m dvc remote remove storage', cwd=dataset_path)
        run_command(f'"{get_venv_python()}" -m dvc remote remove uploads', cwd=dataset_path)

        # Add storage remote
        if database_id and selected_cred:
            run_command(f'"{get_venv_python()}" -m dvc remote add -d storage "gdrive://{database_id}"', cwd=dataset_path)
            run_command(f'"{get_venv_python()}" -m dvc remote modify storage gdrive_service_account_json_file_path "{selected_cred}"', cwd=dataset_path)
            run_command(f'"{get_venv_python()}" -m dvc remote modify storage gdrive_use_service_account true', cwd=dataset_path)
            print("  ✓ Storage remote configured")

        # Add uploads remote
        if user_upload_id and selected_cred:
            run_command(f'"{get_venv_python()}" -m dvc remote add uploads "gdrive://{user_upload_id}"', cwd=dataset_path)
            run_command(f'"{get_venv_python()}" -m dvc remote modify uploads gdrive_service_account_json_file_path "{selected_cred}"', cwd=dataset_path)
            run_command(f'"{get_venv_python()}" -m dvc remote modify uploads gdrive_use_service_account true', cwd=dataset_path)
            print("  ✓ Uploads remote configured")

        print()

    print(f"{Colors.GREEN}✅ All datasets configured{Colors.NC}")
    print()

    # Step 4: Verify setup
    print(f"{Colors.YELLOW}[4/6] Verifying setup...{Colors.NC}")
    configured_count = 0
    for dataset_path in all_datasets:
        code, output = run_command(f'"{get_venv_python()}" -m dvc remote list', cwd=dataset_path, capture_output=True)
        if "storage" in output:
            configured_count += 1
    if configured_count > 0:
        print(f"{Colors.GREEN}✅ {configured_count} dataset(s) configured with DVC remotes{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ Error: No datasets configured{Colors.NC}")
        return False
    print()

    # Summary
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.GREEN}          Owner Setup Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Configuration Summary:{Colors.NC}")
    print(f"  Credentials: {Colors.GREEN}{selected_cred.name}{Colors.NC}")
    print(f"  Storage Remote: {Colors.GREEN}gdrive://{database_id}{Colors.NC}")
    print(f"  Uploads Remote: {Colors.GREEN}gdrive://{user_upload_id}{Colors.NC}")
    print()
    
    return True


######## Function 2: Update Dataset

def owner_update_dataset():
    """Update dataset - pull from remote storage"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}   Update Dataset - Owner Mode                     {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()

    # Load config
    config = VesselVerseConfig()

    # Step 1: Select target dataset (like upload)
    dataset_base = DATASET_GIT_ROOT / 'datasets'
    print(f"{Colors.YELLOW}[1/5] Select target dataset...{Colors.NC}")
    available_datasets = sorted([
        d.name for d in dataset_base.glob('D-*') 
        if d.is_dir()
    ])
    print("Available datasets:")
    for i, dataset in enumerate(available_datasets):
        print(f"  [{i}] {dataset}")
    print("  [n] Create new dataset")
    print()
    choice = input("Select dataset: ").strip().lower()
    if choice == 'n':
        new_name = input("Enter new dataset name (without D- prefix): ").strip()
        selected_dataset = f"D-{new_name}"
        dataset_dir = dataset_base / selected_dataset
        dataset_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}✅ Created new dataset: {selected_dataset}{Colors.NC}")
    else:
        try:
            idx = int(choice)
            if 0 <= idx < len(available_datasets):
                selected_dataset = available_datasets[idx]
                dataset_dir = dataset_base / selected_dataset
            else:
                print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
                return False
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
            return False
    print(f"{Colors.GREEN}Target dataset: {selected_dataset}{Colors.NC}")
    print()

    # Use the data directory inside the selected dataset
    data_dir = dataset_dir
    if not data_dir.exists():
        print(f"{Colors.RED}❌ Error: Data directory not found: {data_dir}{Colors.NC}")
        return False

    # Check DVC config in the selected dataset directory
    code, output = run_command('dvc remote list', cwd=dataset_dir, capture_output=True)
    print(f"{Colors.YELLOW}DVC remotes in {dataset_dir}:{Colors.NC}\n{output}")  # Debug print
    if 'storage' not in output:
        print(f"{Colors.RED}❌ Error: DVC remotes not configured in {dataset_dir}{Colors.NC}")
        print("Run option [1] Initial Setup first")
        return False

    # Step 2: Update Git
    print(f"{Colors.YELLOW}[2/5] Updating Git repository...{Colors.NC}")
    code, _ = run_command('git pull', cwd=DATASET_GIT_ROOT)
    if code == 0:
        print(f"{Colors.GREEN}✅ Git repository updated{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Git pull had issues, continuing anyway...{Colors.NC}")
    print()

    # Step 3: Restore deleted .dvc files
    print(f"{Colors.YELLOW}[3/5] Restoring .dvc files if needed...{Colors.NC}")
    code, output = run_command('git status --short', cwd=data_dir, capture_output=True)
    deleted_dvc = output.count('.dvc')
    if deleted_dvc > 0:
        print(f"  Restoring {deleted_dvc} deleted .dvc file(s)...")
        run_command('git restore *.dvc', cwd=data_dir)
        print(f"{Colors.GREEN}✅ .dvc files restored{Colors.NC}")
    else:
        print(f"{Colors.GREEN}✅ All .dvc files present{Colors.NC}")
    print()

    # Step 4: Scan for .dvc files
    print(f"{Colors.YELLOW}[4/5] Scanning for .dvc files...{Colors.NC}")
    dvc_files = sorted(f for f in data_dir.glob('*.dvc') if f.is_file())
    if not dvc_files:
        print(f"{Colors.YELLOW}⚠️  No .dvc files found in {data_dir}{Colors.NC}")
        return True
    print(f"{Colors.GREEN}Found {len(dvc_files)} tracked item(s):{Colors.NC}")
    for dvc_file in dvc_files:
        print(f"  • {dvc_file.stem}")
    print()

    # Step 5: Download data
    print(f"{Colors.YELLOW}[5/5] Downloading updates from remote...{Colors.NC}")
    print()
    total_updated = 0
    total_failed = 0
    for dvc_file in dvc_files:
        dvc_name = dvc_file.stem
        print(f"{Colors.CYAN}Pulling: {dvc_name}{Colors.NC}")
        code, _ = run_command(f'dvc pull "{dvc_file.name}"', cwd=dataset_dir)
        if code == 0:
            print(f"  {Colors.GREEN}✅ {dvc_name} downloaded{Colors.NC}")
            total_updated += 1
        else:
            print(f"  {Colors.YELLOW}⚠️  {dvc_name} - Failed to download{Colors.NC}")
            total_failed += 1
    print()

    # Summary
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.GREEN}          Download Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Update Summary:{Colors.NC}")
    print(f"  Total datasets processed: {Colors.GREEN}{len(dvc_files)}{Colors.NC}")
    print(f"  Successfully updated:     {Colors.GREEN}{total_updated}{Colors.NC}")
    if total_failed > 0:
        print(f"  Warnings:                 {Colors.YELLOW}{total_failed}{Colors.NC}")
    print()
    return True


######## Function 3: Upload Dataset

def owner_upload_dataset():
    """Upload dataset changes - track with DVC and push to remote"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}   Upload Dataset Changes - Owner Mode             {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()

    # Load config
    config = VesselVerseConfig()
    
    # Step 1: Select target dataset
    dataset_base = DATASET_GIT_ROOT / 'datasets'
    print(f"{Colors.YELLOW}[1/5] Select target dataset...{Colors.NC}")
    available_datasets = sorted([
        d.name for d in dataset_base.glob('D-*') 
        if d.is_dir()
    ])
    print("Available datasets:")
    for i, dataset in enumerate(available_datasets):
        print(f"  [{i}] {dataset}")
    print("  [n] Create new dataset")
    print()
    choice = input("Select dataset: ").strip().lower()
    if choice == 'n':
        new_name = input("Enter new dataset name (without D- prefix): ").strip()
        selected_dataset = f"D-{new_name}"
        dataset_dir = dataset_base / selected_dataset
        dataset_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Colors.GREEN}✅ Created new dataset: {selected_dataset}{Colors.NC}")
    else:
        try:
            idx = int(choice)
            if 0 <= idx < len(available_datasets):
                selected_dataset = available_datasets[idx]
                dataset_dir = dataset_base / selected_dataset
            else:
                print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
                return False
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
            return False
    print(f"{Colors.GREEN}Target dataset: {selected_dataset}{Colors.NC}")
    print()

    # Use the data directory inside the selected dataset
    data_dir = dataset_dir 
    if not data_dir.exists():
        print(f"{Colors.RED}❌ Error: Data directory not found: {data_dir}{Colors.NC}")
        return False

    # Check DVC config in the selected dataset directory
    code, output = run_command('dvc remote list', cwd=dataset_dir, capture_output=True)
    print(f"{Colors.YELLOW}DVC remotes in {dataset_dir}:{Colors.NC}\n{output}")  # Debug print
    if 'storage' not in output:
        print(f"{Colors.RED}❌ Error: DVC remotes not configured in {dataset_dir}{Colors.NC}")
        print("Run option [1] Initial Setup first")
        return False

    # Step 2: List and select folders
    print(f"{Colors.YELLOW}[2/5] Listing available folders...{Colors.NC}")
    
    # Find folders with data
    available_folders = []
    folder_display = []
    
    for folder in sorted(data_dir.iterdir()):
        if folder.is_dir() and not folder.name.startswith('.'):
            file_count = len(list(folder.glob('**/*')))
            if file_count > 0:
                available_folders.append(folder.name)
                if (folder.with_suffix('.dvc')).exists():
                    folder_display.append(f"  [{len(available_folders)-1}] {folder.name} {Colors.GREEN}(already tracked, {file_count} files){Colors.NC}")
                else:
                    folder_display.append(f"  [{len(available_folders)-1}] {folder.name} {Colors.YELLOW}(not tracked, {file_count} files){Colors.NC}")
    
    if not available_folders:
        print(f"{Colors.RED}❌ No folders with data found{Colors.NC}")
        return False
    
    for display in folder_display:
        print(display)
    print("  [a] All folders")
    print()
    
    choice = input("Select folder(s) to upload (comma-separated numbers or 'a' for all): ").strip()
    
    selected_folders = []
    if choice.lower() == 'a':
        selected_folders = available_folders
    else:
        try:
            indices = [int(c.strip()) for c in choice.split(',')]
            for idx in indices:
                if 0 <= idx < len(available_folders):
                    selected_folders.append(available_folders[idx])
        except ValueError:
            print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
            return False
    
    if not selected_folders:
        print(f"{Colors.RED}❌ No valid folders selected{Colors.NC}")
        return False
    
    print(f"{Colors.GREEN}✅ Selected {len(selected_folders)} folder(s) for upload{Colors.NC}")
    print()

    # Step 2: Track folders with DVC
    print(f"{Colors.YELLOW}[2/7] Adding folders to DVC...{Colors.NC}")

    tracked_folders = []
    for folder in selected_folders:
        print(f"{Colors.CYAN}Processing: {folder}{Colors.NC}")
        print(f"  Running: dvc add {folder}")
        code, _ = run_command(f'dvc add "{folder}"', cwd=dataset_dir)
        if code == 0:
            print(f"  {Colors.GREEN}✅ Added {folder} to DVC{Colors.NC}")
            tracked_folders.append(folder)
        else:
            print(f"  {Colors.RED}❌ Failed to add {folder} to DVC{Colors.NC}")

    print()

    if not tracked_folders:
        print(f"{Colors.RED}❌ No folders were tracked{Colors.NC}")
        return False

    # Step 3: Stage .dvc files for Git
    print(f"{Colors.YELLOW}[3/7] Staging .dvc files and .gitignore for Git...{Colors.NC}")
    
    for folder in tracked_folders:
        dvc_file = data_dir / f'{folder}.dvc'
        if dvc_file.exists():
            print(f"  Running: git add {folder}.dvc")
            run_command(f'git add "{folder}.dvc"', cwd=data_dir)
    
    print("  Running: git add .gitignore")
    run_command('git add .gitignore', cwd=data_dir)
    
    print(f"{Colors.GREEN}✅ Files staged{Colors.NC}")
    print()

    # Step 4: Commit to Git
    print(f"{Colors.YELLOW}[4/7] Committing to Git...{Colors.NC}")
    
    commit_msg = input("Enter commit message for .dvc files: ").strip() or "Track data with DVC"
    
    code, output = run_command('git diff --cached --quiet', cwd=data_dir)
    if code == 0:
        print(f"{Colors.YELLOW}⚠️  No changes to commit{Colors.NC}")
    else:
        print(f"  Running: git commit -m \"{commit_msg}\"")
        code, _ = run_command(f'git commit -m "{commit_msg}"', cwd=data_dir)
        if code == 0:
            print(f"{Colors.GREEN}✅ Changes committed to Git{Colors.NC}")
        else:
            print(f"{Colors.RED}❌ Git commit failed{Colors.NC}")
            return False
    
    print()

    # Step 5: Copy .dvc files to dataset directory
    print(f"{Colors.YELLOW}[5/7] Copying .dvc files to dataset directory...{Colors.NC}")
    
    import shutil
    for folder in tracked_folders:
        src = data_dir / f'{folder}.dvc'
        dst = dataset_dir / f'{folder}.dvc'
        if src.exists():
            try:
                if src.resolve() != dst.resolve():
                    print(f"  Copying: {folder}.dvc -> {dataset_dir.relative_to(REPO_ROOT)}/")
                    shutil.copy(src, dst)
                else:
                    print(f"  Skipped copying {folder}.dvc (source and destination are the same)")
            except Exception as e:
                print(f"{Colors.RED}❌ Error copying {folder}.dvc: {e}{Colors.NC}")
    
    print(f"{Colors.GREEN}✅ .dvc files copied{Colors.NC}")
    print()

    # Step 6: Push data to DVC remote
    print(f"{Colors.YELLOW}[6/7] Pushing data to DVC remote...{Colors.NC}")
    print("This may take a while depending on data size...")
    print()
    
    push_failed = False
    for folder in tracked_folders:
        dvc_file = data_dir / f'{folder}.dvc'
        if dvc_file.exists():
            print(f"{Colors.CYAN}Pushing: {folder}{Colors.NC}")
            code, _ = run_command(f'dvc push "{dvc_file.name}"', cwd=dataset_dir)
            if code != 0:
                print(f"  {Colors.RED}❌ Failed to push {folder}{Colors.NC}")
                push_failed = True
            else:
                print(f"  {Colors.GREEN}✅ {folder} pushed to remote{Colors.NC}")
    
    if push_failed:
        print()
        print(f"{Colors.YELLOW}⚠️  Some files failed to push{Colors.NC}")
        print(f"{Colors.YELLOW}Possible reasons:{Colors.NC}")
        print("  • Your credentials may not have write permissions")
        print("  • Network connection issues")
        print("  • Google Drive quota exceeded")
        return False
    else:
        print()
        print(f"{Colors.GREEN}✅ All selected data pushed to DVC remote{Colors.NC}")
    
    print()

    # Step 7: Push .dvc files to Git
    print(f"{Colors.YELLOW}[7/7] Pushing .dvc files to Git remote...{Colors.NC}")
    
    # Stage .dvc files in dataset directory
    for folder in tracked_folders:
        dvc_file = dataset_dir / f'{folder}.dvc'
        if dvc_file.exists():
            rel_path = dvc_file.relative_to(REPO_ROOT)
            print(f"  Running: git add {rel_path}")
            run_command(f'git add "{rel_path}"', cwd=DATASET_GIT_ROOT)
    
    # Commit if there are changes
    code, _ = run_command('git diff --cached --quiet', cwd=DATASET_GIT_ROOT)
    if code == 0:
        print(f"{Colors.YELLOW}⚠️  No new .dvc files to commit in dataset directory{Colors.NC}")
    else:
        print(f"  Running: git commit -m \"Add .dvc files to {selected_dataset}\"")
        code, _ = run_command(f'git commit -m "Add .dvc files to {selected_dataset}"', cwd=VesselVerse-Dataset)
        if code == 0:
            print(f"{Colors.GREEN}✅ .dvc files committed{Colors.NC}")
    
    # Push to Git
    print("  Running: git push")
    code, _ = run_command('git push', cwd=DATASET_GIT_ROOT)
    if code == 0:
        print(f"{Colors.GREEN}✅ Pushed to Git remote{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Git push failed. Push manually later with: git push{Colors.NC}")
    
    print()

    # Summary
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.GREEN}          Upload Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Upload Summary:{Colors.NC}")
    print(f"  Source Directory:  {Colors.GREEN}VESSELVERSE_DATA_IXI/data{Colors.NC}")
    print(f"  Dataset Directory: {Colors.GREEN}{dataset_dir.relative_to(REPO_ROOT)}{Colors.NC}")
    print(f"  Folders Uploaded:  {Colors.GREEN}{len(tracked_folders)}{Colors.NC}")
    for folder in tracked_folders:
        print(f"    • {folder}")
    print()
    print(f"{Colors.BLUE}What happened:{Colors.NC}")
    print(f"  ✅ Data tracked with DVC (created .dvc files)")
    print(f"  ✅ .dvc files and .gitignore committed to Git")
    print(f"  ✅ Data pushed to DVC remote storage")
    print(f"  ✅ .dvc files pushed to Git remote")
    print()
    print(f"{Colors.CYAN}Collaborators can now:{Colors.NC}")
    print(f"  1. Run: git pull")
    print(f"  2. Organize data (using notebook)")
    print(f"  3. Run: dvc pull")
    print()
    
    return True


######## Function 4: Review User Uploads

def owner_review_user_uploads():
    """Review user uploads - download from uploads remote"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}   Review User Uploads - Owner Mode                {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()

    # Load config
    config = VesselVerseConfig()
    
    # Check DVC config
    code, output = run_command('dvc remote list', cwd=REPO_ROOT, capture_output=True)
    if 'uploads' not in output:
        print(f"{Colors.RED}❌ Error: Uploads remote not configured{Colors.NC}")
        print("Run option [1] Initial Setup first")
        return False
    
    user_upload_id = config.get('user_upload_ID', '')
    
    print(f"{Colors.YELLOW}ℹ️  Review Information{Colors.NC}")
    print(f"  This will download data that users have uploaded to the shared folder.")
    print(f"  Download source: {Colors.CYAN}uploads (gdrive://{user_upload_id}){Colors.NC}")
    print()

    data_dir = REPO_ROOT / 'VESSELVERSE_DATA_IXI' / 'data'

    # Step 1: Update Git
    print(f"{Colors.YELLOW}[1/3] Updating Git repository (to get .dvc pointer files)...{Colors.NC}")
    code, _ = run_command('git pull', cwd=REPO_ROOT)
    if code == 0:
        print(f"{Colors.GREEN}✅ Git repository updated{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Git pull had issues, continuing anyway...{Colors.NC}")
    print()

    # Step 2: Restore deleted .dvc files
    print(f"{Colors.YELLOW}[2/3] Restoring .dvc files if needed...{Colors.NC}")
    
    code, output = run_command('git status --short', cwd=data_dir, capture_output=True)
    deleted_dvc = output.count('.dvc')
    if deleted_dvc > 0:
        print(f"  Restoring {deleted_dvc} deleted .dvc file(s)...")
        run_command('git restore *.dvc', cwd=data_dir)
        print(f"{Colors.GREEN}✅ .dvc files restored{Colors.NC}")
    else:
        print(f"{Colors.GREEN}✅ All .dvc files present{Colors.NC}")
    
    # Count .dvc files
    dvc_count = len(list(data_dir.glob('*.dvc')))
    print(f"  Found {dvc_count} tracked item(s)")
    print()

    # Step 3: Pull from uploads remote
    print(f"{Colors.YELLOW}[3/3] Downloading from user uploads remote...{Colors.NC}")
    print(f"Pulling from remote: {Colors.CYAN}uploads (gdrive://{user_upload_id}){Colors.NC}")
    print("This may take a while depending on data size...")
    print()
    
    code, _ = run_command('dvc pull -r uploads', cwd=REPO_ROOT)
    
    print()

    # Summary
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    if code == 0:
        print(f"{Colors.GREEN}          Download Complete! 🎉{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}          Download Finished{Colors.NC}")
        print(f"{Colors.YELLOW}  (Some files may only exist in main storage, not uploads){Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Review Summary:{Colors.NC}")
    print(f"  Source Remote:     {Colors.CYAN}uploads (gdrive://{user_upload_id}){Colors.NC}")
    print(f"  Destination:       {Colors.GREEN}VESSELVERSE_DATA_IXI/data{Colors.NC}")
    print()
    print(f"{Colors.YELLOW}ℹ️  Note:{Colors.NC}")
    print(f"  Only files that users uploaded to 'uploads' remote will be downloaded.")
    print(f"  Files that only exist in main 'storage' will show as errors (this is normal).")
    print()
    print(f"{Colors.YELLOW}ℹ️  Next steps:{Colors.NC}")
    print(f"  • Review the downloaded data in VESSELVERSE_DATA_IXI/data")
    print(f"  • If approved, use option [3] Upload Dataset to push to main storage")
    print()
    
    return True


######## Main Menu

def owner_main():
    """Main menu loop"""
    # Setup virtual environment first
    if not setup_virtual_environment():
        print(f"{Colors.RED}Failed to setup virtual environment. Exiting...{Colors.NC}")
        sys.exit(1)
    
    display_header()
    
    while True:
        print()
        show_menu()
        
        choice = input("Enter your choice [1-5]: ").strip()
        
        if choice == '1':
            initial_owner_setup()
        elif choice == '2':
            owner_update_dataset()
        elif choice == '3':
            owner_upload_dataset()
        elif choice == '4':
            owner_review_user_uploads()
        elif choice == '5':
            print(f"{Colors.BLUE}Goodbye!{Colors.NC}")
            sys.exit(0)
        else:
            print(f"{Colors.RED}Invalid option. Please select 1-5{Colors.NC}")
        
        print()
        input("Press Enter to continue...")


if __name__ == '__main__':
    owner_main()
