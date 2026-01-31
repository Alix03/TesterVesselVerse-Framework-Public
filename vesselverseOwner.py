#!/usr/bin/env python3

import os
import sys
import subprocess
import json

from pathlib import Path
from typing import List, Tuple, Optional
from config import VesselVerseConfig
from vv_utils import Colors, get_repo_root, get_venv_path, get_venv_python, setup_virtual_environment, run_command, check_prerequisites, configure_credentials, configure_dvc_remotes


# Use shared utility functions
REPO_ROOT = get_repo_root()
DATASET_GIT_ROOT = REPO_ROOT / "VesselVerse-Dataset"
VENV_ROOT = DATASET_GIT_ROOT
VENV_PATH = get_venv_path(REPO_ROOT)


def display_header():
    """Display script header"""
    print(f"\n{Colors.BLUE}{'='*55}{Colors.NC}")
    print(f"{Colors.BLUE}         VesselVerse Dataset Owner Manager          {Colors.NC}")
    print(f"{Colors.BLUE}{'='*55}{Colors.NC}\n")



def show_menu():
    """Display owner menu"""
    print(f"{Colors.CYAN}What would you like to do?{Colors.NC}")
    print()
    print("  [1] Initial Setup     - First time setup (configure credentials & download)")
    print("  [2] Update Dataset    - Sync latest changes from remote")
    print("  [3] Upload Dataset    - Push changes to the remote storage")
    print("  [4] Exit")
    print()


######## Function 1: Initial Setup

def initial_owner_setup():
    """Initial setup - configure credentials and DVC remotes"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}   Initial Setup - First Time Configuration        {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()

    # Step 1: Check prerequisites
    print(f"{Colors.YELLOW}[1/3] Checking prerequisites...{Colors.NC}")
    if not check_prerequisites(VENV_PATH, REPO_ROOT):
        return False
    print()

    # Step 2: Configure credentials
    print(f"{Colors.YELLOW}[2/3] Configuring user credentials...{Colors.NC}")

    success, config = configure_credentials()
    if not success:
        return False
    print()

    # Step 3: Initialize and configure DVC in each dataset
    print(f"{Colors.YELLOW}[3/3] Configuring dvc remotes...{Colors.NC}")

    datasets_dir = DATASET_GIT_ROOT / "datasets"
    if not configure_dvc_remotes(config, datasets_dir):
        return False
    
    
    # Summary
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.GREEN}          Owner Setup Complete! 🎉{Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()
    print(f"{Colors.BLUE}Configuration Summary:{Colors.NC}")
    print(f"  Credentials: {Colors.GREEN}{config.user_auth_path.name}{Colors.NC}")
    print(f"  Datasets configured with per-dataset storage IDs")
    print(f"    • IXI: {Colors.GREEN}{config.get_storage_id('IXI')[:20]}...{Colors.NC}")
    print(f"    • COW23MR: {Colors.GREEN}{config.get_storage_id('COW23MR')[:20]}...{Colors.NC}")
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
    venv_python = str(get_venv_python(VENV_PATH))

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

    # Update the ID storage based on the selected dataset
    dataset_name = selected_dataset.replace('D-', '')
    storage_id = config.get_storage_id(dataset_name)
    run_command(f'dvc remote modify storage url gdrive://{storage_id}', cwd=dataset_dir)

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


######## Function 3: Upload Dataset

def owner_upload_dataset():
    """Upload dataset changes - track with DVC and push to remote"""
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print(f"{Colors.BLUE}   Upload Dataset Changes - Owner Mode             {Colors.NC}")
    print(f"{Colors.BLUE}═══════════════════════════════════════════════════{Colors.NC}")
    print()

    # Load config
    config = VesselVerseConfig()
    venv_python = str(get_venv_python(VENV_PATH))
    
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

    # Update the ID storage based on the selected dataset
    dataset_name = selected_dataset.replace('D-', '')
    storage_id = config.get_storage_id(dataset_name)
    run_command(f'dvc remote modify storage url gdrive://{storage_id}', cwd=dataset_dir)

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
        code, _ = run_command(f'\"{venv_python}\" -m dvc add \"{folder}\"', cwd=dataset_dir)
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
            code, _ = run_command(f'\"{venv_python}\" -m dvc push \"{dvc_file.name}\"', cwd=dataset_dir)
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
    print(f"{Colors.CYAN}Collaborators can now:{Colors.NC}")
    print(f"  1. Run: git pull")
    print(f"  2. Organize data (using notebook)")
    print(f"  3. Run: dvc pull")
    print()
    
    return True


######## Main Menu

def owner_main():
    """Main menu loop"""
    # Setup virtual environment first
    if not setup_virtual_environment(VENV_PATH, REPO_ROOT):
        print(f"{Colors.RED}Failed to setup virtual environment. Exiting...{Colors.NC}")
        sys.exit(1)
    
    display_header()
    
    while True:
        print()
        show_menu()
        
        choice = input("Enter your choice [1-4]: ").strip()
        
        if choice == '1':
            initial_owner_setup()
        elif choice == '2':
            owner_update_dataset()
        elif choice == '3':
            owner_upload_dataset()
        elif choice == '4':
            print(f"{Colors.BLUE}Goodbye!{Colors.NC}")
            sys.exit(0)
        else:
            print(f"{Colors.RED}Invalid option. Please select 1-4{Colors.NC}")
        
        print()
        input("Press Enter to continue...")


if __name__ == '__main__':
    owner_main()
