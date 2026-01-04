# VesselVerse Restoration Guide

## Backed Up Files

- ✅ config.sh
- ✅ vesselverseOwner.py
- ✅ vesselverseOwner.sh
- ✅ vesselverseUser.py
- ✅ vesselverseUser.sh
- ✅ credentials/ folder

## Step-by-Step Re-cloning Process

### 1. Remove the corrupted repository

```bash
cd ~/Desktop
rm -rf VesselVerse-Framework
```

### 2. Clone both repositories separately

```bash
# Clone Framework repo
git clone https://github.com/i-vesseg/VesselVerse-Framework.git

# Clone Dataset repo
git clone https://github.com/i-vesseg/VesselVerse-Dataset.git
```

### 3. Restore your custom files

#### To VesselVerse-Framework:

```bash
cp ~/Desktop/VesselVerse-BACKUP/config.sh ~/Desktop/VesselVerse-Framework/
cp ~/Desktop/VesselVerse-BACKUP/vesselverseOwner.py ~/Desktop/VesselVerse-Framework/
cp ~/Desktop/VesselVerse-BACKUP/vesselverseOwner.sh ~/Desktop/VesselVerse-Framework/
cp ~/Desktop/VesselVerse-BACKUP/vesselverseUser.py ~/Desktop/VesselVerse-Framework/
cp ~/Desktop/VesselVerse-BACKUP/vesselverseUser.sh ~/Desktop/VesselVerse-Framework/
cp -r ~/Desktop/VesselVerse-BACKUP/credentials ~/Desktop/VesselVerse-Framework/
```

#### Update config.sh paths:

Edit `~/Desktop/VesselVerse-Framework/config.sh` and change:

- `DATASET_PATH` to point to: `~/Desktop/VesselVerse-Dataset/datasets/D-$DATASET_NAME`
- Update any absolute paths as needed

### 4. Verify the setup

```bash
# Check Framework repo
cd ~/Desktop/VesselVerse-Framework
git remote -v
ls -la .git

# Check Dataset repo
cd ~/Desktop/VesselVerse-Dataset
git remote -v
ls -la .git
```

Both should now have their own `.git` folders!

### 5. Set up your branches

```bash
# Framework
cd ~/Desktop/VesselVerse-Framework
git checkout -b dev  # or your preferred branch

# Dataset
cd ~/Desktop/VesselVerse-Dataset
git checkout -b dev  # if needed
```

## Notes

- The two repositories are now **independent** as they should be
- Each has its own git tracking and history
- Update any scripts that reference paths between the repos
