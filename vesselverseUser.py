#!/usr/bin/env python3

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Tuple
from config import VesselVerseConfig
from vv_utils import Colors, get_repo_root, get_venv_path, get_venv_python, setup_virtual_environment, run_command, check_prerequisites, configure_credentials, configure_dvc_remotes


# Get repo root
REPO_ROOT = get_repo_root()
DATASET_GIT_ROOT = REPO_ROOT / "VesselVerse-Dataset"
VENV_ROOT = DATASET_GIT_ROOT
VENV_PATH = get_venv_path(REPO_ROOT)


def display_header():
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
    print("  [4] Create Pull Request - Request owner review of your D-Expert data")
    print("  [5] Exit\n")


def user_initial_setup():
    """Function 1: Initial Setup"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Initial Setup - First Time Configuration        {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}[1/4] Checking prerequisites...{Colors.NC}")
    print()
    if not check_prerequisites(VENV_PATH, REPO_ROOT):
        return
    
    datasets_dir = DATASET_GIT_ROOT / "datasets"


    print(f"{Colors.YELLOW}[2/4] Configuring user credentials...{Colors.NC}")
    print()

    success, config = configure_credentials()
    if not success:
        return
    
    print(f"{Colors.YELLOW}[3/4] Configuring user folder...{Colors.NC}")
    print()
    expert_dir = datasets_dir / "D-Expert"
    if not expert_dir.exists():
        expert_dir.mkdir(parents=True)
        print(f"{Colors.GREEN}✅ Cartella personale D-Expert creata: {expert_dir}{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}ℹ️ Cartella D-Expert già esistente: {expert_dir}{Colors.NC}")

    # Ask User for the Google Drive ID for D-Expert
    print(f"\n{Colors.CYAN}Inserisci l'ID della cartella Google Drive per D-Expert:{Colors.NC}")
    print(f"{Colors.YELLOW}(Questa cartella verrà usata per upload e download dei tuoi dati){Colors.NC}")
    print(f"{Colors.YELLOW}L'ID deve essere in formato base64url (25-50 caratteri: a-z, A-Z, 0-9, _, -){Colors.NC}")
    
    import re
    gdrive_id_pattern = re.compile(r'^[a-zA-Z0-9_-]{25,50}$')
    
    while True:
        gdrive_id = input("ID GDrive D-Expert: ").strip()
        if not gdrive_id:
            print(f"{Colors.YELLOW}⚠️  No ID inserted for D-Expert. Remote uploads won't be configured.{Colors.NC}")
            break
        
        # Validate ID format
        if gdrive_id_pattern.match(gdrive_id):
            vv_config = VesselVerseConfig()
            # Save ID for both storage and uploads (D-Expert uses same ID for both)
            vv_config.set_storage_id('Expert', gdrive_id, save=False, is_upload=False)
            vv_config.set_storage_id('Expert', gdrive_id, save=True, is_upload=True)
            print(f"{Colors.GREEN}✅ ID GDrive for D-Expert saved!{Colors.NC}")
            # Reload config to include the newly saved IDs
            config = VesselVerseConfig()
            break
        else:
            print(f"{Colors.RED}❌ ID non valido! Deve essere formato base64url (25-50 caratteri).{Colors.NC}")
            print(f"{Colors.YELLOW}Esempio: 1Lt5rGwBPkmdXGeGmpNKrzZ07xJzY_yYv{Colors.NC}")
            retry = input("Vuoi riprovare? [s/n]: ").strip().lower()
            if retry != 's':
                print(f"{Colors.YELLOW}⚠️  Setup interrotto. Remote uploads non configurato.{Colors.NC}")
                break
    
    print()

    print(f"{Colors.YELLOW}[4/4] Configuring dvc remotes...{Colors.NC}")
    print()

    if not configure_dvc_remotes(config, datasets_dir):
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
    
    # Load config
    config = VesselVerseConfig()
    venv_python = str(get_venv_python(VENV_PATH))

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

    # Update the ID storage based on the selected dataset
    dataset_name = selected_dataset.replace('D-', '')
    storage_id = config.get_storage_id(dataset_name)
    run_command(f'"{venv_python}" -m dvc remote modify storage url gdrive://{storage_id}', cwd=dataset_dir)

    # Check DVC config in the selected dataset directory
    code, output = run_command(f'"{venv_python}" -m dvc remote list', cwd=dataset_dir, capture_output=True)
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
        code, _ = run_command(f'"{venv_python}" -m dvc pull "{dvc_file.name}"', cwd=dataset_dir)
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

def user_upload_data():
    """Function 3: Upload Data - Upload to D-Expert personal folder"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Upload Data - User Mode (D-Expert)             {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    # Load config
    config = VesselVerseConfig()
    venv_python = str(get_venv_python(VENV_PATH))
    
    # Step 1: Use D-Expert dataset (user's personal folder)
    dataset_base = DATASET_GIT_ROOT / 'datasets'
    selected_dataset = "D-Expert"
    dataset_dir = dataset_base / selected_dataset
    
    print(f"{Colors.YELLOW}[1/5] Checking D-Expert configuration...{Colors.NC}")
    
    # Check if D-Expert exists
    if not dataset_dir.exists():
        print(f"{Colors.RED}❌ Error: D-Expert directory not found: {dataset_dir}{Colors.NC}")
        print("Run option [1] Initial Setup first to configure D-Expert")
        return False
    
    print(f"{Colors.GREEN}✓ Using dataset: {selected_dataset} (your personal folder){Colors.NC}")
    
    # Check DVC config in D-Expert directory
    code, output = run_command(f'"{venv_python}" -m dvc remote list', cwd=dataset_dir, capture_output=True)
    
    if 'storage' not in output or 'uploads' not in output:
        print(f"{Colors.RED}❌ Error: DVC remotes not configured in {dataset_dir}{Colors.NC}")
        print(f"{Colors.YELLOW}Current remotes:{Colors.NC}\n{output}")
        print("Run option [1] Initial Setup first to configure DVC remotes")
        return False
    
    # Verify Expert ID is configured (check if attribute exists, not if it equals TESTING_ID)
    if not hasattr(config, 'Expert_STORAGE_ID'):
        print(f"{Colors.RED}❌ Error: D-Expert Google Drive ID not configured{Colors.NC}")
        print("Run option [1] Initial Setup first to set your personal Google Drive ID")
        return False
    
    expert_storage_id = config.get_storage_id("Expert")
    print(f"{Colors.GREEN}✓ DVC remotes configured correctly{Colors.NC}")
    print(f"{Colors.GREEN}✓ Upload ID: {expert_storage_id[:20]}...{Colors.NC}")
    print()

    # Use D-Expert as data directory
    data_dir = dataset_dir

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
        print(f"{Colors.CYAN}ℹ️  D-Expert is currently empty - no folders to upload.{Colors.NC}")
        print(f"\n{Colors.YELLOW}To upload data, you need to:{Colors.NC}")
        print(f"  1. Create folders inside: {Colors.GREEN}{dataset_dir}{Colors.NC}")
        print(f"  2. Add your files to those folders")
        print(f"  3. Run this upload option again")
        print(f"\n{Colors.CYAN}Example structure:{Colors.NC}")
        print(f"  D-Expert/")
        print(f"  ├── MyAnnotations/      ← Your segmentation results")
        print(f"  │   ├── case001.nii.gz")
        print(f"  │   └── case002.nii.gz")
        print(f"  └── MyExperiments/      ← Your analysis data")
        print(f"      └── results.csv")
        return True
    
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
        code, _ = run_command(f'"{venv_python}" -m dvc add "{folder}"', cwd=dataset_dir)
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
            code, output = run_command(f'"{venv_python}" -m dvc push "{dvc_file.name}"', cwd=dataset_dir, capture_output=True)
            if code != 0:
                if "403" in output or "insufficient rights" in output.lower():
                    print(f"  {Colors.RED}❌ Failed to push {folder}: Insufficient Rights (errore 403).{Colors.NC}")
                    print(f"  {Colors.YELLOW}Please verify that you have the correct permissions for the remote control or contact your administrator.{Colors.NC}")
                else:
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
            rel_path = dvc_file.relative_to(DATASET_GIT_ROOT)
            print(f"  Running: git add {rel_path}")
            run_command(f'git add "{rel_path}"', cwd=DATASET_GIT_ROOT)
    
    # Commit if there are changes
    code, _ = run_command('git diff --cached --quiet', cwd=DATASET_GIT_ROOT)
    if code == 0:
        print(f"{Colors.YELLOW}⚠️  No new .dvc files to commit in dataset directory{Colors.NC}")
    else:
        print(f"  Running: git commit -m \"Add .dvc files to {selected_dataset}\"")
        code, _ = run_command(f'git commit -m "Add .dvc files to {selected_dataset}"', cwd=DATASET_GIT_ROOT)
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
    print(f"Your modifications are ready for owner review!")


