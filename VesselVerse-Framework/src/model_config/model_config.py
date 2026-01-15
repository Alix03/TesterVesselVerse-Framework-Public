from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Dict, List

@dataclass
class ModelConfig:
    """Configuration for a segmentation model"""
    name: str  # Full name (directory name)
    prefix: str  # Short prefix for unique keys
    owner: str  # Default owner
    filename_processor: Optional[Callable[[Path], Path]] = None

@dataclass
class DatasetConfig:
    """Configuration for a specific dataset"""
    name: str  # Dataset name (e.g., 'IXI', 'COW')
    unique_name: str  # Unique identifier for dataset (e.g., 'IXI_TOT', '301_CT23', '302_MR23', etc.)
    base_path: Path  # Base path for dataset
    image_dir: str  # Directory name for original images
    image_suffix: str  # File suffix for images (e.g., 'MRA', 'CTA')
    supported_models: List[str]  # List of supported model names
    modality: str  # Modality of images (e.g., 'MR', 'CT')
    year: Optional[str] = None  # Year of TOPCOW dataset (e.g., '23', '24')
    file_pattern: str = "*.nii.gz"  # File pattern for image files
    base_model_name: str = "TOT"  # Base model for STAPLE
    
    def get_image_path(self, case_id: str) -> Path:
        """Get path to original image for a case"""
        return self.base_path / self.image_dir / f"{case_id}.{self.image_suffix}"

