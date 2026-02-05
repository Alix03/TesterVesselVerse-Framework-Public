# VesselVerse

**VesselVerse** is a collaborative platform for vessel segmentation dataset management, annotation, and reproducible research. It integrates DVC (Data Version Control), 3D Slicer, and automated workflows to simplify data sharing and contribution in medical imaging projects.

---

## 🚀 What is VesselVerse?

- **Unified framework** for managing, annotating, and sharing large medical imaging datasets
- **Automated scripts** for both users (contributors) and owners (maintainers)
- **DVC integration** for versioning large files with Google Drive as remote storage
- **3D Slicer extension** for expert annotation and visualization
- **Monorepo architecture**: all datasets and tools in a single repository for easy onboarding

---

## 📚 Documentation

- **[User Manual](USER_MANUAL.md)**: Step-by-step guide for contributors (downloading, annotating, uploading, submitting data)
- **[Developer Manual](DEVELOPER_MANUAL.md)**: Technical documentation for maintainers and advanced users (architecture, scripts, configuration, best practices)
- **[Visualization Parameters Guide](VIZ_PARAMS.md)**: How to save and share 3D Slicer visualization settings
- **[Framework API Reference](VesselVerse-Framework/docs/viz_params_README.md)**: Advanced usage and customization

---

## 🏗️ Project Structure

- **VesselVerse-Framework/**: Core scripts, 3D Slicer extension, utilities, and documentation
- **VesselVerse-Dataset/**: All datasets, each with independent DVC configuration
- **credentials/**: Service account credentials (not tracked in Git)
- **vesselverseOwner.py / vesselverseUser.py**: Central configuration scripts
- **config.py / config.sh**: Central configuration files

---

## ⚡ Quick Start

1. **Read the [User Manual](USER_MANUAL.md) or [Developer Manual](DEVELOPER_MANUAL.md)**
2. **Run the provided scripts** for setup, data download, annotation, and upload
3. **Use the 3D Slicer extension** for annotation and visualization
4. **Submit your work** via the automated Pull Request workflow

---

## 🤝 Contributing

- Fork the repository and follow the [User Manual](USER_MANUAL.md) for setup
- Use the provided scripts and 3D Slicer extension for your workflow
- Submit your contributions via Pull Request
- See the [Developer Manual](DEVELOPER_MANUAL.md) for advanced development and maintenance

---

For more details, see the full documentation linked above.
