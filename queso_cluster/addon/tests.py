

from ..runners import base as baseRun
from ..atoms import aux as auxAtom
from ..atoms import scores as scoreAtom

import numpy as np
import matplotlib.pyplot as plt

def kSearchTest(prepSquare):
	distanceK, distanceAvgK = baseRun.kFinder(prepSquare)

	fig = plt.figure(layout='constrained', figsize=(20, 10), dpi=300)
	ax = fig.add_subplot(221)
	ax.autoscale(enable=True, axis='x', tight=True)
	ax.scatter(np.arange(distanceK.shape[1])+1, distanceK[0, :], color='black')
	ax.set_ylabel("++")
	ax.set_title("Staggered Distance Dist(k-1, k)")
	ax.set_xticklabels([])

	ax = fig.add_subplot(223)
	ax.autoscale(enable=True, axis='x', tight=True)
	ax.scatter(np.arange(distanceK.shape[1])+1, distanceK[1, :], color='black')
	ax.set_ylabel("max")

	ax = fig.add_subplot(222)
	ax.autoscale(enable=True, axis='x', tight=True)
	ax.scatter(np.arange(distanceK.shape[1])+1, distanceAvgK[0, :], color='black')
	ax.set_xticklabels([])
	ax.set_title("Avgerage Distance")

	ax = fig.add_subplot(224)
	ax.autoscale(enable=True, axis='x', tight=True)
	ax.scatter(np.arange(distanceK.shape[1])+1, distanceAvgK[1, :], color='black')


	plt.savefig("./distanceK.png")



def scoreEvaluation(prepSquare, intrinsicLine, labelLine):
	i0Arr = auxAtom.pick_jth_label(intrinsicLine, 0)
	intrinsicLst = np.unique(i0Arr)

	scoresArray = np.zeros((2, intrinsicLst.size))
	for ii in range(intrinsicLst.size):
		indx = np.where(i0Arr == intrinsicLst[ii])[0]
		nSSb = scoreAtom.calcNeighborSilhouetteScore(prepSquare[indx,:], labelLine[indx])
		scoresArray[0, ii] = nSSb
		
		db = scoreAtom.calcDaviesBouldin(prepSquare[indx, :], labelLine[indx])
		scoresArray[1, ii] = db
	
	return(scoresArray)

	