class DatasetRegistry:
    """Registry of supported datasets"""
    def __init__(self):
        self.datasets: Dict[str, DatasetConfig] = {}
        self._register_default_datasets()
    
    def register_dataset(self, config: DatasetConfig):
        """Register a new dataset configuration"""
        #print("Registering dataset:", config.unique_name)
        self.datasets[config.unique_name] = config
    
    def get_dataset(self, name: str) -> Optional[DatasetConfig]:
        """Get dataset configuration by unique name"""
        return self.datasets.get(name)
    
    def get_dataset_by_unique_name(self, unique_name: str) -> Optional[DatasetConfig]:
        """Get dataset configuration by unique name"""
        for dataset in self.datasets.values():
            if dataset.unique_name == unique_name:
                return dataset
        return None
    
    def _load_dataset_config_file(self, dataset_dir: Path) -> Optional[dict]:
        """Load dataset configuration from dataset_config.json if exists"""
        config_file = dataset_dir / "dataset_config.json"
        if config_file.exists():
            import json
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load {config_file}: {e}")
        return None
    
    def _register_dataset_from_config(self, dataset_dir: Path, config_data: dict):
        """Register dataset from configuration dictionary"""
        dataset_config = DatasetConfig(
            name=config_data.get("name", dataset_dir.name[2:]),
            unique_name=config_data.get("unique_name", dataset_dir.name[2:]),
            base_path=dataset_dir,
            image_dir=config_data.get("image_dir", ""),
            image_suffix=config_data.get("image_suffix", "nii.gz"),
            modality=config_data.get("modality", "MR"),
            year=config_data.get("year"),
            supported_models=config_data.get("supported_models", []),
            file_pattern=config_data.get("file_pattern", "*.nii.gz"),
            base_model_name=config_data.get("base_model_name", "TOT")
        )
        self.register_dataset(dataset_config)
        return True
    
    def _register_generic_dataset(self, dataset_dir: Path, dataset_name: str):
        """Register a dataset with generic/default configuration"""
        # Auto-detect possible models by looking for subdirectories
        supported_models = []
        
        # Check for common model directories
        for model_dir in dataset_dir.iterdir():
            if model_dir.is_dir() and not model_dir.name.startswith('.'):
                model_name = model_dir.name
                # Skip certain directories
                if model_name not in ['viz_params', '__pycache__', '.dvc', '.git']:
                    supported_models.append(model_name)
        
        # If no models found, add generic defaults
        if not supported_models:
            supported_models = [
                f"{dataset_name.upper()}_TOT",
                "STAPLE",
                "ExpertAnnotations"
            ]
        
        generic_config = DatasetConfig(
            name=dataset_name,
            unique_name=dataset_name,
            base_path=dataset_dir,
            image_dir="",
            image_suffix="nii.gz",
            modality="MR",
            supported_models=supported_models
        )
        self.register_dataset(generic_config)
        print(f"✓ Auto-registered dataset '{dataset_name}' with models: {supported_models}")
    
    def _register_default_datasets(self):
        """Register default supported datasets"""
        ################################### DYNAMIC DATASET DISCOVERY ###################################################
        # This method now automatically discovers ALL datasets in VesselVerse-Dataset/datasets/D-*
        # 
        # Priority order:
        # 1. If dataset has dataset_config.json → use that configuration
        # 2. If dataset name matches legacy patterns (IXI, COW23MR, etc.) → use legacy config
        # 3. Otherwise → auto-detect models from subdirectories (generic fallback)
        #
        # To customize a dataset, create dataset_config.json in the dataset directory:
        # {
        #   "name": "MyDataset",
        #   "unique_name": "MyDataset",
        #   "image_suffix": "nii.gz",
        #   "modality": "MR",
        #   "supported_models": ["MODEL1", "MODEL2", "STAPLE"]
        # }
        ######################################################################################################################################
        
        # Calculate absolute path from this file's location
        # Go up from src/model_config/ to VesselVerse-Framework/
        repo_root = Path(__file__).resolve().parent.parent.parent
        
        # Try to load datasets from VesselVerse-Dataset/datasets/
        datasets_root = repo_root.parent / "VesselVerse-Dataset" / "datasets"
        
        if datasets_root.exists():
            # Dynamically discover and register datasets from VesselVerse-Dataset
            import os
            for dataset_dir in datasets_root.glob("D-*"):
                if dataset_dir.is_dir():
                    dataset_name = dataset_dir.name[2:]  # Remove "D-" prefix
                    
                    # Priority 1: Check for dataset_config.json
                    config_data = self._load_dataset_config_file(dataset_dir)
                    if config_data:
                        self._register_dataset_from_config(dataset_dir, config_data)
                        continue
                    
                    # Priority 2: Legacy hardcoded configurations (for backward compatibility)
                    registered = False
                    if dataset_name == "IXI":
                        ixi_config = DatasetConfig(
                            name="IXI",
                            unique_name="IXI",
                            base_path=dataset_dir,
                            image_dir="",
                            image_suffix="nii.gz",
                            modality="MR",
                            supported_models=[
                                "IXI_TOT",
                                "STAPLE", "STAPLE_base",
                                "StochasticAL", 
                                "nnUNet",
                                "A2V",
                                "Filtering", 
                                "ExpertAnnotations", "ExpertVAL"
                            ]
                        )
                        self.register_dataset(ixi_config)
                        
                    elif dataset_name == "COW23MR":
                        cow23mr_config = DatasetConfig(
                            name="COW",
                            unique_name="302_MR23",
                            base_path=dataset_dir,
                            image_dir="",
                            image_suffix="nii.gz",
                            modality="MR",
                            year="23",
                            supported_models=[
                                "COW_TOT",
                                "STAPLE", "STAPLE_base",
                                "A2V",
                                "StochasticAL",
                                "nnUNet",
                                "COW_SEG",
                                "JOB-VS",
                                "JOB-VS-SHINY-1", 
                                "JOB-VS-SHINY-2",
                                "ExpertAnnotations", 
                                "ExpertVAL"
                            ]
                        )
                        self.register_dataset(cow23mr_config)
                        
                    elif dataset_name == "ITKTubeTK":
                        itk_config = DatasetConfig(
                            name="ITKTubeTK",
                            unique_name="ITKTubeTK",
                            base_path=dataset_dir,
                            image_dir="",
                            image_suffix="nii.gz",
                            modality="MR",
                            supported_models=[
                                "ITK_TOT",
                                "STAPLE", "STAPLE_base",
                                "ExpertAnnotations", "ExpertVAL"
                            ]
                        )
                        self.register_dataset(itk_config)
                        
                    # Priority 3: Generic fallback - auto-detect everything
                    if not registered:
                        self._register_generic_dataset(dataset_dir, dataset_name)
        else:
            # Fallback to old behavior for backward compatibility
            ixi_config = DatasetConfig(
                name="IXI",
                unique_name="IXI",
                base_path=repo_root / "VESSELVERSE_DATA_IXI" / "data",
                image_dir="IXI_TOT",
                image_suffix="nii.gz",
                modality="MR",
                supported_models=[
                    "IXI_TOT",
                    "STAPLE", "STAPLE_base",
                    "StochasticAL", 
                    "nnUNet",
                    "A2V",
                    "Filtering", 
                    "ExpertAnnotations", "ExpertVAL"
                ]
            )
            self.register_dataset(ixi_config)
        
        ################################################################################################################################
        ################################################################################################################################
        ################################################################################################################################