def create_pull_request():
    """Function 4: Create Pull Request for D-Expert folder"""
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}   Create Pull Request - Submit D-Expert for Review  {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    
    print(f"{Colors.YELLOW}ℹ️  This will create a Pull Request with your D-Expert modifications{Colors.NC}")
    print(f"{Colors.YELLOW}   The owner will review your data before merging it into the official dataset.{Colors.NC}\n")
    
    # Step 1: Check if we're in a forked repository
    print(f"{Colors.YELLOW}[1/6] Checking repository status...{Colors.NC}")
    
    code, remote_output = run_command('git remote -v', cwd=DATASET_GIT_ROOT, capture_output=True)
    if code != 0:
        print(f"{Colors.RED}❌ Failed to check git remotes{Colors.NC}")
        return False
    
    # Check if origin points to a fork (not the main repo)
    lines = remote_output.strip().split('\n')
    origin_url = None
    for line in lines:
        if line.startswith('origin') and '(push)' in line:
            origin_url = line.split()[1]
            break
    
    if not origin_url:
        print(f"{Colors.RED}❌ Could not find origin remote{Colors.NC}")
        return False
    
    print(f"  Repository URL: {origin_url}")
    
    # Extract owner and repo name from URL
    import re
    # Match both HTTPS and SSH URLs
    github_pattern = r'github\.com[:/]([^/]+)/([^/\.]+)'
    match = re.search(github_pattern, origin_url)
    
    if not match:
        print(f"{Colors.RED}❌ This doesn't appear to be a GitHub repository{Colors.NC}")
        return False
    
    repo_owner = match.group(1)
    repo_name = match.group(2)
    
    print(f"  Owner: {Colors.CYAN}{repo_owner}{Colors.NC}")
    print(f"  Repo: {Colors.CYAN}{repo_name}{Colors.NC}")
    print(f"{Colors.GREEN}✅ Repository detected{Colors.NC}\n")
    
    # Step 2: Check for uncommitted changes
    print(f"{Colors.YELLOW}[2/6] Checking for uncommitted changes...{Colors.NC}")
    expert_dir = DATASET_GIT_ROOT / "datasets" / "D-Expert"
    
    code, status_output = run_command('git status --porcelain', cwd=expert_dir, capture_output=True)
    if status_output.strip():
        print(f"{Colors.YELLOW}⚠️  You have uncommitted changes in D-Expert{Colors.NC}")
        print(f"\nUncommitted files:")
        print(status_output)
        print()
        commit_now = input("Do you want to commit them now? [y/n]: ").strip().lower()
        if commit_now == 'y':
            commit_msg = input("Enter commit message: ").strip() or "Update D-Expert annotations"
            run_command(f'git add .', cwd=expert_dir)
            code, _ = run_command(f'git commit -m "{commit_msg}"', cwd=expert_dir)
            if code == 0:
                print(f"{Colors.GREEN}✅ Changes committed{Colors.NC}\n")
            else:
                print(f"{Colors.RED}❌ Commit failed{Colors.NC}")
                return False
        else:
            print(f"{Colors.YELLOW}⚠️  Please commit your changes first, then run this option again{Colors.NC}")
            return False
    else:
        print(f"{Colors.GREEN}✅ No uncommitted changes{Colors.NC}\n")
    
    # Step 3: Create a new branch for the PR
    print(f"{Colors.YELLOW}[3/6] Creating pull request branch...{Colors.NC}")
    
    # Generate branch name with timestamp
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    branch_name = f"expert-submission-{timestamp}"
    
    # Check current branch
    code, current_branch = run_command('git branch --show-current', cwd=DATASET_GIT_ROOT, capture_output=True)
    current_branch = current_branch.strip()
    
    # Create and checkout new branch
    code, _ = run_command(f'git checkout -b {branch_name}', cwd=DATASET_GIT_ROOT)
    if code != 0:
        print(f"{Colors.RED}❌ Failed to create branch{Colors.NC}")
        return False
    
    print(f"  Created branch: {Colors.CYAN}{branch_name}{Colors.NC}")
    print(f"{Colors.GREEN}✅ Branch created{Colors.NC}\n")
    
    # Step 4: Push branch to fork
    print(f"{Colors.YELLOW}[4/6] Pushing branch to your fork...{Colors.NC}")
    print(f"  This may take a moment...\n")
    
    code, _ = run_command(f'git push -u origin {branch_name}', cwd=DATASET_GIT_ROOT)
    if code != 0:
        print(f"{Colors.RED}❌ Failed to push branch{Colors.NC}")
        print(f"{Colors.YELLOW}⚠️  Switching back to {current_branch}{Colors.NC}")
        run_command(f'git checkout {current_branch}', cwd=DATASET_GIT_ROOT)
        return False
    
    print(f"{Colors.GREEN}✅ Branch pushed to fork{Colors.NC}\n")
    
    # Step 5: Get upstream repository info
    print(f"{Colors.YELLOW}[5/6] Checking upstream repository...{Colors.NC}")
    
    code, upstream_output = run_command('git remote -v', cwd=DATASET_GIT_ROOT, capture_output=True)
    upstream_url = None
    upstream_owner = None
    upstream_repo = None
    
    for line in upstream_output.strip().split('\n'):
        if line.startswith('upstream') and '(push)' in line:
            upstream_url = line.split()[1]
            match = re.search(github_pattern, upstream_url)
            if match:
                upstream_owner = match.group(1)
                upstream_repo = match.group(2)
            break
    
    # If no upstream, try to detect from common patterns or ask user
    if not upstream_owner:
        print(f"{Colors.YELLOW}⚠️  No upstream remote configured{Colors.NC}")
        print(f"\n{Colors.CYAN}Enter the original repository owner (the repo you forked from):{Colors.NC}")
        upstream_owner = input("Owner (e.g., 'Alix03'): ").strip()
        upstream_repo = repo_name  # Assume same repo name
        
        if not upstream_owner:
            print(f"{Colors.RED}❌ Upstream owner required{Colors.NC}")
            return False
    
    print(f"  Upstream: {Colors.CYAN}{upstream_owner}/{upstream_repo}{Colors.NC}")
    print(f"{Colors.GREEN}✅ Upstream identified{Colors.NC}\n")
    
    # Step 6: Create Pull Request
    print(f"{Colors.YELLOW}[6/6] Creating Pull Request...{Colors.NC}\n")
    
    # Try using GitHub CLI if available
    code, gh_version = run_command('gh --version', capture_output=True)
    
    if code == 0:
        print(f"{Colors.GREEN}✓ GitHub CLI detected{Colors.NC}")
        print(f"\n{Colors.CYAN}Enter Pull Request details:{Colors.NC}")
        pr_title = input("Title (default: 'D-Expert Submission for Review'): ").strip() or "D-Expert Submission for Review"
        pr_body = input("Description (optional): ").strip() or "Submitting my D-Expert annotations for review and potential inclusion in the official dataset."
        
        print(f"\n{Colors.YELLOW}Creating PR...{Colors.NC}")
        pr_command = f'gh pr create --base main --head {repo_owner}:{branch_name} --title "{pr_title}" --body "{pr_body}" --repo {upstream_owner}/{upstream_repo}'
        
        code, pr_output = run_command(pr_command, cwd=DATASET_GIT_ROOT, capture_output=True)
        
        if code == 0:
            print(f"\n{Colors.GREEN}✅ Pull Request created successfully!{Colors.NC}")
            print(f"\n{pr_output}")
        else:
            print(f"\n{Colors.YELLOW}⚠️  Could not create PR automatically{Colors.NC}")
            print(f"Error: {pr_output}")
            print(f"\n{Colors.CYAN}Please create the PR manually using this URL:{Colors.NC}")
            pr_url = f"https://github.com/{upstream_owner}/{upstream_repo}/compare/main...{repo_owner}:{branch_name}"
            print(f"{Colors.GREEN}{pr_url}{Colors.NC}")
    else:
        # GitHub CLI not available - branch pushed, PR must be created manually
        print(f"{Colors.GREEN}✅ Branch pushed successfully!{Colors.NC}\n")
        print(f"{Colors.CYAN}GitHub will display a banner on YOUR fork page:{Colors.NC}")
        print(f"  '{branch_name} had recent pushes'")
        print(f"  {Colors.GREEN}[Compare & pull request]{Colors.NC} ← Green button\n")
        
        print(f"{Colors.YELLOW}⚠️  You must click the banner or use the URL to CREATE the pull request.{Colors.NC}")
        print(f"{Colors.YELLOW}   The owner will see your PR only after you create it.{Colors.NC}\n")
        
        print(f"{Colors.CYAN}Two ways to create the PR:{Colors.NC}")
        print(f"\n  Option 1: Visit your fork on GitHub and click the green banner button")
        print(f"  Option 2: Use this direct URL:")
        pr_url = f"https://github.com/{upstream_owner}/{upstream_repo}/compare/main...{repo_owner}:{branch_name}"
        print(f"    {Colors.GREEN}{pr_url}{Colors.NC}")
        print(f"\n  Both options will open a form to create the Pull Request.\n")
        
        print(f"{Colors.CYAN}For automatic PR creation in the future:{Colors.NC}")
        print(f"  Install GitHub CLI: brew install gh")
        print(f"  Authenticate: gh auth login\n")
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.GREEN}          Pull Request Prepared! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")
    print(f"{Colors.BLUE}Summary:{Colors.NC}")
    print(f"  Branch: {Colors.GREEN}{branch_name}{Colors.NC}")
    print(f"  Fork: {Colors.GREEN}{repo_owner}/{repo_name}{Colors.NC}")
    print(f"  Target: {Colors.GREEN}{upstream_owner}/{upstream_repo}{Colors.NC}")
    print(f"\n{Colors.YELLOW}Next steps:{Colors.NC}")
    print(f"  • The repository owner will review your D-Expert data")
    print(f"  • You'll be notified of any comments or requests for changes")
    print(f"  • Once approved, your data will be merged into the official dataset\n")
    
    return True


def main():
    """Main execution loop"""
    # Setup virtual environment first
    if not setup_virtual_environment(VENV_PATH, REPO_ROOT):
        print(f"{Colors.RED}Failed to setup virtual environment. Exiting...{Colors.NC}")
        sys.exit(1)
    
    display_header()
    
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
            create_pull_request()
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
