import numpy as np
#import dask.array as da
import numba as nb

from . import base as baseAtom

from ..addon import logg


def inertiaScore(dataSquare, labelLine, distortion=False):
	"""
	Calculates the inertia (or distortion) of a given dataset

	Parameters
	----------
	dataSquare : ndarray
		2D array of datapoints
	labelLine : ndarray
		1D array of labels
	distortion : boolean, optional
		Decides whether to calculate inertia or distortion

	Returns
	-------
	float
		The score
	"""


	labelLst = np.unique(labelLine)
	decisions = np.zeros((labelLst.size, dataSquare.shape[-1]), dtype=dataSquare.dtype)

	for l in range(labelLst.size):
		lindx = np.where(labelLine == labelLst[l])[0]
		decisions[l, :] = dataSquare[lindx, :].sum(axis=0)/lindx.size

	_, D_x = baseAtom.minimize(dataSquare, decisions, labelLst.size)
	if distortion:
		score = D_x.sum()
	else:
		score = (D_x**2).sum()

	return(score)

# @nb.njit(cache=True)
# def distanceArray(point, dataSquare):

# 	dist = np.zeros(dataSquare.shape[0]) + np.inf
# 	for i in range(dataSquare.shape[0]):
# 		if point == i:
# 			continue
# 		delta = dataSquare[point, :] - dataSquare[i, :]
# 		dist[i] = np.sqrt(delta.dot(delta))
	
# 	return(dist)
	

# @nb.njit(cache=True)
# def intraMapping(dataSquare):

# 	labelLine = np.arange(dataSquare.shape[0])
# 	nxtLabelLine = np.zeros(labelLine.shape)
# 	i = 0
# 	killer = 0
# 	while True:
# 		converge = np.unique(nxtLabelLine).size
# 		labelLst = np.unique(labelLine)
# 		lindx = np.where(labelLine == labelLst[i])[0]
# 		pindx = np.where(labelLine != labelLst[i])[0]

# 		for j in range(lindx.size):
# 			nDist = distanceArray(lindx[j], dataSquare)
# 			if lindx.size < 5:
# 				nxtLabelLine[np.argmin(nDist)] = i
# 			# else:
# 			# 	test = nDist[lindx]
# 			# 	test = np.mean(test[np.isfinite(test)])
# 			# 	for p in range(pindx.size):
# 			# 		if test < nDist[pindx[p]]:
# 			# 			nxtLabelLine[pindx[p]] = i
# 		i += 1

# 		if converge == np.unique(nxtLabelLine).size:
# 			killer += 1
# 			if killer > 10:
# 				return(nxtLabelLine)
# 		else:
# 			killer = 0
		
@nb.njit(cache=True)
def speedTest2(intraSamples, intraIndxSize, i):
	intra_d2 = 0.0
	for j in range(intraIndxSize):
		if j == i:
			continue
		d = intraSamples[j, :] - intraSamples[i, :]
		intra_d2 += np.sqrt(d.dot(d))	
	return(intra_d2/(intraIndxSize-1))	


@nb.njit(cache=True)
def speedTest(interSamples, intraSample, interIndxSize):
	inter_d2 = 0.0
	for k in range(interIndxSize):
		d = interSamples[k, :] - intraSample
		inter_d2 += np.sqrt(d.dot(d))
	return(inter_d2/interIndxSize)


@nb.njit(cache=True)
def findSampleNeighbor(dataSquare, labelLine, pointIndx):
	"""
	Calculates the nearest label to a given sample

	Parameters
	----------
	dataSquare : ndarray
		2D array (nsamples, nfeatures) containing the pool of data
	labelLine : ndarray
		1D array (nsamples,) for the labels on the data
	pointIndx : int
		sample index

	Returns
	-------
	int
		The label of the nearest cluster to that point

	"""
	store = np.zeros((dataSquare.shape[0])) + np.inf
	interIndx = np.where(labelLine != labelLine[pointIndx])[0]
	for l in range(interIndx.size):
		delta = dataSquare[pointIndx, :] - dataSquare[interIndx[l], :]
		store[interIndx[l]] = np.sqrt(delta.dot(delta))

	neighborLabel = labelLine[np.argmin(store)]

	return(neighborLabel)

