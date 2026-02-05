# 🎯 QUICK GUIDE: Visualization Parameters System

## ✅ WHAT HAS BEEN IMPLEMENTED

Complete system to save/load 3D Slicer visualization parameters in lightweight JSON format (~2-5 KB instead of .mrml ~100+ KB).

### Created Files:

1. **Directory structure**:
   - `D-Prova/viz_params/` - Directory for JSON parameters
   - `D-Prova/viz_params/schema.json` - JSON validation schema

2. **Standalone Python scripts**:
   - `scripts_py/viz_params_manager.py` - Manager for saving/loading parameters
   - `scripts_py/autoload_viz_params.py` - Automatic auto-load hook
   - `scripts_py/autocommit_viz_params.py` - Auto-commit Git script

3. **Slicer Module with UI**:
   - `src/slicer_extension/VesselVerseVizParams/VesselVerseVizParams.py`
   - Panel with Save/Load buttons
   - Auto-detect dataset path
   - Git integration

4. **Documentation**:
   - `docs/viz_params_README.md` - Complete guide

---

## 📝 STEPS TO USE THE SYSTEM

### STEP 1: Prepare Dataset

Each dataset must have a `viz_params/` directory:

```bash
cd /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Dataset/datasets

# Create viz_params in other datasets
mkdir -p D-IXI/viz_params
mkdir -p D-COW23MR/viz_params
cp D-Prova/viz_params/schema.json D-IXI/viz_params/
cp D-Prova/viz_params/schema.json D-COW23MR/viz_params/
```

### STEP 2: Load VesselVerseVizParams Module

#### Option A - Developer Mode (manual -> every time you open Slicer)

In 3D Slicer, Python Console:

```python
# Add path to module
import sys
framework_path = '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework'
sys.path.insert(0, framework_path + '/src/slicer_extension')
sys.path.insert(0, framework_path + '/scripts_py')

# Register module in menu
factory = slicer.app.moduleManager().factoryManager()
factory.registerModule(qt.QFileInfo(framework_path + '/src/slicer_extension/VesselVerseVizParams/VesselVerseVizParams.py'))
factory.loadModules(['VesselVerseVizParams'])

# Open module
slicer.util.selectModule('VesselVerseVizParams')

# Reload module
import importlib
import sys
sys.path.insert(0, '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py')
import autocommit_viz_params
importlib.reload(autocommit_viz_params)
```

After these commands, the module appears in the Modules menu and the panel with buttons opens automatically.

#### Option B - Permanent Installation (one time only)

Copy the module to Slicer's Extensions directory:

```bash
# Find Slicer modules directory (macOS)
SLICER_MODULES=~/Library/Application\ Support/NA-MIC/Slicer\ 5.8/Extensions-*/lib/Slicer-*/qt-scripted-modules/

# Create symlink
ln -s /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/src/slicer_extension/VesselVerseVizParams \
      "$SLICER_MODULES/"

# Restart Slicer → module appears automatically in Modules menu
```

After this installation, the module is always available without running scripts.

## 🔍 VERIFY FUNCTIONALITY

### Test 1: Save Parameters

```python
# In Slicer Python Console
import sys
sys.path.append('/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py')
from viz_params_manager import VizParamsManager

# Create test volume
import numpy as np
imageSize = [128, 128, 128]
voxelType = vtk.VTK_UNSIGNED_CHAR
imageData = vtk.vtkImageData()
imageData.SetDimensions(imageSize)
imageData.AllocateScalars(voxelType, 1)

volume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "TestVolume")
volume.SetAndObserveImageData(imageData)
volume.CreateDefaultDisplayNodes()

# Save
manager = VizParamsManager()
success = manager.save_params(
    volume,
    '/tmp/test_viz.json'
)
print(f"Save success: {success}")

# Verify file
import json
with open('/tmp/test_viz.json') as f:
    params = json.load(f)
print(f"Parameters saved: {list(params.keys())}")
```

### Test 2: Load Parameters

```python
# Load parametri salvati
success = manager.load_params(
    volume,
    '/tmp/test_viz.json'
)
print(f"Load success: {success}")
```

### Test 3: Auto-commit

```bash
cd /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py

# Test without push
python3 autocommit_viz_params.py /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Dataset/datasets/D-Prova

# Test with push
python3 autocommit_viz_params.py /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Dataset/datasets/D-Prova --push
```

---

## 📦 JSON FILE STRUCTURE

Example `IXI001_MRA_viz.json`:

