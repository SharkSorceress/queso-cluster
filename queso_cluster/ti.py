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

from functools import cached_property

class timeIndependent:
	"""
	Time independent clustering framework

	Parameters
	----------
	config : :class:`~queso_cluster.loaders.event.eventInput`
		object containing yaml configuration
	instrumentObj : :class:`~queso_cluster.loaders.visp.visp` :class:`~queso_cluster.loaders.fiss.fiss`, :class:`~queso_cluster.loaders.iris.iris` 
		A `loader` object for specific instruments
	"""
	def __init__(self, config, instrumentObj):
		self._instrumentObj = instrumentObj
		self._config 		= config 

	@loggTimer
	def cluster(self, intrinsicLine=None, kLst=None):
		"""
		Primary clustering function
		
		"""
		
		#> Start of Intrinsic Layer
		if intrinsicLine is None:
			intrinsicLine = baseMain.mainIntrinsic(self._config, 
								np.floor(self.dataSquare*1000.)/1000.)
		
		if "keepI0" in list(self._config.runnerConfig.keys()):
			self.maskLine *= maskAtom.maskIntrinsic(self._config.runnerConfig['keepI0'], 
										   			#self.prepSquare, 
													intrinsicLine,
													(self._config.timeFrames.size, 
													self._instrumentObj.dimInfo['rasterSize'], 
													self._instrumentObj.dimInfo['alongSlitSize']), 
													self._config.timeFrames.size)

		intrinsicLine = intrinsicLine[self.maskLine]
		#prepSquare = self.prepSquare[self.maskLine, :]
		#>> End of Intrinsic Layer

		_ct_ = logg("start", "compute Time")
		prepSquare = self.prepSquare[self.maskLine, 
							   self._config.blueEdge:self._config.redEdge+1].compute()
		logg("stop", _log=_ct_)

		#> Start of Optimized Layer
		labelLine, scoreTuple = baseMain.mainOptimization(prepSquare, 
															intrinsicLine, kLst=kLst)
		#>> End of Optimized Layer

		if not self.maskLine.all():
			unmaskLabelLine = np.zeros(self.maskLine.shape)
			unmaskLabelLine[self.maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)
	

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