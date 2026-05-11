#> file:  ./queso-cluster/approach
#> lang:  python
#> synopsis: 
#> author: Sarah Olivia Riley  <academic@sriley.dev>
from . import base as baseMain
from .atoms import aux as auxAtom
from .atoms import base as baseAtom

from .addon.logg import loggTimer

import numpy as np
import os

class timeIndependent:
	def __init__(self, config, catalogName, instrumentObj):
		self.catalogBase = catalogName
		self.instrumentObj = instrumentObj

		#self.figDir 	 = './tests/dev/fig/{}/'.format(self.catalogBase)
		self.qsBase 	= config.runners.qs_config + '-' + config.runners.config['aia']
		#self.qsFigDir 	 = './tests/dev/fig/{}/'.format(self.qsBase) 
		#os.makedirs(self.figDir, exist_ok=True)


		self.config = config 
		self.dirid = ''.join(config.date.split('-'))


		spectralConfig 			= self.config.srcLst.lines[0]
		self.spectralWindow 	= spectralConfig['window']
		self.lineCenter 		= spectralConfig['core']
		self.continuum 			= spectralConfig['continuum']
		self.waveCoeff			= self.config.srcLst.waveCoeff

		self.stepCadence = 15.67
		self.mapCadence = np.inf

		self.prepSquare = None

		self.waveFit = np.poly1d(self.waveCoeff)(np.arange(self.instrumentObj.shape[-1]))

	def __getattr__(self, name):
		parentLst = [self.config, self.instrumentObj]
		for p in parentLst:
			if hasattr(p, name):
				return getattr(p, name)
			else:
				continue
		raise AttributeError("No parents have object with attribute '%s'" % name)

	def cluster(self, prepSquare, maskLine, intrinsicLine=None, keepI0=None, kLst=None):
		#> detail: 
		#> param type self:
		#> param type prepSquare:
		#> param type maskLine:
		#> return (type): 
		#> test-method:
		
		ii, jj = self.spectralWindow
		if intrinsicLine is None:
			intrinsicLine = baseMain._mainIntrinsic(self.config.srcLst, 
										   np.floor(self.dataSquare*100)/100., 0, intrinsicSkip=False)
			intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)
		
		if not (keepI0 is None):
			i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
			for i in keepI0:
				#print(np.unique(intrinsicLine[(intrinsicLine == i)]))
				#print(np.unique(intrinsicLine[(intrinsicLine == i)*maskLine]))
				i0Mask[(intrinsicLine == i)] = 1
			maskLine *= i0Mask

		self.prepSquare = prepSquare[maskLine, :]
		intrinsicLine = intrinsicLine[maskLine]

		labelLine, scoreTuple = baseMain._mainOptimization(self.prepSquare[:, ii:jj].compute(), intrinsicLine, kLst=kLst)
		print(np.unique(labelLine))

		if not maskLine.all():
			print(labelLine.shape)
			print(maskLine.shape)
			unmaskLabelLine = np.zeros(maskLine.shape)
			unmaskLabelLine[maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)


from numba_progress import ProgressBar
class timeDependent:
	def __init__(self, config, catalogBase, instrumentObj):

		self.config = config

		self.catalogBase = catalogBase
		#self.figDir 	 = './fig/{}/'.format(self.catalogBase)

		self.instrumentObj = instrumentObj

		spectralConfig 			= self.config.srcLst.lines[0]
		self.spectralWindow 	= spectralConfig['window']
		self.lineCenter 		= spectralConfig['core']
		self.continuum 			= spectralConfig['continuum']
		#self.waveCoeff			= self.config.srcLst.waveCoeff

		self.stepCadence = 1.5
		self.mapCadence = 3.11*60

		self.prepSquare = None

		#self.waveFit = np.poly1d(self.waveCoeff)(np.arange(self.instrumentObj.shape[-1]))

	def __getattr__(self, name):
		parentLst = [self.config, self.instrumentObj]
		for p in parentLst:
			if hasattr(p, name):
				return getattr(p, name)
			else:
				continue
		raise AttributeError("No parents have object with attribute '%s'" % name)

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
		print([rangeMin, rangeMax])

		tLst = np.arange(int(rangeMin), int(rangeMax)+1)
		print(tLst)
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
		
		ii, jj = self.spectralWindow
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

		labelLine, scoreTuple = baseMain._mainOptimization(self.prepSquare[:, ii:jj].compute(), intrinsicLine, kLst=kLst, stageMax=1)
		print(np.unique(labelLine))

		if not maskLine.all():
			print(labelLine.shape)
			print(maskLine.shape)
			unmaskLabelLine = np.zeros(maskLine.shape)
			unmaskLabelLine[maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)

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