@nb.njit(cache=True)
def calcNeighborSilhouetteScore(dataSquare, labelLine, point):
	"""
	Calculates the Silhouette Score for a specific cluster

	Parameters
	-----------
	dataSquare : ndarray
		2D array (nsamples, nfeatures) containing the pool of data
	labelLine : ndarray
		1D array (nsamples,) for the labels on the data
	point : int
		cluster label to evaluate

	Returns
	-------
	int
		Silhouette Score


	"""

	intraIndxs = np.where(labelLine == point)[0]
	score = np.zeros(intraIndxs.size)
	for i in range(intraIndxs.size):
		neighbor = findSampleNeighbor(dataSquare, labelLine, intraIndxs[i])

		interIndxs = np.where(labelLine == neighbor)[0]
		intraSamples = dataSquare[intraIndxs, :]
		interSamples = dataSquare[interIndxs, :]
	
		intraDistance = speedTest2(intraSamples, intraIndxs.size, i)
		interDistance = speedTest(interSamples, intraSamples[i, :], interIndxs.size)

		#if unbound:
		#score[i] = 1 - intraDistance/interDistance
		#else:
		score[i] = (interDistance - intraDistance)/np.maximum(intraDistance, interDistance)

	return(np.mean(score))





@nb.njit()
def calcDaviesBouldin(data, labels):

	labelLst = np.unique(labels)
	Ri = np.zeros(labelLst.size) 
	for i in range(labelLst.size):
		intraIndx = np.where(labels == labelLst[i])[0]
		
		intraCentroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
		si = 0.0
		for k in range(len(intraIndx)):
			d = data[intraIndx[k], :] - intraCentroid
			si += np.sqrt(d.dot(d))	
		si /= intraIndx.size

		Rij = np.zeros(labelLst.size) + np.nan
		for j in range(labelLst.size):
			if i == j:
				continue

			interIndx = np.where(labels == labelLst[j])[0]
			interCentroid = data[interIndx, :].sum(axis=0)/interIndx.size
			sj = 0.0
			for k in range(len(interIndx)):
				d = data[interIndx[k], :] - interCentroid
				sj += np.sqrt(d.dot(d))
			
			sj /= interIndx.size

			dij = intraCentroid - interCentroid
			dij = np.sqrt(dij.dot(dij))

			Rij[j] = (si + sj) / dij

		Ri[i] = np.nanmax(Rij)

	return(Ri.sum()/labelLst.size)



# @nb.njit()
# def calcCHindex(data, labels):
# 	#> detail: 
# 	#> param type data:
# 	#> param type labels:
# 	#> return (type): 
# 	#> test-method:
# 	N = data.shape[0]
# 	K = len(np.unique(labels))

# 	labelLst = np.unique(labels)
# 	if len(labelLst) == 1:
# 		return(np.nan)
	
# 	wgss = np.zeros(len(labelLst)) #+ np.nan
# 	bgss = np.zeros(len(labelLst))# np.nan
# 	for k in range(len(labelLst)):
# 		intraIndx = np.where(labels == labelLst[k])[0]
# 		interIndx = np.where(labels != labelLst[k])[0]

# 		intra_centroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
# 		intra_d2 = 0.0
# 		for i in range(len(intraIndx)):
# 			d = data[intraIndx[i], :] - intra_centroid
# 			intra_d2 += d.dot(d)

# 		inter_centroid = (data[interIndx, :].sum(axis=0) + data[intraIndx, :].sum(axis=0))/(len(intraIndx) + len(interIndx))
# 		# print(inter_centroid)
# 		d = inter_centroid - intra_centroid
# 		bgss[k] = nb.float32(len(intraIndx) * d.dot(d))
# 		wgss[k] = nb.float32(intra_d2)#/len(intraIndx)

# 	return((bgss.sum()/wgss.sum()) * (N - K)/(K - 1))