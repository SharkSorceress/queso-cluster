"""
	:file:  queso_cluster/atoms/flare.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>
"""


import numpy as np

def kernelClusterMask(optLabels, kernel=None):
	"""
	Creates a NaN mask of the kernel cluster
	
	Parameters
	----------
	optLabels : ndarray
		3d array containing the labels in space and time
	kernel : int, list, array, optional
		Cluster label(s) for the kernel cluster(s)
	
	Returns
	-------
	ndarray
		NaN mask which changes all pixels that are not the kernelCluster to NaN 
	"""
	
	if kernel is None:
		kernel = str(int(np.nanmax(optLabels)))
		kernel = float(kernel[0] + '1'*(len(kernel)-1))
	
	kernel = np.asarray(kernel)

	hiIntMask = np.zeros(optLabels.shape[1:])
	for t in range(optLabels.shape[0]):
		for k in range(kernel.size):
			hiIntMask = np.logical_or(hiIntMask, optLabels[t, ...] == kernel)

	hiIntMask = hiIntMask.astype(float)
	hiIntMask[hiIntMask == 0] = np.nan
	hiIntMask = np.broadcast_to(hiIntMask, optLabels.shape)
	return(hiIntMask)