```json
{
  "volume": "IXI001_MRA.nii.gz",
  "timestamp": "2026-01-09T10:30:00Z",
  "slicer_version": "5.6.2",
  "schema_version": "1.0.0",
  "window_level": {
    "window": 500,
    "level": 250
  },
  "color_map": "Grey",
  "opacity_transfer": [
    [0, 0.0],
    [64, 0.1],
    [128, 0.5],
    [192, 0.8],
    [255, 1.0]
  ],
  "gradient_opacity": [
    [0.0, 1.0],
    [255.0, 1.0]
  ],
  "rendering_mode": "VR_GPU_Ray_Casting",
  "camera": {
    "position": [100.0, 200.0, 300.0],
    "focal_point": [0.0, 0.0, 0.0],
    "view_up": [0.0, 1.0, 0.0],
    "view_angle": 30.0
  },
  "slice_views": {
    "red": 0.0,
    "yellow": 0.0,
    "green": 0.0
  },
  "segmentation_visibility": {
    "vessels": true,
    "background": false
  },
  "segmentation_opacity": {
    "vessels": 0.8
  },
  "notes": "Optimized for MRA vessel visualization"
}
```

### Saved Parameters:

**Metadata**:

- `volume` - Volume name
- `timestamp` - Save date/time (ISO 8601)
- `slicer_version` - 3D Slicer version
- `schema_version` - JSON schema version

**Volume Display**:

- `window_level.window` - Intensity window width
- `window_level.level` - Intensity window center
- `color_map` - Color map (Grey/Viridis/Rainbow/etc.)
- `opacity_transfer` - Array `[intensity, opacity]` for transfer function
- `gradient_opacity` - Gradient transfer function (volume rendering)
- `rendering_mode` - Rendering method (VR_GPU_Ray_Casting/MIP/MinIP/etc.)

**3D Camera**:

- `camera.position` - Camera position [x, y, z]
- `camera.focal_point` - Focal point [x, y, z]
- `camera.view_up` - "Up" vector [x, y, z]
- `camera.view_angle` - Field of view angle (degrees)

**Slice Views**:

- `slice_views.red` - Axial view offset (mm)
- `slice_views.yellow` - Sagittal view offset (mm)
- `slice_views.green` - Coronal view offset (mm)

**Segmentation** (optional):

- `segmentation_visibility` - Visibility for each segment
- `segmentation_opacity` - Opacity for each segment (0.0-1.0)

**Notes** (optional):

- `notes` - Owner's descriptive notes

### Possible Future Parameters:

```json
{
  "slice_thickness": 1.0,
  "interpolation": "linear",
  "3d_visibility": true,
  "background_color": [0.0, 0.0, 0.0],
  "preset_name": "MR-Angio"
}
```

**Typical size**: 2-5 KB (vs .mrml 100-500 KB)

---

## 🚀 SOLUTION BENEFITS

### Owner:

- ✅ **1 click to save** (UI button or script)
- ✅ **Optional auto-commit** (checkbox or automatic script)
- ✅ **Automatic naming** (`{volume}_viz.json`)
- ✅ **Git-friendly** (lightweight files, simple merges)

### User:

- ✅ **0 clicks with auto-load** (hook installed once)
- ✅ **1 manual click** ("Auto-Load Settings" button)
- ✅ **Identical visualization** to owner
- ✅ **No complex setup**

### System:

- ✅ **Lightweight**: 2-5 KB vs 100-500 KB
- ✅ **Version-controllable**: Git (no DVC)
- ✅ **Scalable**: works with 10 or 1000 volumes
- ✅ **Cross-platform**: Pure Python
- ✅ **Extensible**: easy to add parameters

---

## 🐛 TROUBLESHOOTING

### "Cannot import viz_params_manager"

```python
# Verify path
import sys
print(sys.path)

# Add manually
sys.path.insert(0, '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py')
```

### "Module not found: VesselVerseVizParams"

```python
# Verify file exists
import os
path = '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/src/slicer_extension/VesselVerseVizParams/VesselVerseVizParams.py'
print(os.path.exists(path))

# Reload module
slicer.util.reloadScriptedModule('VesselVerseVizParams')
```

### "No parameters found"

- Verify naming: `volume_name.nii.gz` → `volume_name_viz.json`
- Check that `viz_params/` exists
- Verify correct dataset path

### Auto-load not working

- Verify hook is in `~/.config/NA-MIC/Extensions-*/SlicerStartup/`
- Restart Slicer
- Check Slicer console for errors
- Verify framework path in `autoload_viz_params.py` (line 14)

---

## 📚 NEXT STEPS

1. **Test with real dataset** (D-IXI, D-COW23MR)
2. **Create parameters for existing volumes**
3. **Test complete owner→user workflow**
4. **Add viz_params/ to other datasets**
5. **Document best practices for team**

---

## 📞 SUPPORT

- Complete README: `VesselVerse-Framework/docs/viz_params_README.md`
- JSON Schema: `D-Prova/viz_params/schema.json`
- Examples: See tests in this guide

---

**✅ System complete and ready to use!**
