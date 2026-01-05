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
    └── datasets/                    # Individual dataset repositories traced with DVC
        ├── D-COW23MR/              # COW23MR dataset
        │   ├── .git/               # Independent Git repository
        │   ├── .dvc/               # DVC configuration
        │   └── *.dvc               # DVC tracked files
        ├── D-ITKTubeTK/            # ITKTubeTK dataset
        ├── D-IXI/                  # IXI dataset
        │   ├── .git/
        │   ├── .dvc/
        │   └── *.dvc
        └── D-Prova/                # Test dataset
```

## 🎯 Key Components

### 1. **User/Owner Scripts**

- **vesselverseUser.sh**: User-facing operations (download, upload, switch datasets)
- **vesselverseOwner.sh**: Owner operations (dataset management, user upload review)

### 2. **DVC Integration**

Each dataset in `VesselVerse-Dataset/datasets/` is an independent Git+DVC repository:

- Separate `.git` and `.dvc` directories
- Google Drive remote storage
- Individual version control per dataset

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

**VesselVerse** - Collaborative Medical Image Segmentation Platform
