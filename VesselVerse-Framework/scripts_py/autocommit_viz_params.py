#!/usr/bin/env python3
"""
Auto-commit and push viz_params to Git
Used by Slicer module or as standalone script.

Usage:
    python3 autocommit_viz_params.py /path/to/D-IXI
    python3 autocommit_viz_params.py /path/to/D-IXI --push
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple


def git_add_viz_params(dataset_path: Path) -> Tuple[bool, str]:
    """
    Add viz_params/*.json to Git staging area.
    
    Returns:
        (success, message)
    """
    try:
        # Use pathlib to find all JSON files in viz_params
        viz_params_dir = dataset_path / "viz_params"
        if not viz_params_dir.exists():
            return False, f"❌ Directory not found: {viz_params_dir}"
        
        json_files = list(viz_params_dir.glob("*.json"))
        if not json_files:
            return False, "❌ No JSON files found in viz_params/"
        
        # Add files one by one (relative to dataset_path)
        for json_file in json_files:
            relative_path = json_file.relative_to(dataset_path)
            subprocess.run(
                ["git", "add", str(relative_path)],
                cwd=dataset_path,
                capture_output=True,
                text=True,
                check=True
            )
        
        return True, f"✅ {len(json_files)} file(s) added to Git"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Git add failed: {e.stderr}"


def git_commit_viz_params(dataset_path: Path, message: str = None) -> Tuple[bool, str]:
    """
    Commit viz_params changes.
    
    Returns:
        (success, message)
    """
    if message is None:
        message = "Update visualization parameters"
    
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=dataset_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            if "nothing to commit" in result.stdout:
                return True, "ℹ️ No changes to commit"
            else:
                return False, f"❌ Git commit failed: {result.stderr}"
        
        return True, "✅ Changes committed"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Git commit failed: {e}"


def git_push(dataset_path: Path) -> Tuple[bool, str]:
    """
    Push commits to remote.
    
    Returns:
        (success, message)
    """
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=dataset_path,
            capture_output=True,
            text=True,
            check=True
        )
        return True, "✅ Pushed to remote"
    except subprocess.CalledProcessError as e:
        return False, f"❌ Git push failed: {e.stderr}"


def autocommit_viz_params(dataset_path: str, push: bool = False) -> bool:
    """
    Auto-commit (and optionally push) viz_params.
    
    Args:
        dataset_path: Path to dataset directory (e.g., D-IXI)
        push: Whether to push after commit
        
    Returns:
        True if successful, False otherwise
    """
    dataset_path = Path(dataset_path)
    
    if not dataset_path.exists():
        print(f"❌ Dataset path not found: {dataset_path}")
        return False
    
    viz_params_dir = dataset_path / "viz_params"
    if not viz_params_dir.exists():
        print(f"❌ viz_params directory not found: {viz_params_dir}")
        return False
    
    print(f"📂 Working directory: {dataset_path}")
    print(f"📁 Target: viz_params/*.json")
    print()
    
    # Step 1: Git add
    print("[1/3] Adding files to Git...")
    success, message = git_add_viz_params(dataset_path)
    print(f"      {message}")
    if not success:
        return False
    
    # Step 2: Git commit
    print("[2/3] Committing changes...")
    success, message = git_commit_viz_params(dataset_path)
    print(f"      {message}")
    if not success:
        return False
    
    # Step 3: Git push (optional)
    if push:
        print("[3/3] Pushing to remote...")
        success, message = git_push(dataset_path)
        print(f"      {message}")
        if not success:
            return False
    else:
        print("[3/3] Skipping push (use --push to enable)")
    
    print()
    print("✅ Auto-commit complete!")
    return True


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Auto-commit visualization parameters to Git"
    )
    parser.add_argument(
        "dataset_path",
        type=str,
        help="Path to dataset directory (e.g., /path/to/D-IXI)"
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push commits to remote after committing"
    )
    parser.add_argument(
        "--message", "-m",
        type=str,
        default=None,
        help="Custom commit message"
    )
    
    args = parser.parse_args()
    
    success = autocommit_viz_params(args.dataset_path, args.push)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
