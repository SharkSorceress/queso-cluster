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

@nb.njit()
def calcSilhouetteScore(dataSquare, labelLine):
	#> detail: 
	#> param type dataSquare:
	#> param type labelLine:
	#> return (type): 
	#> test-method:
	
	labelLst = np.unique(labelLine)
	# intraDistance = np.zeros(len(labelLst))
	# interDistance = np.zeros(len(labelLst))
	scoreLine = np.zeros(labelLst.size)
	if len(labelLst) > 1:
		for j in range(labelLst.size):
			scoreLine[j] = calcSingleSilhouetteScore(dataSquare, labelLine, labelLst[j])
			# intraIndx = np.where(labelLine == labelLst[j])[0]
			# interIndx = np.where(labelLine != labelLst[j])[0]

			# centroid = dataSquare[intraIndx, :].sum(axis=0)/len(intraIndx)
			# intra_d2 = 0.0
			# for k in range(len(intraIndx)):
			# 	d = dataSquare[intraIndx[k], :] - centroid
			# 	intra_d2 += np.sqrt(d.dot(d))		
			
			# inter_d2 = 0.0
			# for k in range(len(interIndx)):
			# 	d = dataSquare[interIndx[k], :] - centroid
			# 	inter_d2 += np.sqrt(d.dot(d))

			#intraDistance[j] = intra_d2/len(intraIndx)
			#interDistance[j] = inter_d2/len(interIndx)

	return(scoreLine)


@nb.njit()
def calcSingleSilhouetteScore(data, labels, lab):
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

#	return((interDistance - intraDistance)/np.maximum(intraDistance, interDistance))

	return(1 - intraDistance/interDistance)

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