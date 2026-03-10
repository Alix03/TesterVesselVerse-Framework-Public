# VesselVerse

**VesselVerse** is a collaborative platform for vessel segmentation dataset management, annotation, and reproducible research. It integrates DVC (Data Version Control), 3D Slicer, and automated workflows to simplify data sharing and contribution in medical imaging projects.

---

## 🚀 What is VesselVerse?

- **Unified framework** for managing, annotating, and sharing large medical imaging datasets
- **Automated scripts** for both users (contributors) and owners (maintainers)
- **DVC integration** for versioning large files with Google Drive as remote storage
- **3D Slicer extension** for expert annotation and visualization
- **Clear Repository Architecture:**: strict separation between the Framework (functions & tools ONLY) and the Dataset (data management ONLY).

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

## 🏆 Impact & Results

[cite_start]Previously, users had to execute over 15 manual commands to set up the environment, leading to a high barrier to entry and confusion between Git and DVC tracking[cite: 30, 44, 45]. By developing automated CLI scripts (`vesselverseOwner.py` and `vesselverseUser.py`), this project achieved:

* [cite_start]**83% Setup Time Reduction:** Decreased initial setup from 30+ minutes to just 5 minutes[cite: 192].
* [cite_start]**80% Command Reduction:** Streamlined 15+ manual terminal commands into 3 simple menu selections[cite: 192].
* [cite_start]**Zero Technical Barrier:** Abstracted complex Git, DVC, and Google Drive interactions[cite: 192].
* [cite_start]**Fully Automated PRs:** Implemented 1-command automated Pull Request creation directly from the terminal[cite: 65, 192].
* [cite_start]**Significantly Reduced Error Rate:** Replaced manual typing with validated inputs[cite: 192].

---

## 👩‍💻 Author

[cite_start]**Alice Boccadifuoco** 
* [cite_start]EURECOM - Semester Project (February 2026) 
* [[LinkedIn](https://it.linkedin.com/in/alice-boccadifuoco-557454217)]

---

For more details, see the full documentation linked above.
