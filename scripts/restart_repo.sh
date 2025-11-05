#!/bin/bash

# Load Config
config_path="$(dirname "$(dirname "$(realpath "$0")")")/config.sh"

if [ ! -f "$config_path" ]; then
    echo "Config file not found: $config_path"
    exit 1
fi

echo "Loading config.sh from $config_path"
source "$config_path"


# Ask for confirmation before proceeding and wait for enter
read -p "This will reset the repository to a fresh state. Are you sure? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting..."
    exit 1
fi

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
VV_MODULE_DIR="$(dirname "$(dirname "$(realpath "$0")")")/src/slicer_extension/VesselVerse"

cd "$(dirname "$(dirname "$(realpath "$0")")")"
cd datasets/D-$DATASET_NAME
echo "Changing directory to $(pwd)"

# First clean up all DVC and Git files/directories
rm -rf .dvc #.git                   # Remove DVC and Git directories
rm -f dvc.lock            # Remove DVC pipeline files
find . -name "*.dvc" -delete       # Remove all .dvc files

# Remove all data directories
rm */model_metadata/*                 # Remove metadata files
rm */ExpertAnnotations/*              # Remove ExpertAnnotations
rm */metadata/*                       # Remove metadata

# Initialize fresh Git repository
#git init

# Initialize fresh DVC
dvc init
dvc config core.autostage true

# Configure DVC remotes
dvc remote add -d storage gdrive://$database_ID #(DATABASE)
dvc remote add uploads gdrive://$user_upload_ID #(WHOLE UPLOADS)

# Add only input data directories to DVC tracking
# Note: We don't add STAPLE/ STAPLE_base or model_metadata since they're pipeline outputs
bash $SCRIPT_DIR/3_update_staple.sh "$DATASET_NAME" "$VV_MODULE_DIR"



echo ""
echo "Fresh repository setup with DVC configuration."
echo ""
echo "TO COMPLETE THE SETUP, RUN"
echo "$ git add ."
echo "$ git commit -m 'Initial Commit - DVC Setup'"
echo "dvc push"