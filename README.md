# VesselVerse Project

VesselVerse is a comprehensive framework for vessel segmentation dataset management and annotation, integrating DVC (Data Version Control), 3D Slicer, and collaborative annotation workflows.

## 📁 Project Structure

```
VesselVerse/
├── config.sh
├── vesselverseUser.sh
├── vesselverseOwner.sh
├── credentials/
│
├── VesselVerse-Framework/
│   ├── requirements.txt
│   ├── scripts/
│   ├── scripts_py/
│   ├── src/
│   ├── notebooks/
│   ├── docs/
│   └── VESSELVERSE_DATA_IXI/
│       └── data/
│           ├── A2V/                  # Artery-to-Vein predictions
│           ├── ExpertAnnotations/    # Expert manual annotations
│           ├── ExpertVAL/           # Expert validation set
│           ├── Filtering/           # Filtered segmentations
│           ├── IXI_TOT/             # Original IXI images
│           ├── metadata/            # Dataset metadata
│           ├── nnUNet/              # nnUNet predictions
│           ├── STAPLE/              # STAPLE consensus
│           ├── STAPLE_base/         # STAPLE baseline
│           └── StochasticAL/        # Stochastic Active Learning
│
└── VesselVerse-Dataset/             # Dataset repository with DVC
    ├── requirements.txt
    ├── toy_config.sh
    ├── scripts/
    └── datasets/                    # Datasets managed in monorepo with independent DVC configs
        ├── D-COW23MR/              # COW23MR dataset (12 tracked items)
        │   ├── .dvc/               # Independent DVC configuration
        │   └── *.dvc               # DVC tracked files
        ├── D-ITKTubeTK/            # ITKTubeTK dataset
        │   └── .dvc/
        ├── D-IXI/                  # IXI dataset (4 tracked items)
        │   ├── .dvc/
        │   └── *.dvc
        └── D-Prova/                # Test dataset (1 tracked item)
            └── .dvc/
```

## 🎯 Key Components

### 1. **User/Owner Scripts**

- **vesselverseUser.sh**: User-facing operations (download, upload, switch datasets)
- **vesselverseOwner.sh**: Owner operations (dataset management, user upload review)

### 2. **DVC Integration**

Each dataset in `VesselVerse-Dataset/datasets/` has independent DVC configuration:

- Single Git repository for entire project (monorepo architecture)
- Each dataset maintains separate `.dvc` directory
- Independent DVC remotes pointing to Google Drive storage
- Simplified workflow: single `git clone` for complete project setup

**Architecture Benefits:**

- No Git submodules required
- Single repository for all datasets
- Each dataset has isolated DVC tracking
- Simpler collaboration and onboarding

### 3. **3D Slicer Extension**

- Custom VesselVerse extension for annotation
- Integrated with dataset registry (`model_config.py`)
- Supports collaborative annotation workflows

### 4. **Data Management**

- **VESSELVERSE_DATA_IXI/**: Local data storage for IXI dataset
- Folder structure tracked in Git (via `.gitkeep`)
- Data files managed via DVC (not in Git)

## 🚀 Usage

### User Mode

```bash
bash vesselverseUser.sh
# Options:
# [1] Initial setup - Download datasets
# [2] Update current dataset
# [3] Upload modifications
# [4] Switch dataset
```

### Owner Mode

```bash
bash vesselverseOwner.sh
# Options:
# [1] Owner initial setup
# [2] Update dataset (incorporate user changes)
# [3] Review user uploads
```

### 3D Slicer

```bash
cd VesselVerse-Framework/scripts
bash launch_slicer.sh
```

## 📋 Requirements

- Python 3.12+
- DVC 3.64+
- 3D Slicer (for annotation)
- Google Cloud service account (for DVC remote access)

Install Python dependencies:

```bash
cd VesselVerse-Framework
pip install -r requirements.txt

cd ../VesselVerse-Dataset
pip install -r requirements.txt
```

## 🔑 Authentication

Google Cloud service account credentials are stored in `credentials/`:

- Used for DVC remote access to Google Drive
- Configure via `GOOGLE_APPLICATION_CREDENTIALS` environment variable

## 📝 Configuration

Main configuration in `config.sh`:

- Dataset paths
- Google Drive folder IDs
- Active dataset selection
- Credentials selection

## 🤝 Contributing

1. Use `vesselverseUser.sh` to download and work on datasets
2. Make annotations using 3D Slicer extension
3. Upload modifications via script option [3]
4. Owner reviews and incorporates changes

## 📄 License

See individual LICENSE files in Framework and Dataset directories.

---

## 🔄 Recent Updates

### Monorepo Architecture (January 2026)

The project was converted from individual Git repositories per dataset to a unified monorepo structure:

**Changes:**

- ✅ Removed `.git` directories from individual datasets (D-IXI, D-COW23MR, D-ITKTubeTK, D-Prova)
- ✅ All datasets now tracked in single main Git repository
- ✅ Each dataset maintains independent DVC configuration (`.dvc/`)
- ✅ Simplified `vesselverseUser.sh` and `vesselverseOwner.sh` scripts
- ✅ DVC initialization now uses `--no-scm` flag (no Git requirement per dataset)
- ✅ Removed Git submodule logic

**Benefits:**

- Single `git clone` for complete project setup
- Simplified collaboration workflow
- No submodule complexity
- DVC functionality unchanged (pull/push work identically)
- Easier onboarding for new contributors

**Migration:**

- Git history backed up in `.backup_git_datasets/`
- All DVC remotes maintained
- Zero downtime for data operations

---

**VesselVerse** - Collaborative Medical Image Segmentation Platform
