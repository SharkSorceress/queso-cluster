#> file:  ./queso-cluster/ti
#> lang:  python
#> synopsis: 
#> author: Sarah Olivia Riley  <academic@sriley.dev>
import numpy as np
from . import base as baseMain
from .atoms import aux as auxAtom

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

		spectralConfig 			= self.config.srcLst.lines[0]
		self.spectralWindow 	= spectralConfig['window']
		self.lineCenter 		= spectralConfig['core']
		self.continuum 			= spectralConfig['continuum']

		self.prepSquare = None

		if hasattr(self.config.srcLst, "waveFitFunc"):
			self.waveFit = self.config.srcLst.waveFitFunc(self.dataSquare.shape[-1]+1)

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
			intrinsicLine = baseMain.mainIntrinsic(self.config.srcLst, 
										   np.floor(self.dataSquare*100)/100., 0, intrinsicSkip=False)
			intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)
		
		if not (keepI0 is None):
			i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
			for i in keepI0:
				i0Mask[(intrinsicLine == i)] = 1
			maskLine *= i0Mask

		self.prepSquare = prepSquare[maskLine, :]
		intrinsicLine = intrinsicLine[maskLine]

		labelLine, scoreTuple = baseMain.mainOptimization(self.prepSquare[:, ii:jj].compute(), intrinsicLine, kLst=kLst)

		if not maskLine.all():
			unmaskLabelLine = np.zeros(maskLine.shape)
			unmaskLabelLine[maskLine] = labelLine
			return(unmaskLabelLine, scoreTuple)
		
		return(labelLine, scoreTuple)