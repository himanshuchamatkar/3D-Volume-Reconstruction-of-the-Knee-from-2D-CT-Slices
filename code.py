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
    print("🔁 Converting SimpleITK image to VTK format...")
    np_array = sitk.GetArrayFromImage(sitk_image)  # shape: (z, y, x)
    print(f"📐 NumPy shape: {np_array.shape}, dtype: {np_array.dtype}")

    np_array = np_array.astype(np.uint16)
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

def visualize_3d_volume(vtk_image):
    print("🎨 Setting up 3D volume renderer...")

    mapper = vtk.vtkSmartVolumeMapper()
    mapper.SetInputData(vtk_image)

    # Opacity function
    opacity = vtk.vtkPiecewiseFunction()
    opacity.AddPoint(0, 0.00)
    opacity.AddPoint(300, 0.05)
    opacity.AddPoint(700, 0.1)
    opacity.AddPoint(1150, 0.25)

    # Color function
    color = vtk.vtkColorTransferFunction()
    color.AddRGBPoint(0, 0.0, 0.0, 0.0)
    color.AddRGBPoint(500, 1.0, 0.5, 0.3)
    color.AddRGBPoint(1000, 1.0, 1.0, 0.9)

    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color)
    volume_property.SetScalarOpacity(opacity)
    volume_property.ShadeOn()
    volume_property.SetInterpolationTypeToLinear()

    volume = vtk.vtkVolume()
    volume.SetMapper(mapper)
    volume.SetProperty(volume_property)

    renderer = vtk.vtkRenderer()
    renderer.AddVolume(volume)
    renderer.SetBackground(0.1, 0.1, 0.2)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(900, 900)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    print("🌀 Launching interactive 3D viewer...")
    interactor.Initialize()
    render_window.Render()
    interactor.Start()

def main():
    try:
        dicom_dir = os.path.join(os.getcwd(), "Sample_DICOM")
        print(f"📂 Reading from: {dicom_dir}")

        sitk_img = load_dicom_series(dicom_dir)
        print(f"✅ Loaded volume: {sitk_img.GetSize()}, spacing: {sitk_img.GetSpacing()}")

        vtk_img = sitk_to_vtk(sitk_img)
        print("✅ Converted to VTK image")

        visualize_3d_volume(vtk_img)
        print("✅ Visualization completed")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
