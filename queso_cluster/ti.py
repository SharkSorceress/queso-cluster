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

class timeIndependent:
	"""
	Time independent clustering framework

	Parameters
	----------
	config : :class:`~queso_cluster.loaders.event.eventInput`
		object containing yaml configuration
	catalogBase : str
		base string for catalog name
	instrumentObj : :class:`~queso_cluster.loaders.visp.visp`, :class:`~queso_cluster.loaders.fiss.fiss`, :class:`~queso_cluster.loaders.iris.iris` 
		A `loader` object for specific instruments

	"""
	def __init__(self, config, catalogName, instrumentObj):
		baseMain.clusterBase.__init__(self, config, catalogName, instrumentObj)

	def __getattr__(self, name):
		return(baseMain.clusterBase.__getattr__(self, name))


	# 	self.catalogBase = catalogName
	# 	self.instrumentObj = instrumentObj

	# 	self.config = config 
	# 	self.dirid = ''.join(config.date.split('-'))

	# 	spectralConfig 			= self.config.srcLst.lines[0]
	# 	self.ii, self.jj 		= spectralConfig['window']
	# 	self.lineCenter 		= spectralConfig['center']
	# 	self.continuum 			= self.config.srcLst.continuum

	# 	#self.prepSquare = None

	# 	#self.timeFrames = np.arange(1)

	# 	if hasattr(self.config.srcLst, "waveFitFunc"):
	# 		print(self.dataSquare.shape[-1]+1)
	# 		self.waveFit = self.config.srcLst.waveFitFunc(self.dataSquare.shape[-1]+1).to('angstrom')

	# 		print(self.waveFit[self.lineCenter])

	# def __getattr__(self, name):
	# 	parentLst = [self.config, self.instrumentObj]
	# 	for p in parentLst:
	# 		if hasattr(p, name):
	# 			return getattr(p, name)
	# 		else:
	# 			continue
	# 	raise AttributeError("No parents have object with attribute '%s'" % name)

	@loggTimer
	def cluster(self, intrinsicLine=None, kLst=None):
		"""
		Primary clustering function
		
		"""
		
		#> Start of Intrinsic Layer
		if intrinsicLine is None:
			intrinsicLine = baseMain.mainIntrinsic(self.config, 
										   np.floor(self.dataSquare*100)/100.)
		
		if "keepI0" in list(self.config.runners.config.keys()):
			
			self.maskLine *= maskAtom.maskIntrinsic(self.config.runners.config['keepI0'], 
										   			self.prepSquare, intrinsicLine,
													(self.timeFrames.size, self.dimInfo['rasterSize'], self.dimInfo['alongSlitSize']), self.timeFrames.size)

		intrinsicLine = intrinsicLine[self.maskLine]
		#prepSquare = self.prepSquare[self.maskLine, :]
		#>> End of Intrinsic Layer

		# prepSquare_compute = np.zeros(self.prepSquare)
		# prepSquare_compute[self.maskLine, self.ii:self.jj+1] = self.prepSquare[self.maskLine, self.ii:self.jj+1].compute()
		# self.prepSquare = prepSquare_compute
		_ct_ = logg("start", "compute Time")
		prepSquare = self.prepSquare[self.maskLine, self.ii:self.jj+1].compute()
		logg("stop", _log=_ct_)

		#> Start of Optimized Layer
		labelLine, scoreTuple = baseMain.mainOptimization(prepSquare, intrinsicLine, kLst=kLst)
		#>> End of Optimized Layer

		if not self.maskLine.all():
			unmaskLabelLine = np.zeros(self.maskLine.shape)
			unmaskLabelLine[self.maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)