import vtk
import os

def create_medical_visualization():
    # --- 1. LOAD THE DATASET ---
    file_path = r"D:\3D_reconstruction_of_2D_ct_scan\Sample_DICOM"
    
    if not os.path.exists(file_path):
        print(f"Error: Directory not found at '{file_path}'")
        print("Please check your path and make sure the directory exists.")
        return

    reader = vtk.vtkDICOMImageReader()
    reader.SetDirectoryName(file_path)
    reader.Update()
    data = reader.GetOutput()
    bounds = data.GetBounds()

    # --- 2. DEFINE THE COLOR AND OPACITY TRANSFER FUNCTIONS ---
    opacity_transfer_function = vtk.vtkPiecewiseFunction()
    opacity_transfer_function.AddPoint(0, 0.0)
    opacity_transfer_function.AddPoint(50, 0.0)
    opacity_transfer_function.AddPoint(200, 0.2)
    opacity_transfer_function.AddPoint(1000, 1.0)

    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(0, 0.0, 0.0, 0.0)
    color_transfer_function.AddRGBPoint(50, 0.8, 0.5, 0.2)
    color_transfer_function.AddRGBPoint(200, 0.9, 0.8, 0.7)
    color_transfer_function.AddRGBPoint(1000, 1.0, 1.0, 1.0)

    # --- 3. CREATE THE VOLUME RENDERER PIPELINE ---
    volume_property = vtk.vtkVolumeProperty()
    volume_property.SetColor(color_transfer_function)
    volume_property.SetScalarOpacity(opacity_transfer_function)
    volume_property.SetInterpolationTypeToLinear()
    
    volume_mapper = vtk.vtkGPUVolumeRayCastMapper()
    volume_mapper.SetInputConnection(reader.GetOutputPort())
    
    volume = vtk.vtkVolume()
    volume.SetMapper(volume_mapper)
    volume.SetProperty(volume_property)

    # --- 4. CREATE THE ORTHOGONAL SLICES ---
    axial_matrix = vtk.vtkMatrix4x4()
    axial_matrix.SetElement(0, 0, 1)
    axial_matrix.SetElement(1, 1, 1)
    axial_matrix.SetElement(2, 2, 1)
    axial_matrix.SetElement(0, 3, (bounds[0] + bounds[1]) / 2)
    axial_matrix.SetElement(1, 3, (bounds[2] + bounds[3]) / 2)
    axial_matrix.SetElement(2, 3, (bounds[4] + bounds[5]) / 2)

    axial_slice = vtk.vtkImageReslice()
    axial_slice.SetInputConnection(reader.GetOutputPort())
    axial_slice.SetResliceAxes(axial_matrix)
    axial_slice.SetInterpolationModeToLinear()
    
    axial_actor = vtk.vtkImageActor()
    axial_actor.SetInputData(axial_slice.GetOutput())

    coronal_matrix = vtk.vtkMatrix4x4()
    coronal_matrix.SetElement(0, 0, 1)
    coronal_matrix.SetElement(1, 2, 1)
    coronal_matrix.SetElement(2, 1, 1)
    coronal_matrix.SetElement(0, 3, (bounds[0] + bounds[1]) / 2)
    coronal_matrix.SetElement(1, 3, (bounds[2] + bounds[3]) / 2)
    coronal_matrix.SetElement(2, 3, (bounds[4] + bounds[5]) / 2)

    coronal_slice = vtk.vtkImageReslice()
    coronal_slice.SetInputConnection(reader.GetOutputPort())
    coronal_slice.SetResliceAxes(coronal_matrix)
    coronal_slice.SetInterpolationModeToLinear()
    
    coronal_actor = vtk.vtkImageActor()
    coronal_actor.SetInputData(coronal_slice.GetOutput())
    
    sagittal_matrix = vtk.vtkMatrix4x4()
    sagittal_matrix.SetElement(0, 1, 1)
    sagittal_matrix.SetElement(1, 2, 1)
    sagittal_matrix.SetElement(2, 0, 1)
    sagittal_matrix.SetElement(0, 3, (bounds[0] + bounds[1]) / 2)
    sagittal_matrix.SetElement(1, 3, (bounds[2] + bounds[3]) / 2)
    sagittal_matrix.SetElement(2, 3, (bounds[4] + bounds[5]) / 2)
    
    sagittal_slice = vtk.vtkImageReslice()
    sagittal_slice.SetInputConnection(reader.GetOutputPort())
    sagittal_slice.SetResliceAxes(sagittal_matrix)
    sagittal_slice.SetInterpolationModeToLinear()

    sagittal_actor = vtk.vtkImageActor()
    sagittal_actor.SetInputData(sagittal_slice.GetOutput())
    
    # --- 5. SETUP THE RENDER WINDOW AND VIEWPORTS ---
    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(1200, 900)
    
    ren1 = vtk.vtkRenderer()
    ren2 = vtk.vtkRenderer()
    ren3 = vtk.vtkRenderer()
    ren4 = vtk.vtkRenderer()
    
    ren1.SetViewport(0.0, 0.0, 0.5, 1.0)
    ren2.SetViewport(0.5, 0.66, 1.0, 1.0)
    ren3.SetViewport(0.5, 0.33, 1.0, 0.66)
    ren4.SetViewport(0.5, 0.0, 1.0, 0.33)

    ren1.AddVolume(volume)
    ren2.AddActor(axial_actor)
    ren3.AddActor(coronal_actor)
    ren4.AddActor(sagittal_actor)
    
    render_window.AddRenderer(ren1)
    render_window.AddRenderer(ren2)
    render_window.AddRenderer(ren3)
    render_window.AddRenderer(ren4)
    
    camera = ren1.GetActiveCamera()
    camera.SetPosition(400, 300, 500)
    camera.SetFocalPoint(99.5, 126.5, 77.5)
    
    # --- 6. INTERACT AND RENDER ---
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # --- 7. ADD COORDINATE AXES TO THE 3D VIEW ---
    axes = vtk.vtkAxesActor()
    axes.SetShaftTypeToCylinder()
    axes.SetTipTypeToCone()
    axes.SetXAxisLabelText("X")
    axes.SetYAxisLabelText("Y")
    axes.SetZAxisLabelText("Z")
    
    orientation_marker = vtk.vtkOrientationMarkerWidget()
    orientation_marker.SetOutlineColor(0.93, 0.57, 0.13)
    orientation_marker.SetOrientationMarker(axes)
    orientation_marker.SetInteractor(interactor)
    # MODIFIED: Increased the viewport size to make the axes bigger
    orientation_marker.SetViewport(0.0, 0.0, 0.4, 0.4) 
    orientation_marker.SetDefaultRenderer(ren1)
    orientation_marker.EnabledOn()
    orientation_marker.InteractiveOff()
    
    render_window.Render()
    interactor.Initialize()
    interactor.Start()

if __name__ == "__main__":
    create_medical_visualization()