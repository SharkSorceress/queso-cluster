"""
	:file:  queso_cluster/ti.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>
"""

import numpy as np
from . import base as baseMain
from .atoms import aux as auxAtom

from .addon.logg import loggTimer, logg
from .atoms import mask as maskAtom
from .atoms import scores as scoreAtom

from functools import cached_property
import matplotlib.pyplot as plt

import timeit

class timeIndependent:
	"""
	Time independent clustering framework

	Parameters
	----------
	config : :class:`~queso_cluster.loaders.event.eventInput`
		object containing yaml configuration
	instrumentObj : :class:`~queso_cluster.loaders.visp.visp`, :class:`~queso_cluster.loaders.fiss.fiss`, :class:`~queso_cluster.loaders.iris.iris` 
		A `loader` object for specific instruments
	"""
	def __init__(self, config, instrumentObj):
		self._instrumentObj = instrumentObj
		self._config 		= config 

	@loggTimer
	def cluster(self, intrinsicLine=None, kLst=None, initialize='++'):
		"""
		Primary clustering function
		
		"""
		
		#> Start of Intrinsic Layer
		if intrinsicLine is None:
			intrinsicLine = baseMain.mainIntrinsic(self._config, 
								np.floor(self.dataSquare*1000.)/1000.)
		
		if "keepI0" in list(self._config.runnerConfig.keys()):
			if self._instrumentObj.dimInfo['numRasters'] > 1:
				self.maskLine *= maskAtom.maskIntrinsic(self._config.runnerConfig['keepI0'], 
													intrinsicLine,
													(self._config.timeFrames.size, 
													self._instrumentObj.dimInfo['rasterSize'], 
													self._instrumentObj.dimInfo['alongSlitSize']))
			else:
				self.maskLine *= maskAtom.maskIntrinsic(self._config.runnerConfig['keepI0'],  
													intrinsicLine,
													(self._instrumentObj.dimInfo['rasterSize'], 
													self._instrumentObj.dimInfo['alongSlitSize']))

		# print(self.maskLine.dtype)
		# self.maskLine *= maskAtom.maskNaN(self.prepSquare[:, self._config.blueEdge:self._config.redEdge+1].compute())

		intrinsicLine = intrinsicLine[self.maskLine]

		#>> End of Intrinsic Layer

		_ct_ = logg("start", "compute Time")
		try:
			prepSquare = self.prepSquare[self.maskLine, 
							   self._config.blueEdge:self._config.redEdge+1].compute()
		except AttributeError:
			prepSquare = self.prepSquare[self.maskLine, 
							   self._config.blueEdge:self._config.redEdge+1]
		
		prepSquare = prepSquare[:, self.waveGrid-self._config.blueEdge]
		logg("stop", _log=_ct_)


		#i0Arr = auxAtom.pick_jth_label(intrinsicLine, 0)#*10 + auxAtom.pick_jth_label(intrinsicLine, 1)
		#intrinsicLst = np.unique(i0Arr)			

	
		#from .addon import tests as tests


		# inertiaScoreArr = np.zeros((3, 5, 9))
		# otherCounter = 10
		# for k in range(9):
		# 	kLst[1]['layerGroups'] = [1, 1, k+1, k+1, 1, k+1, k+1, k+1]
		# 	counter3 = 0
		# 	while counter3 < otherCounter:
		# 		print((k, counter3))
		# 		labelLine  = baseMain.mainOptimization(prepSquare, intrinsicLine, initialize=initialize,
		# 															kLst=kLst, stageMax=len(kLst))

		# 		ll = 0
		# 		for ii in range(intrinsicLst.size):
		# 			indx = np.where(i0Arr == intrinsicLst[ii])[0]
		# 			optimized = intrinsicLst[ii]*10 + auxAtom.pick_jth_label(labelLine[indx], 1)
		# 			optLst = np.unique(optimized)
		# 			for jj in range(optLst.size):
		# 				oindx = indx[np.where(optimized == optLst[jj])[0]]
		# 				inertiaScoreArr[0, ll, k] += scoreAtom.inertiaScore(prepSquare[oindx, :], labelLine[oindx])
		# 				inertiaScoreArr[1, ll, k] += scoreAtom.inertiaScore(prepSquare[oindx, :], labelLine[oindx], distortion=True)/oindx.size
						
		# 				ooLst = np.unique(labelLine[oindx])
		# 				for nn in range(ooLst.size):
		# 					inertiaScoreArr[2, ll, k] += scoreAtom.calcNeighborSilhouetteScore(prepSquare[oindx, :], labelLine[oindx], point=ooLst[nn])/ooLst.size
	
		# 				ll += 1
		# 		counter3 += 1

		# inertiaScoreArr /= otherCounter

		# fig = plt.figure(layout='constrained', figsize=(10, 10), dpi=300)

		# legendLabels = ["31X", "32X", "51X", "61X", "62X"]
		# colors = ["red", "orange", "green", "blue", "magenta", "black"]

		# for jj in range(inertiaScoreArr.shape[0]):
		# 	ax1 = fig.add_subplot(inertiaScoreArr.shape[0], 1, jj+1)
		# 	for ii in range(len(legendLabels)):
				
		# 		norm = 1
		# 		if jj < 2:
		# 			norm  = inertiaScoreArr[jj, ii, :].max()

		# 		ax1.plot(np.arange(inertiaScoreArr.shape[2])+1, inertiaScoreArr[jj, ii, :]/norm, color=colors[ii], label=legendLabels[ii])
		# 		ax1.scatter(np.arange(inertiaScoreArr.shape[2])+1, inertiaScoreArr[jj, ii, :]/norm, color=colors[ii])


		# 	# ax3.plot(np.arange(inertiaScoreArr.shape[2])+1, inertiaScoreArr[1, ii, :]/inertiaScoreArr[1, ii, :].max(), color=colors[ii], label=legendLabels[ii])
		# 	# ax3.scatter(np.arange(inertiaScoreArr.shape[2])+1, inertiaScoreArr[1, ii, :]/inertiaScoreArr[1, ii, :].max(), color=colors[ii])


		# ax1.legend()
		# fig.savefig("./elbow_i0o1.png")
		# plt.close()

		#kLst[1]['layerGroups'] = [1, 1, 3, 3, 1, 3, 5, 3]

		counter2endAllCounters = 0
		counterCap = 1
		i0Scores = np.zeros((4, np.unique(intrinsicLine).size, counterCap))
		s = timeit.default_timer()

		#print(initialize)
		while counter2endAllCounters < counterCap:
			#print(counter2endAllCounters)
			#print(np.unique(intrinsicLine))
			# > Start of Optimized Layer
			labelLine  = baseMain.mainOptimization(prepSquare, intrinsicLine, initialize=initialize,
																kLst=kLst, stageMax=len(kLst))
			#>> End of Optimized Layer
			# i0Arr = auxAtom.pick_jth_label(intrinsicLine, 0)
			# intrinsicLst = np.unique(i0Arr)
			# #finals = np.zeros(intrinsicLst.size)
			# for ii in range(intrinsicLst.size):
			# 	indx = np.where(i0Arr == intrinsicLst[ii])[0]
			# 	labelLst = np.unique(labelLine[indx])
			# 	i0Scores[0, ii, counter2endAllCounters] = scoreAtom.calcDaviesBouldin(prepSquare[indx, :], labelLine[indx])
			# 	ssScores = np.zeros(labelLst.size)
			# 	for l in range(labelLst.size):
			# 		ssScores[l] = scoreAtom.calcNeighborSilhouetteScore(prepSquare[indx, :], labelLine[indx], point=labelLst[l])
			# 		#print([labelLst[l], ssScores])
			# 	i0Scores[1, ii, counter2endAllCounters] = ssScores.min()
			# 	i0Scores[2, ii, counter2endAllCounters] = np.median(ssScores)
			# 	i0Scores[3, ii, counter2endAllCounters] = scoreAtom.inertiaScore(prepSquare[indx, :], labelLine[indx])
			# #	print(scoreAtom.inertia(prepSquare[indx, :], labelLine[indx]))
				#interia = scoreAtom.inertia(prepSquare[indx, :], labelLine[indx])

				#i0Scores[3, ii, counter2endAllCounters] = interia
				

			# i0Arr = auxAtom.pick_jth_label(intrinsicLine, 0)
			# intrinsicLst = np.unique(i0Arr)

			# scoresArray = np.zeros((2, intrinsicLst.size))
			# for ii in range(intrinsicLst.size):
			# 	indx = np.where(i0Arr == intrinsicLst[ii])[0]
			# 	nSSb = scoreAtom.calcNeighborSilhouetteScore(prepSquare[indx,:], labelLine[indx], point=labelLst[l])
			# 	scoresArray[0, ii] = nSSb
				
			# 	db = scoreAtom.calcDaviesBouldin(prepSquare[indx, :], labelLine[indx])
			# 	scoresArray[1, ii] = db				
			# i0Scores[..., counter2endAllCounters] = scoresArray#tests.scoreEvaluation(prepSquare, intrinsicLine, labelLine)
			#print(i0Scores[..., counter2endAllCounters])


			#print(finals)
			#print(i0Scores[1, :, counter2endAllCounters])
			# if (i0Scores[1, :, counter2endAllCounters] > 0.45).all():
			# 	print(i0Scores[:, :, counter2endAllCounters])
			# 	print(counter2endAllCounters)
			# 	break

			counter2endAllCounters += 1
		e = timeit.default_timer()
		print(e - s)
		
		# fig = plt.figure(layout='constrained', figsize=(10*2, 15), dpi=300)
		# colors = ['black', 'red', 'blue', 'green']
		# counter = 1
		# for ii in range(i0Scores.shape[1]):
		# 	for jj in range(i0Scores.shape[0]):
		# 		ax = fig.add_subplot(i0Scores.shape[1], i0Scores.shape[0], counter)
		# 		ax.autoscale(enable=True, axis='x', tight=True)
		# 		ax.scatter(np.arange(counterCap), i0Scores[jj, ii, :], color=colors[jj])
		# 		# if jj !=  2:
		# 		# 	ax.axhline(y = 0.5, color='blue', linestyle='dotted')
		# 		counter += 1

		# 		if ii < i0Scores.shape[1]-1:
		# 			ax.set_xticklabels([])

		# 		if jj == 0:
		# 			ax.set_ylabel(np.unique(intrinsicLine)[ii])

		# fig.savefig("./scoreTest_{}.png".format(initialize))

		# if (i0Scores[1, :, -1] <= 0.5).all():
		# 	raise Exception("Criteria not satisfied")

		#gSS = scoreAtom.calcGlobalSilhouetteScore(prepSquare, labelLine)


		if not self.maskLine.all():
			unmaskLabelLine = np.zeros(self.maskLine.shape)
			unmaskLabelLine[self.maskLine] = labelLine
			return(unmaskLabelLine)
		
		return(labelLine)
	

	@cached_property
	def geometry(self):
		"""
		Imports spatial and temporal properties from instrumentObj 
		
		Returns
		-------
		dict
			Dictionary containing the geometry and cadence of the observations
		"""
		
		return({"numRasters": self._instrumentObj.dimInfo['numRasters'],
					"rasterSize": self._instrumentObj.dimInfo['rasterSize'],
					"alongSlitSize": self._instrumentObj.dimInfo['alongSlitSize'],
					"pxlSlitWidth": self._instrumentObj.pxlDelta['pxlSlitWidth'],
					"pxlAlongSlit": self._instrumentObj.pxlDelta['pxlAlongSlit'],
					"stepCadence": self._instrumentObj.stepCadence,
					"mapCadence": self._instrumentObj.mapCadence,
					"resetDuration": self._instrumentObj.resetDuration,
		})
	
	def clusterCompoundLabels(self, optLabels):
		"""
		Concatenates the labels by time to form a sequence cluster

		Parameters
		----------
		optLabels : ndarray
			3D array containing the finalized cluster labels

		Returns
		-------
		
		compoundLabels : ndarray
			2D array containing the cluster *sequence* labels

		"""
		labelLst = np.unique(optLabels)
		recountedLabels = np.zeros(optLabels.shape) + np.nan
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			if np.isnan(labelLst[l]):
				continue

			lindx = np.where(optLabels == labelLst[l])
			recountedLabels[lindx] = l+1

		compoundLabels = np.zeros((self._instrumentObj.dimInfo['rasterSize'], self._instrumentObj.dimInfo['alongSlitSize']), dtype=str)
		nindxT, nindxX, nindxY = np.where(np.isnan(recountedLabels))
		for t in range(optLabels.shape[0]):
			compoundLabels = np.char.add(compoundLabels, 
								np.char.zfill(recountedLabels[t, ...].astype(np.uint).astype(str), 2))
			
		compoundLabels[nindxX, nindxY] = "X"
		return(compoundLabels)


	@cached_property
	def waveGrid(self):
		ii, jj = [self._config.blueEdge, self._config.redEdge]
		if "adaptive" in list(self._config.lines[0].keys()):
			dataLine = np.std(self.prepSquare[:, ii:jj+1], axis=0).compute()
			std_quantile = np.quantile(dataLine, float(self._config.lines[0]['adaptive']))

			w = np.unique([ii] + np.arange(ii, jj+1)[dataLine > std_quantile].tolist() + [jj])
		else:
			w = np.arange(ii,jj+1)
		return(np.asarray(w).astype(int))