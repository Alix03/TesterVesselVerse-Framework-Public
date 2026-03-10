# VesselVerse – Developer Manual

## Table of Contents

1. [DVC and Git Integration](#1-dvc-and-git-integration)
2. [Main Python Files](#2-main-python-files)
   - [vesselverseOwner.py](#vesselverseownerpy)
   - [vesselverseUser.py](#vesselverseuserpy)
   - [vv_utils.py](#vv_utilspy)
3. [Configuration Management](#3-configuration-management)
4. [Collaboration Workflow](#4-collaboration-workflow)
   - [Owner Workflow](#owner-workflow)
   - [User Workflow](#user-workflow)
5. [Best Practices](#5-best-practices)
6. [Architecture Overview](#6-architecture-overview)
7. [Visualization Parameters (viz_params)](#7-visualization-parameters-viz_params)
8. [Dynamic Dataset Discovery](#8-dynamic-dataset-discovery)
9. [Extending the System](#9-extending-the-system)

---

## Overview

This manual provides technical details for developers working on the VesselVerse project. It covers the integration of DVC and Git, the main Python modules, and visualization parameters.

---

## 1. DVC and Git Integration

- **DVC (Data Version Control)** is used to track large data files, models, and datasets. It stores metadata in `.dvc` files and manages data storage on remote backends (e.g., Google Drive).
- **Git** tracks code, configuration, and `.dvc` pointer files, but not the actual data files.
- **Workflow:**
  1. Data is added with `dvc add <folder>`; this creates a `.dvc` file.
  2. The `.dvc` file and `.gitignore` are committed to Git.
  3. Data is pushed to the DVC remote (`dvc push`).
  4. Collaborators pull code and pointers with `git pull`, then fetch data with `dvc pull`.
- **Remotes:**
  - `storage`: Main shared remote for approved data.
  - `uploads`: User-specific remote for personal uploads.
- **Permissions:**
  - Only users with the correct credentials can push to their assigned remotes.
  - Permission errors (403) are handled with custom messages in the user interface.

---

## 2. Main Python Files

### vesselverseOwner.py

**Purpose**: Command-line interface for dataset owners/maintainers to manage VesselVerse datasets.

**Main Functions**:

#### `initial_owner_setup()`

- **Purpose**: First-time configuration for dataset owners
- **Structure** (3 steps):
  1. **Prerequisites Check**: Validates Python, Git, DVC installation and virtual environment
  2. **Credentials Configuration**: Prompts user to select owner credentials (service account JSON)
  3. **DVC Remotes Configuration**: Initializes DVC and configures remotes for all datasets in `VesselVerse-Dataset/datasets/D-*`
- **Output**: Summary showing configured credentials and per-dataset storage IDs
- **Use Case**: Run once when setting up the repository as an owner

#### `owner_update_dataset()`

- **Purpose**: Download latest dataset changes from remote storage
- **Structure** (5 steps):
  1. **Dataset Selection**: Interactive prompt to choose from available D-\* datasets
  2. **Git Update**: Pulls latest commits (`git pull`)
  3. **Restore .dvc Files**: Recovers any deleted .dvc pointer files
  4. **Scan for .dvc Files**: Lists all tracked datasets in selected folder
  5. **Download Data**: Executes `dvc pull` for each .dvc file to fetch actual data
- **Output**: Summary with total processed, successfully updated, and failed downloads
- **Use Case**: Sync local copy with remote storage (Google Drive)

#### `owner_upload_dataset()`

- **Purpose**: Track new data with DVC and push to remote storage
- **Structure** (7 steps):
  1. **Dataset Selection**: Choose target D-\* dataset or create new one
  2. **Folder Selection**: Lists folders with data, shows tracking status and file counts
  3. **DVC Tracking**: Runs `dvc add` for selected folders (creates .dvc files)
  4. **Git Staging**: Stages .dvc files and .gitignore
  5. **Git Commit**: Commits .dvc metadata with custom message
  6. **DVC Push**: Uploads actual data to Google Drive remote
  7. **Git Push**: Pushes .dvc files to Git repository
- **Output**: Summary showing uploaded folders and what happened at each step
- **Use Case**: Add new datasets or update existing data for distribution

### vesselverseUser.py

**Purpose**: Command-line interface for end users/contributors to download data and submit contributions.

**Main Functions**:

#### `user_initial_setup()`

- **Purpose**: First-time configuration for users
- **Structure** (4 steps):
  1. **Prerequisites Check**: Validates Python, Git, DVC installation
  2. **Credentials Configuration**: Prompts user to select user credentials (service account JSON)
  3. **D-Expert Folder Setup**: Creates personal `D-Expert` folder for user contributions
     - Prompts for Google Drive ID (validated with regex for base64url format)
     - Configures both storage and uploads remotes for D-Expert
     - Saves configuration to `config.json`
  4. **DVC Remotes Configuration**: Initializes DVC for all accessible datasets
- **Output**: Summary showing available operations
- **Use Case**: First-time setup for users who want to download or contribute data

#### `user_update_dataset()`

- **Purpose**: Download approved datasets from remote storage
- **Structure** (5 steps):
  1. **Dataset Selection**: Interactive prompt to choose from available D-\* datasets
  2. **Git Update**: Pulls latest commits
  3. **Restore .dvc Files**: Recovers any deleted .dvc pointer files
  4. **Scan for .dvc Files**: Lists all tracked datasets
  5. **Download Data**: Executes `dvc pull` for each .dvc file
- **Output**: Summary with download statistics
- **Use Case**: Get latest approved data from official remote storage

#### `user_upload_data()`

- **Purpose**: Upload user contributions to D-Expert folder
- **Structure** (7 steps):
  1. **D-Expert Configuration Check**: Verifies D-Expert setup and DVC remotes
     - Shows helpful message if D-Expert is empty with example folder structure
  2. **Folder Selection**: Lists folders in D-Expert with tracking status
  3. **DVC Tracking**: Runs `dvc add` for selected folders
  4. **Git Staging**: Stages .dvc files and .gitignore
  5. **Git Commit**: Commits metadata
  6. **DVC Push**: Uploads data to user's personal Google Drive folder
     - Provides specific error messages for permission issues (403 errors)
  7. **Git Push**: Pushes .dvc files to Git
- **Output**: Summary of uploaded folders
- **Use Case**: Share user annotations/modifications with owner for review

#### `create_pull_request()`

- **Purpose**: Submit D-Expert contributions for owner review via GitHub Pull Request
- **Structure** (6 steps):
  1. **Repository Status Check**: Validates GitHub repository, extracts owner/repo names
  2. **Uncommitted Changes**: Checks for uncommitted files, offers to commit them
  3. **Branch Creation**: Creates timestamped branch (e.g., `expert-submission-20260130_143045`)
  4. **Push Branch**: Pushes branch to user's fork
  5. **Upstream Detection**: Identifies original repository (prompts if not configured)
  6. **PR Creation**:
     - If GitHub CLI available: Creates PR automatically with title/description prompts
     - Otherwise: Provides URL for manual PR creation
- **Output**: Summary with branch name, fork/target info, and next steps
- **Use Case**: Request that owner reviews and merges D-Expert data into official datasets
- **Requirements**: User must have forked the repository and configured remotes properly

### vv_utils.py

**Purpose**: Shared utility functions and common operations for both owner and user scripts.

**Key Functions**:

#### `setup_virtual_environment(venv_path, repo_root)`

- **Purpose**: Creates and configures Python virtual environment
- **Behavior**:
  - Searches for Python 3.12/3.11 installations (excludes 3.9/3.10 due to compatibility)
  - Creates venv if it doesn't exist
  - Automatically upgrades pip
  - Installs dependencies from `requirements.txt`
- **Returns**: Boolean indicating success
- **Use Case**: Called at start of both owner and user scripts

#### `get_venv_python(venv_path)`

- **Purpose**: Gets path to Python executable inside virtual environment
- **Returns**: Path object to venv Python binary
- **Use Case**: Used to ensure DVC runs with correct Python environment

#### `check_prerequisites(venv_path, repo_root)`

- **Purpose**: Validates system requirements
- **Checks**:
  - Virtual environment exists
  - Git is installed
  - DVC is installed
  - Dataset repository exists
- **Returns**: Boolean indicating all checks passed
- **Use Case**: Called during initial setup to catch configuration issues early

#### `configure_credentials()`

- **Purpose**: Interactive credential selection and validation
- **Behavior**:
  - Lists available .json credential files in `credentials/` folder
  - Prompts user to select appropriate credential file
  - Validates JSON format
  - Creates VesselVerseConfig instance with selected credentials
- **Returns**: Tuple of (success: bool, config: VesselVerseConfig)
- **Use Case**: Used during initial setup for both owner and user

#### `configure_dvc_remotes(config, datasets_dir)`

- **Purpose**: Initializes DVC and configures remotes for all datasets
- **Behavior**:
  - Iterates through all D-\* folders in datasets directory
  - Initializes DVC in each dataset (`dvc init`)
  - Configures `storage` remote with dataset-specific Google Drive ID
  - Configures `uploads` remote (for D-Expert only)
  - Sets service account authentication
- **Returns**: Boolean indicating success
- **Use Case**: Automates DVC setup across multiple datasets

#### `run_command(command, cwd, capture_output)`

- **Purpose**: Execute shell commands with proper error handling
- **Parameters**:
  - `command`: Shell command string
  - `cwd`: Working directory (optional)
  - `capture_output`: If True, returns output instead of printing
- **Returns**: Tuple of (exit_code: int, output: str)
- **Use Case**: All Git and DVC operations use this for consistent behavior

#### Color Constants (`Colors` class)

- **Purpose**: ANSI color codes for terminal output formatting
- **Available Colors**: BLUE, CYAN, GREEN, YELLOW, RED, NC (no color)
- **Use Case**: Provides colored, user-friendly console output

## 3. Configuration Management

### config.py

**Purpose**: Central configuration management for VesselVerse project.

**Class: VesselVerseConfig**

#### Core Attributes

- `REPO_ROOT`: Path to VesselVerse root directory
- `DATASET_GIT_ROOT`: Path to VesselVerse-Dataset subdirectory
- `SLICER_PATH`: Auto-detected path to 3D Slicer installation (OS-specific)
- `CREDENTIALS_DIR`: Path to credentials folder
- `owner_auth_path`: Path to owner service account JSON
- `user_auth_path`: Path to user service account JSON
- `VENV_PATH`: Path to virtual environment
- `DATASET_NAME`: Currently active dataset name
- `DATASET_PATH`: Path to current dataset directory

#### Storage ID Management

Dynamic attributes for each dataset:

- `{DatasetName}_STORAGE_ID`: Google Drive folder ID for dataset storage
- `{DatasetName}_UPLOAD_ID`: Google Drive folder ID for user uploads (D-Expert only)

**Key Methods**:

#### `__init__(config_file=None)`

- **Purpose**: Initialize configuration
- **Behavior**:
  - Detects repository root from file location
  - Auto-detects Slicer path based on OS (macOS/Linux/Windows)
  - Sets up default dataset storage IDs
  - Loads overrides from `config.json` if exists

#### `_setup_dataset_storage()`

- **Purpose**: Configures default Google Drive IDs for known datasets
- **Default Datasets**:
  - IXI: Production storage ID
  - COW23MR: Production storage ID
  - ITKTubeTK: Testing ID
  - Prova/Prova2: Testing IDs
  - Expert: Configured dynamically by user during setup

#### `set_storage_id(dataset_name, storage_id, save=True, is_upload=False)`

- **Purpose**: Set or update Google Drive ID for a dataset
- **Parameters**:
  - `dataset_name`: Name without "D-" prefix (e.g., "Expert", "IXI")
  - `storage_id`: Google Drive folder ID
  - `save`: If True, persists to config.json
  - `is_upload`: If True, sets as UPLOAD_ID instead of STORAGE_ID
- **Use Case**: Used during user setup to configure D-Expert personal folder

#### `get_storage_id(dataset_name)`

- **Purpose**: Retrieve Google Drive storage ID for a dataset
- **Returns**: Storage folder ID string or TESTING_ID if not configured
- **Use Case**: Called before DVC operations to ensure correct remote

#### `get_upload_id(dataset_name)`

- **Purpose**: Retrieve Google Drive upload ID for a dataset
- **Returns**: Upload folder ID string or None if not configured
- **Use Case**: Used for D-Expert uploads remote configuration

#### `get_dataset_path(dataset_name)`

- **Purpose**: Get full path to a specific dataset
- **Returns**: Path object to `VesselVerse-Dataset/datasets/D-{dataset_name}`
- **Use Case**: Navigate to dataset directories programmatically

#### `save_json(output_path=None)`

- **Purpose**: Persist configuration to JSON file
- **Behavior**:
  - Saves all _\_STORAGE_ID and _\_UPLOAD_ID attributes
  - Creates `config.json` in repository root
- **Use Case**: Called after user sets custom Google Drive IDs

#### `_load_from_json()`

- **Purpose**: Load configuration overrides from config.json
- **Behavior**:
  - Silently continues if file doesn't exist or is corrupted
  - Only loads _\_STORAGE_ID and _\_UPLOAD_ID fields
- **Use Case**: Called during **init** to apply saved configuration

#### `validate()`

- **Purpose**: Check configuration completeness
- **Returns**: Tuple of (is_valid: bool, errors: List[str])
- **Checks**:
  - Owner credentials exist
  - User credentials exist
  - Dataset repository exists
  - Slicer installation found (warning only)
- **Use Case**: Can be called to diagnose configuration issues

#### `to_dict()`

- **Purpose**: Export configuration as dictionary
- **Returns**: Dict with all configuration values as strings
- **Use Case**: Debugging, logging, or exporting config for inspection

### CLI Interface (config.py)

When run as script (`python3 config.py`), provides commands:

- `--get PARAM`: Print specific configuration parameter
- `--export`: Print all configuration as key-value pairs
- `--validate`: Check configuration validity
- `--set-dataset NAME`: Switch active dataset

**Use Case**: Shell scripts or external tools can query configuration without importing Python module

---

## 4. Collaboration Workflow

### Owner Workflow

1. **Initial Repository Setup**

   ```bash
   python3 vesselverseOwner.py
   # Choose [1] Initial Setup
   # - Select owner credentials
   # - Configure DVC remotes for all datasets
   ```

2. **Adding New Data**

   ```bash
   # Choose [3] Upload Dataset
   # - Select target dataset (or create new D-* folder)
   # - Choose folders to track
   # - Data is uploaded to Google Drive
   # - .dvc files are committed to Git
   ```

3. **Syncing Latest Changes**

   ```bash
   # Choose [2] Update Dataset
   # - Select dataset to update
   # - Downloads latest data from Google Drive
   ```

4. **Reviewing User Contributions**
   - Users submit Pull Requests with D-Expert data
   - Review PR on GitHub (changes to D-Expert folder)
   - If approved, merge PR to include data in repository
   - Optionally move D-Expert data to official datasets

### User (Contributor) Workflow

1. **Create Workspace and Fork Both Repositories**
   - Create a parent folder for the project: `mkdir vesselverse && cd vesselverse`
   - Fork **VesselVerse-Framework** on GitHub: https://github.com/i-vesseg/VesselVerse-Framework
   - Fork **VesselVerse-Dataset** on GitHub: https://github.com/i-vesseg/VesselVerse-Dataset
   - Clone **both** of your forks into the parent folder

2. **Clone Your Forks**

   ```bash
   # Inside vesselverse/ parent folder

   # Clone Dataset repository (your fork)
   git clone https://github.com/YourUsername/VesselVerse-Dataset.git

   # Clone Framework repository (your fork)
   git clone https://github.com/YourUsername/VesselVerse-Framework.git

   # Your structure should be:
   # vesselverse/
   # ├── vesselverseUser.py
   # ├── vv_utils.py
   # ├── config.py
   # ├── credentials/
   # ├── VesselVerse-Dataset/
   # └── VesselVerse-Framework/
   ```

3. **Configure Upstream Remotes (Recommended)**

   ```bash
   # Configure Dataset upstream
   cd VesselVerse-Dataset
   git remote add upstream https://github.com/i-vesseg/VesselVerse-Dataset.git
   cd ..

   # Configure Framework upstream
   cd VesselVerse-Framework
   git remote add upstream https://github.com/i-vesseg/VesselVerse-Framework.git
   cd ..
   ```

4. **Initial Setup**

   ```bash
   # Run from parent vesselverse/ folder
   python3 vesselverseUser.py
   # Choose [1] Initial Setup
   # - Select user credentials
   # - Configure D-Expert folder
   # - Enter your personal Google Drive ID
   ```

5. **Download Approved Datasets**

   ```bash
   python3 vesselverseUser.py
   # Choose [2] Update Dataset
   # - Select datasets to download
   # - Downloads from official storage
   ```

6. **Work on Annotations**
   - Create folders in D-Expert (e.g., MyAnnotations/)
   - Add your segmentation files
   - Test and validate your work

7. **Upload Your Work**

   ```bash
   python3 vesselverseUser.py
   # Choose [3] Upload Data
   # - Tracks folders with DVC
   # - Uploads to your personal Google Drive
   # - Commits .dvc files to Git
   ```

8. **Submit for Review**

   ```bash
   python3 vesselverseUser.py
   # Choose [4] Create Pull Request
   # - Creates timestamped branch
   # - Pushes to your fork
   # - Creates PR to original repository
   ```

9. **Keep Fork Updated**
   ```bash
   cd VesselVerse-Dataset
   git fetch upstream
   git checkout main
   git merge upstream/main
   git push origin main
   cd ..
   ```

---

## 5. Best Practices

### For Owners

- **Never commit large files directly to Git** - Always use DVC (`dvc add`)
- **Use descriptive commit messages** - Explain what data was added/modified
- **Test DVC remotes** - Verify Google Drive permissions before large uploads
- **Document new datasets** - Update README or documentation when adding D-\* folders
- **Review PR carefully** - Check data quality and format before merging user contributions
- **Backup credentials** - Keep service account JSON files secure and backed up

### For Users

- **Always fork first** - Don't clone the original repository directly if you plan to contribute
- **Configure upstream remote** - Makes it easier to sync with original repository
- **Commit incrementally** - Don't wait until you have massive changes
- **Test before submitting** - Verify your data loads correctly in Slicer/notebooks
- **Use clear folder names** - Name D-Expert subfolders descriptively (e.g., "MyAnnotations_IXI_2026")
- **Document your work** - Add README files explaining your annotation methodology
- **Respect permissions** - Only upload to your assigned Google Drive folder

### For Both

- **Use virtual environment** - Scripts automatically create and manage venv
- **Check DVC status** - Run `dvc status` to see what's changed before uploading
- **Monitor Git status** - Use `git status` to track uncommitted changes
- **Handle conflicts carefully** - Pull before pushing to avoid merge conflicts
- **Keep credentials secure** - Never commit .json credential files to public repos
- **Document changes** - Update VIZ_PARAMS.md when modifying visualization settings

### Error Handling

Common issues and solutions:

1. **403 Permission Error**
   - Verify you're using correct credentials (owner vs user)
   - Check Google Drive folder permissions
   - Ensure service account has write access

2. **DVC Pull Fails**
   - Check internet connection
   - Verify remote configuration (`dvc remote list`)
   - Ensure .dvc files are committed to Git

3. **Git Push Rejected**
   - Pull latest changes first (`git pull`)
   - Resolve any merge conflicts
   - Ensure you have push access to your fork

4. **Python Version Issues**
   - Scripts require Python 3.11+
   - Script automatically creates venv with correct version
   - Delete `.venv` and rerun if version mismatch

5. **Circular Pull Request**
   - Ensure you're working on a fork, not the original repo
   - Configure upstream remote to point to original repository
   - Check `git remote -v` shows different URLs for origin/upstream

---

## 6. Architecture Overview

### Directory Structure

```
VesselVerse/
├── config.py                          # Central configuration management
├── config.sh                          # Legacy shell configuration (deprecated)
├── config.json                        # User-specific config (git-ignored)
├── vesselverseOwner.py               # Owner CLI interface
├── vesselverseUser.py                # User/Contributor CLI interface
├── vv_utils.py                       # Shared utility functions
├── .gitignore                        # Git ignore rules
├── README.md                         # Main project documentation
├── USER_MANUAL.md                    # End-user guide
├── DEVELOPER_MANUAL.md               # This file
├── VIZ_PARAMS.md                     # Visualization parameters guide
├── credentials/                      # Service account credentials (git-ignored)
│
├── VesselVerse-Dataset/              # Data repository submodule
│   ├── .venv/                       # Python virtual environment (git-ignored)
│   ├── LICENSE                      # Dataset license
│   ├── README.md                    # Dataset documentation
│   ├── requirements.txt             # Python dependencies
│   ├── logos/                       # Project logos and branding
│   ├── scripts/                     # Dataset management scripts
│   │   ├── 0_activate_user_mode.sh
│   │   ├── 1_modify_segmentation.sh
│   │   ├── 2_upload_modification.sh
│   │   └── 3_update_staple.sh
│   └── datasets/                    # All dataset folders
│       ├── D-IXI/                   # IXI brain MRA dataset
│       │   ├── .dvc/               # DVC configuration
│       │   ├── .dvcignore          # DVC ignore rules
│       │   └── .gitignore          # Git ignore rules
│       ├── D-COW23MR/              # TOPCOW 2023 MR dataset
│       │   ├── .dvc/               # DVC configuration
│       │   ├── .dvcignore          # DVC ignore rules
│       │   └── .gitignore          # Git ignore rules
│       ├── D-ITKTubeTK/            # ITK-TubeTK dataset
│       │   ├── .dvc/               # DVC configuration
│       │   ├── .dvcignore          # DVC ignore rules
│       │   └── .gitignore          # Git ignore rules
│       ├── D-Expert/               # User contributions folder
│       │   ├── .dvc/              # User-specific DVC config
│       │   ├── .dvcignore          # DVC ignore rules
│       │   └── [User folders]/    # User annotation folders
└── VesselVerse-Framework/         # Framework and tools
    ├── LICENSE                    # Framework license
    ├── README.md                  # Framework documentation
    ├── requirements.txt           # Python dependencies
    ├── docs/                      # Documentation files
    │   ├── DYNAMIC_DATASET_REGISTRATION.md
    │   ├── viz_params_README.md
    │   ├── 3DSLICER/             # Slicer-specific docs
    │   └── imgs/                 # Documentation images
    ├── notebooks/                 # Jupyter notebooks
    │   ├── check_req_version.ipynb
    │   ├── extract_vessel_mask.ipynb
    │   └── organize_data.ipynb
    ├── scripts/                   # Shell scripts
    │   ├── activate_owner_mode.sh
    │   ├── install_slicer.sh
    │   ├── launch_slicer.sh
    │   ├── restart_repo.sh
    ├── scripts_py/                # Python utility scripts
    │   ├── __init__.py
    │   ├── autocommit_viz_params.py
    │   ├── autoload_viz_params.py
    │   ├── compute_staple.py
    │   ├── generate_metadata.py
    │   ├── staple_params.yaml
    │   ├── test_setup.py
    │   └── viz_params_manager.py
    └── src/                       # Source code
        ├── __init__.py
        ├── core/                  # Core functionality
        ├── model_config/          # Model configurations
        │   ├── __init__.py
        │   └── model_config.py   # Dataset registry
        ├── slicer_extension/      # 3D Slicer extension
        │   ├── VesselVerse/      # Main extension module
        │   │   ├── __init__.py
        │   │   ├── VesselVerse.py
        │   │   ├── loading_dialog.py
        │   │   └── opacity_slicer.py
        │   ├── VesselVerseVizParams/  # Viz params extension
        │   │   ├── __init__.py
        │   │   └── VesselVerseVizParams.py
        │   └── sql_files/        # SQL tracking files
        └── tracking/              # Data tracking utilities
```

### Why D-Expert Has Different Ignore Configuration

**D-Expert is unique** because it's designed for **user contributions**, not official datasets:

#### Official Datasets (D-IXI, D-COW23MR, D-ITKTubeTK):

- ✅ **Has .dvcignore**: Tells DVC which files to ignore
- ✅ **Has .gitignore**: Tells Git to ignore actual data folders
- 📦 **Workflow**: `dvc add folder/` creates `.dvc` pointer → Git tracks only `.dvc` files
- 🔒 **Data tracked by**: Owner only, centralized storage

#### D-Expert (User Contributions):

- ✅ **Has .dvcignore**: Still uses DVC for data
- ❌ **No .gitignore**: User folders and `.dvc` files are **both tracked in Git**
- 📦 **Workflow**: Users create folders → `dvc add` → Both folder structure and `.dvc` committed
- 🌐 **Data tracked by**: Individual users, personal Google Drive
- 🔄 **Purpose**: Enable Pull Requests showing what users contributed

**Why this design?**

1. **PR Visibility**: When users create PRs, the repository shows new folders/structure in D-Expert
2. **Collaboration**: Owner can see exactly what users added without downloading data first
3. **Decentralized**: Each user tracks their data in their own Google Drive
4. **Review Process**: Owner reviews PR, then optionally moves approved data to official datasets

**In summary**: D-Expert tracks **structure** in Git (folders + .dvc pointers) but **data** in DVC (user's Google Drive), allowing collaborative review via GitHub PRs while keeping large files out of Git.

### Data Flow

**Owner Upload**:

```
Local Data → dvc add → .dvc file → git commit → dvc push (uploads) → Google Drive
                                        ↓
                                    git push → GitHub
```

**User Download**:

```
GitHub --[git pull]--> .dvc files (metadata pointers)
                           ↓
                   dvc pull (reads .dvc)
                           ↓
              Google Drive (remote storage)
                           ↓
                  downloads actual data
                           ↓
                    Local Data (files)
```

**User Contribution**:

```
D-Expert Work → dvc add → .dvc file → dvc push (uploads) → User's Google Drive
                                          ↓
                                      git commit → git push → Fork (with .dvc metadata)
                                          ↓
                                    Create PR → Review → Merge
```

### Key Technologies

- **Git**: Version control for code and .dvc pointer files
- **DVC**: Data version control for large datasets
- **Google Drive**: Remote storage backend for data
- **Python 3.11+**: Required for google-api-core compatibility
- **Service Accounts**: Authentication for Google Drive access
- **GitHub**: Repository hosting and Pull Request workflow

---

## 7. Visualization Parameters (viz_params)

- Visualization parameters are documented in `VIZ_PARAMS.md` and related files.
- These parameters control how data is visualized in notebooks and scripts (e.g., color maps, rendering options, thresholds).
- The `VesselVerse-Framework/docs/viz_params_README.md` and `VesselVerse-Dataset/datasets/*/viz_params/` folders contain detailed documentation and examples.
- Developers should refer to these files when implementing or modifying visualization features to ensure consistency and reproducibility.

---

## 8. Dynamic Dataset Discovery

The system automatically discovers and registers all datasets in `VesselVerse-Dataset/datasets/D-*`:

### Registration Priority

1. **Custom Configuration**: If `dataset_config.json` exists in dataset folder
2. **Legacy Hardcoded**: Built-in configuration for IXI, COW23MR, ITKTubeTK
3. **Auto-Detection**: Automatically scans subdirectories for models

### Creating Custom Dataset Configuration

Create `dataset_config.json` in your D-\* folder:

```json
{
  "name": "MyDataset",
  "unique_name": "MyDataset",
  "image_suffix": "nii.gz",
  "modality": "MR",
  "supported_models": ["MODEL1", "MODEL2", "STAPLE"],
  "file_pattern": "*.nii.gz",
  "base_model_name": "TOT"
}
```

### Auto-Detection Behavior

If no configuration file exists:

- Scans for subdirectories (excluding `.dvc`, `.git`, `__pycache__`, `viz_params`)
- Treats each subdirectory as a supported model
- Uses generic defaults for image format and modality

### Example

```
datasets/
├── D-IXI/                    # Legacy: Hardcoded configuration
├── D-MyDataset/              # Auto-detected
│   ├── ModelA/              #   → Registered as supported model
│   ├── ModelB/              #   → Registered as supported model
│   └── STAPLE/              #   → Registered as supported model
└── D-CustomDataset/          # Custom configuration
    └── dataset_config.json  #   → Uses custom settings
```

All discovered datasets appear in Slicer extension dropdown automatically.

---

## 9. Extending the System

### Adding a New Dataset Type

1. Create folder: `VesselVerse-Dataset/datasets/D-YourDataset/`
2. Add data folders inside
3. Run owner script: `[3] Upload Dataset`
4. Dataset appears automatically in user interface

### Adding Custom Models

Option 1: **Auto-detection**

- Create folder in dataset: `D-YourDataset/YourModel/`
- System automatically recognizes it

Option 2: **Custom Configuration**

- Create `dataset_config.json` with `supported_models` list

### Modifying DVC Workflow

Key files:

- `vv_utils.py`: `configure_dvc_remotes()` function
- `vesselverseOwner.py`: Upload/update functions
- `vesselverseUser.py`: Upload/update functions

All DVC commands use: `"{venv_python}" -m dvc <command>`
This ensures virtual environment Python is used, not system Python.

### Adding New Credential Types

1. Add .json file to `credentials/` folder
2. Update `configure_credentials()` in `vv_utils.py` if special handling needed
3. Optionally add new config fields in `config.py`

---

For further details, see the code comments and the documentation files in the repository.
