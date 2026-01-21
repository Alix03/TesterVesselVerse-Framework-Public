from config import VesselVerseConfig
import sys
import subprocess
from pathlib import Path
from typing import Optional, Tuple


### ANSI Color codes
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

### Sets up DVC remotes

def configure_dvc_remotes(config: VesselVerseConfig, datasets_dir: Path = None) -> bool:
    """Sets up DVC remotes (Google Drive) for all datasets, 
        initializing DVC if needed and configuring storage/upload remotes using credentials."""
    if datasets_dir is None:
        repo_root = get_repo_root()
        datasets_dir = repo_root / 'VesselVerse-Dataset' / 'datasets'
    if not datasets_dir.exists():
        print(f"{Colors.RED}❌ Error: Datasets directory not found: {datasets_dir}{Colors.NC}")
        return False

    all_datasets = sorted([d for d in datasets_dir.glob('D-*') if d.is_dir()])
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
    user_auth_path = str(config.user_auth_path)

    venv_path = get_venv_path(get_repo_root())
    venv_python = str(get_venv_python(venv_path))

    for dataset_path in all_datasets:
        print(f"{Colors.CYAN}► Processing: {dataset_path.name}{Colors.NC}")
        dvc_dir = dataset_path / ".dvc"
        # Initialize DVC if not present
        if not dvc_dir.exists():
            code, _ = run_command(f'"{venv_python}" -m dvc init --no-scm', cwd=dataset_path)
            if code == 0:
                run_command(f'"{venv_python}" -m dvc config core.autostage true', cwd=dataset_path)
                print("  ✓ DVC initialized")
            else:
                print(f"  {Colors.RED}❌ Failed to initialize DVC{Colors.NC}")
                continue
        else:
            print("  ✓ DVC already initialized")

        # Remove existing remotes
        run_command(f'"{venv_python}" -m dvc remote remove storage', cwd=dataset_path)
        run_command(f'"{venv_python}" -m dvc remote remove uploads', cwd=dataset_path)

        # Add storage remote
        if database_id and user_auth_path:
            run_command(f'"{venv_python}" -m dvc remote add -d storage "gdrive://{database_id}"', cwd=dataset_path)
            run_command(f'"{venv_python}" -m dvc remote modify storage gdrive_service_account_json_file_path "{user_auth_path}"', cwd=dataset_path)
            run_command(f'"{venv_python}" -m dvc remote modify storage gdrive_use_service_account true', cwd=dataset_path)
            print("  ✓ Storage remote configured")

        # Add uploads remote
        if user_upload_id and user_auth_path:
            run_command(f'"{venv_python}" -m dvc remote add uploads "gdrive://{user_upload_id}"', cwd=dataset_path)
            run_command(f'"{venv_python}" -m dvc remote modify uploads gdrive_service_account_json_file_path "{user_auth_path}"', cwd=dataset_path)
            run_command(f'"{venv_python}" -m dvc remote modify uploads gdrive_use_service_account true', cwd=dataset_path)
            print("  ✓ Uploads remote configured")

        print()

    print(f"{Colors.GREEN}✅ All datasets configured{Colors.NC}")
    print()

    # Step 4: Verify setup
    print(f"{Colors.YELLOW}Verifying setup...{Colors.NC}")
    configured_count = 0
    for dataset_path in all_datasets:
        code, output = run_command(f'"{venv_python}" -m dvc remote list', cwd=dataset_path, capture_output=True)
        if "storage" in output:
            configured_count += 1
    if configured_count > 0:
        print(f"{Colors.GREEN}✅ {configured_count} dataset(s) configured with DVC remotes{Colors.NC}")
    else:
        print(f"{Colors.RED}❌ Error: No datasets configured{Colors.NC}")
        return False
    print()
    return True

###  Returns the root directory of the repository

def get_repo_root() -> Path:
    return Path(__file__).parent.resolve()

### Returns the path to the Python virtual environment in VesselVerse-Dataset

def get_venv_path(repo_root: Path) -> Path:
    return repo_root / "VesselVerse-Dataset" / ".venv"

### Returns the path to the Python executable in the virtual environment, handling OS differences

def get_venv_python(venv_path: Path) -> Path:
    if sys.platform == 'win32':
        return venv_path / 'Scripts' / 'python.exe'
    else:
        return venv_path / 'bin' / 'python'

### Runs a shell command and handles output

