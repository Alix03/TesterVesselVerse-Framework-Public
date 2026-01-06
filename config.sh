# ═══════════════════════════════════════════════════════════════════════════
# Cross-Platform Configuration
# ═══════════════════════════════════════════════════════════════════════════

# Absolute path to the repository root (portable across machines)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-detect OS and set appropriate Slicer path
case "$(uname -s)" in
    Darwin*)
        # macOS
        SLICER_PATH='/Applications/Slicer.app/Contents/MacOS/Slicer'
        ;;
    Linux*)
        # Linux - adjust path as needed
        SLICER_PATH="${HOME}/Slicer-5.6.2-linux-amd64/Slicer"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        # Windows (Git Bash) - adjust path as needed
        SLICER_PATH="/c/Program Files/Slicer 5.6/Slicer.exe"
        ;;
    *)
        # Default fallback
        SLICER_PATH="${HOME}/Slicer/Slicer"
        ;;
esac

# Credential paths (relative to REPO_ROOT for portability)
owner_auth_path="$REPO_ROOT/credentials/vesselverse25-141593c63cd7.json"
user_auth_path="$REPO_ROOT/credentials/vesselverse25-141593c63cd7.json"
DATASET_NAME='IXI'
DATASET_PATH="$REPO_ROOT/VesselVerse-Dataset/datasets/D-$DATASET_NAME"
database_ID='1qzVGvHThjVuZ9n7k1jNOBjOa2wPM4LZi'
user_upload_ID='1qzVGvHThjVuZ9n7k1jNOBjOa2wPM4LZi'

# ═══════════════════════════════════════════════════════════════════════════
# Dataset Storage Mapping (Testing Phase - same ID for all datasets)
# ═══════════════════════════════════════════════════════════════════════════
# Note: Folder IDs are not sensitive without credentials (protected by .gitignore)

# Testing ID (temporary - used for all datasets during development)
TESTING_ID='1qzVGvHThjVuZ9n7k1jNOBjOa2wPM4LZi'

# IXI Dataset
IXI_STORAGE_ID="$TESTING_ID"
# Production IDs (commented for future use):
# IXI_STORAGE_ID='1Lt5rGwBPkmdXGeGmpNKrzZ07xJzY_yYv'
# IXI_UPLOAD_IDS: BravePanda='1OzAuvCBUkH2Lt4HOBxmEPmdYR1H88C-Y'
#                 SwiftCheetah='1PoD3eV41h_EWb1uDuMNGlfIUg8gi5_8a'
#                 SilentOwl='1dgXeYwaOxKeS1NGJSBCzatk8l1Qwmh8q'

# COW23MR Dataset
COW23MR_STORAGE_ID="$TESTING_ID"
# Production IDs (commented for future use):
# COW23MR_STORAGE_ID='1jBDBZb8MNNXpGGWe0nTeOLlK_KIIW60p'
# COW23MR_UPLOAD_IDS: BravePanda='1HaOSkx8ANp9S-mzSh-XJ56ZapTBsHCDX'
#                     SwiftCheetah='1mdgCXcgNuLtP6YkCNyWbkNCbPiG0AHzZ'
#                     SilentOwl='1ObMn6yrPPnw4Ua8OYFt34ct7lcakK1OU'

# ITKTubeTK Dataset
ITKTubeTK_STORAGE_ID="$TESTING_ID"

# Prova Dataset (has both storage and upload)
Prova_STORAGE_ID="$TESTING_ID"
Prova_UPLOAD_ID="$TESTING_ID"

