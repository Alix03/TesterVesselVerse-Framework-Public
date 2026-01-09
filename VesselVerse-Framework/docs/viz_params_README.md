# VesselVerse Visualization Parameters

Sistema leggero per salvare e condividere parametri di visualizzazione 3D Slicer tramite JSON (~2-5 KB) invece di file .mrml pesanti (~100+ KB).

## 📁 Struttura Directory

```
D-IXI/                              # Dataset directory
  ExpertAnnotations/
  STAPLE/
  viz_params/                       # ← Nuova directory
    schema.json                     # Schema JSON per validazione
    IXI001_MRA_viz.json            # Parametri per IXI001_MRA.nii.gz
    IXI002_MRA_viz.json
    IXI003_MRA_viz.json
```

## 🎯 Workflow Owner

### Opzione A: Slicer Scripted Module (Consigliato - UI con bottoni)

1. **Apri 3D Slicer**
2. **Carica il modulo**:
   - Moduli → VesselVerse → VesselVerse Viz Params
3. **Configura visualizzazione**:
   - Regola window/level, opacity, camera, ecc.
4. **Salva parametri**:
   - Seleziona volume
   - Click "Auto-Detect Dataset" o specifica path manualmente
   - Click "💾 Save Visualization Settings"
5. **Commit & Push** (opzionale auto):
   - Attiva "Auto-commit & push" per commit automatico
   - Oppure click "📤 Commit & Push Params"

### Opzione B: Script Python Console (Più veloce)

```python
# In Slicer Python Console:
import sys
sys.path.append('/Users/.../VesselVerse-Framework/scripts_py')
from viz_params_manager import VizParamsManager

manager = VizParamsManager()
volume = slicer.util.getNode('IXI001_MRA')
segmentation = slicer.util.getNode('Segmentation')  # Opzionale

# Salva parametri
manager.save_params(
    volume,
    '/path/to/D-IXI/viz_params/IXI001_MRA_viz.json',
    segmentation,
    notes="Ottimizzato per visualizzazione vasi MRA"
)
```

### Opzione C: Commit Automatico da Terminale

```bash
# Dopo aver salvato i parametri in Slicer:
cd /path/to/VesselVerse-Framework/scripts_py
python3 autocommit_viz_params.py /path/to/D-IXI --push
```

## 👥 Workflow User

### Auto-Load Automatico (Consigliato)

1. **Installa Auto-Load Hook** (una sola volta):
   ```bash
   # Copia lo script nella directory di avvio di Slicer
   mkdir -p ~/.config/NA-MIC/Extensions-*/SlicerStartup/
   cp autoload_viz_params.py ~/.config/NA-MIC/Extensions-*/SlicerStartup/
   ```

2. **Usa normalmente**:
   ```bash
   git pull
   dvc pull
   # Apri volume in Slicer
   # → Parametri caricati automaticamente! 🎉
   ```

### Load Manuale (Senza Auto-Load)

```python
# In Slicer Python Console:
import sys
sys.path.append('/Users/.../VesselVerse-Framework/scripts_py')
from viz_params_manager import VizParamsManager

manager = VizParamsManager()
volume = slicer.util.getNode('IXI001_MRA')
segmentation = slicer.util.getNode('Segmentation')

# Load parametri
manager.load_params(
    volume,
    '/path/to/D-IXI/viz_params/IXI001_MRA_viz.json',
    segmentation
)
```

O usa il modulo UI:
- Moduli → VesselVerse → VesselVerse Viz Params
- Click "🔄 Auto-Load Settings"

## 📋 Parametri Salvati

Il file JSON include:

- **Window/Level**: Contrasto e luminosità
- **Color Map**: Lookup table (Grey, Viridis, ecc.)
- **Opacity Transfer Function**: Curva opacità per volume rendering
- **Gradient Opacity**: Opacità basata su gradienti
- **3D Camera**: Posizione, focal point, view angle
- **Slice Views**: Posizioni slice Axial/Sagittal/Coronal
- **Segmentation** (opzionale):
  - Visibility per ogni segmento
  - Opacity 3D per ogni segmento