class ModelRegistry:
    """Registry of all supported models across datasets"""
    
    def __init__(self):
        self.models = {}
        self.dataset_registry = DatasetRegistry()
        self._register_default_models()
    
    def register_model(self, model_config: ModelConfig):
        """Register a new model configuration"""
        self.models[model_config.name] = model_config
    
    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get model configuration by name"""
        return self.models.get(name)
    
    def get_models_for_dataset(self, dataset_name: str) -> List[ModelConfig]:
        """Get all models supported by a specific dataset"""
        dataset_config = self.dataset_registry.get_dataset(dataset_name)
        if not dataset_config:
            return []
        return [
            model for model_name, model in self.models.items()
            if model_name in dataset_config.supported_models
        ]
    
    ####################################### Add here the models that you want to support ###########################################
    ################################################################################################################################
    ################################################################################################################################
    def _register_default_models(self):
        """Register default supported models"""
        # Helper functions for filename processing
        def process_nnunet(path: Path) -> Path:
            """Remove suffix and last character"""
            base = path.stem
            for suffix in ['-MRA', '-CTA']:
                base = base.replace(suffix, '')
            base = base.replace('.nii', '')
            
            if not path.with_name(f"{base[:-1]}.nii.gz").exists():
                return path.with_name(f"{base}.nii.gz")
            else:    
                return path.with_name(f"{base[:-1]}.nii.gz") 
            
        def process_stochastic(path: Path) -> Path:
            """Add vessel_mask suffix and restored prefix"""
            base = path.stem.replace('.nii', '')
            if path.with_name(f"restored_{base}_vessel_mask.nii.gz").exists():
                return path.with_name(f"restored_{base}_vessel_mask.nii.gz")
            else:
                return path.with_name(f"{base}.nii.gz") 
            
        def process_a2v(path: Path) -> Path:
            """Add pred suffix"""
            base = path.stem.replace('.nii', '')
            a2v_path = path.with_name(f"{base}.nii.gz")
            if not a2v_path.exists():
                a2v_path = path.with_name(f"{base}_pred.nii.gz")
            return a2v_path
        
        def process_shiny(path: Path) -> Path:
            """Add shiny suffix _0000"""
            base = path.stem.replace('.nii', '')
            return path.with_name(f"{base}_0000.nii.gz")
        
        def process_costa(path: Path) -> Path:
            """Add costa suffix"""
            base = path.stem.replace('.nii', '')
            ID = base.split('-')[0]
            if path.with_name(f"translated_{ID}_vessel_mask_int8.nii.gz").exists():
                return path.with_name(f"translated_{ID}_vessel_mask_int8.nii.gz")
            
            return path.with_name(f"translated_{ID}_vessel_mask.nii.gz")
        
        # Register default models
        default_models = [
            ModelConfig("IXI_TOT", "IXI", "ORIGINAL_IMG"),
            ModelConfig("COW_TOT", "TOP", "ORIGINAL_IMG"),
            
            ModelConfig("STAPLE", "STP", "STAPLE"),
            ModelConfig("STAPLE_base", "STB", "STAPLE_base"),
            
            ModelConfig("StochasticAL", "SAL", "AI", process_stochastic),
            ModelConfig("nnUNet", "UNet", "AI", process_nnunet),
            ModelConfig("A2V", "A2V", "AI", process_a2v),
            ModelConfig("COW_SEG", "COW", "AI"),
            ModelConfig("JOB-VS", "JobVs", "AI"),
            ModelConfig("JOB-VS-SHINY-1", "JobVsShiny1", "AI", process_shiny),
            ModelConfig("JOB-VS-SHINY-2", "JobVsShiny2", "AI", process_shiny),
            
            ModelConfig("Filtering", "FIL", "AI"),
            
            ModelConfig("ExpertAnnotations", "EXP", "Unknown"),
            ModelConfig("ExpertVAL", "EXPVAL", "Unknown"),
            
            ModelConfig("COSTA", "COSTA", "COSTA", process_costa),
            ModelConfig("IXI_EXP", "IXI_EXP", "MANUAL_SEG")
        ]
        
        for model in default_models:
            self.register_model(model)
    ################################################################################################################################
    ################################################################################################################################
    ################################################################################################################################
            
    def get_file_processor(self, model_name: str, dataset_name: str) -> Optional[Callable]:
        """Get the appropriate file processor for a model-dataset combination"""
        model = self.get_model(model_name)
        if not model:
            return None
            
        dataset = self.dataset_registry.get_dataset(dataset_name)
        if not dataset:
            return None
            
        if model_name not in dataset.supported_models:
            return None
            
        return model.filename_processor

# Global registry instances
model_registry = ModelRegistry()
dataset_registry = DatasetRegistry()