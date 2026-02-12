import vtk

def show_cube():
    # --- Create the Cube Pipeline ---
    cube = vtk.vtkCubeSource()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(cube.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # --- Setup the Renderer and Window ---
    renderer = vtk.vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.2, 0.4)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(600, 600)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # --- Add the X, Y, Z Axes ---
    axes = vtk.vtkAxesActor()
    
    orientation_marker = vtk.vtkOrientationMarkerWidget()
    orientation_marker.SetOutlineColor(0.93, 0.57, 0.13)
    orientation_marker.SetOrientationMarker(axes)
    orientation_marker.SetInteractor(interactor)
    orientation_marker.SetViewport(0.0, 0.0, 0.2, 0.2)
    orientation_marker.SetDefaultRenderer(renderer)
    orientation_marker.EnabledOn()
    orientation_marker.InteractiveOff()

    # --- Start the Visualization ---
    render_window.Render()
    interactor.Initialize()
    interactor.Start()

if __name__ == "__main__":
    show_cube()