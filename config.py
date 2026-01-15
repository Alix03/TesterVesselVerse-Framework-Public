#!/usr/bin/env python3
"""
VesselVerse Configuration
Cross-platform configuration for VesselVerse dataset management.
Replaces config.sh for better Windows/macOS/Linux compatibility.
"""

import os
import platform
import sys
from pathlib import Path
import json

# ═══════════════════════════════════════════════════════════════════════════
# Cross-Platform Configuration
# ═══════════════════════════════════════════════════════════════════════════

class VesselVerseConfig:
    """Configuration class for VesselVerse project"""
    
    def __init__(self, config_file=None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to custom config file
        """
        # Repository root (portable across machines)
        if config_file:
            self.REPO_ROOT = Path(config_file).parent.resolve()
        else:
            self.REPO_ROOT = Path(__file__).parent.resolve()
        
        # Detect OS and set Slicer path
        self._detect_slicer_path()
        
        # Credentials
        self.CREDENTIALS_DIR = self.REPO_ROOT / "credentials"
        self.owner_auth_path = self.CREDENTIALS_DIR / "vesselverse25-9f62c69233a4.json"
        self.user_auth_path = self.CREDENTIALS_DIR / "vesselverse25-141593c63cd7.json"
        
        # Dataset configuration
        self.DATASET_NAME = 'Prova'
        self.DATASET_GIT_ROOT = self.REPO_ROOT / "VesselVerse-Dataset"
        self.DATASET_PATH = self.DATASET_GIT_ROOT / "datasets" / f"D-{self.DATASET_NAME}"
        
        # Virtual environment
        self.VENV_ROOT = self.DATASET_GIT_ROOT
        self.VENV_PATH = self.VENV_ROOT / ".venv"
        
        # Google Drive folder IDs
        self.database_ID = '1qzVGvHThjVuZ9n7k1jNOBjOa2wPM4LZi'
        self.user_upload_ID = '1qzVGvHThjVuZ9n7k1jNOBjOa2wPM4LZi'
        
        # Testing ID (temporary - used for all datasets during development)
        self.TESTING_ID = '1qzVGvHThjVuZ9n7k1jNOBjOa2wPM4LZi'
        
        # Dataset storage mapping
        self._setup_dataset_storage()
        
    def _detect_slicer_path(self):
        """Auto-detect 3D Slicer installation path based on OS"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            self.SLICER_PATH = Path("/Applications/Slicer.app/Contents/MacOS/Slicer")
        elif system == "Linux":
            # Try common locations
            possible_paths = [
                Path.home() / "Slicer-5.6.2-linux-amd64" / "Slicer",
                Path("/opt/Slicer/Slicer"),
                Path.home() / "Slicer" / "Slicer"
            ]
            self.SLICER_PATH = next((p for p in possible_paths if p.exists()), possible_paths[0])
        elif system == "Windows":
            # Windows paths
            possible_paths = [
                Path("C:/Program Files/Slicer 5.6/Slicer.exe"),
                Path("C:/Program Files/Slicer/Slicer.exe"),
                Path.home() / "AppData/Local/Slicer/Slicer.exe"
            ]
            self.SLICER_PATH = next((p for p in possible_paths if p.exists()), possible_paths[0])
        else:
            # Fallback
            self.SLICER_PATH = Path.home() / "Slicer" / "Slicer"
    
    def _setup_dataset_storage(self):
        """Setup storage IDs for all datasets"""
        # IXI Dataset
        self.IXI_STORAGE_ID = self.TESTING_ID
        # Production IDs (commented for future use):
        # self.IXI_STORAGE_ID = '1Lt5rGwBPkmdXGeGmpNKrzZ07xJzY_yYv'
        # IXI_UPLOAD_IDS: 
        #   BravePanda='1OzAuvCBUkH2Lt4HOBxmEPmdYR1H88C-Y'
        #   SwiftCheetah='1PoD3eV41h_EWb1uDuMNGlfIUg8gi5_8a'
        #   SilentOwl='1dgXeYwaOxKeS1NGJSBCzatk8l1Qwmh8q'
        
        # COW23MR Dataset
        self.COW23MR_STORAGE_ID = self.TESTING_ID
        # Production IDs (commented for future use):
        # self.COW23MR_STORAGE_ID = '1jBDBZb8MNNXpGGWe0nTeOLlK_KIIW60p'
        # COW23MR_UPLOAD_IDS:
        #   BravePanda='1HaOSkx8ANp9S-mzSh-XJ56ZapTBsHCDX'
        #   SwiftCheetah='1mdgCXcgNuLtP6YkCNyWbkNCbPiG0AHzZ'
        #   SilentOwl='1ObMn6yrPPnw4Ua8OYFt34ct7lcakK1OU'
        
        # ITKTubeTK Dataset
        self.ITKTubeTK_STORAGE_ID = self.TESTING_ID
        
        # Prova Dataset
        self.Prova_STORAGE_ID = self.TESTING_ID
        self.Prova_UPLOAD_ID = self.TESTING_ID
        
        # Prova2 Dataset
        self.Prova2_STORAGE_ID = self.TESTING_ID
        self.Prova2_UPLOAD_ID = self.TESTING_ID
    
    def get_dataset_path(self, dataset_name):
        """
        Get path for a specific dataset.
        
        Args:
            dataset_name: Name of dataset (e.g., 'IXI', 'COW23MR')
            
        Returns:
            Path object to dataset directory
        """
        return self.DATASET_GIT_ROOT / "datasets" / f"D-{dataset_name}"
    
    def get_storage_id(self, dataset_name):
        """
        Get Google Drive storage ID for a dataset.
        
        Args:
            dataset_name: Name of dataset (e.g., 'IXI', 'COW23MR')
            
        Returns:
            Storage folder ID string
        """
        attr_name = f"{dataset_name}_STORAGE_ID"
        return getattr(self, attr_name, self.TESTING_ID)
    
    def to_dict(self):
        """Export configuration as dictionary"""
        return {
            'REPO_ROOT': str(self.REPO_ROOT),
            'SLICER_PATH': str(self.SLICER_PATH),
            'DATASET_NAME': self.DATASET_NAME,
            'DATASET_PATH': str(self.DATASET_PATH),
            'VENV_PATH': str(self.VENV_PATH),
            'owner_auth_path': str(self.owner_auth_path),
            'user_auth_path': str(self.user_auth_path),
            'database_ID': self.database_ID,
            'user_upload_ID': self.user_upload_ID,
            'TESTING_ID': self.TESTING_ID,
            'IXI_STORAGE_ID': self.IXI_STORAGE_ID,
            'COW23MR_STORAGE_ID': self.COW23MR_STORAGE_ID,
            'ITKTubeTK_STORAGE_ID': self.ITKTubeTK_STORAGE_ID,
            'Prova_STORAGE_ID': self.Prova_STORAGE_ID,
            'Prova2_STORAGE_ID': self.Prova2_STORAGE_ID
        }
    
    def to_shell_exports(self):
        """
        Export configuration as shell export statements.
        Useful for sourcing in bash scripts.
        
        Returns:
            String with export statements
        """
        exports = []
        for key, value in self.to_dict().items():
            exports.append(f'export {key}="{value}"')
        return '\n'.join(exports)
    
    def save_json(self, output_path=None):
        """
        Save configuration to JSON file.
        
        Args:
            output_path: Optional output path, defaults to config.json in repo root
        """
        if output_path is None:
            output_path = self.REPO_ROOT / "config.json"
        
        with open(output_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def update_dataset(self, dataset_name):
        """
        Update current dataset configuration.
        
        Args:
            dataset_name: Name of dataset to switch to
        """
        self.DATASET_NAME = dataset_name
        self.DATASET_PATH = self.DATASET_GIT_ROOT / "datasets" / f"D-{dataset_name}"
    
    def validate(self):
        """
        Validate configuration.
        
        Returns:
            Tuple of (is_valid, errors_list)
        """
        errors = []
        
        # Check if credentials exist
        if not self.owner_auth_path.exists():
            errors.append(f"Owner credentials not found: {self.owner_auth_path}")
        if not self.user_auth_path.exists():
            errors.append(f"User credentials not found: {self.user_auth_path}")
        
        # Check if dataset directory exists
        if not self.DATASET_GIT_ROOT.exists():
            errors.append(f"Dataset root not found: {self.DATASET_GIT_ROOT}")
        
        # Check if Slicer exists (warning, not error)
        if not self.SLICER_PATH.exists():
            errors.append(f"WARNING: Slicer not found at: {self.SLICER_PATH}")
        
        return (len(errors) == 0, errors)


# ═══════════════════════════════════════════════════════════════════════════
# CLI Interface
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Command-line interface for config.py"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VesselVerse Configuration')
    parser.add_argument('--export-shell', action='store_true',
                       help='Export as shell variables (for sourcing in bash)')
    parser.add_argument('--export-json', type=str, metavar='FILE',
                       help='Export as JSON to specified file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate configuration')
    parser.add_argument('--get', type=str, metavar='KEY',
                       help='Get specific configuration value')
    parser.add_argument('--dataset', type=str, metavar='NAME',
                       help='Set active dataset name')
    
    args = parser.parse_args()
    
    # Initialize config
    config = VesselVerseConfig()
    
    # Handle dataset switch
    if args.dataset:
        config.update_dataset(args.dataset)
    
    # Handle commands
    if args.export_shell:
        print(config.to_shell_exports())
    elif args.export_json:
        config.save_json(args.export_json)
        print(f"✅ Configuration exported to {args.export_json}")
    elif args.validate:
        is_valid, errors = config.validate()
        if is_valid:
            print("✅ Configuration is valid")
            sys.exit(0)
        else:
            print("❌ Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    elif args.get:
        value = getattr(config, args.get, None)
        if value is None:
            print(f"❌ Unknown configuration key: {args.get}", file=sys.stderr)
            sys.exit(1)
        print(value)
    else:
        # Default: print summary
        print("VesselVerse Configuration")
        print("=" * 50)
        print(f"Repository Root: {config.REPO_ROOT}")
        print(f"Slicer Path: {config.SLICER_PATH}")
        print(f"Current Dataset: {config.DATASET_NAME}")
        print(f"Dataset Path: {config.DATASET_PATH}")
        print(f"Virtual Env: {config.VENV_PATH}")
        print("\nValidation:")
        is_valid, errors = config.validate()
        if is_valid:
            print("  ✅ Configuration is valid")
        else:
            print("  ❌ Errors found:")
            for error in errors:
                print(f"    - {error}")


if __name__ == "__main__":
    main()
