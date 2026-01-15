# 🔧 Dynamic Dataset Registration

## Sistema di Rilevamento Automatico

Il sistema rileva **automaticamente** tutti i dataset nella directory `VesselVerse-Dataset/datasets/D-*` senza dover modificare codice!

## 📋 Come Funziona

Quando Slicer si avvia:

1. Scansiona ogni directory che inizia con `D-*`
2. Rileva automaticamente i modelli dalle sottodirectory
3. Registra il dataset con i modelli trovati

**Zero configurazione necessaria!**

---

## 🚀 Come Aggiungere un Nuovo Dataset

Basta creare la directory:

```bash
cd VesselVerse-Dataset/datasets
mkdir D-MyNewDataset

# Crea sottodirectory per i modelli
mkdir D-MyNewDataset/STAPLE
mkdir D-MyNewDataset/ExpertAnnotations
mkdir D-MyNewDataset/MyCustomModel
```

**Risultato automatico**:

- `MyNewDataset` appare in Slicer
- Modelli rilevati: `STAPLE`, `ExpertAnnotations`, `MyCustomModel`

**Riavvia Slicer** → Funziona subito! ✅

---

## 🔍 Dettagli Auto-Detection

Il sistema:

1. **Scansiona tutte le sottodirectory** in `D-MyDataset/`
2. **Esclude directory speciali**:
   - `.git`, `.dvc`, `__pycache__`
   - `viz_params` (parametri visualizzazione)
   - File `.dvc` e `.dvcignore`
3. **Registra ogni directory** come modello disponibile
4. **Se directory vuota**: crea modelli default `[MYDATASET_TOT, STAPLE, ExpertAnnotations]`

### Esempio Pratico:

```
D-TestDataset/
├── STAPLE/          → Modello disponibile
├── nnUNet/          → Modello disponibile
├── CustomModel/     → Modello disponibile
├── viz_params/      → IGNORATO
└── .dvc/            → IGNORATO
```

**Output**: Dataset `TestDataset` con 3 modelli: `STAPLE`, `nnUNet`, `CustomModel`

### Prima (Sistema Legacy):

```python
# Dovevi modificare model_config.py per ogni dataset
elif dataset_name == "Prova2":
    prova2_config = DatasetConfig(
        name="Prova2",
        unique_name="Prova2",
        # ... 15+ righe di configurazione manuale
    )
```

### Ora (Auto-Detection):

```bash
# Basta creare le directory!
mkdir -p D-Prova2/STAPLE D-Prova2/ExpertAnnotations
```

**Vantaggi**:

- ✅ **Zero codice da modificare**
- ✅ **Scalabile** a infiniti dataset
- ✅ **Aggiungi modelli = crea directory**
- ✅ **Nessun file di configurazione**
- ✅ **Struttura self-documenting**
- ✅ **Scalabile** a 100+ dataset
- ✅ **Backward compatible** con dataset esistenti
- ✅ **Versionabile** con Git (config dentro dataset)

---

## 🐛 Troubleshooting

### Dataset non appare in Slicer

1. **Verifica nome directory**:

   ````bash
   # CORRETTO
   D-MyDataset/

   ```bash
   # ✅ CORRETTO
   D-MyDataset/

   # ❌ SBAGLIATO
   MyDataset/    # Manca prefisso "D-"
   d-MyDataset/  # "d" minuscolo
   ````

2. **Controlla console Slicer**:

   - Cerca: `✓ Auto-registered dataset 'MyDataset' with models: [...]`
   - Se non appare, verifica che la directory esista e contenga sottodirectory

3. **Verifica sottodirectory**:
   ```bash
   ls -d D-MyDataset/*/  # Deve mostrare almeno una directory
   ```

### Modelli non rilevati

- Verifica che le sottodirectory **non inizino** con `.` o `_`
- Directory ignorate: `viz_params`, `.dvc`, `.git`, `__pycache__`
- **Directory vuota?** Sistema crea modelli default automaticamente

### Directory vuota ma dataset non appare

Anche una directory vuota dovrebbe funzionare (usa modelli default). Se non appare:

```bash
# Test manuale
cd VesselVerse-Framework
python3 -c "
import sys
sys.path.insert(0, 'src')
from model_config.model_config import DatasetRegistry
r = DatasetRegistry()
print([d for d in r.datasets.keys()])
"
```

---

## 📚 Esempi Pratici

### Dataset Completo

```bash
mkdir -p D-MyVessels/{STAPLE,nnUNet,ExpertAnnotations,CustomAI}
# → Risultato: 4 modelli auto-rilevati
```

### Dataset Minimo

```bash
mkdir D-QuickTest
# → Risultato: modelli default [QUICKTEST_TOT, STAPLE, ExpertAnnotations]
```

### Aggiungere Modello a Dataset Esistente

```bash
mkdir D-IXI/MyNewModel
# → Riavvia Slicer → MyNewModel appare nella lista
```

---

## 💡 Best Practices

1. **Naming consistente**: `D-{DatasetName}` con CamelCase (es: `D-MyVessels2024`)
2. **Un modello = una directory**: Struttura chiara e auto-documentante
3. **Test immediato**: Dopo ogni modifica, riavvia Slicer per verificare
4. **Directory vuote OK**: Sistema gestisce automaticamente con modelli default
5. **Legacy datasets**: IXI, COW23MR, ITKTubeTK mantengono config storico per compatibilità

---

## 🔍 Come Funziona Internamente

Il sistema in `model_config.py`:

1. Scansiona `VesselVerse-Dataset/datasets/D-*/`
2. Per dataset legacy (IXI, COW, ITK): usa config hardcoded
3. Per tutti gli altri: chiama `_register_generic_dataset()`
4. `_register_generic_dataset()`:
   - Itera su `dataset_dir.iterdir()`
   - Filtra directory (esclude `.git`, `viz_params`, etc.)
   - Raccoglie nomi directory come modelli
   - Se lista vuota → usa default `[{NAME}_TOT, STAPLE, ExpertAnnotations]`

**Nota**: Ogni sottodirectory può contenere file con estensioni diverse (`.nii.gz`, `.nrrd`, etc.) - nessun limite globale.

---

\*\*✅ Sistema completamente automatico - crea directory e funziona
