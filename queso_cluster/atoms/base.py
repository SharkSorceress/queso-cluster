"""
	:file: queso_cluster/atoms/base.py
	:lang:  python
	:synopsis:
	:author: Sarah Riley <academic@sriley.dev>
"""
import numpy as np
import dask.array as da
import numba as nb

from . import error as errAtom

def concatSpectra(dataSquareLst):
	"""
	Function to concatenate several channels of data into one array for clustering

	Parameters
	----------
	dataSquareLst : dask.array
		dask arrays containing spectral data to be concatenated
	
	Returns
	-------
	dask.array
		Concatenated spectral profiles
	
	TODO
	----
	This feature needs to be properly tested

	"""
	return(da.concatenate(dataSquareLst))	

@nb.njit()
def numba_histogram(a, bins, lim):
	"""
	Numba accelerated histogram function

	Parameters
	----------
	a : int
		detail
	bins : int
		the number of bins in the histogram
	lim : ndarray
		the top and bottom of the histogram		
	
	Returns
	-------
	hist : ndarray
		the histogram
	bin_edges : ndarray
		1D array of the bin edges

	"""
	hist = np.zeros((bins,), dtype=np.intp)
	bin_edges = get_bin_edges(bins, lim)

	for x in a.flat:
		bin = compute_bin(x, bin_edges)
		if bin is not None:
			hist[int(bin)] += 1

	return hist, bin_edges

def rotateArray(image, turns):
	"""
	Rotates an array

	Parameters
	----------
	image : ndarray
		2D array to be rotated
	turns : int
		Number of pi/2 turns to rotate
	
	Returns
	-------
	ndarray
		Rotated array
	
	"""
	
	for i in range(turns):
		image = np.array(list(zip(*image[::-1])))

	return(image[::-1])

@nb.njit(cache=True)
def get_bin_edges(bins, lim):
	#> detail: 
	#> param type bins:
	#> param type lim:
	#> return (type): 
	#> test-method:
	bin_edges = np.zeros((bins+1,), dtype=np.float64)
	a_min = lim.min()
	a_max = lim.max()
	delta = (a_max - a_min) / bins
	for i in range(bin_edges.shape[0]):
		bin_edges[i] = a_min + i * delta

	bin_edges[-1] = a_max  # Avoid roundoff error on last point
	return bin_edges


@nb.njit()
def compute_bin(x, bin_edges):
	#> detail: 
	#> param type x:
	#> param type bin_edges:
	#> return (type): 
	#> test-method:
	# assuming uniform bins for now
	n = bin_edges.shape[0] - 1
	a_min = bin_edges[0]
	a_max = bin_edges[-1]

	# special case to mirror NumPy behavior for last bin
	if x == a_max:
		return n - 1 # a_max always in last bin

	bin = int(n * (x - a_min) / (a_max - a_min))

	if bin < 0 or bin >= n:
		return None
	else:
		return bin

@nb.njit
def np_gradient(f):
	"""
	Numba accelerated gradient

	Paramters
	---------
	f : ndarray
		1D array to take the gradient of
	
	Returns
	-------
	ndarray
		Gradient of f
	"""

	out = np.empty_like(f, np.float64)
	out[1:-1] = (f[2:] - f[:-2]) / 2.0
	out[0] = f[1] - f[0]
	out[-1] = f[-1] - f[-2]
	return(out)

@nb.njit(cache=True)
def minimize(data, decisions, size):
	"""
	
	"""

	data_label      = np.zeros(data.shape[0], dtype=np.int32)
	D_x             = np.zeros(data.shape[0], dtype=data.dtype)
	sq_dist         = np.zeros(size, dtype=data.dtype)
	for ii in range(data.shape[0]):
		for kk in range(size):
			sq_dist[kk] 	= similarityMetric(data[ii,:], decisions[kk, :])
		data_label[ii]  = sq_dist.argmin()
		D_x[ii]         = sq_dist[nb.u4(data_label[ii])]
	return(data_label, D_x)

