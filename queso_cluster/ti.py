#> file:  ./queso-cluster/ti
#> lang:  python
#> synopsis: 
#> author: Sarah Olivia Riley  <academic@sriley.dev>
import numpy as np
from . import base as baseMain
from .atoms import aux as auxAtom

from .addon.logg import logger
from .atoms import mask as maskAtom

class timeIndependent:
	def __init__(self, config, catalogName, instrumentObj):
		self.catalogBase = catalogName
		self.instrumentObj = instrumentObj

		#self.figDir 	 = './tests/dev/fig/{}/'.format(self.catalogBase)
		#self.qsBase 	= config.runners.qs_config + '-' + config.runners.config['aia']
		#self.qsFigDir 	 = './tests/dev/fig/{}/'.format(self.qsBase) 
		#os.makedirs(self.figDir, exist_ok=True)

		self.config = config 
		self.dirid = ''.join(config.date.split('-'))

		#lineIndx = 0

		#print(self.config.srcLst)
		spectralConfig 			= self.config.srcLst.lines[0]
		self.spectralWindow 	= spectralConfig['window']
		print(self.spectralWindow)
		self.lineCenter 		= spectralConfig['center']
		self.continuum 			= self.config.srcLst.continuum

		self.prepSquare = None

		self.timeFrames = np.arange(1)

		if hasattr(self.config.srcLst, "waveFitFunc"):
			print(self.dataSquare.shape[-1]+1)
			self.waveFit = self.config.srcLst.waveFitFunc(self.dataSquare.shape[-1]+1).to('angstrom')

			print(self.waveFit[self.lineCenter])

	def __getattr__(self, name):
		parentLst = [self.config, self.instrumentObj]
		for p in parentLst:
			if hasattr(p, name):
				return getattr(p, name)
			else:
				continue
		raise AttributeError("No parents have object with attribute '%s'" % name)

	def cluster(self, prepSquare, intrinsicLine=None, kLst=None):
		#> detail: 
		#> param type self:
		#> param type prepSquare:
		#> param type maskLine:
		#> return (type): 
		#> test-method:
		
		ii, jj = self.spectralWindow
		if intrinsicLine is None:
			intrinsicLine = baseMain.mainIntrinsic(self.config, 
										   np.floor(self.dataSquare*100)/100., intrinsicSkip=False)
			intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)
		
		if "keepI0" in list(self.config.runners.config.keys()):
			# i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
			# for i in self.config.runners.config['keepI0']:
			# 	i0Mask[(intrinsicLine == i)] = 1
			
			self.maskLine *= maskAtom.maskIntrinsic(self.config.runners.config['keepI0'], 
										   			prepSquare, intrinsicLine,
													(self.timeFrames.size, self.rasterSize, self.alongSlitSize), self.timeFrames.size)

		self.prepSquare = prepSquare[self.maskLine, :]
		intrinsicLine = intrinsicLine[self.maskLine]

		labelLine, scoreTuple = baseMain.mainOptimization(self.prepSquare[:, ii:jj].compute(), intrinsicLine, kLst=kLst)

		if not self.maskLine.all():
			unmaskLabelLine = np.zeros(self.maskLine.shape)
			unmaskLabelLine[self.maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)