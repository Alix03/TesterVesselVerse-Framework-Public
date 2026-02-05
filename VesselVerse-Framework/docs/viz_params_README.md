# VesselVerse Visualization Parameters

Lightweight system for saving and sharing 3D Slicer visualization parameters using JSON (~2-5 KB) instead of heavy .mrml files (~100+ KB).

## 📁 Directory Structure

```
D-IXI/                              # Dataset directory
  ExpertAnnotations/
  STAPLE/
  viz_params/                       # ← New directory
    schema.json                     # JSON schema for validation
    IXI001_MRA_viz.json            # Parameters for IXI001_MRA.nii.gz
    IXI002_MRA_viz.json
    IXI003_MRA_viz.json
```

## 🎯 Owner Workflow

### Option A: Slicer Scripted Module (Recommended - UI with buttons)

1. **Open 3D Slicer**
2. **Load the module**:
   - Modules → VesselVerse → VesselVerse Viz Params
3. **Configure visualization**:
   - Adjust window/level, opacity, camera, etc.
4. **Save parameters**:
   - Select volume
   - Click "Auto-Detect Dataset" or specify the path manually
   - Click "💾 Save Visualization Settings"
5. **Commit & Push** (optional auto):
   - Enable "Auto-commit & push" for automatic commits
   - Or click "📤 Commit & Push Params"

### Option B: Python Console Script (Faster)

```python
# In Slicer Python Console:
import sys
sys.path.append('/Users/.../VesselVerse-Framework/scripts_py')
from viz_params_manager import VizParamsManager

manager = VizParamsManager()
volume = slicer.util.getNode('IXI001_MRA')
segmentation = slicer.util.getNode('Segmentation')  # Optional

# Save parameters
manager.save_params(
    volume,
    '/path/to/D-IXI/viz_params/IXI001_MRA_viz.json',
    segmentation,
    notes="Optimized for MRA vessel visualization"
)
```

### Option C: Automatic Commit from Terminal

```bash
# After saving parameters in Slicer:
cd /path/to/VesselVerse-Framework/scripts_py
python3 autocommit_viz_params.py /path/to/D-IXI --push
```

## 👥 User Workflow

### Automatic Auto-Load (Recommended)

1. **Install Auto-Load Hook** (one-time setup):

   ```bash
   # Copy the script to Slicer's startup directory
   mkdir -p ~/.config/NA-MIC/Extensions-*/SlicerStartup/
   cp autoload_viz_params.py ~/.config/NA-MIC/Extensions-*/SlicerStartup/
   ```

2. **Use normally**:
   ```bash
   git pull
   dvc pull
   # Open volume in Slicer
   # → Parameters automatically loaded! 🎉
   ```

### Manual Load (Without Auto-Load)

```python
# In Slicer Python Console:
import sys
sys.path.append('/Users/.../VesselVerse-Framework/scripts_py')
from viz_params_manager import VizParamsManager

manager = VizParamsManager()
volume = slicer.util.getNode('IXI001_MRA')
segmentation = slicer.util.getNode('Segmentation')

# Load parameters
manager.load_params(
    volume,
    '/path/to/D-IXI/viz_params/IXI001_MRA_viz.json',
    segmentation
)
```

Or use the UI module:

- Modules → VesselVerse → VesselVerse Viz Params
- Click "🔄 Auto-Load Settings"

## 📋 Saved Parameters

The JSON file includes:

- **Window/Level**: Contrast and brightness
- **Color Map**: Lookup table (Grey, Viridis, etc.)
- **Opacity Transfer Function**: Opacity curve for volume rendering
- **Gradient Opacity**: Gradient-based opacity
- **3D Camera**: Position, focal point, view angle
- **Slice Views**: Axial/Sagittal/Coronal slice positions
- **Segmentation** (optional):
  - Visibility for each segment
  - 3D opacity for each segment

## 📊 JSON Example

