#!/bin/bash

# VesselVerse Dataset - Owner Management Script
# Handles initial setup and dataset management for OWNER only

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate venv if it exists (fixes Python 3.9 importlib.metadata issue)
if [ -f "$REPO_ROOT/.venv/bin/activate" ]; then
    source "$REPO_ROOT/.venv/bin/activate" 2>/dev/null || true
fi

# Display header
owner_display_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}         VesselVerse Dataset Owner Manager         ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# Owner menu
owner_show_menu() {
    echo -e "${CYAN}What would you like to do?${NC}"
    echo ""
    echo "  [1] Initial Setup     - First time setup (configure credentials & download)"
    echo "  [2] Update Dataset    - Sync latest changes from remote"
    echo "  [3] Upload Dataset    - Push changes to the remote storage"
    echo "  [4] Review Uploads    - Download user contributions for review"
    echo "  [5] Exit"
    echo ""
}

######## Function 1 : Initial Setup

Initial_owner_setup() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Initial Setup - First Time Configuration        ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""

    # Step 1.1 : Check prerequisites
    echo -e "${YELLOW}[1/4] Checking prerequisites...${NC}"
    # python 3
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Error: Python 3 is not installed${NC}"
        echo "Please install Python 3.10+ first"
        exit 1
    fi
   # dvc
    if ! command -v dvc &> /dev/null; then
        echo -e "${YELLOW}⚠️  DVC is not installed. Installing now...${NC}"
        python3 -m pip install "dvc[gdrive]"
    fi

    # g-drive
    if ! python3 -c "import dvc_gdrive" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  DVC is installed but missing gdrive support. Installing now...${NC}"
        python3 -m pip install "dvc[gdrive]" >/dev/null 2>&1
    fi
    # git
    if ! command -v git &> /dev/null; then
        echo -e "${RED}❌ Error: Git is not installed${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ All prerequisites met${NC}"
    echo ""

    # Step 1.2 : Configure owner credentials
    echo -e "${YELLOW}[2/4] Configuring owner credentials...${NC}"
    
    # Look for config.sh file
    if [ ! -f "$REPO_ROOT/config.sh" ]; then
        echo -e "${RED}❌ Error: config.sh not found${NC}"
        exit 1
    fi
    
    # Look for credential files
    echo "Available credential files:"
    CRED_FILES=($(find "$REPO_ROOT/credentials" -name "*.json" 2>/dev/null))
    if [ ${#CRED_FILES[@]} -eq 0 ]; then
        echo -e "${RED}No credential files found. Please add a credential file first.${NC}"
        return
    fi
    
    # List credential files
    for i in "${!CRED_FILES[@]}"; do
        echo "  [$i] ${CRED_FILES[$i]}"
    done
    
    # Select file
    echo ""
    read -p "Select credential file number [0]: " CRED_CHOICE
    CRED_CHOICE=${CRED_CHOICE:-0}

    if [ $CRED_CHOICE -lt 0 ] || [ $CRED_CHOICE -ge ${#CRED_FILES[@]} ]; then
        echo -e "${RED}❌ Invalid selection${NC}"
        exit 1
    fi

    SELECTED_CRED="${CRED_FILES[$CRED_CHOICE]}"
    echo -e "${GREEN}✅ Using credentials: $SELECTED_CRED${NC}"
    
    # Update config.sh with selected credentials
    sed -i.bak "s|owner_auth_path=.*|owner_auth_path=\"$SELECTED_CRED\"|g" "$REPO_ROOT/config.sh"

    # Step 1.3 : Configure all datasets (DVC only - monorepo)
    echo -e "${YELLOW}[3/6] Initializing all datasets...${NC}"
    
    DATASETS_DIR="$REPO_ROOT/VesselVerse-Dataset/datasets"
    
    if [ ! -d "$DATASETS_DIR" ]; then
        echo -e "${RED}❌ Error: Datasets directory not found: $DATASETS_DIR${NC}"
        exit 1
    fi
    
    # Find all datasets
    ALL_DATASETS=($(find "$DATASETS_DIR" -maxdepth 1 -type d -name "D-*" | sort))
    
    if [ ${#ALL_DATASETS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No datasets found in $DATASETS_DIR${NC}"
        exit 1
    fi
    
    echo "Found ${#ALL_DATASETS[@]} dataset(s):"
    for dataset in "${ALL_DATASETS[@]}"; do
        echo "  • $(basename "$dataset")"
    done
    echo ""
    
    echo "Configuring DVC for each dataset..."
    echo ""
    
    # Load config for database IDs
    source "$REPO_ROOT/config.sh"
    
    for dataset_path in "${ALL_DATASETS[@]}"; do
        dataset_name=$(basename "$dataset_path")
        echo -e "${CYAN}► Processing: $dataset_name${NC}"
        
        cd "$dataset_path"
        
        # Initialize DVC if not present (no Git needed - monorepo)
        if [ ! -d ".dvc" ]; then
            dvc init --no-scm >/dev/null 2>&1
            dvc config core.autostage true >/dev/null 2>&1
            echo "  ✓ DVC initialized"
        else
            echo "  ✓ DVC already initialized"
        fi
        
        # Configure DVC remotes
        dvc remote list | grep -q "^storage" && dvc remote remove storage 2>/dev/null || true
        dvc remote list | grep -q "^uploads" && dvc remote remove uploads 2>/dev/null || true
        
        if [ -n "$database_ID" ] && [ -n "$SELECTED_CRED" ]; then
            dvc remote add -d storage "gdrive://${database_ID}" >/dev/null 2>&1
            dvc remote modify storage gdrive_service_account_json_file_path "$SELECTED_CRED" >/dev/null 2>&1
            dvc remote modify storage gdrive_use_service_account true >/dev/null 2>&1
            echo "  ✓ Storage remote configured"
        fi
        
        if [ -n "$user_upload_ID" ] && [ -n "$SELECTED_CRED" ]; then
            dvc remote add uploads "gdrive://${user_upload_ID}" >/dev/null 2>&1
            dvc remote modify uploads gdrive_service_account_json_file_path "$SELECTED_CRED" >/dev/null 2>&1
            dvc remote modify uploads gdrive_use_service_account true >/dev/null 2>&1
            echo "  ✓ Uploads remote configured"
        fi
        
        echo ""
    done
    
    cd "$REPO_ROOT"
    echo -e "${GREEN}✅ All datasets configured${NC}"
    echo ""

    # Step 1.4: Verify setup
    echo -e "${YELLOW}[4/6] Verifying setup...${NC}"
    
    # Check at least one dataset has DVC configured
    CONFIGURED_COUNT=0
    for dataset_path in "${ALL_DATASETS[@]}"; do
        cd "$dataset_path"
        if dvc remote list 2>/dev/null | grep -q "storage"; then
            ((CONFIGURED_COUNT++))
        fi
    done
    
    cd "$REPO_ROOT"
    
    if [ $CONFIGURED_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ $CONFIGURED_COUNT dataset(s) configured with DVC remotes${NC}"
    else
        echo -e "${RED}❌ Error: No datasets configured${NC}"
        exit 1
    fi
    echo ""
    
    # Step 1.5: Select default dataset
    echo -e "${YELLOW}[5/6] Selecting default dataset...${NC}"
    
    # Find datasets with .dvc files
    echo "Available datasets with tracked data:"
    DATASETS=()
    for dataset_dir in "$DATASETS_DIR/D-"*; do
        if [ -d "$dataset_dir" ]; then
            dataset_name=$(basename "$dataset_dir")
            DVC_COUNT=$(find "$dataset_dir" -maxdepth 1 -name "*.dvc" -type f 2>/dev/null | wc -l | tr -d ' ')
            if [ "$DVC_COUNT" -gt 0 ]; then
                DATASETS+=("$dataset_name")
                INDEX=$((${#DATASETS[@]} - 1))
                echo "  [$INDEX] ${dataset_name#D-} ($DVC_COUNT tracked items)"
            else
                echo "  [-] ${dataset_name#D-} (no tracked data yet)"
            fi
        fi
    done

    if [ ${#DATASETS[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No datasets with tracked data found yet${NC}"
        SELECTED_DATASET="IXI"  # Default
    else
        echo ""
        read -p "Select default dataset number [0]: " DATASET_CHOICE
        DATASET_CHOICE=${DATASET_CHOICE:-0}

        if [ $DATASET_CHOICE -lt 0 ] || [ $DATASET_CHOICE -ge ${#DATASETS[@]} ]; then
            echo -e "${RED}❌ Invalid selection${NC}"
            exit 1
        fi

        SELECTED_DATASET="${DATASETS[$DATASET_CHOICE]#D-}"
    fi
    
    echo -e "${GREEN}✅ Default dataset: $SELECTED_DATASET${NC}"

    # Update config.sh with selected dataset
    sed -i.bak "s|DATASET_NAME=.*|DATASET_NAME='$SELECTED_DATASET'|g" "$REPO_ROOT/config.sh"
    echo ""
    
    # Step 1.6: Final verification
    echo -e "${YELLOW}[6/6] Final verification...${NC}"
    
    # Check DVC status for all datasets
    echo -e "${CYAN}DVC status per dataset:${NC}"
    for dataset_path in "${ALL_DATASETS[@]}"; do
        dataset_name=$(basename "$dataset_path")
        cd "$dataset_path"
        HAS_DVC="❌"
        [ -d ".dvc" ] && HAS_DVC="✅"
        echo "  $dataset_name: DVC $HAS_DVC"
    done
    
    cd "$REPO_ROOT"
    echo ""

    # Summary
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}          Owner Setup Complete! 🎉${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Configuration Summary:${NC}"
    echo -e "  Credentials:       ${GREEN}$SELECTED_CRED${NC}"
    echo -e "  Default Dataset:   ${GREEN}$SELECTED_DATASET${NC}"
    echo -e "  Datasets Init:     ${GREEN}${#ALL_DATASETS[@]} total${NC}"
    echo -e "  Storage Remote:    ${GREEN}gdrive://$database_ID${NC}"
    echo -e "  Uploads Remote:    ${GREEN}gdrive://$user_upload_ID${NC}"
    echo ""
    echo -e "${CYAN}Initialized datasets:${NC}"
    for dataset_path in "${ALL_DATASETS[@]}"; do
        echo -e "  • $(basename "$dataset_path")"
    done
    echo ""
}

######## Function 2 : Update Dataset

owner_update_dataset() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Update Dataset - Owner Mode                     ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""

   # Step 2.1 : Check config
    if [ ! -f "$REPO_ROOT/config.sh" ]; then
        echo -e "${RED}❌ Error: config.sh not found${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi

    # Load config
    source "$REPO_ROOT/config.sh"
    
    if [ -z "$DATASET_NAME" ]; then
        echo -e "${RED}❌ Error: No dataset selected${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi
    
    echo -e "${CYAN}Active dataset: $DATASET_NAME${NC}"
    echo ""

    # Define dataset directory
    DATASET_DIR="$REPO_ROOT/VesselVerse-Dataset/datasets/D-$DATASET_NAME"
    
    if [ ! -d "$DATASET_DIR" ]; then
        echo -e "${RED}❌ Error: Dataset directory not found: $DATASET_DIR${NC}"
        return 1
    fi

    # Step 2.2 : Check DVC config in the dataset directory
    cd "$DATASET_DIR"
    
    if ! dvc remote list 2>/dev/null | grep -q "storage"; then
        echo -e "${RED}❌ Error: DVC remotes not configured for this dataset${NC}"
        echo "Run option [1] Initial Setup first"
        cd "$REPO_ROOT"
        return 1
    fi
    
    echo -e "${GREEN}✅ DVC remotes configured${NC}"
    echo ""

    # Step 2.3 : Update Git Repo
    echo -e "${YELLOW}[1/3] Updating Git repository...${NC}"
    
    git pull 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Warning: Git pull failed or had conflicts${NC}"
        echo "This dataset might not be tracked by Git remote yet"
    else
        echo -e "${GREEN}✅ Git repository updated${NC}"
    fi
    echo ""

    # Step 2.4: Check for tracked data
    echo -e "${YELLOW}[2/3] Checking for tracked data...${NC}"
    
    DVC_FILES=($(find . -maxdepth 1 -name "*.dvc" -type f 2>/dev/null))
    if [ ${#DVC_FILES[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No tracked data (.dvc files) found in this dataset${NC}"
        cd "$REPO_ROOT"
        return 0
    fi

    echo -e "Found ${#DVC_FILES[@]} tracked item(s)"
    echo ""
    echo ""
    
    # Step 2.5: Download updates
    echo -e "${YELLOW}[3/3] Updating dataset from remote...${NC}"
    echo "Syncing ${#DVC_FILES[@]} tracked items..."
    echo ""
    
    TOTAL_SUCCESS=0
    TOTAL_FAILED=0
    
    for dvc_file in "${DVC_FILES[@]}"; do
        dvc_name=$(basename "$dvc_file" .dvc)
        echo -e "${CYAN}Pulling: $dvc_name${NC}"
        dvc pull "$dvc_file"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}  ✅ $dvc_name downloaded${NC}"
            ((TOTAL_SUCCESS++))
        else
            echo -e "${YELLOW}  ⚠️  $dvc_name - Failed to download${NC}"
            ((TOTAL_FAILED++))
        fi
    done

    cd "$REPO_ROOT"
    echo ""

    if [ $TOTAL_FAILED -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Warning: $TOTAL_FAILED file(s) failed to download${NC}"
        echo "This is normal if some data is not yet available"
    else
        echo -e "${GREEN}✅ Dataset updated successfully${NC}"
    fi
    echo ""

    # Summary
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}          Update Complete! 🎉${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Update Summary:${NC}"
    echo -e "  Dataset:      ${GREEN}$DATASET_NAME${NC}"
    echo -e "  Items synced: ${GREEN}${#DVC_FILES[@]}${NC}"
    echo -e "  Successful:   ${GREEN}$TOTAL_SUCCESS${NC}"
    if [ $TOTAL_FAILED -gt 0 ]; then
        echo -e "  Failed:       ${YELLOW}$TOTAL_FAILED${NC}"
    fi
    echo ""
}

######## Function 3 : Upload Dataset Changes (Owner)

owner_upload_dataset() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Upload Dataset Changes - Owner Mode             ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

    # Step 3.1: Check config
    if [ ! -f "$REPO_ROOT/config.sh" ]; then
        echo -e "${RED}❌ Error: config.sh not found${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi

    # Load config
    source "$REPO_ROOT/config.sh"

    # Step 3.2: Check DVC config
    if ! dvc remote list | grep -q "storage"; then
        echo -e "${RED}❌ Error: DVC remotes not configured${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi

    # Step 3.3: Select target dataset (D-IXI, D-COW23MR, etc.)
    echo -e "${YELLOW}[1/5] Select target dataset...${NC}"
    
    DATASETS_BASE="$REPO_ROOT/VesselVerse-Dataset/datasets"
    
    # Find existing D-* directories
    AVAILABLE_DATASETS=()
    for dataset_dir in "$DATASETS_BASE"/D-*; do
        if [ -d "$dataset_dir" ]; then
            dataset_name=$(basename "$dataset_dir")
            AVAILABLE_DATASETS+=("$dataset_name")
        fi
    done
    
    echo "Available datasets:"
    for i in "${!AVAILABLE_DATASETS[@]}"; do
        echo "  [$i] ${AVAILABLE_DATASETS[$i]}"
    done
    echo "  [n] Create new dataset"
    echo ""
    
    read -p "Select dataset: " DATASET_CHOICE
    
    if [[ "$DATASET_CHOICE" == "n" || "$DATASET_CHOICE" == "N" ]]; then
        read -p "Enter new dataset name (without D- prefix): " NEW_DATASET_NAME
        SELECTED_DATASET="D-$NEW_DATASET_NAME"
        mkdir -p "$DATASETS_BASE/$SELECTED_DATASET"
        echo -e "${GREEN}✅ Created new dataset: $SELECTED_DATASET${NC}"
    elif [[ "$DATASET_CHOICE" =~ ^[0-9]+$ ]] && [ "$DATASET_CHOICE" -ge 0 ] && [ "$DATASET_CHOICE" -lt ${#AVAILABLE_DATASETS[@]} ]; then
        SELECTED_DATASET="${AVAILABLE_DATASETS[$DATASET_CHOICE]}"
    else
        echo -e "${RED}❌ Invalid selection${NC}"
        return 1
    fi
    
    DATASET_DIR="$DATASETS_BASE/$SELECTED_DATASET"
    echo -e "${GREEN}Target dataset: $SELECTED_DATASET${NC}"
    echo ""

    # TODO: Update database_ID based on selected dataset
    # case "$SELECTED_DATASET" in
    #     "D-IXI")
    #         database_ID='1Lt5rGwBPkmdXGeGmpNKrzZ07xJzY_yYv'
    #         user_upload_ID='1PoD3eV41h_EWb1uDuMNGlfIUg8gi5_8a'
    #         echo -e "${CYAN}Using IXI remote: gdrive://$database_ID${NC}"
    #         ;;
    #     "D-COW23MR")
    #         database_ID='1jBDBZb8MNNXpGGWe0nTeOLlK_KIIW60p'
    #         user_upload_ID='1mdgCXcgNuLtP6YkCNyWbkNCbPiG0AHzZ'  # SwiftCheetah for COW23MR
    #         echo -e "${CYAN}Using COW23MR remote: gdrive://$database_ID${NC}"
    #         ;;
    #     *)
    #         echo -e "${YELLOW}⚠️  Unknown dataset, using default remote from config.sh${NC}"
    #         ;;
    # esac
    # 
    # # Update DVC remotes with new database_ID
    # dvc remote modify storage url "gdrive://${database_ID}"
    # dvc remote modify uploads url "gdrive://${user_upload_ID}"
    # echo -e "${GREEN}✅ DVC remotes updated for $SELECTED_DATASET${NC}"
    # echo ""

    # Define source directory
    DATA_PATH="VESSELVERSE_DATA_IXI/data"
    DATA_DIR="$REPO_ROOT/$DATA_PATH"
    
    if [ ! -d "$DATA_DIR" ]; then
        echo -e "${RED}❌ Error: Data directory not found: $DATA_DIR${NC}"
        return 1
    fi
    
    echo -e "${CYAN}Source: $DATA_DIR${NC}"
    echo -e "${CYAN}Target: $DATASET_DIR${NC}"
    echo ""

    # Step 3.4: List available folders and let user select
    echo -e "${YELLOW}[2/5] Listing available folders...${NC}"
    cd "$DATA_DIR"
    
    # Find all subdirectories (excluding hidden ones)
    FOLDERS=()
    while IFS= read -r -d '' folder; do
        folder_name=$(basename "$folder")
        # Skip hidden folders
        if [[ ! "$folder_name" == .* ]]; then
            FOLDERS+=("$folder_name")
        fi
    done < <(find . -maxdepth 1 -type d ! -name "." -print0 | sort -z)
    
    if [ ${#FOLDERS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No folders found in $DATA_DIR${NC}"
        cd "$REPO_ROOT"
        return 1
    fi
    
    echo "Available folders (with data):"
    AVAILABLE_FOLDERS=()
    FOLDER_INDEX=0
    for folder in "${FOLDERS[@]}"; do
        # Check if folder has files
        FILE_COUNT=$(find "$folder" -type f 2>/dev/null | wc -l)
        if [ "$FILE_COUNT" -gt 0 ]; then
            AVAILABLE_FOLDERS+=("$folder")
            # Check if already tracked by DVC
            if [ -f "$folder.dvc" ]; then
                echo -e "  [$FOLDER_INDEX] $folder ${GREEN}(already tracked, $FILE_COUNT files)${NC}"
            else
                echo -e "  [$FOLDER_INDEX] $folder ${YELLOW}(not tracked, $FILE_COUNT files)${NC}"
            fi
            ((FOLDER_INDEX++))
        else
            echo -e "  ✗ $folder ${YELLOW}(empty, skipped)${NC}"
        fi
    done
    FOLDERS=("${AVAILABLE_FOLDERS[@]}")
    
    if [ ${#FOLDERS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No folders with data found${NC}"
        cd "$REPO_ROOT"
        return 1
    fi
    
    echo "  [a] All folders"
    echo ""
    
    read -p "Select folder(s) to upload (comma-separated numbers or 'a' for all): " FOLDER_CHOICE
    
    SELECTED_FOLDERS=()
    if [[ "$FOLDER_CHOICE" == "a" || "$FOLDER_CHOICE" == "A" ]]; then
        SELECTED_FOLDERS=("${FOLDERS[@]}")
    else
        IFS=',' read -ra CHOICES <<< "$FOLDER_CHOICE"
        for choice in "${CHOICES[@]}"; do
            choice=$(echo "$choice" | tr -d ' ')
            if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 0 ] && [ "$choice" -lt ${#FOLDERS[@]} ]; then
                SELECTED_FOLDERS+=("${FOLDERS[$choice]}")
            fi
        done
    fi
    
    if [ ${#SELECTED_FOLDERS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No valid folders selected${NC}"
        cd "$REPO_ROOT"
        return 1
    fi
    
    echo -e "${GREEN}✅ Selected ${#SELECTED_FOLDERS[@]} folder(s) for upload${NC}"
    echo ""

    # Step 3.4: Track folders with DVC (in DATA_DIR)
    echo -e "${YELLOW}[2/7] Adding folders to DVC...${NC}"
    
    cd "$DATA_DIR"
    
    TRACKED_FOLDERS=()
    for folder in "${SELECTED_FOLDERS[@]}"; do
        echo -e "${CYAN}Processing: $folder${NC}"
        
        # Add to DVC (this creates folder.dvc and updates .gitignore)
        echo "  Running: dvc add $folder"
        dvc add "$folder"
        if [ $? -eq 0 ]; then
            echo -e "  ${GREEN}✅ Added $folder to DVC${NC}"
            TRACKED_FOLDERS+=("$folder")
        else
            echo -e "  ${RED}❌ Failed to add $folder to DVC${NC}"
        fi
    done
    echo ""

    if [ ${#TRACKED_FOLDERS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No folders were tracked${NC}"
        cd "$REPO_ROOT"
        return 1
    fi

    # Step 3.5: Stage .dvc files and .gitignore for Git (in DATA_DIR)
    echo -e "${YELLOW}[3/7] Staging .dvc files and .gitignore for Git...${NC}"
    
    for folder in "${TRACKED_FOLDERS[@]}"; do
        if [ -f "$folder.dvc" ]; then
            echo "  Running: git add $folder.dvc"
            git add "$folder.dvc"
        fi
    done
    echo "  Running: git add .gitignore"
    git add .gitignore 2>/dev/null || true
    
    echo -e "${GREEN}✅ Files staged${NC}"
    echo ""

    # Step 3.6: Commit to Git (from DATA_DIR)
    echo -e "${YELLOW}[4/7] Committing to Git...${NC}"
    
    read -p "Enter commit message for .dvc files: " COMMIT_MSG
    COMMIT_MSG=${COMMIT_MSG:-"Track data with DVC"}
    
    if git diff --cached --quiet; then
        echo -e "${YELLOW}⚠️  No changes to commit${NC}"
    else
        echo "  Running: git commit -m \"$COMMIT_MSG\""
        git commit -m "$COMMIT_MSG"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Changes committed to Git${NC}"
        else
            echo -e "${RED}❌ Git commit failed${NC}"
            cd "$REPO_ROOT"
            return 1
        fi
    fi
    echo ""

    # Step 3.7: Push data to DVC remote (from DATASET_DIR)
    echo -e "${YELLOW}[5/7] Copying .dvc files to dataset directory...${NC}"
    
    # Copy .dvc files to the target dataset directory
    for folder in "${TRACKED_FOLDERS[@]}"; do
        DVC_FILE="$DATA_DIR/$folder.dvc"
        if [ -f "$DVC_FILE" ]; then
            echo "  Copying: $folder.dvc -> $DATASET_DIR/"
            cp "$DVC_FILE" "$DATASET_DIR/"
        fi
    done
    
    echo -e "${GREEN}✅ .dvc files copied${NC}"
    echo ""
    
    # Step 3.8: Push data to DVC remote (from DATASET_DIR)
    echo -e "${YELLOW}[6/7] Pushing data to DVC remote...${NC}"
    echo "This may take a while depending on data size..."
    echo ""
    
    # Push from repo root where DVC remotes are configured
    cd "$REPO_ROOT"
    
    PUSH_FAILED=0
    for folder in "${TRACKED_FOLDERS[@]}"; do
        # Use the .dvc file from DATA_DIR (original location)
        DVC_FILE="$DATA_DIR/$folder.dvc"
        if [ -f "$DVC_FILE" ]; then
            echo -e "${CYAN}Pushing: $folder${NC}"
            dvc push "$DVC_FILE"
            if [ $? -ne 0 ]; then
                echo -e "${RED}❌ Failed to push $folder${NC}"
                PUSH_FAILED=1
            else
                echo -e "${GREEN}✅ $folder pushed to remote${NC}"
            fi
        fi
    done
    
    if [ $PUSH_FAILED -eq 1 ]; then
        echo -e "${YELLOW}⚠️  Some files failed to push${NC}"
        echo -e "${YELLOW}Possible reasons:${NC}"
        echo "  • Your credentials may not have write permissions"
        echo "  • Network connection issues"
        echo "  • Google Drive quota exceeded"
        cd "$REPO_ROOT"
        return 1
    else
        echo -e "${GREEN}✅ All selected data pushed to DVC remote${NC}"
    fi
    echo ""

    # Step 3.9: Stage and push .dvc files to Git remote
    echo -e "${YELLOW}[7/7] Pushing .dvc files to Git remote...${NC}"
    
    cd "$REPO_ROOT"
    
    # Stage the .dvc files in the dataset directory
    for folder in "${TRACKED_FOLDERS[@]}"; do
        DVC_FILE="VesselVerse-Dataset/datasets/$SELECTED_DATASET/$folder.dvc"
        if [ -f "$DVC_FILE" ]; then
            echo "  Running: git add $DVC_FILE"
            git add "$DVC_FILE"
        fi
    done
    
    # Commit if there are changes
    if git diff --cached --quiet; then
        echo -e "${YELLOW}⚠️  No new .dvc files to commit in dataset directory${NC}"
    else
        echo "  Running: git commit -m \"Add .dvc files to $SELECTED_DATASET\""
        git commit -m "Add .dvc files to $SELECTED_DATASET"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ .dvc files committed${NC}"
        fi
    fi
    
    # Push to Git
    echo "  Running: git push"
    git push
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Pushed to Git remote${NC}"
    else
        echo -e "${YELLOW}⚠️  Git push failed. Push manually later with: git push${NC}"
    fi
    
    cd "$REPO_ROOT"
    echo ""

    # Summary
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}          Upload Complete! 🎉${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Upload Summary:${NC}"
    echo -e "  Source Directory:  ${GREEN}$DATA_PATH${NC}"
    echo -e "  Dataset Directory: ${GREEN}$DATASET_DIR${NC}"
    echo -e "  Folders Uploaded:  ${GREEN}${#TRACKED_FOLDERS[@]}${NC}"
    for folder in "${TRACKED_FOLDERS[@]}"; do
        echo -e "    • $folder"
    done
    echo ""
    echo -e "${BLUE}What happened:${NC}"
    echo -e "  ✅ Data tracked with DVC (created .dvc files)"
    echo -e "  ✅ .dvc files and .gitignore committed to Git"
    echo -e "  ✅ Data pushed to DVC remote storage"
    echo -e "  ✅ .dvc files pushed to Git remote"
    echo ""
    echo -e "${CYAN}Collaborators can now:${NC}"
    echo -e "  1. Run: git pull"
    echo -e "  2. Organize data (using notebook)"
    echo -e "  3. Run: dvc pull"
    echo ""
}

######## Function 4 : Review User Uploads (Owner)

owner_review_user_uploads() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Review User Uploads - Owner Mode                ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""

    # Step 4.1: Check config
    if [ ! -f "$REPO_ROOT/config.sh" ]; then
        echo -e "${RED}❌ Error: config.sh not found${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi

    # Load config
    source "$REPO_ROOT/config.sh"

    # Step 4.2: Check DVC config
    if ! dvc remote list | grep -q "uploads"; then
        echo -e "${RED}❌ Error: Uploads remote not configured${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi

    echo -e "${YELLOW}ℹ️  Review Information${NC}"
    echo -e "  This will download data that users have uploaded to the shared folder."
    echo -e "  Download source: ${CYAN}uploads (gdrive://$user_upload_ID)${NC}"
    echo ""

    DATA_PATH="VESSELVERSE_DATA_IXI/data"
    DATA_DIR="$REPO_ROOT/$DATA_PATH"

    # Step 4.3: Update Git first to get .dvc files
    echo -e "${YELLOW}[1/3] Updating Git repository (to get .dvc pointer files)...${NC}"
    cd "$REPO_ROOT"
    git pull
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Git repository updated${NC}"
    else
        echo -e "${YELLOW}⚠️  Git pull had issues, continuing anyway...${NC}"
    fi
    echo ""

    # Step 4.4: Restore any deleted .dvc files
    echo -e "${YELLOW}[2/3] Restoring .dvc files if needed...${NC}"
    cd "$DATA_DIR"
    
    # Check if any .dvc files were deleted and restore them
    DELETED_DVC=$(git status --short 2>/dev/null | grep "\.dvc$" | grep "^ D\|^D " | wc -l | tr -d ' ')
    if [ "$DELETED_DVC" -gt 0 ]; then
        echo "  Restoring $DELETED_DVC deleted .dvc file(s)..."
        git restore *.dvc 2>/dev/null || git checkout -- *.dvc 2>/dev/null || true
        echo -e "${GREEN}✅ .dvc files restored${NC}"
    else
        echo -e "${GREEN}✅ All .dvc files present${NC}"
    fi
    
    # Count .dvc files
    DVC_COUNT=$(find "$DATA_DIR" -maxdepth 1 -name "*.dvc" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  Found $DVC_COUNT tracked item(s)"
    echo ""

    # Step 4.5: Pull from uploads remote
    echo -e "${YELLOW}[3/3] Downloading from user uploads remote...${NC}"
    echo -e "Pulling from remote: ${CYAN}uploads (gdrive://$user_upload_ID)${NC}"
    echo "This may take a while depending on data size..."
    echo ""
    
    cd "$REPO_ROOT"
    
    # Pull from uploads remote
    dvc pull -r uploads 2>&1
    PULL_RESULT=$?
    
    echo ""

    # Summary
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    if [ $PULL_RESULT -eq 0 ]; then
        echo -e "${GREEN}          Download Complete! 🎉${NC}"
    else
        echo -e "${YELLOW}          Download Finished${NC}"
        echo -e "${YELLOW}  (Some files may only exist in main storage, not uploads)${NC}"
    fi
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Review Summary:${NC}"
    echo -e "  Source Remote:     ${CYAN}uploads (gdrive://$user_upload_ID)${NC}"
    echo -e "  Destination:       ${GREEN}$DATA_PATH${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  Note:${NC}"
    echo -e "  Only files that users uploaded to 'uploads' remote will be downloaded."
    echo -e "  Files that only exist in main 'storage' will show as errors (this is normal)."
    echo ""
    echo -e "${YELLOW}ℹ️  Next steps:${NC}"
    echo -e "  • Review the downloaded data in $DATA_PATH"
    echo -e "  • If approved, use option [3] Upload Dataset to push to main storage"
    echo ""
}


# Main execution for owner
owner_main() {
    owner_display_header
    while true; do
        echo ""
        owner_show_menu
        read -p "Enter your choice [1-5]: " owner_choice
        case $owner_choice in
            1)
                Initial_owner_setup
                ;;
            2)
                owner_update_dataset
                ;;
            3)
                owner_upload_dataset
                ;;
            4)
                owner_review_user_uploads
                ;;
            5)
                echo -e "${BLUE}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid option. Please select 1-5${NC}"
                ;;
        esac
        echo ""
        read -p "Press Enter to continue..." dummy
    done
}

# Run main
owner_main "$@"