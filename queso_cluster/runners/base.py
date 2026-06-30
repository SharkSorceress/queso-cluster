from ..atoms import base as baseAtom
from ..atoms import scores as scoresAtom
from ..addon.logg import loggTimer

import sys
import numba as nb
import numpy as np
import matplotlib.pyplot as plt
from numba_progress import ProgressBar

def runOptimalKSearch(dataSquare, funcLst, checkLst):
	# labelLst = np.unique(labelLine)
	# for l in range(labelLst.size):
	scores, optimalK = findOptimalK(dataSquare, funcLst, checkLst)

	fig = plt.figure(layout='constrained')
	ax = fig.add_subplot(111)
	ax2 = ax.twinx()

	axLst = [ax, ax2]
	color= ["black", "red"]
	for f in range(len(funcLst)):
		axLst[f].plot(scores[f, :], color=color[f])
	
	fig.savefig("./scores_{}.png".format(0))
	plt.close()

	sys.exit()
	return(optimalK[0])


def runPrep(dataSquare, norm, quSquare=None, **kwargs):
	
	prepSquare = norm(dataSquare, **kwargs)
	
	if not (quSquare is None):
		#> TODO: Implement quSquare normalization
		prepSquare -= quSquare

	return(prepSquare)


@nb.njit
def runLabelSort(dataSquare, labelLine):
	labelLst = np.unique(labelLine)

	m0Lst = np.zeros(labelLst.size)
	for l in range(labelLst.size):
		lindx = np.where(labelLine == labelLst[l])[0]
		m0Lst[l] = (dataSquare[lindx, :].sum(axis=0)/lindx.size).mean()

	sortIndx = np.argsort(m0Lst)[::-1]
	sortedLabelLst = labelLst[sortIndx]
	
	sortedLabelLine = np.zeros(labelLine.shape, dtype=labelLine.dtype)
	for l in range(sortedLabelLst.size):
		lindx = np.where(labelLine == sortedLabelLst[l])[0]
		sortedLabelLine[lindx] = l+1

	return(sortedLabelLine, sortIndx)

@nb.njit()
def runIntrinsic(edges, data):
	init_label  = np.ones(data.shape[0], dtype=np.uint16)
	for q in range(edges.size-1):
		for r in np.where((edges[q+1] > data) * (edges[q] <= data)):
			init_label[r] = nb.u8(q+1)
	return(init_label)


@nb.njit()
def kFinder(data):

	k = 20
	startLst = ("++", "max")
	distanceK = np.zeros((len(startLst), k-1))
	distanceAvgK = np.zeros(distanceK.shape)
	for s in range(len(startLst)):
		ic = runStart(20, data, startLst[s])

		for kk in range(k):
			if kk == 0:
				continue

			avgD = 0
			counter = 0
			for ll in range(k):
				if ll < kk:
					avgD += baseAtom.similarityMetric(ic[kk, :], ic[ll, :])
					counter += 1

			distanceAvgK[s, kk] = avgD/counter


			distanceK[s, kk] = baseAtom.similarityMetric(ic[kk-1, :], ic[kk, :])



	return(distanceK, distanceAvgK)



@nb.njit()
def runStart(k, data, initialize, seed=np.random.random()):
	N                          = data.shape[0]
	starting_centroid          = np.zeros((k, data.shape[1]), data.dtype)
	starter 				   = nb.u4(N * seed)
	starting_centroid[0, :]    = data[starter, :]
	match initialize:
		case '++':
			initial_condition  = baseAtom.startPlusPlus(data, k, starting_centroid)
		case 'max':
			initial_condition  = baseAtom.startMax(data, k, starting_centroid)
		case _:
			raise Exception("Invalid Initialization")
		
	return(initial_condition)

@nb.njit()
def runOptimization(k, sub_data, converge, initialize='++'):
	ic                      = runStart(k, sub_data, initialize)
	_, data_label           = baseAtom.calcOptimization(k, sub_data, ic, converge)
	#scoreLine 				= scoresAtom.calcGlobalSilhouetteScore(sub_data, data_label)
	return(data_label+1)


@nb.njit()
def findOptimalK(dataSquare,funcLst, criteriaLst, converge=1e-6):
	with ProgressBar(total=30, ascii=False, leave=False, 
					desc='findOptimalK',
					bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as p:
		k = 0
		scores = np.zeros((len(funcLst), 9))
		while k < scores.shape[1]:
			ff = 0
			for f in funcLst:
				labelLine = runOptimization(k+1, dataSquare, converge)
				scores[ff, k] = f(dataSquare, labelLine)	
				ff += 1
			k += 1
			p.update(1)
		
		cc = 0
		kLst = np.zeros(len(criteriaLst))
		for c in criteriaLst:
			kLst[cc] = c(scores[cc, :]) + 1
			cc += 1 
	
	print(kLst)
	return(scores, kLst)




# def intrinsicMask(dataSquare, intrinsicLine, keepI0=None):
# 	intrinsicLine = baseMain._mainIntrinsic(self.config.srcLst, 
# 									np.floor(dataSquare*100)/100., 0, intrinsicSkip=False)
# 	intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)
		
# 	i0Mask = np.ones(dataSquare.shape[0])
# 	if not (keepI0 is None):
# 		i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
# 		for i in keepI0:
# 			#print(np.unique(intrinsicLine[(intrinsicLine == i)]))
# 			#print(np.unique(intrinsicLine[(intrinsicLine == i)*maskLine]))
# 			i0Mask[(intrinsicLine == i)] = 1
# 	return(i0Mask)


# @nb.njit()
# def _findOptimalK(data, converge, zindx, func1, func2):
# 	optimalGroupLst = np.zeros(30)
# 	a = 0
# 	counter = 0
# 	while a < optimalGroupLst.shape[0]:
# 		# print((a, counter))
# 		scores1 = np.zeros(6)
# 		scores2 = np.zeros(6)

# 		groupEntry_tmp = 0
# 		for i in range(scores1.shape[0]):
# 			labels = _runOptimization(i+1, data[zindx, :], converge)#, label[zindx])
# 			scores1_tmp = func1(data[zindx, :], labels)
# 			scores2_tmp = func2(data[zindx, :], labels)
# 			scores1[i] = scores1_tmp#np.nanmean(scores_tmp)
# 			scores2[i] = np.nanmedian(scores2_tmp)


# 			f = 1
# 			if (i > 1 or i < scores1.shape[0]-1) and (scores1[i] > scores1[i-1]*f) and (scores1[i] > scores1[i + 1]*f):
# 				if (scores2[i] > scores2[i-1]*f) and (scores2[i] > scores2[i+1]*f):
# 					optimalGroupLst[a] = i+1
# 					a += 1
# 					break
				
# 		if optimalGroupLst[a] == 0:
# 			counter += 1
# 			if counter == 30:
# 				optimalGroupLst[a] = int(np.min(np.where(scores1 == np.nanmax(scores1))[0]) + 1)
# 				a += 1
# 				counter = 0
		
# 	return(optimalGroupLst)

