"""
	:file:  queso_cluster/td.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>
"""

import numpy as np
from . import base as baseMain
from .runners import base as runBase
# from .atoms import norm as normAtom
from .addon.logg import loggTimer

class timeDependent:
	"""
	Time dependent clustering framework

	Parameters
	----------
	config : :class:`~queso_cluster.loaders.event.eventInput`
		object containing yaml configuration
	catalogBase : str
		base string for catalog name
	instrumentObj : :class:`~queso_cluster.loaders.visp.visp`, :class:`~queso_cluster.loaders.fiss.fiss`, :class:`~queso_cluster.loaders.iris.iris` 
		A `loader` object for specific instruments
	
	"""
	# def __init__(self, config, catalogName, instrumentObj):
	# 	baseMain.clusterBase.__init__(self, config, catalogName, instrumentObj)

	# def __getattr__(self, name):
	# 	baseMain.clusterBase.__getattr__(self, name)

	def __init__(self, config, instrumentObj):
		self._config 		= config 
		self._instrumentObj = instrumentObj

	@loggTimer
	def timeFrames(self, nframes=5, peakTime=None):
		if nframes % 2:
			nframes += 1
		
		if peakTime is None:
			#ii, jj = self.spectralWindow
			#peakTimeSquare = self.dataCube[..., ii:jj].sum(axis=-1).argmax(axis=0)
			peakTime = 2

		rangeMin = np.max([0, peakTime-nframes//2])
		rangeMax = np.min([self.dataSquare.shape[0], peakTime + nframes//2])

		tLst = np.arange(int(rangeMin), int(rangeMax)+1)
		timeFrames = np.zeros((len(tLst), self.dataSquare.shape[1], self.dataSquare.shape[2]))
		for t in range(len(tLst)):
			timeFrames[t, ...] = self.dataCube[tLst[t], ...].reshape(self.dataSquare.shape[1], self.dataSquare.shape[2])
		return(timeFrames, tLst)


	@loggTimer
	def cluster(self, prepSquare, maskLine, intrinsicLine=None, kLst=None):
		#> detail: 
		#> param type self:
		#> param type prepSquare:
		#> param type maskLine:
		#> return (type): 
		#> test-method:
		
		ii = self.blueEdge
		jj = self.redEdge
		#ii, jj = self.spectralWindow
		# if intrinsicLine is None:
		# 	intrinsicLine = baseMain._mainIntrinsic(self.config.srcLst, 
		# 								   np.floor(self.dataSquare*100)/100., 0, intrinsicSkip=False)
		# 	intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)
		
		# if not (keepI0 is None):
		# 	i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
		# 	for i in keepI0:
		# 		#print(np.unique(intrinsicLine[(intrinsicLine == i)]))
		# 		#print(np.unique(intrinsicLine[(intrinsicLine == i)*maskLine]))
		# 		i0Mask[(intrinsicLine == i)] = 1
		# 	maskLine *= i0Mask

		self.prepSquare = prepSquare[maskLine, :]
		intrinsicLine = intrinsicLine[maskLine]

		labelLine, scoreTuple = baseMain.mainOptimization(self.prepSquare[:, ii:jj].compute(), intrinsicLine, kLst=kLst, stageMax=1)

		if not maskLine.all():
			print(labelLine.shape)
			print(maskLine.shape)
			unmaskLabelLine = np.zeros(maskLine.shape)
			unmaskLabelLine[maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)


	def prepSequence(self, timeFrames, **kwargs):
		prepCube = np.zeros((timeFrames.shape))
		for t in range(timeFrames.shape[0]):
			prepCube[t, ...] = runBase.runPrep(timeFrames[t,...], **kwargs)
		return(prepCube)



	def clusterSequence(self, prepCube, maskLine, klst, intrinsicLine=None):
		labelSquare = np.zeros((prepCube.shape[0], prepCube.shape[1]))
		for t in range(prepCube.shape[0]):
			#prepSquare = runBase.runPrep(timeFrames[t,...], norm=normAtom.normContinuum, continuumIndx=self.continuum)			
			labelLine, scores = self.cluster(prepCube[t], maskLine, kLst=[klst[t]], intrinsicLine=intrinsicLine)
			labelSquare[t, :] = labelLine
		return(labelSquare)

	# def clustering(self, prepCube, tlst, groups, intrinsicSquare=None):
	# 	#> detail: low temporal resolution clustering
	# 	#> param type self:
	# 	#> param type prepCube:
	# 	#> param type tlst:
	# 	#> param type groups:
	# 	#> param type [None] intrinsicSquare:
	# 	#> return (type): 
	# 	#> test-method:


	# 	peakPrepSquare = baseAtom._calcDynamicFrame(self.dataCube, peakTimeSquare).reshape(self.dataFrame.shape[1:])
	# 	peakIntrinsicSquare = baseMain._mainIntrinsic(self.config.srcLst, peakPrepSquare, 0)

	# 	labelSquare 		= np.zeros((prepCube.shape[0], prepCube.shape[1]*prepCube.shape[2])) + np.nan
	# 	for dt in range(prepCube.shape[0]):
	# 		epochLabel 	= np.ones(labelSquare.shape[1]) * 111
	# 		with ProgressBar(total=int(labelSquare.shape[1]), ascii=False, leave=True, desc='Epoch Frame {:+}'.format(tlst[dt]),
	# 						bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as epochProgress:	
	# 			prepSquare 	= baseAtom._calcDynamicFrame(prepCube, peakTimeSquare, progress=epochProgress, delta=tlst[dt]).reshape(prepCube.shape[1:]) 
	# 		if groups[dt] > 1:
	# 			# util.logg("msg", "Time delta Runner (peak{:+})".format(tlst[dt]))				
	# 			if intrinsicSquare is None:
	# 				intrinsicSquare = baseMain._mainIntrinsic(self.config.srcLst, self.dataCube, 0, intrinsicSkip=True)
	# 				intrinsicSquare = auxAtom.pick_jth_label(intrinsicSquare, 0).astype(int)
				
	# 			labelLine, scoreTuple = baseMain._mainOptimization(self.config.srcLst, prepSquare*peakIntrinsicSquare[:, None], intrinsicSquare)

	# 		filter_indx = np.where(np.logical_not(np.isnan(prepSquare.sum(axis=-1))))[0]
	# 		#prepCube[dt, ...] 					= prepSquare
	# 		labelSquare[dt, filter_indx] 		= epochLabel.reshape(labelLine.shape[1:])[filter_indx]	
	# 	return(labelLine, score)