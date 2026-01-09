import os
import sys
from pathlib import Path

# Add scripts_py to Python path
framework_root = Path(__file__).parent.parent.parent.parent
scripts_py_path = framework_root / "scripts_py"
if str(scripts_py_path) not in sys.path:
    sys.path.insert(0, str(scripts_py_path))

import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
from viz_params_manager import VizParamsManager


class VesselVerseVizParams(ScriptedLoadableModule):
    """
    VesselVerse Visualization Parameters Module
    
    Lightweight parameter management for 3D Slicer visualizations.
    Saves camera, opacity, window/level, and segmentation settings to JSON files.
    """
    
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "VesselVerse Viz Params"
        self.parent.categories = ["VesselVerse"]
        self.parent.dependencies = []
        self.parent.contributors = ["VesselVerse Team"]
        self.parent.helpText = """
        This module allows you to save and load visualization parameters 
        (camera, opacity, window/level, segmentation) to lightweight JSON files.
        
        Perfect for version control with Git - files are typically 2-5 KB.
        """
        self.parent.acknowledgementText = """
        VesselVerse Visualization Parameters Module
        """


class VesselVerseVizParamsWidget(ScriptedLoadableModuleWidget):
    """UI Widget for VesselVerse Viz Params module"""
    
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.logic = VesselVerseVizParamsLogic()
        self.manager = VizParamsManager()
    
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # ═══════════════════════════════════════════════════
        # Volume Selection
        # ═══════════════════════════════════════════════════
        volumeCollapsible = ctk.ctkCollapsibleButton()
        volumeCollapsible.text = "1. Select Volume"
        self.layout.addWidget(volumeCollapsible)
        volumeLayout = qt.QFormLayout(volumeCollapsible)
        
        self.volumeSelector = slicer.qMRMLNodeComboBox()
        self.volumeSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
        self.volumeSelector.selectNodeUponCreation = True
        self.volumeSelector.addEnabled = False
        self.volumeSelector.removeEnabled = False
        self.volumeSelector.noneEnabled = False
        self.volumeSelector.showHidden = False
        self.volumeSelector.showChildNodeTypes = False
        self.volumeSelector.setMRMLScene(slicer.mrmlScene)
        self.volumeSelector.setToolTip("Select the volume node")
        volumeLayout.addRow("Volume: ", self.volumeSelector)
        
        # Segmentation selector (optional)
        self.segmentationSelector = slicer.qMRMLNodeComboBox()
        self.segmentationSelector.nodeTypes = ["vtkMRMLSegmentationNode"]
        self.segmentationSelector.selectNodeUponCreation = False
        self.segmentationSelector.addEnabled = False
        self.segmentationSelector.removeEnabled = False
        self.segmentationSelector.noneEnabled = True
        self.segmentationSelector.showHidden = False
        self.segmentationSelector.setMRMLScene(slicer.mrmlScene)
        self.segmentationSelector.setToolTip("Optional: Select segmentation to save visibility/opacity")
        volumeLayout.addRow("Segmentation (opt): ", self.segmentationSelector)
        
        # Dataset path selector
        self.datasetPathEdit = ctk.ctkPathLineEdit()
        self.datasetPathEdit.filters = ctk.ctkPathLineEdit.Dirs
        self.datasetPathEdit.setToolTip("Path to dataset directory (e.g., /path/to/D-IXI)")
        volumeLayout.addRow("Dataset Path: ", self.datasetPathEdit)
        
        # Auto-detect button
        self.autoDetectButton = qt.QPushButton("Auto-Detect Dataset")
        self.autoDetectButton.toolTip = "Try to auto-detect dataset path from volume file path"
        self.autoDetectButton.connect('clicked(bool)', self.onAutoDetectDataset)
        volumeLayout.addRow(self.autoDetectButton)
        
        # ═══════════════════════════════════════════════════
        # Save Parameters
        # ═══════════════════════════════════════════════════
        saveCollapsible = ctk.ctkCollapsibleButton()
        saveCollapsible.text = "2. Save Visualization Parameters"
        self.layout.addWidget(saveCollapsible)
        saveLayout = qt.QFormLayout(saveCollapsible)
        
        # Notes field
        self.notesEdit = qt.QLineEdit()
        self.notesEdit.setPlaceholderText("Optional: Add notes about these settings")
        saveLayout.addRow("Notes: ", self.notesEdit)
        
        # Save button
        self.saveButton = qt.QPushButton("💾 Save Visualization Settings")
        self.saveButton.toolTip = "Save current visualization parameters to JSON file"
        self.saveButton.enabled = False
        self.saveButton.connect('clicked(bool)', self.onSaveParams)
        saveLayout.addRow(self.saveButton)
        
        # Status label for save
        self.saveStatusLabel = qt.QLabel("")
        self.saveStatusLabel.setWordWrap(True)
        saveLayout.addRow(self.saveStatusLabel)
        
        # ═══════════════════════════════════════════════════
        # Load Parameters
        # ═══════════════════════════════════════════════════
        loadCollapsible = ctk.ctkCollapsibleButton()
        loadCollapsible.text = "3. Load Visualization Parameters"
        self.layout.addWidget(loadCollapsible)
        loadLayout = qt.QFormLayout(loadCollapsible)
        
        # Auto-load button
        self.autoLoadButton = qt.QPushButton("🔄 Auto-Load Settings")
        self.autoLoadButton.toolTip = "Auto-detect and load saved parameters for current volume"
        self.autoLoadButton.enabled = False
        self.autoLoadButton.connect('clicked(bool)', self.onAutoLoadParams)
        loadLayout.addRow(self.autoLoadButton)
        
        # Manual load button
        self.manualLoadButton = qt.QPushButton("📂 Load from File...")
        self.manualLoadButton.toolTip = "Manually select a JSON file to load"
        self.manualLoadButton.enabled = False
        self.manualLoadButton.connect('clicked(bool)', self.onManualLoadParams)
        loadLayout.addRow(self.manualLoadButton)
        
        # Status label for load
        self.loadStatusLabel = qt.QLabel("")
        self.loadStatusLabel.setWordWrap(True)
        loadLayout.addRow(self.loadStatusLabel)
        
        # ═══════════════════════════════════════════════════
        # Git Integration
        # ═══════════════════════════════════════════════════
        gitCollapsible = ctk.ctkCollapsibleButton()
        gitCollapsible.text = "4. Git Integration (Owner Only)"
        gitCollapsible.collapsed = True
        self.layout.addWidget(gitCollapsible)
        gitLayout = qt.QFormLayout(gitCollapsible)
        
        # Auto-commit checkbox
        self.autoCommitCheckbox = qt.QCheckBox()
        self.autoCommitCheckbox.checked = False
        self.autoCommitCheckbox.toolTip = "Automatically commit and push after saving parameters"
        gitLayout.addRow("Auto-commit & push: ", self.autoCommitCheckbox)
        
        # Manual commit button
        self.commitButton = qt.QPushButton("📤 Commit & Push Params")
        self.commitButton.toolTip = "Manually commit and push viz_params to Git"
        self.commitButton.connect('clicked(bool)', self.onCommitParams)
        gitLayout.addRow(self.commitButton)
        
        # Git status label
        self.gitStatusLabel = qt.QLabel("")
        self.gitStatusLabel.setWordWrap(True)
        gitLayout.addRow(self.gitStatusLabel)
        
        # ═══════════════════════════════════════════════════
        # Info Section
        # ═══════════════════════════════════════════════════
        infoCollapsible = ctk.ctkCollapsibleButton()
        infoCollapsible.text = "ℹ️ Information"
        infoCollapsible.collapsed = True
        self.layout.addWidget(infoCollapsible)
        infoLayout = qt.QVBoxLayout(infoCollapsible)
        
        infoText = qt.QLabel("""
        <b>Saved Parameters Include:</b>
        <ul>
        <li>Window/Level settings</li>
        <li>Color lookup table</li>
        <li>Opacity transfer function</li>
        <li>3D camera position</li>
        <li>Slice view positions</li>
        <li>Segmentation visibility & opacity (if selected)</li>
        </ul>
        
        <b>File Naming:</b><br>
        Files are saved as <code>{volume_name}_viz.json</code> in the dataset's <code>viz_params/</code> directory.
        
        <br><br>
        <b>Workflow:</b>
        <ol>
        <li>Select volume & dataset path</li>
        <li>Adjust visualization in Slicer</li>
        <li>Click "Save Visualization Settings"</li>
        <li>Parameters saved to JSON (~2-5 KB)</li>
        <li>Git commit & push (manual or auto)</li>
        <li>Users pull and auto-load settings</li>
        </ol>
        """)
        infoText.setWordWrap(True)
        infoLayout.addWidget(infoText)
        
        # Add vertical spacer
        self.layout.addStretch(1)
        
        # Connect volume selector to enable/disable buttons
        self.volumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onVolumeSelected)
        
        # Initial state
        self.onVolumeSelected()
    
    def cleanup(self):
        pass
    
    def onVolumeSelected(self):
        """Called when volume selection changes"""
        has_volume = self.volumeSelector.currentNode() is not None
        has_dataset_path = len(self.datasetPathEdit.currentPath) > 0
        
        self.saveButton.enabled = has_volume and has_dataset_path
        self.autoLoadButton.enabled = has_volume and has_dataset_path
        self.manualLoadButton.enabled = has_volume
    
    def onAutoDetectDataset(self):
        """Try to auto-detect dataset path from volume file path"""
        volume_node = self.volumeSelector.currentNode()
        if not volume_node:
            self.saveStatusLabel.text = "❌ No volume selected"
            return
        
        # Try to get volume file path
        storage_node = volume_node.GetStorageNode()
        if not storage_node:
            self.saveStatusLabel.text = "❌ Volume has no storage node"
            return
        
        file_path = storage_node.GetFileName()
        if not file_path:
            self.saveStatusLabel.text = "❌ Could not get volume file path"
            return
        
        # Navigate up to find dataset directory (looks for D-*)
        current_path = Path(file_path).parent
        for _ in range(5):  # Max 5 levels up
            if current_path.name.startswith('D-'):
                self.datasetPathEdit.setCurrentPath(str(current_path))
                self.saveStatusLabel.text = f"✅ Auto-detected: {current_path.name}"
                self.onVolumeSelected()  # Update button states
                return
            current_path = current_path.parent
        
        self.saveStatusLabel.text = "❌ Could not auto-detect dataset (no D-* directory found)"
    
    def onSaveParams(self):
        """Save visualization parameters"""
        volume_node = self.volumeSelector.currentNode()
        segmentation_node = self.segmentationSelector.currentNode()
        dataset_path = self.datasetPathEdit.currentPath
        notes = self.notesEdit.text
        
        if not volume_node:
            self.saveStatusLabel.text = "❌ No volume selected"
            return
        
        if not dataset_path:
            self.saveStatusLabel.text = "❌ No dataset path specified"
            return
        
        # Generate output filename
        volume_name = volume_node.GetName()
        base_name = volume_name.replace('.nii.gz', '').replace('.nii', '').replace('.nrrd', '')
        output_filename = f"{base_name}_viz.json"
        
        # Construct full path
        viz_params_dir = Path(dataset_path) / "viz_params"
        viz_params_dir.mkdir(parents=True, exist_ok=True)
        output_path = viz_params_dir / output_filename
        
        # Save parameters
        success = self.manager.save_params(
            volume_node,
            str(output_path),
            segmentation_node,
            notes
        )
        
        if success:
            self.saveStatusLabel.text = f"✅ Saved to: {output_filename}"
            
            # Auto-commit if enabled
            if self.autoCommitCheckbox.checked:
                self.onCommitParams()
        else:
            self.saveStatusLabel.text = "❌ Failed to save parameters"
    
    def onAutoLoadParams(self):
        """Auto-detect and load parameters"""
        volume_node = self.volumeSelector.currentNode()
        segmentation_node = self.segmentationSelector.currentNode()
        dataset_path = self.datasetPathEdit.currentPath
        
        if not volume_node or not dataset_path:
            self.loadStatusLabel.text = "❌ Volume or dataset path not specified"
            return
        
        # Auto-detect params file
        params_file = self.manager.auto_detect_params_file(volume_node, dataset_path)
        
        if not params_file:
            self.loadStatusLabel.text = "❌ No saved parameters found for this volume"
            return
        
        # Load parameters
        success = self.manager.load_params(volume_node, params_file, segmentation_node)
        
        if success:
            self.loadStatusLabel.text = f"✅ Loaded from: {Path(params_file).name}"
        else:
            self.loadStatusLabel.text = "❌ Failed to load parameters"
    
    def onManualLoadParams(self):
        """Manually select and load parameters file"""
        volume_node = self.volumeSelector.currentNode()
        segmentation_node = self.segmentationSelector.currentNode()
        
        if not volume_node:
            self.loadStatusLabel.text = "❌ No volume selected"
            return
        
        # Open file dialog
        file_path = qt.QFileDialog.getOpenFileName(
            self.parent,
            "Select Visualization Parameters File",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
        
        # Load parameters
        success = self.manager.load_params(volume_node, file_path, segmentation_node)
        
        if success:
            self.loadStatusLabel.text = f"✅ Loaded from: {Path(file_path).name}"
        else:
            self.loadStatusLabel.text = "❌ Failed to load parameters"
    
    def onCommitParams(self):
        """Commit and push viz_params to Git"""
        dataset_path = self.datasetPathEdit.currentPath
        
        if not dataset_path:
            self.gitStatusLabel.text = "❌ No dataset path specified"
            return
        
        self.gitStatusLabel.text = "⏳ Committing..."
        
        success = self.logic.commit_and_push_params(dataset_path)
        
        if success:
            self.gitStatusLabel.text = "✅ Committed and pushed to Git"
        else:
            self.gitStatusLabel.text = "❌ Git commit failed (check terminal for details)"


class VesselVerseVizParamsLogic(ScriptedLoadableModuleLogic):
    """Logic class for VesselVerse Viz Params module"""
    
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
    
    def commit_and_push_params(self, dataset_path: str) -> bool:
        """
        Commit and push viz_params directory to Git.
        
        Args:
            dataset_path: Path to dataset directory
            
        Returns:
            True if successful, False otherwise
        """
        import subprocess
        
        try:
            dataset_path = Path(dataset_path)
            viz_params_dir = dataset_path / "viz_params"
            
            if not viz_params_dir.exists():
                print(f"❌ viz_params directory not found: {viz_params_dir}")
                return False
            
            # Git add
            subprocess.run(
                ["git", "add", "viz_params/*.json"],
                cwd=dataset_path,
                check=True,
                capture_output=True
            )
            
            # Git commit
            result = subprocess.run(
                ["git", "commit", "-m", "Update visualization parameters"],
                cwd=dataset_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("ℹ️ No changes to commit")
                    return True
                else:
                    print(f"❌ Git commit failed: {result.stderr}")
                    return False
            
            # Git push
            subprocess.run(
                ["git", "push"],
                cwd=dataset_path,
                check=True,
                capture_output=True
            )
            
            print("✅ Visualization parameters committed and pushed")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False


class VesselVerseVizParamsTest(ScriptedLoadableModuleTest):
    """Test class for VesselVerse Viz Params module"""
    
    def setUp(self):
        slicer.mrmlScene.Clear()
    
    def runTest(self):
        self.setUp()
        self.test_VesselVerseVizParams1()
    
    def test_VesselVerseVizParams1(self):
        self.delayDisplay("Starting the test")
        self.delayDisplay('Test passed')
