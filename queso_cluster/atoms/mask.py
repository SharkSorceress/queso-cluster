import numpy as np

def maskCoordinate(bEx, dim):
    print(dim)
    bboxMask = np.zeros(dim)
    if len(dim) == 2:
        bboxMask[bEx[0]:bEx[1], bEx[2]:bEx[3]] = 1
    elif len(dim) == 3:
        bboxMask[:, bEx[0]:bEx[1], bEx[2]:bEx[3]] = 1
    return(bboxMask.reshape(np.prod(bboxMask.shape)).astype(bool))

def maskIntrinsic(keepI0, prepSquare, intrinsicLine, dim, timeSize):
    i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
    for i in keepI0:
        i0Mask[intrinsicLine == i] = 1

    if len(dim) == 3:
        i0MaskXD = i0Mask.reshape(dim)
        i0MaskNew = np.zeros((dim[1], dim[2]))
        for t in range(timeSize):
            i0MaskNew = np.logical_or(i0MaskXD[t, ...], i0MaskNew)
        i0Mask = np.broadcast_to(i0MaskNew, dim).reshape(np.prod(dim))

    return(i0Mask.astype(bool))