import numpy as np
#import dask.array as da
import numba as nb

from . import base as baseAtom

def calcResolvingIndex(dataSquare, labelLine):
	labelLst = np.unique(labelLine)
	resolveSquare = np.zeros((len(labelLst), dataSquare.shape[1]))
	for l in range(labelLst.size):
		lindx = np.where(labelLine == labelLst[l])[0]
		resolveSquare[l, :] = calcSingleResolvingIndex(dataSquare[lindx, :])

	return(resolveSquare)		

def calcSingleResolvingIndex(dataSquare):

	centroid_mins, centroid_plus = np.quantile(dataSquare, [0.25, 0.75], axis=0)
	centroid = dataSquare.sum(axis=0)/dataSquare.shape[0]
	# centroid_plus = dataSquare.max(axis=0)
	# centroid_mins = dataSquare.min(axis=0)
	
	plusIndx = np.where(dataSquare > centroid_plus)[0]
	centroid_plus = dataSquare[plusIndx, :].sum()/plusIndx.size

	minsIndx = np.where(dataSquare < centroid_mins)[0]
	centroid_mins = dataSquare[minsIndx, :].sum()/minsIndx.size

	delta_plus = np.abs(centroid_plus - centroid)
	delta_mins = np.abs(centroid_mins - centroid)

	return((delta_plus - delta_mins)/(delta_plus + delta_mins))
	

@nb.njit()
def calcElbowEntry(data, labels):
	#> detail: 
	#> param type data:
	#> param type labels:
	#> return (type): 
	#> test-method:

	labelLst = np.unique(labels)
	localDistance = np.zeros(len(labelLst))
	for j in range(len(labelLst)):
		indx = np.where(labels == labelLst[j])[0]
		centroid = data[indx, :].sum(axis=0)/len(indx)
		d2 = 0.0
		for k in range(len(indx)):
			d = data[indx[k], :] - centroid
			d2 += np.sqrt(d.dot(d))
		#print(d2/len(indx))
		localDistance[j] = d2/len(indx)

	# def _calcScore(scores):
	# 	return(np.argmax(np_gradient(np_gradient(_calcCurvature(scores)))) + 1)

	return(localDistance)#, _calcScore)

@nb.njit()
def calcVarianceScore(data):
	#> detail: 
	#> param type data:
	#> return (type): 
	#> test-method:

	avg_var = np.std(data, axis=0).sum()/data.shape[1]
	centroid = data.sum(axis=0)/data.shape[0]

@nb.njit()
def criteriaInertiaScore(score):
	#> detail: 
	#> param type score:
	#> return (type): 
	#> test-method:
	diff = baseAtom.np_gradient(score)
	for d in range(diff.size):
		if diff[d] < diff[0]*0.8:
			return d		

@nb.njit()
def calcInertiaScore(dataSquare, labelLine):
	#> detail: 
	#> param type dataSquare:
	#> param type labelLine:
	#> return (type): 
	#> test-method:
	labelLst = np.unique(labelLine)
	inertia = 0
	for l in range(labelLst.size):
		lindx = np.where(labelLine == labelLst[l])[0]
		centroid = dataSquare[lindx, :].sum(axis=0)/labelLst.size
		for ll in range(lindx.size):
			delta = dataSquare[lindx[ll], :] - centroid
			inertia += delta.dot(delta)
	return(inertia)	

@nb.njit()
def criteriaSilhouetteScore(score):
	#> detail: 
	#> param type score:
	#> return (type): 
	#> test-method:
	return(score.argmax())


@nb.njit(cache=True)
def calcNeighborSilhouetteScore(dataSquare, labelLine, neighbor=None, unbound=False):
	labelLst = np.unique(labelLine)
	scores = np.zeros(labelLst.size)
	for l in range(labelLst.size):
		#scores[l] = calcNeighborSingleSilhouetteScore(dataSquare, labelLine, 
		#										labelLst[l], unbound)
		intraIndxs = np.where(labelLine == labelLst[l])[0]

		sampleScore = np.zeros(intraIndxs.size)

		for j in range(intraIndxs.size):
			intraIndx = intraIndxs[j]
			neighbor = findSampleNeighbor(dataSquare, labelLine, intraIndx)

			interIndxs = np.where(labelLine == neighbor)[0]
			
			intraSample = dataSquare[intraIndx, :]#.sum(axis=0)/len(intraIndx)

			intra_d2 = 0.0
			for k in range(len(intraIndxs)):
				d = dataSquare[intraIndxs[k], :] - intraSample
			intra_d2 += np.sqrt(d.dot(d))		
			
			inter_d2 = 0.0
			for k in range(len(interIndxs)):
				d = dataSquare[interIndxs[k], :] - intraSample
				inter_d2 += np.sqrt(d.dot(d))

			intraDistance = intra_d2/len(intraIndxs)
			interDistance = inter_d2/len(interIndxs)

			if unbound:
				sampleScore[j] = 1 - intraDistance/interDistance
			else:
				sampleScore[j] = (interDistance - intraDistance)/np.maximum(intraDistance, interDistance)

		scores[l] = sampleScore.mean()

		if neighbor == labelLst[l]:
			return(scores[l])
		
	return(scores.min())

