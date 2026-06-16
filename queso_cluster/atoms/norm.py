import numpy as np
import dask.array as da
import numba as nb

def normFunc(dataSquare, func):
	"""
	Normalizes the data with a user-defined function

	Parameters
	----------
	dataSquare : ndarray
		2D array containing the spectral data
	func : function
		user function which accepts an array and outputs an array of the same shape

	Returns
	--------
	ndarray
		2D array of normalized spectral data

	"""
   
	return(func(dataSquare))

def normZ(dataSquare):
	"""
	Z-Normalization

	TODO
	-----
	I have to write this function.

	Parameters
	----------

	dataSquare : ndarray
		2D array containing the spectral data
	
	Returns
	-------
	ndarray
		2D array of normalized spectral data

	"""
	print("TBD")
	return(dataSquare)

def normMaximum(dataSquare, windowIndx=None):
	"""
	Normalizes the data to the maximum value in a given range

	Parameters
	----------

	dataSquare : ndarray
		2D array containing the spectral data
	windowIndx : list, optional
		List containing the beginning and end (inclusive) of the desired range to find maximum. 
		If not set, this function will use the full avaliable range of the data
	
	Returns
	-------
	ndarray
		2D array of normalized spectral data

	"""
	if windowIndx is None:
		windowIndx = [0, dataSquare.shape[1]]

	ii, jj = windowIndx
	#norm_func = lambda x: x/np.nanmax(x[: ii:jj+1], axis=1)[:,None]
	#normSquare = da.blockwise(norm_func, 'ij', dataSquare, 'ij', dtype=np.float32)
	
	dataMin = np.nanmin(dataSquare[:, ii:jj+1], axis=1) - 0.001

	normSquare = (dataSquare - dataMin[:, None])
	dataMax = np.nanmax(normSquare[:, ii:jj+1], axis=1)
	normSquare /= dataMax[:, None]

	return(normSquare)

def normContinuum(dataSquare, continuumIndx):
	"""
	Normalizes the data to the intensity of a reference position

	Parameters
	----------

	dataSquare : ndarray
		2D array containing the spectral data
	continuumIndx : int
		Integer index of the position to normalize with respect to
	
	Returns
	-------
	ndarray
		2D array of normalized spectral data

	"""
	norm_func = lambda x: x/(x[:, int(continuumIndx)])[:,None]
	normSquare = da.blockwise(norm_func, 'ij', dataSquare, 'ij', dtype=np.float32)
	return(normSquare)