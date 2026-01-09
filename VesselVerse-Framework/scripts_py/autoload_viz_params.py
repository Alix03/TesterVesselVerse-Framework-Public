"""
VesselVerse Auto-Load Hook
Automatically loads visualization parameters when a volume is opened in Slicer.

Installation:
    Copy this file to: ~/.config/NA-MIC/Extensions-*/SlicerStartup/
    
    Or add to SlicerRC.py:
    exec(open('/path/to/autoload_viz_params.py').read())
"""

import sys
from pathlib import Path

# Add scripts_py to path
framework_root = Path.home() / "Desktop" / "VesselVerse" / "VesselVerse-Framework"
scripts_py_path = framework_root / "scripts_py"
if str(scripts_py_path) not in sys.path:
    sys.path.insert(0, str(scripts_py_path))

try:
    from viz_params_manager import VizParamsManager
    
    class VizParamsAutoLoader:
        """Auto-loads visualization parameters when volumes are added to scene"""
        
        def __init__(self):
            self.manager = VizParamsManager()
            self.processed_volumes = set()
            
            # Connect to scene events
            slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAddedEvent, self.onNodeAdded)
            print("✅ VesselVerse Auto-Load Hook activated")
        
        def onNodeAdded(self, caller, event):
            """Called when a node is added to the scene"""
            # Get the newly added node
            nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode")
            nodes.UnRegister(slicer.mrmlScene)
            
            for i in range(nodes.GetNumberOfItems()):
                volume_node = nodes.GetItemAsObject(i)
                node_id = volume_node.GetID()
                
                # Skip if already processed
                if node_id in self.processed_volumes:
                    continue
                
                self.processed_volumes.add(node_id)
                
                # Try to auto-load parameters
                self.tryAutoLoad(volume_node)
        
        def tryAutoLoad(self, volume_node):
            """Try to auto-load parameters for a volume"""
            try:
                # Get volume file path
                storage_node = volume_node.GetStorageNode()
                if not storage_node:
                    return
                
                file_path = storage_node.GetFileName()
                if not file_path:
                    return
                
                # Find dataset directory
                dataset_path = self.findDatasetPath(file_path)
                if not dataset_path:
                    return
                
                # Auto-detect params file
                params_file = self.manager.auto_detect_params_file(volume_node, str(dataset_path))
                if not params_file:
                    print(f"ℹ️ No saved visualization parameters for: {volume_node.GetName()}")
                    return
                
                # Load parameters
                print(f"📂 Auto-loading visualization parameters for: {volume_node.GetName()}")
                
                # Try to find segmentation node
                segmentation_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
                
                success = self.manager.load_params(volume_node, params_file, segmentation_node)
                
                if success:
                    print(f"✅ Visualization parameters loaded automatically")
                else:
                    print(f"❌ Failed to load parameters")
                    
            except Exception as e:
                print(f"❌ Auto-load error: {e}")
        
        def findDatasetPath(self, file_path: str) -> Path:
            """Find dataset directory (D-*) in file path"""
            current_path = Path(file_path).parent
            
            for _ in range(5):  # Max 5 levels up
                if current_path.name.startswith('D-'):
                    return current_path
                current_path = current_path.parent
            
            return None
    
    # Create global instance
    if not hasattr(slicer, 'vizParamsAutoLoader'):
        slicer.vizParamsAutoLoader = VizParamsAutoLoader()

except ImportError as e:
    print(f"⚠️ VesselVerse Auto-Load Hook: Could not import viz_params_manager")
    print(f"   Make sure VesselVerse-Framework is installed at: {framework_root}")
except Exception as e:
    print(f"❌ VesselVerse Auto-Load Hook failed: {e}")
