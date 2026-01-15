# 🎯 GUIDA RAPIDA: Sistema Parametri Visualizzazione

## ✅ COSA È STATO IMPLEMENTATO

Sistema completo per salvare/caricare parametri visualizzazione 3D Slicer in formato JSON leggero (~2-5 KB invece di .mrml ~100+ KB).

### File Creati:

1. **Directory struttura**:

   - `D-Prova/viz_params/` - Directory per parametri JSON
   - `D-Prova/viz_params/schema.json` - Schema JSON validazione

2. **Script Python standalone**:

   - `scripts_py/viz_params_manager.py` - Manager save/load parametri
   - `scripts_py/autoload_viz_params.py` - Hook auto-load automatico
   - `scripts_py/autocommit_viz_params.py` - Script auto-commit Git

3. **Slicer Module con UI**:

   - `src/slicer_extension/VesselVerseVizParams/VesselVerseVizParams.py`
   - Pannello con bottoni Save/Load
   - Auto-detect dataset path
   - Integrazione Git

4. **Documentazione**:
   - `docs/viz_params_README.md` - Guida completa

---

## 📝 PASSAGGI PER USARE IL SISTEMA

### STEP 1: Preparare Dataset

Ogni dataset deve avere una directory `viz_params/`:

```bash
cd /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Dataset/datasets

# Crea viz_params in altri dataset
mkdir -p D-IXI/viz_params
mkdir -p D-COW23MR/viz_params
cp D-Prova/viz_params/schema.json D-IXI/viz_params/
cp D-Prova/viz_params/schema.json D-COW23MR/viz_params/
```

### STEP 2: Caricare Modulo VesselVerseVizParams

#### Opzione A - Developer Mode (manuale -> ogni volta che apri Slicer)

In 3D Slicer, Python Console:

```python
# Aggiungi path al modulo
import sys
framework_path = '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework'
sys.path.insert(0, framework_path + '/src/slicer_extension')
sys.path.insert(0, framework_path + '/scripts_py')

# Registra il modulo nel menu
factory = slicer.app.moduleManager().factoryManager()
factory.registerModule(qt.QFileInfo(framework_path + '/src/slicer_extension/VesselVerseVizParams/VesselVerseVizParams.py'))
factory.loadModules(['VesselVerseVizParams'])

# Apri il modulo
slicer.util.selectModule('VesselVerseVizParams')

# Ricarica modulo
import importlib
import sys
sys.path.insert(0, '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py')
import autocommit_viz_params
importlib.reload(autocommit_viz_params)
```

Dopo questi comandi, il modulo appare nel menu Modules e il pannello con i bottoni si apre automaticamente.

#### Opzione B - Installazione Permanente (una volta sola)

Copia il modulo nella directory Extensions di Slicer:

```bash
# Trova directory modules di Slicer (macOS)
SLICER_MODULES=~/Library/Application\ Support/NA-MIC/Slicer\ 5.8/Extensions-*/lib/Slicer-*/qt-scripted-modules/

# Crea symlink
ln -s /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/src/slicer_extension/VesselVerseVizParams \
      "$SLICER_MODULES/"

# Riavvia Slicer → il modulo appare automaticamente in Modules menu
```

Dopo questa installazione, il modulo è sempre disponibile senza eseguire script.

## 🔍 VERIFICA FUNZIONAMENTO

### Test 1: Salvare Parametri

```python
# In Slicer Python Console
import sys
sys.path.append('/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py')
from viz_params_manager import VizParamsManager

# Crea volume test
import numpy as np
imageSize = [128, 128, 128]
voxelType = vtk.VTK_UNSIGNED_CHAR
imageData = vtk.vtkImageData()
imageData.SetDimensions(imageSize)
imageData.AllocateScalars(voxelType, 1)

volume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "TestVolume")
volume.SetAndObserveImageData(imageData)
volume.CreateDefaultDisplayNodes()

# Salva
manager = VizParamsManager()
success = manager.save_params(
    volume,
    '/tmp/test_viz.json'
)
print(f"Save success: {success}")

# Verifica file
import json
with open('/tmp/test_viz.json') as f:
    params = json.load(f)
print(f"Parameters saved: {list(params.keys())}")
```

### Test 2: Caricare Parametri

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

# Test senza push
python3 autocommit_viz_params.py /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Dataset/datasets/D-Prova

# Test con push
python3 autocommit_viz_params.py /Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Dataset/datasets/D-Prova --push
```

---

## 📦 STRUTTURA FILE JSON

Esempio `IXI001_MRA_viz.json`:

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
  "notes": "Ottimizzato per visualizzazione vasi MRA"
}
```

