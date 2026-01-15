#!/usr/bin/env python3
"""
VesselVerse Visualization Parameters Manager
Save and load 3D Slicer visualization parameters to/from lightweight JSON files.

Usage:
    # Inside 3D Slicer Python console:
    import sys
    sys.path.append('/path/to/VesselVerse-Framework/scripts_py')
    from viz_params_manager import VizParamsManager
    
    manager = VizParamsManager()
    
    # Save current visualization
    manager.save_params(volume_node, '/path/to/viz_params/volume_viz.json')
    
    # Load visualization
    manager.load_params(volume_node, '/path/to/viz_params/volume_viz.json')
"""

import json
import slicer
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple


class VizParamsManager:
    """Manager for saving/loading 3D Slicer visualization parameters"""
    
    SCHEMA_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the visualization parameters manager"""
        pass
    
    def get_volume_display_node(self, volume_node):
        """Get the display node for a volume"""
        if volume_node is None:
            return None
        return volume_node.GetDisplayNode()
    
    def get_volume_rendering_node(self, volume_node):
        """Get the volume rendering display node"""
        if volume_node is None:
            return None
        
        # Get volume rendering logic
        volRenLogic = slicer.modules.volumerendering.logic()
        return volRenLogic.GetFirstVolumeRenderingDisplayNode(volume_node)
    
    def extract_window_level(self, display_node) -> Optional[Dict[str, float]]:
        """Extract window/level settings"""
        if display_node is None:
            return None
        
        return {
            "window": display_node.GetWindow(),
            "level": display_node.GetLevel()
        }
    
    def extract_color_map(self, display_node) -> Optional[str]:
        """Extract color lookup table name"""
        if display_node is None:
            return None
        
        color_node = display_node.GetColorNode()
        if color_node:
            return color_node.GetName()
        return "Grey"
    
    def extract_opacity_transfer(self, vol_render_node) -> Optional[List[Tuple[float, float]]]:
        """Extract opacity transfer function"""
        if vol_render_node is None:
            return None
        
        prop = vol_render_node.GetVolumePropertyNode()
        if prop is None:
            return None
        
        vol_prop = prop.GetVolumeProperty()
        opacity_func = vol_prop.GetScalarOpacity()
        
        # Sample the opacity function
        points = []
        num_points = opacity_func.GetSize()
        for i in range(num_points):
            point = [0.0, 0.0, 0.0, 0.0]
            opacity_func.GetNodeValue(i, point)
            points.append([point[0], point[1]])  # [intensity, opacity]
        
        return points if points else None
    
    def extract_gradient_opacity(self, vol_render_node) -> Optional[List[Tuple[float, float]]]:
        """Extract gradient opacity function"""
        if vol_render_node is None:
            return None
        
        prop = vol_render_node.GetVolumePropertyNode()
        if prop is None:
            return None
        
        vol_prop = prop.GetVolumeProperty()
        gradient_func = vol_prop.GetGradientOpacity()
        
        # Sample the gradient function
        points = []
        num_points = gradient_func.GetSize()
        for i in range(num_points):
            point = [0.0, 0.0, 0.0, 0.0]
            gradient_func.GetNodeValue(i, point)
            points.append([point[0], point[1]])
        
        return points if points else None
    
    def extract_camera(self) -> Dict[str, Any]:
        """Extract 3D camera parameters"""
        layout_manager = slicer.app.layoutManager()
        threeDWidget = layout_manager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        
        # Get camera from renderer
        renderWindow = threeDView.renderWindow()
        renderers = renderWindow.GetRenderers()
        renderer = renderers.GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        
        position = camera.GetPosition()
        focal_point = camera.GetFocalPoint()
        view_up = camera.GetViewUp()
        view_angle = camera.GetViewAngle()
        
        return {
            "position": list(position),
            "focal_point": list(focal_point),
            "view_up": list(view_up),
            "view_angle": view_angle
        }
    
    def extract_slice_views(self) -> Dict[str, float]:
        """Extract 2D slice view positions"""
        slice_positions = {}
        
        slice_names = ["Red", "Yellow", "Green"]
        for slice_name in slice_names:
            slice_logic = slicer.app.layoutManager().sliceWidget(slice_name).sliceLogic()
            slice_node = slice_logic.GetSliceNode()
            slice_positions[slice_name.lower()] = slice_node.GetSliceOffset()
        
        return slice_positions
    
    def extract_segmentation_visibility(self, segmentation_node) -> Dict[str, bool]:
        """Extract visibility state for each segment"""
        if segmentation_node is None:
            return {}
        
        visibility = {}
        segmentation = segmentation_node.GetSegmentation()
        
        for i in range(segmentation.GetNumberOfSegments()):
            segment_id = segmentation.GetNthSegmentID(i)
            segment = segmentation.GetSegment(segment_id)
            segment_name = segment.GetName()
            
            display_node = segmentation_node.GetDisplayNode()
            is_visible = display_node.GetSegmentVisibility(segment_id) if display_node else True
            
            visibility[segment_name] = is_visible
        
        return visibility
    
    def extract_segmentation_opacity(self, segmentation_node) -> Dict[str, float]:
        """Extract opacity for each segment"""
        if segmentation_node is None:
            return {}
        
        opacity = {}
        segmentation = segmentation_node.GetSegmentation()
        display_node = segmentation_node.GetDisplayNode()
        
        if display_node is None:
            return {}
        
        for i in range(segmentation.GetNumberOfSegments()):
            segment_id = segmentation.GetNthSegmentID(i)
            segment = segmentation.GetSegment(segment_id)
            segment_name = segment.GetName()
            
            segment_opacity = display_node.GetSegmentOpacity3D(segment_id)
            opacity[segment_name] = segment_opacity
        
        return opacity
    
    def save_params(self, volume_node, output_path: str, segmentation_node=None, notes: str = "", user_name: str = "", expertise: str = "") -> bool:
        """
        Save visualization parameters to JSON file.
        
        Args:
            volume_node: Slicer volume node
            output_path: Path to save JSON file
            segmentation_node: Optional segmentation node
            notes: Optional notes about settings
            user_name: Name of the user saving the params
            expertise: Level of expertise (basic/intermediate/advanced)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get display nodes
            display_node = self.get_volume_display_node(volume_node)
            vol_render_node = self.get_volume_rendering_node(volume_node)
            
            # Build parameters dictionary
            params = {
                "volume": volume_node.GetName(),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "slicer_version": slicer.app.applicationVersion,
                "schema_version": self.SCHEMA_VERSION
            }

            # User info
            if user_name or expertise:
                params["user"] = {
                    "name": user_name,
                    "expertise": expertise
                }
            
            # Window/Level
            window_level = self.extract_window_level(display_node)
            if window_level:
                params["window_level"] = window_level
            
            # Color map
            color_map = self.extract_color_map(display_node)
            if color_map:
                params["color_map"] = color_map
            
            # Volume rendering parameters
            if vol_render_node:
                opacity_transfer = self.extract_opacity_transfer(vol_render_node)
                if opacity_transfer:
                    params["opacity_transfer"] = opacity_transfer
                
                gradient_opacity = self.extract_gradient_opacity(vol_render_node)
                if gradient_opacity:
                    params["gradient_opacity"] = gradient_opacity
                
                # Rendering mode
                if vol_render_node.GetVolumePropertyNode():
                    vol_prop = vol_render_node.GetVolumePropertyNode().GetVolumeProperty()
                    params["rendering_mode"] = "VR_GPU_Ray_Casting"  # Default
            
            # Camera
            params["camera"] = self.extract_camera()
            
            # Slice views
            params["slice_views"] = self.extract_slice_views()
            
            # Segmentation (if provided)
            if segmentation_node:
                params["segmentation_visibility"] = self.extract_segmentation_visibility(segmentation_node)
                params["segmentation_opacity"] = self.extract_segmentation_opacity(segmentation_node)
            
            # Notes
            if notes:
                params["notes"] = notes
            
            # Save to file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(params, f, indent=2)
            
            print(f"✅ Saved visualization parameters to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving parameters: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def apply_window_level(self, display_node, window_level: Dict[str, float]):
        """Apply window/level settings"""
        if display_node and window_level:
            # Disable Auto Window/Level so manual values are used
            display_node.SetAutoWindowLevel(0)
            display_node.SetWindow(window_level["window"])
            display_node.SetLevel(window_level["level"])
            display_node.Modified()
    
    def apply_color_map(self, display_node, color_map_name: str):
        """Apply color lookup table"""
        if display_node and color_map_name:
            color_node = slicer.util.getNode(f"*{color_map_name}*")
            if color_node:
                display_node.SetAndObserveColorNodeID(color_node.GetID())
                display_node.Modified()
    
    def apply_opacity_transfer(self, vol_render_node, opacity_points: List[Tuple[float, float]]):
        """Apply opacity transfer function"""
        if vol_render_node is None or not opacity_points:
            return
        
        prop = vol_render_node.GetVolumePropertyNode()
        if prop is None:
            return
        
        vol_prop = prop.GetVolumeProperty()
        opacity_func = vol_prop.GetScalarOpacity()
        
        # Clear existing points
        opacity_func.RemoveAllPoints()
        
        # Add new points
        for intensity, opacity in opacity_points:
            opacity_func.AddPoint(intensity, opacity)
        
        # Notify changes
        prop.Modified()
        vol_render_node.Modified()
    
    def apply_gradient_opacity(self, vol_render_node, gradient_points: List[Tuple[float, float]]):
        """Apply gradient opacity function"""
        if vol_render_node is None or not gradient_points:
            return
        
        prop = vol_render_node.GetVolumePropertyNode()
        if prop is None:
            return
        
        vol_prop = prop.GetVolumeProperty()
        gradient_func = vol_prop.GetGradientOpacity()
        
        gradient_func.RemoveAllPoints()
        for gradient, opacity in gradient_points:
            gradient_func.AddPoint(gradient, opacity)
        
        # Notify changes
        prop.Modified()
        vol_render_node.Modified()
    
    def apply_camera(self, camera_params: Dict[str, Any]):
        """Apply camera parameters"""
        layout_manager = slicer.app.layoutManager()
        threeDWidget = layout_manager.threeDWidget(0)
        threeDView = threeDWidget.threeDView()
        
        # Get camera from the renderer
        renderWindow = threeDView.renderWindow()
        renderers = renderWindow.GetRenderers()
        renderer = renderers.GetFirstRenderer()
        camera = renderer.GetActiveCamera()
        
        camera.SetPosition(camera_params["position"])
        camera.SetFocalPoint(camera_params["focal_point"])
        camera.SetViewUp(camera_params["view_up"])
        camera.SetViewAngle(camera_params["view_angle"])
        
        threeDView.resetFocalPoint()
    
    def apply_slice_views(self, slice_positions: Dict[str, float]):
        """Apply slice view positions"""
        for slice_name, position in slice_positions.items():
            slice_widget = slicer.app.layoutManager().sliceWidget(slice_name.capitalize())
            if slice_widget:
                slice_logic = slice_widget.sliceLogic()
                slice_node = slice_logic.GetSliceNode()
                slice_node.SetSliceOffset(position)
    
    def apply_segmentation_visibility(self, segmentation_node, visibility: Dict[str, bool]):
        """Apply segmentation visibility"""
        if segmentation_node is None or not visibility:
            return
        
        segmentation = segmentation_node.GetSegmentation()
        display_node = segmentation_node.GetDisplayNode()
        
        if display_node is None:
            return
        
        for segment_name, is_visible in visibility.items():
            # Find segment by name
            segment_id = segmentation.GetSegmentIdBySegmentName(segment_name)
            if segment_id:
                display_node.SetSegmentVisibility(segment_id, is_visible)
    
    def apply_segmentation_opacity(self, segmentation_node, opacity: Dict[str, float]):
        """Apply segmentation opacity"""
        if segmentation_node is None or not opacity:
            return
        
        segmentation = segmentation_node.GetSegmentation()
        display_node = segmentation_node.GetDisplayNode()
        
        if display_node is None:
            return
        
        for segment_name, segment_opacity in opacity.items():
            segment_id = segmentation.GetSegmentIdBySegmentName(segment_name)
            if segment_id:
                display_node.SetSegmentOpacity3D(segment_id, segment_opacity)
    
    def load_params(self, volume_node, input_path: str, segmentation_node=None) -> bool:
        """
        Load visualization parameters from JSON file.
        
        Args:
            volume_node: Slicer volume node
            input_path: Path to JSON file
            segmentation_node: Optional segmentation node
            
        Returns:
            True if successful, False otherwise
        """
        try:
            input_path = Path(input_path)
            if not input_path.exists():
                print(f"❌ File not found: {input_path}")
                return False
            
            # Load JSON
            with open(input_path, 'r') as f:
                params = json.load(f)
            
            print(f"📂 Loading visualization parameters from: {input_path}")
            print(f"   Original volume: {params.get('volume', 'unknown')}")
            print(f"   Saved: {params.get('timestamp', 'unknown')}")
            
            # Get display nodes
            display_node = self.get_volume_display_node(volume_node)
            vol_render_node = self.get_volume_rendering_node(volume_node)
            
            # Apply window/level
            if "window_level" in params:
                self.apply_window_level(display_node, params["window_level"])
            
            # Apply color map
            if "color_map" in params:
                self.apply_color_map(display_node, params["color_map"])
            
            # Apply volume rendering
            if vol_render_node:
                if "opacity_transfer" in params:
                    self.apply_opacity_transfer(vol_render_node, params["opacity_transfer"])
                
                if "gradient_opacity" in params:
                    self.apply_gradient_opacity(vol_render_node, params["gradient_opacity"])
            
            # Apply camera
            if "camera" in params:
                self.apply_camera(params["camera"])
            
            # Apply slice views
            if "slice_views" in params:
                self.apply_slice_views(params["slice_views"])
            
            # Apply segmentation
            if segmentation_node:
                if "segmentation_visibility" in params:
                    self.apply_segmentation_visibility(segmentation_node, params["segmentation_visibility"])
                
                if "segmentation_opacity" in params:
                    self.apply_segmentation_opacity(segmentation_node, params["segmentation_opacity"])
            
            # Force refresh all views
            slicer.app.layoutManager().threeDWidget(0).threeDView().forceRender()
            for name in ['Red', 'Yellow', 'Green']:
                slice_widget = slicer.app.layoutManager().sliceWidget(name)
                if slice_widget:
                    slice_widget.sliceView().forceRender()
            
            print("✅ Visualization parameters loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading parameters: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def auto_detect_params_file(self, volume_node, dataset_path: str) -> Optional[str]:
        """
        Auto-detect viz_params JSON file for a volume.
        
        Naming convention: {volume_name}_viz.json
        
        Args:
            volume_node: Slicer volume node
            dataset_path: Path to dataset directory (e.g., D-IXI)
            
        Returns:
            Path to JSON file if found, None otherwise
        """
        volume_name = volume_node.GetName()
        
        # Try with .nii.gz extension removed
        base_name = volume_name.replace('.nii.gz', '').replace('.nii', '').replace('.nrrd', '')
        
        viz_params_dir = Path(dataset_path) / "viz_params"
        
        # Try exact match first
        json_path = viz_params_dir / f"{base_name}_viz.json"
        if json_path.exists():
            return str(json_path)
        
        # Try with original name
        json_path = viz_params_dir / f"{volume_name}_viz.json"
        if json_path.exists():
            return str(json_path)
        
        return None


# Convenience functions for quick use in Slicer console
def save_viz(volume_name: str = None, output_filename: str = None):
    """
    Quick save current visualization parameters.
    
    Usage:
        save_viz()  # Auto-detect active volume
        save_viz("IXI001_MRA")  # Specify volume
    """
    manager = VizParamsManager()
    
    # Get volume node
    if volume_name is None:
        # Get active volume from selection
        volume_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
    else:
        volume_node = slicer.util.getNode(volume_name)
    
    if volume_node is None:
        print("❌ No volume found")
        return False
    
    # Auto-generate filename
    if output_filename is None:
        volume_base = volume_node.GetName().replace('.nii.gz', '').replace('.nii', '')
        output_filename = f"{volume_base}_viz.json"
    
    # Assume viz_params directory in same folder as volume
    # This needs to be customized based on your dataset structure
    output_path = f"/tmp/{output_filename}"  # Placeholder
    
    # Try to get segmentation
    segmentation_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
    
    return manager.save_params(volume_node, output_path, segmentation_node)


def load_viz(volume_name: str = None, input_filename: str = None):
    """
    Quick load visualization parameters.
    
    Usage:
        load_viz()  # Auto-detect active volume and params file
        load_viz("IXI001_MRA", "IXI001_MRA_viz.json")
    """
    manager = VizParamsManager()
    
    # Get volume node
    if volume_name is None:
        volume_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
    else:
        volume_node = slicer.util.getNode(volume_name)
    
    if volume_node is None:
        print("❌ No volume found")
        return False
    
    # Auto-detect params file if not specified
    if input_filename is None:
        # Try to auto-detect
        input_path = "/tmp/placeholder_viz.json"  # Placeholder
    else:
        input_path = input_filename
    
    # Try to get segmentation
    segmentation_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
    
    return manager.load_params(volume_node, input_path, segmentation_node)
