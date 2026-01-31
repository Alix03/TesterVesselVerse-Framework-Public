# VesselVerse – User Manual

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Getting Started](#2-getting-started)
   - [2.1 Repository Setup](#21-repository-setup)
   - [2.2 Verify Setup](#22-verify-setup)
   - [2.3 Why Fork Both Repositories?](#23-why-fork-both-repositories)
3. [Initial Setup](#3-initial-setup)
4. [Downloading Official Datasets](#4-downloading-official-datasets)
5. [Contributing Your Data](#5-contributing-your-data)
   - [5.1 Prepare Your Data](#51-prepare-your-data)
   - [5.2 Upload Your Data](#52-upload-your-data)
   - [5.3 Understanding the Upload](#53-understanding-the-upload)
6. [Submitting for Review (Pull Request)](#6-submitting-for-review-pull-request)
   - [6.1 Prerequisites](#61-prerequisites)
   - [6.2 Create Pull Request](#62-create-pull-request)
   - [6.3 After Submitting](#63-after-submitting)
   - [6.4 Keep Your Fork Updated](#64-keep-your-fork-updated)
7. [D-Expert Personal Folder](#7-d-expert-personal-folder)
8. [Troubleshooting](#8-troubleshooting)
9. [Advanced Tips](#9-advanced-tips)
10. [Getting Help](#10-getting-help)
11. [Summary](#11-summary)

---

## Overview

Welcome to VesselVerse! This manual guides you through downloading official datasets and contributing your own annotations. VesselVerse uses **Git** for code versioning and **DVC** (Data Version Control) for managing large medical imaging datasets.

---

## 1. Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.11 or higher** (Python 3.12 recommended)
- ✅ **Git installed** and configured
- ✅ **GitHub account** (for contributing data)
- ✅ **Credentials file** (.json) provided by the team
  - Place your credentials in the `credentials/` folder
  - File format: `vesselverse25-xxxxxx.json`
- ✅ **Google Drive ID** for your personal D-Expert folder
  - Provided by the team or create your own Google Drive folder
  - Format: 25-50 character alphanumeric ID

---

## 2. Getting Started

VesselVerse is organized into **two separate repositories**:

- **VesselVerse-Dataset**: Contains all the medical imaging data (tracked with DVC)
- **VesselVerse-Framework**: Contains scripts, tools, and 3D Slicer extension

### 2.1 Repository Setup

**⚠️ IMPORTANT**: You MUST fork both repositories to contribute data. Git push will only work on your forked repositories.

#### Step 1: Create a workspace folder

```bash
# Create a parent folder for the project
mkdir vesselverse
cd vesselverse
```

#### Step 2: Fork both repositories on GitHub

1. Go to https://github.com/i-vesseg/VesselVerse-Dataset
   - Click **"Fork"** button (top right)
   - Creates: `https://github.com/YourUsername/VesselVerse-Dataset`

2. Go to https://github.com/i-vesseg/VesselVerse-Framework
   - Click **"Fork"** button (top right)
   - Creates: `https://github.com/YourUsername/VesselVerse-Framework`

#### Step 3: Clone YOUR forks

```bash
# Inside vesselverse/ folder

# Clone Dataset repository (your fork)
git clone https://github.com/YourUsername/VesselVerse-Dataset.git

# Clone Framework repository (your fork)
git clone https://github.com/YourUsername/VesselVerse-Framework.git

# Your structure should be:
# vesselverse/
# ├── VesselVerse-Dataset/
# └── VesselVerse-Framework/
```

#### Step 4: Add upstream remotes

This allows you to pull updates from the official repositories:

**⚠️ IMPORTANT**: The `upstream` remote is **READ-ONLY** for you. You can ONLY:

- ✅ `git fetch upstream` - Download updates from official repo
- ✅ `git pull upstream main` - Merge official updates into your fork
- ❌ `git push upstream` - **NOT ALLOWED** (you don't have write permissions)

You will ALWAYS push to `origin` (your fork), never to `upstream`.

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

#### Step 5: Receive and configure credentials

The VesselVerse team will provide you with:

1. **Credentials file** (`vesselverse25-xxxxxx.json`)
   - Place in: `credentials/`
2. **Google Drive ID** (for your D-Expert folder)
   - Format: `1Lt5rGwBPkmdXGeGmpNKrzZ07xJzY_yYv` (example)
   - You'll enter this during Initial Setup
3. **Configuration files**
   - Place in the main repository folder as instructed by the team

### 2.2 Verify Setup

Check your repository structure and remotes:

```bash
# Check folder structure
ls
# Should show:
# VesselVerse-Dataset/
# VesselVerse-Framework/

# Verify Dataset remotes
cd VesselVerse-Dataset
git remote -v
# Should show:
# origin    https://github.com/YourUsername/VesselVerse-Dataset.git (fetch)
# origin    https://github.com/YourUsername/VesselVerse-Dataset.git (push)
# upstream  https://github.com/i-vesseg/VesselVerse-Dataset.git (fetch)
# upstream  https://github.com/i-vesseg/VesselVerse-Dataset.git (push)

# Verify Framework remotes
cd ../VesselVerse-Framework
git remote -v
# Should show:
# origin    https://github.com/YourUsername/VesselVerse-Framework.git (fetch)
# origin    https://github.com/YourUsername/VesselVerse-Framework.git (push)
# upstream  https://github.com/i-vesseg/VesselVerse-Framework.git (fetch)
# upstream  https://github.com/i-vesseg/VesselVerse-Framework.git (push)
```

### 2.3 Why Fork Both Repositories?

**Critical**: Forking is REQUIRED for the upload workflow to function:

- When you upload data (DVC), it needs to:
  1. **Push data files** → Your Google Drive (via DVC)
  2. **Push .dvc pointer files** → Your forked VesselVerse-Dataset repository (via Git)

- If you only clone (without forking), **git push will fail** with permission errors
- The VesselVerse-Dataset folder MUST be connected to YOUR forked repository
- After uploading, you create a Pull Request from your fork to the official repository

---

## 3. Initial Setup

**Run this ONCE** when you first start using VesselVerse.

```bash
python vesselverseUser.py
# Choose option [1] Initial Setup
```

### What happens during setup:

#### Step 1: Prerequisites Check

- Verifies Python, Git, and DVC are installed
- Creates virtual environment if needed
- Installs required dependencies automatically

#### Step 2: Credentials Configuration

- Lists available credential files in `credentials/` folder
- Select your personal `.json` file
- Example: `vesselverse25-141593c63cd7.json`

#### Step 3: D-Expert Folder Setup

Your personal contribution folder is created:

- **Location**: `VesselVerse-Dataset/datasets/D-Expert/`
- **Purpose**: Store your annotations and modifications
- **Privacy**: Only you can write to this folder's remote storage

You'll be prompted to enter your **Google Drive Folder ID**:

- Format: `1Lt5rGwBPkmdXGeGmpNKrzZ07xJzY_yYv` (example)
- Length: 25-50 characters (letters, numbers, `_`, `-`)
- This ID links to your personal Google Drive storage

#### Step 4: DVC Remotes Configuration

- Configures DVC for all available datasets
- Sets up connection to Google Drive storage
- Links your D-Expert folder to your personal remote

### ✅ Setup Complete!

After successful setup, you'll see:

```
✅ Setup Complete! 🎉
You can now:
  [2] Update Dataset  - Download approved data
  [3] Upload Data     - Share your work
  [4] Create Pull Request - Submit for review
```

---

## 4. Downloading Official Datasets

Download approved, high-quality datasets maintained by the repository owner.

### Steps:

1. **Run the script**:

   ```bash
   python vesselverseUser.py
   ```

2. **Choose option `[2] Update Dataset`**

3. **Select target dataset**:

   ```
   Available datasets:
   [0] D-IXI         - IXI brain MRA dataset
   [1] D-COW23MR     - TOPCOW 2023 MR dataset
   [2] D-ITKTubeTK   - ITK-TubeTK dataset
   [3] D-Expert      - Your contribution folder
   ```

4. **What happens**:
   - Git pulls latest repository changes
   - Restores any missing `.dvc` pointer files
   - Scans for available datasets
   - Downloads data from Google Drive using DVC

### Example Output:

```
[5/5] Downloading updates from remote...

Pulling: IXI_TOT
  ✅ IXI_TOT downloaded
Pulling: STAPLE
  ✅ STAPLE downloaded

═══════════════════════════════════════════════════
          Download Complete! 🎉
═══════════════════════════════════════════════════

Update Summary:
  Total datasets processed: 2
  Successfully updated:     2
```

### 📊 Available Official Datasets:

- **D-IXI**: Brain MRA images with vessel segmentations
  - Contains: IXI_TOT, STAPLE, nnUNet, ExpertAnnotations
- **D-COW23MR**: TOPCOW Challenge 2023 MR data
  - Contains: COW_TOT, COW_SEG, STAPLE, JOB-VS
- **D-ITKTubeTK**: ITK-TubeTK vessel extraction results
  - Contains: ExpertAnnotations, STAPLE

---

## 5. Contributing Your Data

Share your annotations, segmentations, or analysis results with the community.

### 5.1 Prepare Your Data

1. **Create folders in D-Expert**:

   ```bash
   cd VesselVerse-Dataset/datasets/D-Expert
   mkdir MyAnnotations_2026
   ```

2. **Add your files**:

   ```bash
   cp /path/to/your/segmentations/*.nii.gz MyAnnotations_IXI_2026/
   ```

3. **Recommended structure**:
   ```
   D-Expert/
   ├── MyAnnotations_IXI_2026/
   │   ├── case001.nii.gz
   │   ├── case002.nii.gz
   │   └── README.md          # Describe your method
   └── MyExperiments_COW/
       ├── results.csv
       └── analysis.ipynb
   ```

### 5.2 Upload Your Data

1. **Run the script**:

   ```bash
   python vesselverseUser.py
   ```

2. **Choose option `[3] Upload Data`**

3. **System automatically uses D-Expert** (your personal folder)

4. **Select folders to upload**:

   ```
   Available folders:
   [0] MyAnnotations_2026 (not tracked, 150 files)
   [1] MyExperiments_COW (not tracked, 3 files)
   [a] All folders

   Select folder(s): 0,1
   ```

5. **What happens** (7 steps):
   - ✅ DVC tracks your folders (creates `.dvc` pointer files)
   - ✅ Stages `.dvc` files and `.gitignore` for Git
   - ✅ Commits metadata to Git
   - ✅ Uploads actual data to YOUR Google Drive
   - ✅ Pushes `.dvc` files to Git

### 5.3 Understanding the Upload

**Your data goes to TWO places:**

1. **Git Repository** (GitHub):
   - `.dvc` pointer files (tiny, few KB)
   - `.gitignore` files (auto-created by DVC)
   - Folder structure (empty directories)
   - **NOT** the actual data files

2. **DVC Remote** (Your Google Drive):
   - Actual data files (NIfTI images, CSVs, etc.)
   - Can be GBs in size
   - Accessed via your personal credentials

### 🔒 How DVC Protects Your Data from Git

**Important**: DVC automatically prevents large files from entering Git:

When you run `dvc add MyFolder/`, DVC automatically:

1. Creates `MyFolder.dvc` (pointer file with metadata)
2. **Creates/updates `.gitignore`** to exclude `MyFolder/` from Git
3. Uploads actual data to Google Drive

**Example:**

```bash
cd D-Expert
dvc add MyAnnotations_2026/

# DVC automatically creates:
# ├── MyAnnotations_2026.dvc       ← Goes to Git (tiny)
# ├── .gitignore                   ← Goes to Git (auto-updated)
# └── MyAnnotations_2026/          ← Excluded from Git (in .gitignore)
#     └── *.nii.gz                 ← Goes to Google Drive only
```

**Result**: Even though D-Expert doesn't have a pre-existing `.gitignore`, DVC creates one automatically during upload. Your large files are **never** pushed to GitHub.

### ⚠️ Permission Errors

If you see **403 Forbidden** error:

- ✅ Verify you're using the correct credentials
- ✅ Check your Google Drive ID is correct
- ✅ Ensure your service account has write permissions
- ✅ Contact admin if issue persists

---

## 6. Submitting for Review (Pull Request)

Request that the repository owner reviews and potentially includes your data in official datasets.

### 6.1 Prerequisites

- ✅ You've forked the repository (not just cloned)
- ✅ You've uploaded your data to D-Expert (option 3)
- ✅ All changes are committed

### 6.2 Create Pull Request

1. **Run the script**:

   ```bash
   python vesselverseUser.py
   ```

2. **Choose option `[4] Create Pull Request`**

3. **System checks**:
   - Repository status (fork vs original)
   - Uncommitted changes (offers to commit them)
   - Creates timestamped branch: `expert-submission-20260130_143045`
   - Pushes branch to your fork
   - **Checks for upstream remote** (original repository you forked from)

4. **If upstream is not configured**, the system will prompt you:

   ```
   ⚠️  No upstream remote configured

   Enter the original repository owner (the repo you forked from):
   Owner: `i-vesseg` (the official organization)
   Repository: `VesselVerse-Dataset`
   ```

   After entering these details, the system will automatically execute:

   ```bash
   git remote add upstream https://github.com/i-vesseg/VesselVerse-Dataset.git
   ```

   This configures the upstream remote so the pull request can be created to the official repository.

5. **PR Creation**:

   After pushing the branch, GitHub automatically displays a banner **on YOUR fork's page**:

   ```
   expert-submission-20260130_143045 had recent pushes less than a minute ago
   [Compare & pull request]  ← Green button
   ```

   **⚠️ Important**: The banner appears on YOUR fork, not on the owner's repository. You must click the banner or use the URL to CREATE the pull request. The owner will see your PR only after you create it.

   **Two ways to complete the PR:**

   **Option A: With GitHub CLI (fully automatic)**
   - System detects `gh` command
   - Prompts for PR title and description
   - **Creates PR automatically from terminal**
   - Displays PR URL
   - ✅ Best for: Fully automated workflow

   **Option B: Manual (click the banner or use URL)**
   - After pushing, visit YOUR fork on GitHub
   - Click the green "Compare & pull request" button in the banner
   - OR use the direct URL provided by the script:
     `https://github.com/i-vesseg/VesselVerse-Dataset/compare/main...YourUsername:expert-submission-20260130_143045`
   - Fill in PR title and description
   - Submit the Pull Request
   - ✅ Best for: Simple workflow, no extra installation needed

   **Note**: Creating the PR is a required step. Simply pushing the branch does not notify the owner or create a Pull Request automatically.

### 6.3 After Submitting

The repository owner will:

1. **Review your PR** on GitHub (in VesselVerse-Dataset repository)
2. **Check data quality** and documentation
3. **Request changes** if needed (via PR comments)
4. **Merge your contribution** if approved
5. **Optionally move** your data to official datasets

### 6.4 Keep Your Fork Updated

After your PR is merged (or periodically), update both repositories:

```bash
# Update Dataset fork
cd VesselVerse-Dataset
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
cd ..

# Update Framework fork
cd VesselVerse-Framework
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
cd ..
```

---

## 7. D-Expert Personal Folder

### What is D-Expert?

Your private contribution space within VesselVerse:

- **Location**: `VesselVerse-Dataset/datasets/D-Expert/`
- **Access**: Only you can write data (via your credentials)
- **Purpose**: Stage your work before submitting for review

### How it works:

1. **You create folders** and add your files
2. **DVC tracks the data** → uploads to your Google Drive
3. **Git tracks the structure** → `.dvc` pointers go to GitHub
4. **You submit a PR** → owner reviews your contribution
5. **If approved** → data may be moved to official datasets

### Best Practices:

✅ **Use descriptive folder names**:

- Good: `IXI_Manual_Annotations_Smith2026`
- Bad: `folder1`, `test`, `my_stuff`

✅ **Include documentation**:

```
MyAnnotations/
├── README.md          # What, how, why
├── methodology.pdf    # Detailed methods
└── data/
    ├── case001.nii.gz
    └── case002.nii.gz
```

✅ **Follow naming conventions**:

- Use underscores: `my_file_name.nii.gz`
- Include metadata: `case001_segmentation_method_date.nii.gz`

✅ **Test before uploading**:

- Load files in 3D Slicer
- Verify correct dimensions/orientation
- Check for artifacts

❌ **Don't upload**:

- Temporary files (`temp.nii.gz`)
- Large uncompressed files (compress with gzip)
- Duplicates or test data
- Sensitive/identifiable information

---

## 8. Troubleshooting

### Issue 1: Permission Error (403 Forbidden)

**Symptoms**: Error during `dvc push`

```
ERROR: failed to push data to the remote - 403 Forbidden
```

**Solutions**:

1. Verify correct credentials file selected during setup
2. Check Google Drive ID is correct
3. Ensure service account has write access to the folder
4. Re-run Initial Setup (option 1) if needed

---

### Issue 2: DVC Pull Fails

**Symptoms**: Data doesn't download

```
⚠️ ExpertVAL - Failed to download
```

**Solutions**:

1. Check internet connection
2. Verify `.dvc` files exist: `ls *.dvc`
3. Check DVC remotes: `cd VesselVerse-Dataset/datasets/D-IXI && dvc remote list`
4. Try pulling specific file: `dvc pull IXI_TOT.dvc`

---

### Issue 3: Git Push Rejected

**Symptoms**: Can't push commits

```
! [rejected]        main -> main (fetch first)
```

**Solutions**:

1. Pull first: `git pull`
2. Resolve any conflicts
3. Push again: `git push`

---

### Issue 4: Python Version Warnings

**Symptoms**:

```
FutureWarning: Python 3.9 is no longer supported
```

**Solutions**:

1. Delete virtual environment: `rm -rf VesselVerse-Dataset/.venv`
2. Install Python 3.12: `brew install python@3.12` (macOS)
3. Re-run script: `python vesselverseUser.py`
4. System will create new venv with Python 3.12

---

### Issue 5: Empty D-Expert Folder

**Symptoms**: No folders to upload

```
ℹ️ D-Expert is currently empty - no folders to upload
```

**This is normal!** Just means you haven't added data yet.

**Solution**:

1. Create folders: `mkdir VesselVerse-Dataset/datasets/D-Expert/MyWork`
2. Add your files: `cp /path/to/files/* VesselVerse-Dataset/datasets/D-Expert/MyWork/`
3. Run upload again

---

## 9. Advanced Tips

### Viewing DVC Status

Check what's changed before uploading:

```bash
cd VesselVerse-Dataset/datasets/D-Expert
dvc status
```

### Checking Git Status

See uncommitted changes:

```bash
git status
```

### Installing GitHub CLI (for automatic PRs)

**macOS**:

```bash
brew install gh
gh auth login
```

**Linux**:

```bash
sudo apt install gh
gh auth login
```

**Windows**:

```bash
winget install GitHub.cli
gh auth login
```

---

## 10. Getting Help

### Documentation

- **Developer Manual**: Technical details for advanced users
- **VIZ_PARAMS.md**: Visualization parameter configuration
- **STORAGE_CONFIGURATION.md**: Google Drive setup guide

### Support

- **GitHub Issues**: Report bugs or request features
- **Email**: Contact repository maintainer

### Useful Commands

```bash
# Check Python version
python --version    # or: python3 --version if needed

# Check Git version
git --version

# Check DVC version
dvc version

# View DVC remotes
cd VesselVerse-Dataset/datasets/D-IXI
dvc remote list

# View Git remotes
cd VesselVerse-Dataset
git remote -v
```

---

## 11. Summary

### Quick Reference

| Action            | Command                     | Option |
| ----------------- | --------------------------- | ------ |
| First-time setup  | `python vesselverseUser.py` | `[1]`  |
| Download datasets | `python vesselverseUser.py` | `[2]`  |
| Upload your data  | `python vesselverseUser.py` | `[3]`  |
| Submit for review | `python vesselverseUser.py` | `[4]`  |

### Workflow Summary

```
1. Create Workspace Folder (local)
   ↓
2. Fork Both Repositories (GitHub)
   ├─ VesselVerse-Dataset
   └─ VesselVerse-Framework
   ↓
3. Clone Your Forks (local)
   ├─ git clone YourUsername/VesselVerse-Dataset
   └─ git clone YourUsername/VesselVerse-Framework
   ↓
4. Add Upstream Remotes (local)
   ├─ Dataset: upstream → i-vesseg/VesselVerse-Dataset
   └─ Framework: upstream → i-vesseg/VesselVerse-Framework
   ↓
5. Configure Credentials (local)
   ├─ Place .json file in credentials/
   ├─ Receive Google Drive ID
   └─ Receive config files (if any)
   ↓
6. Initial Setup (option 1)
   ↓
7. Download Datasets (option 2) ← Optional
   ↓
8. Create Work in D-Expert (local)
   ├─ VesselVerse-Dataset/datasets/D-Expert/
   └─ Add your annotations/data
   ↓
9. Upload Data (option 3)
   ├─ DVC push → Your Google Drive
   └─ Git push → Your VesselVerse-Dataset fork
   ↓
10. Create Pull Request (option 4)
    ├─ Creates timestamped branch
    ├─ Pushes to your fork
    └─ Opens PR to i-vesseg/VesselVerse-Dataset
    ↓
11. Owner Reviews & Merges
    ↓
12. Keep Forks Updated
    ├─ git fetch/merge upstream (Dataset)
    └─ git fetch/merge upstream (Framework)
```

**Key Points**:

- ⚠️ **MUST fork both repos** - cloning alone won't allow git push
- 📁 **Dataset repo** - where DVC data lives and PRs are submitted
- 🛠️ **Framework repo** - where scripts are run from
- 🔄 **Upload happens in Dataset** - must be connected to YOUR fork

---

**Thank you for contributing to VesselVerse! 🎉**