@nb.njit(cache=True)
def maximize(data, decisions, size):
	#> detail: 
	#> param type data:
	#> param type decisions:
	#> param type size:
	#> return (type): 
	#> test-method:
	data_label      = np.zeros(data.shape[0])
	D_x             = np.zeros(data.shape[0])
	sq_dist         = np.zeros(size)
	for ii in range(data.shape[0]):
		for kk in range(size):
			# diff            = data[ii,:] - decisions[kk, :]
			# sq_dist[kk]     = np.sqrt(diff.dot(diff))
			sq_dist[kk] 	= similarityMetric(data[ii,:], decisions[kk, :])
		data_label[ii]  = sq_dist.argmax()
		D_x[ii]         = sq_dist[nb.u4(data_label[ii])]
	return(data_label, D_x)

@nb.njit(cache=True)
def np_all_axis0(x):
	#> detail: Numba compatible version of np.all(x, axis=0)
	#> param type x:
	#> return (type): 
	#> test-method:
	out = np.ones(x.shape[1], dtype=np.bool8)
	for i in range(x.shape[0]):
		out = np.logical_and(out, x[i, :])
	return out

@nb.njit(cache=True)
def np_all_axis1(x):
	#> detail: Numba compatible version of np.all(x, axis=1)
	#> param type x:
	#> return (type): 
	#> test-method:
	out = np.ones(x.shape[0], dtype=np.bool8)
	for i in range(x.shape[1]):
		out = np.logical_and(out, x[:, i])
	return out

@nb.njit()
def similarityMetric(x, y, type='dist', ref=0):
	#> detail: 
	#> param type x:
	#> param type y:
	#> param type ['dist'] type:
	#> param type [0] ref:
	#> return (type): 
	#> test-method:
	if type  == 'dist':
		delta = (x - y).astype(x.dtype)
		metric = np.sqrt(delta.dot(delta))
	elif type == 'cosine':
		ref = 1.0 - 0.5 * np.exp(-11*np.arange(-int(len(x)/2), int(len(x)/2), step=1)**2)
		x -= ref
		y -= ref
		similarityCoeff = (x).dot(y) / (np.sqrt(x.dot(x)) * np.sqrt(y.dot(y)))	
		metric = 1 - similarityCoeff
	return(metric)

@nb.njit(cache=True)
def curvature(y):
	#> detail: 
	#> param type y:
	#> return (type): 
	#> test-method:
	grady = np_gradient(y)
	signedCurvature = np_gradient(grady)/(np.power(np.sqrt(1 + grady.dot(grady)), 3))
	return(np.sqrt(np.power(signedCurvature, 2)))
#	return(np.abs(np.gradient(np.gradient(y)))/(np.sqrt(1 + np.gradient(y)**2)**3))

@nb.njit()
def startMax(data, k, decisions):
	"""
	Heuristic k-means++. 
	Rather than selecting from a distribution around the furtherest datapoint, this initialization simply selects the furtherest datapoint as the next representative

	Parameters
	----------
	data : ndarray
		data pool for finding the initial representative profiles
	k : int
		The number of clusters
	decisions : ndarray
		Array containing the initial, randomly selected representative profile and empty slots for remaining profiles
	
	Returns
	-------
	decisions : ndarray
		Array containing a full set of representative profiles

	"""
	killer = np.ones(decisions.shape[1], dtype=decisions.dtype)
	while True:
		dc_left = np.flatnonzero(1-np_all_axis1(decisions))
		if len(dc_left) == 0:
			return(decisions)
		_, D_x = minimize(data, decisions, k-len(dc_left))        
	
		if (killer - data[nb.u4(D_x.argmax()), :]).sum() == 0:
			return(decisions)
		
		decisions[dc_left[0], :]    = data[nb.u4(D_x.argmax()), :]
		killer = data[nb.u4(D_x.argmax()), :]

