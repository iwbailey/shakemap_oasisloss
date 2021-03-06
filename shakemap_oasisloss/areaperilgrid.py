import numpy as np
import numpy.ma as ma

# -----------------------------------------------------------------------------


class AreaPerilGrid:
    """Defines a grid with which to assign geographic coordinates. Points assigned
    to grid cells with left and bottom edges closed, i.e. x_i <= x < x_i+1

    Indexing is row-order based

    Properties...
    x0: leftmost edge of the grid
    x1: rightmost edge of the grid
    y0: bottommost edge of the grid
    y1: topmost edge of the grid
    nx: number of grid cells in x-axis direction
    ny: number of grid cells in y-axis direction

    """
    def __init__(self, xlims=(-180.0, 180.0), nx=360, ylims=(-80, 80), ny=160):
        """Constructor takes
        xlims (float, tuple): extent in x direction
        nx (int): number of grid cells in x
        ylims (float, typle): extent in y direction, number of x dimensions
        ny (int): number of grid cells in y
        """
        self.x0 = xlims[0]  # leftmost edge of the grid
        self.x1 = xlims[1]  # rightmost edge of the grid
        self.y0 = ylims[0]
        self.y1 = ylims[1]
        self.nx = nx  # number of grid cells in x direction
        self.ny = ny

        return

    def assign_xcoords(self, xpts):
        """Assign coordinates on the x axis to a grid index. The first grid index is
        0. Returns a list of indices as a masked array.

        """
        ix = np.floor(self.nx*(xpts - self.x0)/(self.x1 - self.x0))

        return ma.masked_outside(ix.astype(int), 0, self.nx-1)

    def assign_ycoords(self, ypts):
        """Assign coordinates on the y-axis to a grid index. The first grid index is
        0. Returns a list of indices as a numpy masked array, defining whether
        the points are inside the grid.

        """
        iy = np.floor(self.ny*(ypts - self.y0)/(self.y1 - self.y0))

        return ma.masked_outside(iy.astype(int), 0, self.ny-1)

    def assign_gridid(self, xpts, ypts):
        """Assign a set of x and y coordinates their grid ids
        IN:
        xpts: numpy array of x coordinates
        ypts: numpy array of y coordinates

        OUT:
        idx: numpy masked array of integer ids, True if within grid bounds
        """

        # Get the x and y coordinates
        ix = self.assign_xcoords(xpts)
        iy = self.assign_ycoords(ypts)

        # Row order
        idx = ma.masked_array(iy*self.nx + ix)

        return idx

    def assign_xytoid(self, xpts, ypts):
        """Return an areaperil_id for combinations of x and y"""
        return self.assign_gridid(xpts, ypts)

    def idtoxy(self, idlist):
        """Return a set of ids, given the list of xy"""

        # TODO: check input is an array
        # TODO: check all ids are within bounds 0 - (nx*ny)

        # Row ordered so id = ix + iy*nx
        ix = np.mod(idlist, self.nx)
        iy = np.floor(idlist/self.nx)

        # Convert to coordinates
        xpts = self.x0 + (self.x1 - self.x0)*(ix+0.5)/self.nx
        ypts = self.y0 + (self.y1 - self.y0)*(iy+0.5)/self.ny

        return xpts, ypts
