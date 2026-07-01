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

		intrinsicLine = intrinsicLine[self.maskLine]
		#>> End of Intrinsic Layer

		_ct_ = logg("start", "compute Time")
		try:
			prepSquare = self.prepSquare[self.maskLine, 
							   self._config.blueEdge:self._config.redEdge+1].compute()
		except AttributeError:
			prepSquare = self.prepSquare[self.maskLine, 
							   self._config.blueEdge:self._config.redEdge+1]
		logg("stop", _log=_ct_)


		#from .addon import tests as tests

		counter2endAllCounters = 0
		counterCap = 1
		i0Scores = np.zeros((2, np.unique(intrinsicLine).size, counterCap))
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
			# 		ssScores[l] = scoreAtom.calcNeighborSilhouetteScore(prepSquare[indx, :], labelLine[indx], labelLst[l])
			# 		#print([labelLst[l], ssScores])
			# 	i0Scores[1, ii, counter2endAllCounters] = ssScores.min()
				
			#i0Scores[..., counter2endAllCounters] = tests.scoreEvaluation(prepSquare, intrinsicLine, labelLine)
			#print(i0Scores[..., counter2endAllCounters])

			# i0Arr = auxAtom.pick_jth_label(intrinsicLine, 0)
			# intrinsicLst = np.unique(i0Arr)
			# #finals = np.zeros(intrinsicLst.size)
			# for ii in range(intrinsicLst.size):
			# 	indx = np.where(i0Arr == intrinsicLst[ii])[0]
			# 	# gSS = scoreAtom.calcGlobalSilhouetteScore(prepSquare[indx,:], labelLine[indx])
			# 	# i0Scores[0, ii, counter2endAllCounters] = np.array(gSS).min()

			# 	nSSb = scoreAtom.calcNeighborSilhouetteScore(prepSquare[indx,:], labelLine[indx], unbound=False)
			# 	i0Scores[0, ii, counter2endAllCounters] = nSSb
				
			# 	db = scoreAtom.calcDaviesBouldin(prepSquare[indx, :], labelLine[indx])
			# 	i0Scores[1, ii, counter2endAllCounters] = db


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

		# fig.savefig("./scoreTest_++.png")

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
