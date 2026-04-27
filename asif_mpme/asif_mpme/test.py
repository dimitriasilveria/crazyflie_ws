import numpy as np

def xyz_to_xy(xyz: np.ndarray) -> np.ndarray:
    """
    Convert (N,3) xyz positions to (N,2) xy positions.

    Parameters
    ----------
    xyz : np.ndarray
        Array of shape (N, 3)

    Returns
    -------
    np.ndarray
        Array of shape (N, 2)
    """
    assert xyz.ndim == 2 and xyz.shape[1] == 3, \
        "Input must have shape (N,3)"

    return xyz[:, :2]

def xy_to_xyz(xy: np.ndarray, z: float = 10.0) -> np.ndarray:
    """
    Convert (N,2) xy positions to (N,3) xyz positions by adding a constant z.

    Parameters
    ----------
    xy : np.ndarray
        Array of shape (N, 2)
    z : float
        Constant z-value to append

    Returns
    -------
    np.ndarray
        Array of shape (N, 3)
    """
    assert xy.ndim == 2 and xy.shape[1] == 2, \
        "Input must have shape (N,2)"

    z_column = np.full((xy.shape[0], 1), z)
    return np.hstack((xy, z_column))


if __name__ == '__main__':

    xyz = np.random.rand(4,3)
    print(xyz)

    xy = xyz_to_xy(xyz)
    print(xy)

    xyz = xy_to_xyz(xy, 20.757565756)
    print(xyz)

    print([i for i in range(3,6)])