```json
{
  "volume": "IXI001_MRA.nii.gz",
  "timestamp": "2026-01-09T10:30:00Z",
  "slicer_version": "5.6.2",
  "window_level": {
    "window": 500,
    "level": 250
  },
  "opacity_transfer": [
    [0, 0.0],
    [128, 0.5],
    [255, 1.0]
  ],
  "camera": {
    "position": [100, 200, 300],
    "focal_point": [0, 0, 0],
    "view_up": [0, 1, 0],
    "view_angle": 30
  },
  "segmentation_visibility": {
    "vessels": true,
    "background": false
  }
}
```

## 🔧 Slicer Module Installation

### Method 1: Extension Manager (Future)

```
Edit → Application Settings → Modules → Additional module paths
Add: /path/to/VesselVerse-Framework/src/slicer_extension
Restart Slicer
```

### Method 2: Developer Mode (Now)

```python
# In Slicer Python Console:
import sys
sys.path.append('/path/to/VesselVerse-Framework/src/slicer_extension')
sys.path.append('/path/to/VesselVerse-Framework/scripts_py')

# Load module
slicer.util.selectModule('VesselVerseVizParams')
```

## 📦 File Sizes Comparison

| Format    | Size       | Git Friendly | DVC Required |
| --------- | ---------- | ------------ | ------------ |
| **.mrml** | 100-500 KB | ❌ No        | ✅ Yes       |
| **.json** | 2-5 KB     | ✅ Yes       | ❌ No        |

## 🚀 Quick Start

1. **Setup** (Owner):

   ```bash
   cd /path/to/dataset
   mkdir -p viz_params
   ```

2. **Save** (Owner in Slicer):
   - Load VesselVerse Viz Params module
   - Adjust visualization
   - Click "Save Visualization Settings"
   - Click "Commit & Push Params"

3. **Load** (User):
   ```bash
   git pull  # Download new JSON files
   # Open Slicer → Auto-load automatically
   ```

## 🐛 Troubleshooting

**Problem**: "No saved parameters found"

- Verify the JSON file exists in `viz_params/`
- Naming convention: `{volume_name}_viz.json`
- Remove extensions: `IXI001_MRA.nii.gz` → `IXI001_MRA_viz.json`

**Problem**: "Auto-load not working"

- Verify `autoload_viz_params.py` is in `SlicerStartup/`
- Check Slicer console for errors
- Framework path: `~/Desktop/VesselVerse/VesselVerse-Framework`

**Problem**: "Git commit failed"

- Verify you are in the dataset directory
- Check that `viz_params/` exists
- Verify Git permissions

## 📚 API Reference

### VizParamsManager

```python
manager = VizParamsManager()

# Save parameters
manager.save_params(
    volume_node,              # vtkMRMLScalarVolumeNode
    output_path,              # str: path to JSON file
    segmentation_node=None,   # vtkMRMLSegmentationNode (optional)
    notes=""                  # str: optional notes
) → bool

# Load parameters
manager.load_params(
    volume_node,              # vtkMRMLScalarVolumeNode
    input_path,               # str: path to JSON file
    segmentation_node=None    # vtkMRMLSegmentationNode (optional)
) → bool

# Auto-detect parameters file
manager.auto_detect_params_file(
    volume_node,              # vtkMRMLScalarVolumeNode
    dataset_path              # str: path to D-* directory
) → Optional[str]
```

## 🎨 Customization

### Adding Custom Parameters

Edit `viz_params_manager.py`:

```python
def extract_custom_params(self, volume_node):
    """Extract custom parameters"""
    return {
        "my_param": value,
        # ...
    }

# In save_params():
params["custom"] = self.extract_custom_params(volume_node)
```

### Custom Naming Convention

Edit `auto_detect_params_file()`:

```python
# Example: also search for {volume_name}_settings.json
json_path = viz_params_dir / f"{base_name}_settings.json"
```

## 📝 Notes

- JSON files are versioned with Git (not DVC)
- Parameters are specific to volumes, not scenes
- Compatible with Slicer 5.0+
- Validation schema available in `schema.json`

## 🤝 Contributing

To add new parameters:

1. Update `schema.json`
2. Implement `extract_*()` and `apply_*()` in `viz_params_manager.py`
3. Test with a real dataset
4. Submit a PR