@nb.njit(cache=True)
def startPlusPlus(data, k, decisions):
	"""
	k-means++ initialization

	Parameters
	----------
	data : ndarray
		data pool for finding the initial representative profiles
	k : int
		The number of clusters
	decisions : ndarray
		Array containing the initial, randomly selected representative profile and empty slots for remaining profiles
	
	Returns
	-------
	decisions : ndarray
		Array containing a full set of representative profiles

	"""
	#> detail: 
	#> param type data:
	#> param type k:
	#> param type decisions:
	#> return (type): 
	#> test-method:
	killer = np.ones(decisions.shape[1], dtype=decisions.dtype)
	while True:
		dc_left = np.flatnonzero(1-np_all_axis1(decisions))
		if len(dc_left) == 0:
			return(decisions)
		_, D_x = minimize(data, decisions, k-len(dc_left))     
		probs = D_x/D_x.sum()
		r = np.random.rand()
		for j, p in enumerate(probs.cumsum()):
			if r < p:
				i = j
				break
		if (killer - data[nb.u4(i), :]).sum() == 0:
			return(decisions)

		decisions[dc_left[0], :]    = data[nb.u4(i), :]
		killer = data[nb.u4(i), :]


@nb.njit(cache=True)
def _calcMoment(waveAxis, ii, jj, lineCore, dataCube, order, ref, counter=0):    
	#> detail: 
	#> param type waveAxis:
	#> param type ii:
	#> param type jj:
	#> param type lineCore:
	#> param type dataCube:
	#> param type order:
	#> param type ref:
	#> param type [0] counter:
	#> return (type): 
	#> test-method:
	momentN = np.zeros((order+1, dataCube.shape[0]))
	while counter <= order:
		factor = np.power((waveAxis[ii:jj] - waveAxis[lineCore]), counter)
		for i in range(dataCube.shape[0]):
			momentN[counter, i] = ((dataCube[i, ii:jj] - ref[ii:jj])*factor).sum()
		if counter > 0:
			momentN[counter, :] /= momentN[0, :]
		counter += 1
	
	return(momentN)

# @nb.njit()
# def _calcFeatureDensity(data, converge, zindx, func1):
# 	#> detail: 
# 	#> param type data:
# 	#> param type converge:
# 	#> param type zindx:
# 	#> param type func1:
# 	#> return (type): 
# 	#> test-method:
# 	featureDensityArr = np.zeros(50)
# 	for a in range(featureDensityArr.shape[0]):
# 		scores1 = np.zeros(len(zindx))
# 		for i in range(int(scores1.shape[0]/100)):
# 			print((a, i, i*100/(len(zindx)/100)))
# 			labels = _runOptimization(i+1, data[zindx, :], converge)
# 			scores1_tmp = func1(data[zindx, :], labels)
# 			scores1[i] = scores1_tmp
# 		featureDensityArr[a] = np.min(np.where(scores1 == np.nanmax(scores1))[0]) + 1
# 	featureDensity = np.median(featureDensityArr)/len(zindx)
# 	return(featureDensity)


@nb.njit()
def calcOptimization(k, data, decision, threshold=1e-6):
	"""
	Calculates the set of k decisions with a convergence threshold

	Parameters
	----------
	k : int
		The number of groups
	data : ndarray
		The data to be clustered
	decision : ndarray
		The previous iteration's decisions
	threshold : float, optional
		The convergence threshold

	Raises
	------
	ConvergenceError
		If the convergence criteria cannot be evaulated or if the convergence criterion is not met after :obj:`~queso_cluster.atoms.error.covergeLimit`
	
	Returns
	-------
	decision : ndarray
		The current iteration's representative profiles
	data_label : ndarray
		The labels for the data
	
	"""
	killCounter = 0
	while True:
		data_label, _ = minimize(data, decision, k)
		new_centroid = np.zeros((k, data.shape[1]), dtype=data.dtype)
		converge = 0
		for kk in range(k):
			sub_data = data[np.where(data_label == kk)[0], :]
			new_centroid[kk,:]  = sub_data.sum(axis=0)/sub_data.shape[0]
			# new_centroid[kk,:]  = np.median(sub_data, axis=0)

			diff_centroid   = new_centroid[kk,:] - decision[kk,:]
			converge        = np.max(np.asarray([converge, 
												np.sqrt(diff_centroid.dot(diff_centroid))]))
		
			if not np.isfinite(converge):
				raise errAtom.ConvergenceError(f"Converge criteria cannot be evaluated. Convergence is not finite")
		
		if killCounter == errAtom.convergeLimit:
			raise errAtom.ConvergenceError(f"Convergence condition not met after {killCounter} steps")
		
		decision = new_centroid
		if converge <= threshold:
			return(decision, data_label) 

		killCounter += 1



