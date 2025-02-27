import numpy as np

from .cs import ColorCoordinates, HdrLinear, SrgbLinear, convert


def save_rgb_gamut(filename: str, colorspace, variant: str = "srgb", n: int = 50):
    import meshio
    import meshzoo

    if variant.lower() in ["srgb", "rec709"]:
        rgb_linear = SrgbLinear()
    else:
        assert variant.lower() in ["hdr", "rec2020", "rec2100"]
        rgb_linear = HdrLinear()

    points, cells = meshzoo.cube_hexa(
        np.linspace(0.0, 1.0, n + 1),
        np.linspace(0.0, 1.0, n + 1),
        np.linspace(0.0, 1.0, n + 1),
    )

    if not colorspace.is_origin_well_defined:
        # cut off [0, 0, 0] to avoid division by 0 in the xyz conversion
        points = points[1:]
        cells = cells[~np.any(cells == 0, axis=1)]
        cells -= 1

    l = ColorCoordinates(points.T, rgb_linear)
    coords = convert(l, colorspace)

    meshio.write_points_cells(
        filename,
        coords.data.T,
        {"hexahedron": cells},
        point_data={"srgb": coords.get_rgb1(mode="clip").T},
    )


def plot_rgb_gamut(colorspace, n: int = 51, show_grid: bool = True):
    import meshzoo
    import pyvista as pv
    import vtk

    points, cells = meshzoo.cube_hexa(
        np.linspace(0.0, 1.0, n + 1),
        np.linspace(0.0, 1.0, n + 1),
        np.linspace(0.0, 1.0, n + 1),
    )
    cells = np.column_stack([np.full(cells.shape[0], cells.shape[1]), cells])

    cs_coords = ColorCoordinates(points.T, SrgbLinear()).convert(colorspace)

    # each cell is a VTK_HEXAHEDRON
    celltypes = np.full(len(cells), vtk.VTK_HEXAHEDRON, dtype=np.uint8)

    grid = pv.UnstructuredGrid(cells.ravel(), celltypes, cs_coords.data)
    # grid = grid.slice_orthogonal()
    # grid.slice_along_axis(n=7, axis="z")
    # single_slice = mesh.slice(normal=[0, 0, 1])

    p = pv.Plotter()
    p.add_mesh(
        grid,
        scalars=cs_coords.get_rgb1("clip"),
        rgb=True,
        # show_edges=True,
    )
    if show_grid:
        p.show_grid(
            xlabel=colorspace.labels[0],
            ylabel=colorspace.labels[1],
            zlabel=colorspace.labels[2],
        )
    # camera_location = (0.5, 2.0, -2.0)
    # focus_point = (0.5, 0.0, 0.0)
    # viewup_vector = [0.0, 0.0, 0.0]
    # viewup_vector[colorspace.k0] = 1.0

    return p


def plot_rgb_slice(
    colorspace,
    lightness: float,
    camera_elevation: float,
    n: int = 50,
    variant: str = "srgb",
    off_screen: bool = False,
):
    import meshzoo
    import pyvista as pv
    import vtk

    # TODO HDR
    assert variant in ["srgb", "rec709"]

    points, cells = meshzoo.cube_hexa(
        np.linspace(0.0, 1.0, n + 1),
        np.linspace(0.0, 1.0, n + 1),
        np.linspace(0.0, 1.0, n + 1),
    )
    cells = np.column_stack([np.full(cells.shape[0], cells.shape[1]), cells])

    srgb_coords = ColorCoordinates(points.T, SrgbLinear())
    cs_coords = srgb_coords.convert(colorspace)

    # each cell is a VTK_HEXAHEDRON
    celltypes = np.full(len(cells), vtk.VTK_HEXAHEDRON, dtype=np.uint8)

    # https://github.com/pyvista/pyvista-support/issues/351#issuecomment-814574043
    grid = pv.UnstructuredGrid(cells.ravel(), celltypes, cs_coords.data.T)
    grid["rgb"] = cs_coords.get_rgb1("clip").T

    slc = grid.slice([1.0, 0.0, 0.0], [lightness, 0.0, 0.0])
    # slc = grid.slice_along_axis(10, 0)
    # slc = grid.slice_orthogonal()

    p = pv.Plotter(off_screen=off_screen)

    p.show_bounds(
        xlabel=colorspace.labels[0],
        ylabel=colorspace.labels[1],
        zlabel=colorspace.labels[2],
    )
    p.add_mesh(slc, scalars="rgb", rgb=True, lighting=False)

    # More camera tools:
    # https://github.com/pyvista/pyvista-support/issues/412
    p.camera.position = (camera_elevation, 0.0, 0.0)
    p.camera.focal_point = (lightness, 0.0, 0.0)
    # p.camera.zoom(zoom)
    # https://github.com/pyvista/pyvista-support/issues/490:
    p.reset_camera_clipping_range()
    # p.camera.Roll(-90.0)
    return p