def run_command(cmd: str, cwd: Optional[Path] = None, capture_output: bool = False, repo_root: Optional[Path] = None) -> Tuple[int, str]:
    """
    Execute a shell command and return exit code and output
    Args:
        cmd: Command to execute
        cwd: Working directory for command
        capture_output: Whether to capture output
        repo_root: fallback working directory
    Returns:
        Tuple of (exit_code, output)
    """
    try:
        if isinstance(cmd, list):
            result = subprocess.run(
                cmd,
                shell=False,
                cwd=cwd or repo_root or get_repo_root(),
                capture_output=capture_output,
                text=True
            )
        else:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or repo_root or get_repo_root(),
                capture_output=capture_output,
                text=True
            )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode, out
    except Exception as e:
        print(f"{Colors.RED}❌ Error running command: {e}{Colors.NC}")
        return 1, str(e)

### Check if all required tools are installed

def check_prerequisites(venv_path: Path, repo_root: Path, get_venv_python_func=get_venv_python, run_command_func=run_command) -> bool:
    """Checks if Python, Git, DVC, and DVC gdrive support are installed, 
        installing DVC if missing"""
    print(f"{Colors.YELLOW}Checking prerequisites...{Colors.NC}")
    import sys
    # Check Python 3
    if sys.version_info < (3, 8):
        print(f"{Colors.RED}❌ Error: Python 3.8+ is required{Colors.NC}")
        return False
    # Check Git
    code, _ = run_command_func('git --version')
    if code != 0:
        print(f"{Colors.RED}❌ Error: Git is not installed{Colors.NC}")
        return False
    # Get venv python
    venv_python = get_venv_python_func(venv_path)
    # Check DVC in venv
    code, _ = run_command_func(f'"{venv_python}" -c "import dvc.cli"')
    if code != 0:
        print(f"{Colors.YELLOW}⚠️  DVC is not installed in venv. Installing now...{Colors.NC}")
        code, _ = run_command_func(f'"{venv_python}" -m pip install "dvc[gdrive]"')
        if code != 0:
            print(f"{Colors.RED}❌ Failed to install DVC{Colors.NC}")
            return False
    # Check DVC gdrive support
    code, _ = run_command_func(f'"{venv_python}" -c "import dvc_gdrive"')
    if code != 0:
        print(f"{Colors.YELLOW}⚠️  DVC gdrive support not found. Installing...{Colors.NC}")
        code, _ = run_command_func(f'"{venv_python}" -m pip install "dvc[gdrive]"')
        if code != 0:
            print(f"{Colors.RED}❌ Failed to install DVC gdrive support{Colors.NC}")
            return False
    print(f"{Colors.GREEN}✅ All prerequisites met{Colors.NC}")
    return True

### Manage Virtual env

def setup_virtual_environment(venv_path: Path, repo_root: Path) -> bool:
    """
    Create and setup virtual environment if not exists
    Returns True if venv is ready, False otherwise
    """
    if not venv_path.exists():
        print(f"{Colors.YELLOW}Creating virtual environment in VesselVerse-Dataset...{Colors.NC}")
        try:
            subprocess.run(
                [sys.executable, '-m', 'venv', str(venv_path)],
                check=True,
                cwd=repo_root
            )
            print(f"{Colors.GREEN}✅ Virtual environment created{Colors.NC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Error: Failed to create virtual environment{Colors.NC}")
            return False
    venv_python = get_venv_python(venv_path)
    if not venv_python.exists():
        print(f"{Colors.RED}❌ Error: Virtual environment is corrupted{Colors.NC}")
        return False
    return True

### Configure user credentials

def configure_credentials() -> Tuple[bool, VesselVerseConfig]:
    """Lets the user select a credentials JSON file, 
        updates the config, and returns the config object."""
    
    # Load config
    config = VesselVerseConfig()
    
    # Find credential files
    creds_dir = config.CREDENTIALS_DIR
    if not creds_dir.exists():
        print(f"{Colors.RED}❌ Error: credentials directory not found{Colors.NC}")
        return False, None
    
    cred_files = list(creds_dir.glob('*.json'))
    if not cred_files:
        print(f"{Colors.RED}❌ Error: No credential files found in credentials/{Colors.NC}")
        print("Please contact dataset maintainers to obtain credentials")
        return False, None
    
    print("Available credential files:")
    for i, cred_file in enumerate(cred_files):
        print(f"  [{i}] {cred_file.name}")
    
    print()
    choice_str = input(f"Select credential file number [0]: ").strip() or "0"
    
    try:
        choice = int(choice_str)
        if choice < 0 or choice >= len(cred_files):
            print(f"{Colors.RED}❌ Invalid selection{Colors.NC}")
            return False, None
    except ValueError:
        print(f"{Colors.RED}❌ Invalid input{Colors.NC}")
        return False, None
    
    selected_cred = cred_files[choice]
    print(f"{Colors.GREEN}✅ Using credentials: {selected_cred.name}{Colors.NC}\n")
    
    # Update config with selected credentials
    config.user_auth_path = selected_cred
    
    return True, config