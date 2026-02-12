import os
import SimpleITK as sitk
import vtk
import numpy as np
from vtk.util import numpy_support
import sys

# --- Constants for Density (Hounsfield Units) ---
# Approximate HU values for CT
SOFT_TISSUE_MAX = 200
BONE_MIN = 300
BONE_MAX = 2000

# --- DICOM Loading and VTK Conversion Functions ---

def load_dicom_series(dicom_dir):
    print("📦 Loading DICOM series...")
    reader = sitk.ImageSeriesReader()
    series_IDs = reader.GetGDCMSeriesIDs(dicom_dir)

    if not series_IDs:
        raise ValueError("❌ No DICOM series found.")

    print(f"🆔 Series ID: {series_IDs[0]}")
    series_file_names = reader.GetGDCMSeriesFileNames(dicom_dir, series_IDs[0])
    print(f"📄 Files found: {len(series_file_names)}")

    reader.SetFileNames(series_file_names)
    image = reader.Execute()
    return image


def sitk_to_vtk(sitk_image):
    # Clip and convert the data for better visualization range
    np_array = sitk.GetArrayFromImage(sitk_image)
    np_array = np.clip(np_array, 0, BONE_MAX).astype(np.uint16) 
    
    flat_array = np_array.ravel()

    vtk_array = numpy_support.numpy_to_vtk(
        flat_array, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT
    )

    vtk_image = vtk.vtkImageData()
    vtk_image.SetDimensions(sitk_image.GetSize())
    vtk_image.SetSpacing(sitk_image.GetSpacing()[::-1])
    vtk_image.SetOrigin(sitk_image.GetOrigin()[::-1])
    vtk_image.GetPointData().SetScalars(vtk_array)

    return vtk_image


# --- Transfer Function Definitions ---

def create_color_function(r, g, b):
    color = vtk.vtkColorTransferFunction()
    # Apply color only to the relevant density range
    color.AddRGBPoint(0, 0.0, 0.0, 0.0) 
    color.AddRGBPoint(BONE_MIN - 1, 0.0, 0.0, 0.0)
    color.AddRGBPoint(BONE_MIN, r, g, b)
    color.AddRGBPoint(BONE_MAX, r, g, b)
    return color

def create_opacity_function(min_hu, max_hu, scale):
    opacity = vtk.vtkPiecewiseFunction()
    opacity.AddPoint(min_hu - 1, 0.0)
    opacity.AddPoint(min_hu, scale * 0.1)
    opacity.AddPoint((min_hu + max_hu) / 2, scale * 0.5)
    opacity.AddPoint(max_hu, scale * 1.0)
    return opacity

# --- Multi-Volume Creation Function (FIXED: SetName removed) ---

def create_bone_volume(vtk_image, color_rgb, opacity_scale, name):
    # 1. Volume Mapper
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(vtk_image)

    # 2. Volume Property
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(create_color_function(*color_rgb))
    
    volume_property.SetScalarOpacity(
        create_opacity_function(BONE_MIN, BONE_MAX, opacity_scale)
    )
    volume_property.ShadeOn()
    volume_property.SetInterpolationTypeToLinear()

    # 3. Volume
    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)
    # The problematic volume.SetName(name) call has been removed.
    
    return volume, volume_property


# --- Visualization Loop ---

def visualize_multi_volume(vtk_image):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.03, 0.03, 0.08)

    # --- Setting up Multiple Volumes for Different Colors (Conceptual Segmentation) ---

    bone_volumes = []
    
    # Bone 1 (e.g., Femur) - Red/White
    v1, p1 = create_bone_volume(vtk_image, (1.0, 0.2, 0.2), 0.7, "Femur") 
    bone_volumes.append(v1)

    # Bone 2 (e.g., Tibia) - Blue/White
    v2, p2 = create_bone_volume(vtk_image, (0.2, 0.2, 1.0), 0.7, "Tibia") 
    bone_volumes.append(v2)

    # Bone 3 (e.g., Fibula) - Yellow/White
    v3, p3 = create_bone_volume(vtk_image, (1.0, 1.0, 0.2), 0.7, "Fibula") 
    bone_volumes.append(v3)

    # Soft Tissue (Grayish)
    soft_tissue_volume_property = vtk.vtkVolumeProperty()
    soft_tissue_volume_property.SetColor(create_color_function(0.5, 0.5, 0.5))
    soft_tissue_volume_property.SetScalarOpacity(
        create_opacity_function(0, SOFT_TISSUE_MAX, 0.1)
    )
    soft_tissue_volume_property.ShadeOn()
    soft_tissue_volume_property.SetInterpolationTypeToLinear()
    
    # Use the same mapper as the first bone
    soft_tissue_volume = vtk.vtkVolume()
    soft_tissue_volume.SetMapper(v1.GetMapper()) 
    soft_tissue_volume.SetProperty(soft_tissue_volume_property)

    # Add all volumes to the renderer (Tissue first, then Bones)
    renderer.AddVolume(soft_tissue_volume)
    for v in bone_volumes:
        renderer.AddVolume(v)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Initial Render
    renderer.ResetCamera()
    render_window.Render()
    interactor.Initialize()
    
    print("\n💡 NOTE: Multi-color rendering is active.")
    print("If colors blend, it means advanced segmentation is needed to separate the bone pixels.")

    interactor.Start()


def mainnn():
    try:
        # NOTE: Ensure a folder named "Sample_DICOM" containing your DICOM files
        # is present in the same directory as this script.
        dicom_dir = os.path.join(os.getcwd(), "Sample_DICOM")
        print(f"📂 Reading from: {dicom_dir}")

        sitk_img = load_dicom_series(dicom_dir)
        print(f"✅ Volume size: {sitk_img.GetSize()}, spacing: {sitk_img.GetSpacing()}")

        vtk_img = sitk_to_vtk(sitk_img)
        print("✅ Converted to VTK format")

        visualize_multi_volume(vtk_img)
        print("✅ Viewer closed")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    mainnn()