#!/bin/bash

# VesselVerse Dataset - User Management Script
# Handles initial setup and dataset management for USER only

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Display header
user_display_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}         VesselVerse Dataset User Manager          ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
}

# User menu
user_show_menu() {
    echo -e "${CYAN}What would you like to do?${NC}"
    echo ""
    echo "  [1] Initial Setup     - First time setup (configure credentials & download)"
    echo "  [2] Update Dataset    - Sync latest changes from remote"
    echo "  [3] Upload Data       - Upload your modifications to the shared folder"
    echo "  [4] Switch Dataset    - Change to a different dataset"
    echo "  [5] Exit"
    echo ""
}

######## Function 1 : Initial Setup

user_initial_setup() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Initial Setup - First Time Configuration        ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""

    # Step 1.1 : Check prerequisites
    echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"
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

    # Step 1.2 : Configure user credentials
    echo -e "${YELLOW}[2/6] Configuring user credentials...${NC}"
    
    # Look for config.sh file
    if [ ! -f "$REPO_ROOT/config.sh" ]; then
        echo -e "${RED}❌ Error: config.sh not found${NC}"
        return 1
    fi
    
    # Look for credential files
    echo "Available credential files:"
    CRED_FILES=($(find "$REPO_ROOT/credentials" -name "*.json" 2>/dev/null))
    if [ ${#CRED_FILES[@]} -eq 0 ]; then
        echo -e "${RED}❌ Error: No credential files found in credentials/${NC}"
        echo "Please contact dataset maintainers to obtain credentials"
        return 1
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
        return 1
    fi

    SELECTED_CRED="${CRED_FILES[$CRED_CHOICE]}"
    echo -e "${GREEN}✅ Using credentials: $SELECTED_CRED${NC}"
    
    # Update config.sh with selected credentials
    sed -i.bak "s|user_auth_path=.*|user_auth_path=\"$SELECTED_CRED\"|g" "$REPO_ROOT/config.sh"
    echo ""

    # Step 1.3 : Initialize all datasets (Git + DVC)
    echo -e "${YELLOW}[3/8] Initializing all datasets...${NC}"
    
    DATASETS_DIR="$REPO_ROOT/VesselVerse-Dataset/datasets"
    
    if [ ! -d "$DATASETS_DIR" ]; then
        echo -e "${RED}❌ Error: Datasets directory not found: $DATASETS_DIR${NC}"
        return 1
    fi
    
    # Find all datasets
    ALL_DATASETS=($(find "$DATASETS_DIR" -maxdepth 1 -type d -name "D-*" | sort))
    
    if [ ${#ALL_DATASETS[@]} -eq 0 ]; then
        echo -e "${RED}❌ No datasets found in $DATASETS_DIR${NC}"
        return 1
    fi
    
    echo "Found ${#ALL_DATASETS[@]} dataset(s):"
    for dataset in "${ALL_DATASETS[@]}"; do
        echo "  • $(basename "$dataset")"
    done
    echo ""
    
    echo "Initializing Git and DVC for each dataset..."
    echo ""
    
    # Load config for database IDs
    source "$REPO_ROOT/config.sh"
    
    for dataset_path in "${ALL_DATASETS[@]}"; do
        dataset_name=$(basename "$dataset_path")
        echo -e "${CYAN}► Processing: $dataset_name${NC}"
        
        cd "$dataset_path"
        
        # Initialize Git if not present
        if [ ! -d ".git" ]; then
            git init >/dev/null 2>&1
            echo "  ✓ Git initialized"
        else
            echo "  ✓ Git already initialized"
        fi
        
        # Initialize DVC if not present
        if [ ! -d ".dvc" ]; then
            dvc init >/dev/null 2>&1
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
    echo -e "${GREEN}✅ All datasets initialized${NC}"
    echo ""

    # Step 1.4 : Select dataset to use
    echo -e "${YELLOW}[4/8] Selecting active dataset...${NC}"
    
    # Find datasets with .dvc files
    echo "Datasets with tracked data:"
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
        echo "You can add data later and pull it."
        SELECTED_DATASET="IXI"  # Default
    else
        echo ""
        read -p "Select dataset number [0]: " DATASET_CHOICE
        DATASET_CHOICE=${DATASET_CHOICE:-0}

        if [ $DATASET_CHOICE -lt 0 ] || [ $DATASET_CHOICE -ge ${#DATASETS[@]} ]; then
            echo -e "${RED}❌ Invalid selection${NC}"
            return 1
        fi

        SELECTED_DATASET="${DATASETS[$DATASET_CHOICE]#D-}"
    fi
    
    echo -e "${GREEN}✅ Active dataset: $SELECTED_DATASET${NC}"

    # Update config.sh with selected dataset
    sed -i.bak "s|DATASET_NAME=.*|DATASET_NAME='$SELECTED_DATASET'|g" "$REPO_ROOT/config.sh"
    echo ""

    # Step 1.5 : Verify setup
    echo -e "${YELLOW}[5/8] Verifying setup...${NC}"
    
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
        return 1
    fi
    echo ""

    # Step 1.6: Download dataset
    echo -e "${YELLOW}[6/8] Downloading selected dataset...${NC}"

    # Use the selected dataset directory
    SELECTED_DATASET_DIR="$DATASETS_DIR/D-$SELECTED_DATASET"
    
    if [ ! -d "$SELECTED_DATASET_DIR" ]; then
        echo -e "${YELLOW}⚠️  Dataset directory not found: $SELECTED_DATASET_DIR${NC}"
        echo "Skipping download step."
        echo ""
    else
        cd "$SELECTED_DATASET_DIR"
        DVC_FILES=($(find . -maxdepth 1 -name "*.dvc" -type f 2>/dev/null))

        if [ ${#DVC_FILES[@]} -eq 0 ]; then
            echo -e "${YELLOW}⚠️  No tracked data (.dvc files) found in this dataset${NC}"
            echo "This might be a test dataset or not yet configured for DVC."
            echo "Skipping download step."
            echo ""
        else
            echo "Found ${#DVC_FILES[@]} data items to download for $SELECTED_DATASET"
            echo "This may take a while depending on dataset size and network speed"
            echo ""

            read -p "Do you want to download the full dataset now? (y/n) [y]: " DOWNLOAD_NOW
            DOWNLOAD_NOW=${DOWNLOAD_NOW:-y}

            if [[ "$DOWNLOAD_NOW" =~ ^[Yy]$ ]]; then
                echo -e "${BLUE}Downloading all data...${NC}"
                
                TOTAL_SUCCESS=0
                TOTAL_FAILED=0
                
                for dvc_file in "${DVC_FILES[@]}"; do
                    dvc_name=$(basename "$dvc_file" .dvc)
                    echo -e "${CYAN}Pulling: $dvc_name${NC}"
                    dvc pull "$dvc_file"
                    if [ $? -eq 0 ]; then
                        ((TOTAL_SUCCESS++))
                    else
                        ((TOTAL_FAILED++))
                    fi
                done
                
                if [ $TOTAL_FAILED -gt 0 ]; then
                    echo -e "${YELLOW}⚠️  Warning: $TOTAL_FAILED file(s) failed to download${NC}"
                    echo "This is normal if some data is not yet available or is excluded."
                else
                    echo -e "${GREEN}✅ Dataset downloaded successfully${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  Skipping download. You can download later with option [2] Update Dataset${NC}"
            fi
        fi
        
        cd "$REPO_ROOT"
    fi
    echo ""

    # Step 1.7: Final verification
    echo -e "${YELLOW}[7/8] Final verification...${NC}"
    
    DATASET_PATH="$DATASETS_DIR/D-$SELECTED_DATASET"
    if [ -d "$DATASET_PATH" ]; then
        echo -e "${GREEN}✅ Dataset directory exists: $DATASET_PATH${NC}"
    else
        echo -e "${YELLOW}⚠️  Dataset directory not found${NC}"
    fi
    
    # Check Git status for all datasets
    echo -e "${CYAN}Git/DVC status per dataset:${NC}"
    for dataset_path in "${ALL_DATASETS[@]}"; do
        dataset_name=$(basename "$dataset_path")
        cd "$dataset_path"
        HAS_GIT="❌"
        HAS_DVC="❌"
        [ -d ".git" ] && HAS_GIT="✅"
        [ -d ".dvc" ] && HAS_DVC="✅"
        echo "  $dataset_name: Git $HAS_GIT | DVC $HAS_DVC"
    done
    
    cd "$REPO_ROOT"
    echo ""

    # Step 1.8: Summary
    echo -e "${YELLOW}[8/8] Setup Summary${NC}"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}          User Setup Complete! 🎉${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Configuration Summary:${NC}"
    echo -e "  Credentials:       ${GREEN}$SELECTED_CRED${NC}"
    echo -e "  Active Dataset:    ${GREEN}$SELECTED_DATASET${NC}"
    echo -e "  Dataset Path:      ${GREEN}$DATASET_PATH${NC}"
    echo -e "  Datasets Init:     ${GREEN}${#ALL_DATASETS[@]} total${NC}"
    echo ""
    echo -e "${CYAN}Initialized datasets:${NC}"
    for dataset_path in "${ALL_DATASETS[@]}"; do
        echo -e "  • $(basename "$dataset_path")"
    done
    echo ""
}

######## Function 2 : Update Dataset

user_update_dataset() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Update Dataset - User Mode                      ${NC}"
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

    # Step 2.3 : Update Git repo (for .dvc files)
    echo -e "${YELLOW}[1/3] Updating Git repository...${NC}"
    
    git pull 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Warning: Git pull failed or had conflicts${NC}"
        echo "This dataset might not be tracked by Git remote yet"
    else
        echo -e "${GREEN}✅ Git repository updated${NC}"
    fi
    echo ""

    # Step 2.4 : Download updates from DVC
    echo -e "${YELLOW}[2/3] Checking for tracked data...${NC}"
    
    DVC_FILES=($(find . -maxdepth 1 -name "*.dvc" -type f 2>/dev/null))
    if [ ${#DVC_FILES[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No tracked data (.dvc files) found in this dataset${NC}"
        cd "$REPO_ROOT"
        return 0
    fi

    echo -e "Found ${#DVC_FILES[@]} tracked item(s)"
    echo ""
    
    # Step 2.5 : Download updates
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

######## Function 3 : Switch Dataset

user_switch_dataset() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Switch Dataset - User Mode                      ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    
    # Step 3.1 : Check config
    if [ ! -f "$REPO_ROOT/config.sh" ]; then
        echo -e "${RED}❌ Error: config.sh not found${NC}"
        echo "Run option [1] Initial Setup first"
        return 1
    fi

    # Load current config
    source "$REPO_ROOT/config.sh"
    
    if [ -n "$DATASET_NAME" ]; then
        echo -e "Current dataset: ${YELLOW}$DATASET_NAME${NC}"
    else
        echo -e "${YELLOW}No dataset currently configured${NC}"
    fi
    echo ""

    # Step 3.2 : Find available datasets
    DATASETS=()
    for dataset_dir in "$REPO_ROOT/VesselVerse-Dataset/datasets/D-"*; do
        if [ -d "$dataset_dir" ]; then
            dataset_name=$(basename "$dataset_dir")
            if find "$dataset_dir" -maxdepth 1 -name "*.dvc" -type f | grep -q .; then
                DATASETS+=("$dataset_name")
            fi
        fi
    done

    if [ ${#DATASETS[@]} -eq 0 ]; then
        echo -e "${RED}❌ Error: No datasets with tracked data found${NC}"
        return 1
    fi

    echo "Available datasets:"
    for i in "${!DATASETS[@]}"; do
        DATASET_NAME_DISPLAY="${DATASETS[$i]#D-}"
        DVC_COUNT=$(find "$REPO_ROOT/VesselVerse-Dataset/datasets/${DATASETS[$i]}" -maxdepth 1 -name "*.dvc" -type f | wc -l | tr -d ' ')
        echo "  [$i] $DATASET_NAME_DISPLAY ($DVC_COUNT tracked items)"
    done

    # Step 3.3 : Choose dataset and set it in config.sh
    echo ""
    read -p "Select dataset number [0]: " DATASET_CHOICE
    DATASET_CHOICE=${DATASET_CHOICE:-0}

    if [ $DATASET_CHOICE -lt 0 ] || [ $DATASET_CHOICE -ge ${#DATASETS[@]} ]; then
        echo -e "${RED}❌ Invalid selection${NC}"
        return 1
    fi

    SELECTED_DATASET="${DATASETS[$DATASET_CHOICE]#D-}"
    
    # Update config.sh
    sed -i.bak "s|DATASET_NAME=.*|DATASET_NAME='$SELECTED_DATASET'|g" "$REPO_ROOT/config.sh"
    
    echo -e "${GREEN}✅ Switched to dataset: $SELECTED_DATASET${NC}"
    echo ""
    
    # Step 3.4 : Download dataset
    read -p "Do you want to download this dataset now? (y/n) [y]: " DOWNLOAD_NOW
    DOWNLOAD_NOW=${DOWNLOAD_NOW:-y}

    if [[ "$DOWNLOAD_NOW" =~ ^[Yy]$ ]]; then
        # Use the dataset directory where DVC files are located
        DATASET_DIR="$REPO_ROOT/VesselVerse-Dataset/datasets/D-$SELECTED_DATASET"
        echo -e "${BLUE}Downloading dataset from: $DATASET_DIR${NC}"
        
        if [ ! -d "$DATASET_DIR" ]; then
            echo -e "${RED}❌ Error: Dataset directory not found: $DATASET_DIR${NC}"
        else
            cd "$DATASET_DIR"
            
            # Find .dvc files in the dataset directory
            DVC_FILES=($(find . -maxdepth 1 -name "*.dvc" -type f 2>/dev/null))
            
            if [ ${#DVC_FILES[@]} -eq 0 ]; then
                echo -e "${YELLOW}⚠️  No tracked data (.dvc files) found in this dataset${NC}"
            else
                echo "Found ${#DVC_FILES[@]} tracked item(s)"
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
                
                echo ""
                if [ $TOTAL_FAILED -gt 0 ]; then
                    echo -e "${YELLOW}⚠️  Warning: $TOTAL_FAILED file(s) failed to download${NC}"
                else
                    echo -e "${GREEN}✅ Dataset downloaded successfully${NC}"
                fi
            fi
            
            cd "$REPO_ROOT"
        fi
    fi
    echo ""
}

######## Function 4 : Upload Data (User)

user_upload_data() {
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}   Upload Data - User Mode                         ${NC}"
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

    # Step 4.2: Check DVC config in the dataset directory
    cd "$DATASET_DIR"
    
    if ! dvc remote list 2>/dev/null | grep -q "uploads"; then
        echo -e "${RED}❌ Error: Upload remote not configured${NC}"
        echo "Run option [1] Initial Setup first"
        cd "$REPO_ROOT"
        return 1
    fi
    
    echo -e "${GREEN}✅ DVC remotes configured${NC}"
    echo ""

    echo -e "${YELLOW}ℹ️  Upload Information${NC}"
    echo -e "  Your data will be uploaded to the shared 'uploads' folder."
    echo -e "  The dataset owner will review and integrate your contributions."
    echo -e "  Upload destination: ${CYAN}gdrive://$user_upload_ID${NC}"
    echo ""

    # Step 4.3: Use dataset directory as source
    # Data tracked by DVC is in the same directory as the .dvc files
    DATA_DIR="$DATASET_DIR"
    
    echo -e "${CYAN}Source: $DATA_DIR${NC}"
    echo ""

    # Step 4.4: List available folders and let user select
    echo -e "${YELLOW}[1/4] Listing available folders/files...${NC}"
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
    
    echo "Available folders:"
    for i in "${!FOLDERS[@]}"; do
        folder="${FOLDERS[$i]}"
        # Check if already tracked by DVC
        if [ -f "$folder.dvc" ]; then
            echo -e "  [$i] $folder ${GREEN}(already tracked)${NC}"
        else
            echo -e "  [$i] $folder ${YELLOW}(not tracked)${NC}"
        fi
    done
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

    # Step 4.5: Track folders with DVC (in DATA_DIR)
    echo -e "${YELLOW}[2/4] Adding folders to DVC...${NC}"
    
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

    # Step 4.6: Stage .dvc files and .gitignore for Git (in DATA_DIR)
    echo -e "${YELLOW}[3/4] Staging .dvc files for Git...${NC}"
    
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

    # Step 4.7: Commit to Git
    echo -e "${YELLOW}[4/4] Committing and pushing...${NC}"
    
    read -p "Enter commit message [User upload: data contribution]: " COMMIT_MSG
    COMMIT_MSG=${COMMIT_MSG:-"User upload: data contribution"}
    
    cd "$REPO_ROOT"
    if git diff --cached --quiet; then
        echo -e "${YELLOW}⚠️  No changes to commit${NC}"
    else
        echo "  Running: git commit -m \"$COMMIT_MSG\""
        git commit -m "$COMMIT_MSG"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Changes committed to Git${NC}"
        else
            echo -e "${RED}❌ Git commit failed${NC}"
        fi
    fi
    echo ""

    # Step 4.8: Push ONLY selected folders to uploads remote
    echo -e "${BLUE}━━━ Pushing data to uploads remote ━━━${NC}"
    echo -e "Pushing to remote: ${CYAN}uploads (gdrive://$user_upload_ID)${NC}"
    echo "This may take a while depending on data size..."
    echo ""
    
    cd "$DATA_DIR"
    
    PUSH_SUCCESS=0
    PUSH_FAILED=0
    
    for folder in "${TRACKED_FOLDERS[@]}"; do
        DVC_FILE="$folder.dvc"
        if [ -f "$DVC_FILE" ]; then
            echo -e "${CYAN}Uploading: $folder${NC}"
            # Push to 'uploads' remote (NOT the default 'storage')
            dvc push "$DVC_FILE" -r uploads
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}  ✅ $folder uploaded${NC}"
                ((PUSH_SUCCESS++))
            else
                echo -e "${RED}  ❌ Failed to upload $folder${NC}"
                ((PUSH_FAILED++))
            fi
        fi
    done
    
    cd "$REPO_ROOT"
    echo ""

    # Summary
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}          Upload Complete! 🎉${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${BLUE}Upload Summary:${NC}"
    echo -e "  Dataset:           ${GREEN}$DATASET_NAME${NC}"
    echo -e "  Source Directory:  ${GREEN}$DATA_DIR${NC}"
    echo -e "  Folders Uploaded:  ${GREEN}$PUSH_SUCCESS${NC}"
    if [ $PUSH_FAILED -gt 0 ]; then
        echo -e "  Failed:            ${RED}$PUSH_FAILED${NC}"
    fi
    for folder in "${TRACKED_FOLDERS[@]}"; do
        echo -e "    • $folder"
    done
    echo -e "  Upload Location:   ${CYAN}gdrive://$user_upload_ID${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  Next steps:${NC}"
    echo -e "  • Notify the dataset owner about your upload"
    echo -e "  • The owner will review and integrate your contributions"
    echo ""
}
user_main() {
    user_display_header
    while true; do
        echo ""
        user_show_menu
        read -p "Enter your choice [1-5]: " user_choice
        case $user_choice in
            1)
                user_initial_setup
                ;;
            2)
                user_update_dataset
                ;;
            3)
                user_upload_data
                ;;
            4)
                user_switch_dataset
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
user_main "$@"