@nb.njit()
def calcGlobalSilhouetteScore(dataSquare, labelLine):
	#> detail: 
	#> param type dataSquare:
	#> param type labelLine:
	#> return (type): 
	#> test-method:
	
	labelLst = np.unique(labelLine)
	scoreLine = np.zeros(labelLst.size)
	if len(labelLst) > 1:
		for j in range(labelLst.size):
			scoreLine[j] = calcGlobalSingleSilhouetteScore(dataSquare, labelLine, labelLst[j], False)
	return(scoreLine)


@nb.njit()
def calcGlobalSingleSilhouetteScore(data, labels, lab, unbound):
	#> detail: 
	#> param type data:
	#> param type labels:
	#> param type lab:
	#> return (type): 
	#> test-method:
	
	labelLst = np.unique(labels)
	if len(labelLst) > 1:
		# for j in range(len(labelLst)):
		intraIndx = np.where(labels == lab)[0]
		interIndx = np.where(labels != lab)[0]
		
		centroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
		intra_d2 = 0.0
		for k in range(len(intraIndx)):
			d = data[intraIndx[k], :] - centroid
			intra_d2 += np.sqrt(d.dot(d))		
		
		inter_d2 = 0.0
		for k in range(len(interIndx)):
			d = data[interIndx[k], :] - centroid
			inter_d2 += np.sqrt(d.dot(d))

		intraDistance = intra_d2/len(intraIndx)
		interDistance = inter_d2/len(interIndx)

	# def _calcScore(scores):
	# 	return(np.argmax(scores) + 1)

	# denomArr 	= np.array([intraDistance, interDistance])
	# maxIndx = np.argmax(np.array([intraDistance.max(), interDistance.max()]))
	if unbound:
		return(1 - intraDistance/interDistance)
	else:
		return((interDistance - intraDistance)/np.maximum(intraDistance, interDistance))

@nb.njit(cache=True)
def findSampleNeighbor(dataSquare, labelLine, pointIndx):
	labelLst = np.unique(labelLine)
	store = np.zeros((dataSquare.shape[0])) + np.nan

	interIndx = np.where(labelLine != labelLine[pointIndx])[0]
	if len(labelLst) > 1:
		for l in range(interIndx.size):
			interCentroid = dataSquare[interIndx[l], :]

			delta = dataSquare[pointIndx, :] - interCentroid
			store[interIndx[l]] = np.sqrt(delta.dot(delta))
	
	neighborLabel = labelLine[np.argmin(store)]
	return(neighborLabel)


@nb.njit()
def calcDaviesBouldin(data, labels, q=2):

	labelLst = np.unique(labels)
	Ri = np.zeros(labelLst.size) 
	for i in range(labelLst.size):
		intraIndx = np.where(labels == labelLst[i])[0]
		
		intraCentroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
		si = 0.0
		for k in range(len(intraIndx)):
			d = data[intraIndx[k], :] - intraCentroid
			si += np.sqrt(d.dot(d))	
		si /= np.sqrt(intraIndx.size)

		Rij = np.zeros(labelLst.size) + np.nan
		for j in range(labelLst.size):
			if i == j:
				continue

			interIndx = np.where(labels == labelLst[j])[0]
			interCentroid = data[interIndx, :].sum(axis=0)/intraIndx.size
			sj = 0.0
			for k in range(len(interIndx)):
				d = data[interIndx[k], :] - interCentroid
				sj += np.sqrt(d.dot(d))
			
			sj /= interIndx.size


			dij = intraCentroid - interCentroid
			dij = np.sqrt(dij.dot(dij))

			Rij[j] = (np.sqrt(si) + np.sqrt(sj)) / dij

		Ri[i] = np.nanmax(Rij)

	return(Ri.sum()/labelLst.size)



@nb.njit()
def calcCHindex(data, labels):
	#> detail: 
	#> param type data:
	#> param type labels:
	#> return (type): 
	#> test-method:
	N = data.shape[0]
	K = len(np.unique(labels))

	labelLst = np.unique(labels)
	if len(labelLst) == 1:
		return(np.nan)
	
	wgss = np.zeros(len(labelLst)) #+ np.nan
	bgss = np.zeros(len(labelLst))# np.nan
	for k in range(len(labelLst)):
		intraIndx = np.where(labels == labelLst[k])[0]
		interIndx = np.where(labels != labelLst[k])[0]

		intra_centroid = data[intraIndx, :].sum(axis=0)/len(intraIndx)
		intra_d2 = 0.0
		for i in range(len(intraIndx)):
			d = data[intraIndx[i], :] - intra_centroid
			intra_d2 += d.dot(d)

		inter_centroid = (data[interIndx, :].sum(axis=0) + data[intraIndx, :].sum(axis=0))/(len(intraIndx) + len(interIndx))
		# print(inter_centroid)
		d = inter_centroid - intra_centroid
		bgss[k] = nb.float32(len(intraIndx) * d.dot(d))
		wgss[k] = nb.float32(intra_d2)#/len(intraIndx)

	return((bgss.sum()/wgss.sum()) * (N - K)/(K - 1))