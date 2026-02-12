import os
import SimpleITK as sitk
import vtk
import numpy as np
from vtk.util import numpy_support


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
    np_array = sitk.GetArrayFromImage(sitk_image)
    np_array = np.clip(np_array, 0, 2000).astype(np.uint16)
    flat_array = np_array.ravel()

    vtk_array = numpy_support.numpy_to_vtk(
        flat_array, deep=True, array_type=vtk.VTK_UNSIGNED_SHORT
    )

    vtk_image = vtk.vtkImageData()
    vtk_image.SetDimensions(sitk_image.GetSize())
    vtk_image.SetSpacing(sitk_image.GetSpacing())
    vtk_image.SetOrigin(sitk_image.GetOrigin())
    vtk_image.GetPointData().SetScalars(vtk_array)

    return vtk_image


def create_opacity_function(bone_scale=1.0, tissue_scale=1.0):
    opacity = vtk.vtkPiecewiseFunction()
    opacity.AddPoint(0, 0.00)
    opacity.AddPoint(150, tissue_scale * 0.02)
    opacity.AddPoint(300, tissue_scale * 0.1)
    opacity.AddPoint(500, tissue_scale * 0.25)
    opacity.AddPoint(800, tissue_scale * 0.5)
    opacity.AddPoint(1000, tissue_scale * 0.85)
    opacity.AddPoint(1300, bone_scale * 1.0)
    return opacity


def add_opacity_sliders(interactor, volume_property, render_window):
    def slider_callback_bone(obj, event):
        bone_val = slider_bone.GetRepresentation().GetValue()
        tissue_val = slider_tissue.GetRepresentation().GetValue()
        volume_property.SetScalarOpacity(create_opacity_function(bone_val, tissue_val))
        render_window.Render()

    def slider_callback_tissue(obj, event):
        bone_val = slider_bone.GetRepresentation().GetValue()
        tissue_val = slider_tissue.GetRepresentation().GetValue()
        volume_property.SetScalarOpacity(create_opacity_function(bone_val, tissue_val))
        render_window.Render()

    # Bone Opacity Slider
    slider_rep_bone = vtk.vtkSliderRepresentation2D()
    slider_rep_bone.SetMinimumValue(0.0)
    slider_rep_bone.SetMaximumValue(1.0)
    slider_rep_bone.SetValue(0.5)
    slider_rep_bone.SetTitleText("Bone Opacity")
    slider_rep_bone.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider_rep_bone.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider_rep_bone.GetPoint1Coordinate().SetValue(0.1, 0.1)  # Bottom-left
    slider_rep_bone.GetPoint2Coordinate().SetValue(0.4, 0.1)
    slider_rep_bone.SetSliderLength(0.02)
    slider_rep_bone.SetSliderWidth(0.03)
    slider_rep_bone.SetEndCapLength(0.01)
    slider_rep_bone.SetEndCapWidth(0.03)
    slider_rep_bone.SetTubeWidth(0.005)
    slider_rep_bone.SetLabelFormat("%0.2f")
    slider_rep_bone.SetTitleHeight(0.02)
    slider_rep_bone.SetLabelHeight(0.02)

    slider_bone = vtk.vtkSliderWidget()
    slider_bone.SetInteractor(interactor)
    slider_bone.SetRepresentation(slider_rep_bone)
    slider_bone.SetAnimationModeToAnimate()
    slider_bone.EnabledOn()
    slider_bone.AddObserver("InteractionEvent", slider_callback_bone)

    # Tissue Opacity Slider
    slider_rep_tissue = vtk.vtkSliderRepresentation2D()
    slider_rep_tissue.SetMinimumValue(0.0)
    slider_rep_tissue.SetMaximumValue(1.0)
    slider_rep_tissue.SetValue(0.5)
    slider_rep_tissue.SetTitleText("Tissue Opacity")
    slider_rep_tissue.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider_rep_tissue.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slider_rep_tissue.GetPoint1Coordinate().SetValue(0.1, 0.15)  # Bottom-left
    slider_rep_tissue.GetPoint2Coordinate().SetValue(0.4, 0.15)
    slider_rep_tissue.SetSliderLength(0.02)
    slider_rep_tissue.SetSliderWidth(0.03)
    slider_rep_tissue.SetEndCapLength(0.01)
    slider_rep_tissue.SetEndCapWidth(0.03)
    slider_rep_tissue.SetTubeWidth(0.005)
    slider_rep_tissue.SetLabelFormat("%0.2f")
    slider_rep_tissue.SetTitleHeight(0.02)
    slider_rep_tissue.SetLabelHeight(0.02)

    slider_tissue = vtk.vtkSliderWidget()
    slider_tissue.SetInteractor(interactor)
    slider_tissue.SetRepresentation(slider_rep_tissue)
    slider_tissue.SetAnimationModeToAnimate()
    slider_tissue.EnabledOn()
    slider_tissue.AddObserver("InteractionEvent", slider_callback_tissue)


def visualize_3d_volume(vtk_image):
    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(vtk_image)

    color = vtk.vtkColorTransferFunction()
    color.AddRGBPoint(0, 0.0, 0.0, 0.0)
    color.AddRGBPoint(150, 0.4, 0.3, 0.2)
    color.AddRGBPoint(300, 0.5, 0.35, 0.3)
    color.AddRGBPoint(800, 0.9, 0.8, 0.7)
    color.AddRGBPoint(1300, 1.0, 1.0, 1.0)

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color)
    volume_property.SetScalarOpacity(create_opacity_function(0.5, 0.5))
    volume_property.ShadeOn()
    volume_property.SetInterpolationTypeToLinear()

    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)

    renderer = vtk.vtkRenderer()
    renderer.AddVolume(volume)
    renderer.SetBackground(0.03, 0.03, 0.08)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1000, 1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Initialize before adding widget
    interactor.Initialize()
    render_window.Render()

    # Now safely add sliders
    add_opacity_sliders(interactor, volume_property, render_window)

    interactor.Start()


def main():
    try:
        dicom_dir = os.path.join(os.getcwd(), "Sample_DICOM")
        print(f"📂 Reading from: {dicom_dir}")

        sitk_img = load_dicom_series(dicom_dir)
        print(f"✅ Volume size: {sitk_img.GetSize()}, spacing: {sitk_img.GetSpacing()}")

        vtk_img = sitk_to_vtk(sitk_img)
        print("✅ Converted to VTK format")

        visualize_3d_volume(vtk_img)
        print("✅ Viewer closed")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