### Parametri Salvati:

**Metadati**:

- `volume` - Nome del volume
- `timestamp` - Data/ora salvataggio (ISO 8601)
- `slicer_version` - Versione 3D Slicer
- `schema_version` - Versione schema JSON

**Visualizzazione Volume**:

- `window_level.window` - Ampiezza finestra intensità
- `window_level.level` - Centro finestra intensità
- `color_map` - Mappa colori (Grey/Viridis/Rainbow/etc.)
- `opacity_transfer` - Array `[intensità, opacità]` per transfer function
- `gradient_opacity` - Transfer function gradiente (volume rendering)
- `rendering_mode` - Metodo rendering (VR_GPU_Ray_Casting/MIP/MinIP/etc.)

**Camera 3D**:

- `camera.position` - Posizione camera [x, y, z]
- `camera.focal_point` - Punto di mira [x, y, z]
- `camera.view_up` - Vettore "su" [x, y, z]
- `camera.view_angle` - Angolo campo visivo (gradi)

**Viste Slice**:

- `slice_views.red` - Offset vista assiale (mm)
- `slice_views.yellow` - Offset vista sagittale (mm)
- `slice_views.green` - Offset vista coronale (mm)

**Segmentazione** (opzionale):

- `segmentation_visibility` - Visibilità per ogni segmento
- `segmentation_opacity` - Opacità per ogni segmento (0.0-1.0)

**Note** (opzionale):

- `notes` - Note descrittive dell'owner

### Parametri Futuri Possibili:

```json
{
  "slice_thickness": 1.0,
  "interpolation": "linear",
  "3d_visibility": true,
  "background_color": [0.0, 0.0, 0.0],
  "preset_name": "MR-Angio"
}
```

**Dimensione tipica**: 2-5 KB (vs .mrml 100-500 KB)

---

## 🚀 VANTAGGI SOLUZIONE

### Owner:

- ✅ **1 click per salvare** (bottone UI o script)
- ✅ **Auto-commit opzionale** (checkbox o script automatico)
- ✅ **Naming automatico** (`{volume}_viz.json`)
- ✅ **Git-friendly** (file leggeri, merge semplici)

### User:

- ✅ **0 click con auto-load** (hook installato una volta)
- ✅ **1 click manuale** (bottone "Auto-Load Settings")
- ✅ **Visualizzazione identica** all'owner
- ✅ **Nessun setup complesso**

### Sistema:

- ✅ **Leggero**: 2-5 KB vs 100-500 KB
- ✅ **Versionabile**: Git (no DVC)
- ✅ **Scalabile**: funziona con 10 o 1000 volumi
- ✅ **Cross-platform**: Python puro
- ✅ **Estensibile**: facile aggiungere parametri

---

## 🐛 TROUBLESHOOTING

### "Cannot import viz_params_manager"

```python
# Verifica path
import sys
print(sys.path)

# Aggiungi manualmente
sys.path.insert(0, '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/scripts_py')
```

### "Module not found: VesselVerseVizParams"

```python
# Verifica che il file esista
import os
path = '/Users/aliceboccadifuoco/Desktop/VesselVerse/VesselVerse-Framework/src/slicer_extension/VesselVerseVizParams/VesselVerseVizParams.py'
print(os.path.exists(path))

# Ricarica modulo
slicer.util.reloadScriptedModule('VesselVerseVizParams')
```

### "No parameters found"

- Verifica naming: `volume_name.nii.gz` → `volume_name_viz.json`
- Controlla che `viz_params/` esista
- Verifica path dataset corretto

### Auto-load non funziona

- Verifica che hook sia in `~/.config/NA-MIC/Extensions-*/SlicerStartup/`
- Riavvia Slicer
- Controlla console Slicer per errori
- Verifica framework path in `autoload_viz_params.py` (linea 14)

---

## 📚 PROSSIMI PASSI

1. **Testare con dataset reale** (D-IXI, D-COW23MR)
2. **Creare parametri per volumi esistenti**
3. **Testare workflow completo owner→user**
4. **Aggiungere viz_params/ ad altri dataset**
5. **Documentare best practices per team**

---

## 📞 SUPPORTO

- README completo: `VesselVerse-Framework/docs/viz_params_README.md`
- Schema JSON: `D-Prova/viz_params/schema.json`
- Esempi: Vedi test in questa guida

---

**✅ Sistema completo e pronto all'uso!**