## 📊 Esempio JSON

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

## 🔧 Installazione Slicer Module

### Metodo 1: Extension Manager (Futuro)
```
Edit → Application Settings → Modules → Additional module paths
Aggiungi: /path/to/VesselVerse-Framework/src/slicer_extension
Restart Slicer
```

### Metodo 2: Developer Mode (Ora)
```python
# In Slicer Python Console:
import sys
sys.path.append('/path/to/VesselVerse-Framework/src/slicer_extension')
sys.path.append('/path/to/VesselVerse-Framework/scripts_py')

# Carica modulo
slicer.util.selectModule('VesselVerseVizParams')
```

## 📦 File Sizes Comparison

| Formato | Dimensione | Git Friendly | DVC Required |
|---------|------------|--------------|--------------|
| **.mrml** | 100-500 KB | ❌ No | ✅ Sì |
| **.json** | 2-5 KB | ✅ Sì | ❌ No |

## 🚀 Quick Start

1. **Setup** (Owner):
   ```bash
   cd /path/to/dataset
   mkdir -p viz_params
   ```

2. **Save** (Owner in Slicer):
   - Carica modulo VesselVerse Viz Params
   - Regola visualizzazione
   - Click "Save Visualization Settings"
   - Click "Commit & Push Params"

3. **Load** (User):
   ```bash
   git pull  # Scarica nuovi JSON
   # Apri Slicer → Auto-load automatico
   ```

## 🐛 Troubleshooting

**Problema**: "No saved parameters found"
- Verifica che il file JSON esista in `viz_params/`
- Naming convention: `{volume_name}_viz.json`
- Rimuovi estensioni: `IXI001_MRA.nii.gz` → `IXI001_MRA_viz.json`

**Problema**: "Auto-load non funziona"
- Verifica che `autoload_viz_params.py` sia in `SlicerStartup/`
- Controlla console Slicer per errori
- Path framework: `~/Desktop/VesselVerse/VesselVerse-Framework`

**Problema**: "Git commit failed"
- Verifica di essere nella directory del dataset
- Controlla che `viz_params/` esista
- Verifica permessi Git

## 📚 API Reference

### VizParamsManager

```python
manager = VizParamsManager()

# Salva parametri
manager.save_params(
    volume_node,              # vtkMRMLScalarVolumeNode
    output_path,              # str: path to JSON file
    segmentation_node=None,   # vtkMRMLSegmentationNode (optional)
    notes=""                  # str: optional notes
) → bool

# Carica parametri
manager.load_params(
    volume_node,              # vtkMRMLScalarVolumeNode
    input_path,               # str: path to JSON file
    segmentation_node=None    # vtkMRMLSegmentationNode (optional)
) → bool

# Auto-detect file parametri
manager.auto_detect_params_file(
    volume_node,              # vtkMRMLScalarVolumeNode
    dataset_path              # str: path to D-* directory
) → Optional[str]
```

## 🎨 Customization

### Aggiungere Parametri Custom

Modifica `viz_params_manager.py`:

```python
def extract_custom_params(self, volume_node):
    """Estrai parametri custom"""
    return {
        "my_param": value,
        # ...
    }

# In save_params():
params["custom"] = self.extract_custom_params(volume_node)
```

### Naming Convention Custom

Modifica `auto_detect_params_file()`:

```python
# Esempio: cerca anche {volume_name}_settings.json
json_path = viz_params_dir / f"{base_name}_settings.json"
```

## 📝 Notes

- File JSON sono versionati con Git (non DVC)
- Parametri sono specifici per volume, non per scena
- Compatibile con Slicer 5.0+
- Schema validazione disponibile in `schema.json`

## 🤝 Contributing

Per aggiungere nuovi parametri:
1. Aggiorna `schema.json`
2. Implementa `extract_*()` e `apply_*()` in `viz_params_manager.py`
3. Testa con dataset reale
4. Submit PR

## 📄 License

See main VesselVerse LICENSE file.