def labelGluer(labels):
	#> detail: 
	#> param type labels:
	#> return (type): 
	#> test-method:
	time_label_concat = np.char.asarray(np.zeros(labels[0].shape[1], dtype=int))
	for i in range(len(labels)):
		for l in range(labels[i].shape[0]):
			time_label_concat = np.char.add(time_label_concat, np.char.asarray(labels[i][l, ...].astype(int)))	

	return(time_label_concat)

def labelReorder(labels):
	#> detail: 
	#> param type labels:
	#> return (type): 
	#> test-method:
	time_label = []
	for i in range(len(labels)):
		time_label_wave = labelGluer([labels[i]])
		time_label_lst 	= np.unique(time_label_wave)
		time_label_bool = [element.decode("utf-8").find("-") < 0 for element in time_label_lst]

		for j in range(len(time_label_lst)):
			if time_label_bool[j]:
				newLabel = int('9' * int(np.ceil(np.log10(len(time_label_lst))) + 1)) - j
				while newLabel in np.unique(time_label_lst):
					if not (newLabel % 10):
						newLabel -= 1
				time_label_wave[np.where(time_label_wave == time_label_lst[j])[0]] = newLabel
			else:
				time_label_wave[np.where(time_label_wave == time_label_lst[j])[0]] = -1
		time_label.append(time_label_wave)

	time_label_concat = np.char.asarray(np.zeros(labels[0].shape[1], dtype=int))
	for i in range(len(labels)):
		time_label_concat = np.char.add(time_label_concat, np.char.asarray(time_label[i]))	

	return(time_label_concat)

@nb.njit()
def _calcQuiescentFrame(spectralData, spectralParams, contIndxs, progress=None):
	#> detail: 
	#> param type spectralData:
	#> param type spectralParams:
	#> param type contIndxs:
	#> param type [None] progress:
	#> return (type): 
	#> test-method:
	lineCore, ii, jj = spectralParams
	quiescentFrame 	= np.zeros(spectralData.shape[1:])
	for x in range(spectralData.shape[1]):
		for y in range(spectralData.shape[2]):
			quiescentScanNum = np.zeros(spectralData.shape[0])
			for t in range(spectralData.shape[0]):
				quiescentScanNum[t] = spectralData[t, x, y, lineCore]/np.nanmax(spectralData[t, x, y, :])#).sum(axis=-1)
			qindx = np.argsort(quiescentScanNum)[len(quiescentScanNum)//4]#np.where(quiescentScanNum == np.median(quiescentScanNum))#
			quiescentFrame[x, y, :] = spectralData[qindx, x, y, :]
			if progress != None:
				progress.update(1)
	return(quiescentFrame.reshape(spectralData.shape[1]*spectralData.shape[2], spectralData.shape[-1]))

@nb.njit()
def _calcDynamicFrame(spectralData, dynamicScanNum, progress=None, delta=0):
	#> detail: 
	#> param type spectralData:
	#> param type dynamicScanNum:
	#> param type [None] progress:
	#> param type [0] delta:
	#> return (type): 
	#> test-method:
	dynamicFrame 	= np.zeros(spectralData.shape[1:]) + np.nan
	for x in range(spectralData.shape[1]):
		for y in range(spectralData.shape[2]):
			T = nb.uint(dynamicScanNum[x, y] + delta)
			if (T < spectralData.shape[0]) and (T >= 0):
				dynamicFrame[x, y, :] = spectralData[T, x, y, :]
				if progress != None:
					progress.update(1)
	return(dynamicFrame)