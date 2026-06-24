"""
	:file:  queso_cluster/loaders/event.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>
"""

import yaml
import pint
import numpy as np
 
from functools import cached_property

from ..atoms import norm as normAtom
from .. import writer

class eventRunner:
	"""

	Detail

	Parameters
	----------
	fname : str
		File path of the eventManager.yml
	eventIndx : list
		integer for the order of the event in the eventManager.yml
	runIndx : int
		integer for the order of the runner in the eventManager.yml
		
	"""
	def __init__(self, fname, eventIndx, runIndx):
		inputLst = self._load(fname)[eventIndx]

		self._eventRaw 	= inputLst['event']
		self._flavor 	= list(self._eventRaw['run'].keys())[runIndx]
		self._runRaw 	= self._eventRaw['run'][self._flavor]

		for s in range(len(self._eventRaw['src'])):
			#self.srcMeta(self._eventRaw['src'][s])

			# id_mod = ""	
			# if 'mod' in list(id.keys()):
			# 	id_mod = id['mod']
						
			#id_mod = ('-' + id_mod)*(bool(id_mod))
			if self._eventRaw['src'][s]['id']['data'] == self._runRaw['config']['src']:
				lines = self._eventRaw['src'][s]['spectralParams']['lineList']
				self.lines = [x for x in lines if x['label'] == self._runRaw['config']['line']]
				self._srcIndx = s
				if "axisFit" in list(self._eventRaw['src'][self._srcIndx].keys()):
					waveCoeff = np.array(self._eventRaw['src'][self._srcIndx]['axisFit']['coeff'])
					self.waveFitFunc = lambda N: np.poly1d(waveCoeff)(np.arange(N))*pint.Unit(self._eventRaw['src'][self._srcIndx]['axisFit']['unit'])
				break

		writer.dirCleanUp(self.directoryFlavor)

	@cached_property
	def normConfig(self):

		match self.clusterConfig['prep']['normalize']:
			case "normContinuum":
				normArgs = {"norm": normAtom.normContinuum, "continuumIndx": self.lineContinuum}
			case "normMaximum":
				normArgs = {"norm": normAtom.normMaximum, "windowIndx": [self.blueEdge, self.redEdge]}

		return(normArgs)

	@cached_property
	def instrument(self):
		return(self._eventRaw['src'][self._srcIndx]['id']['instrument'])

	@cached_property
	def residual(self):
		return(bool(self._eventRaw['src'][self._srcIndx]['residual']))


	@cached_property
	def lineTheme(self):
		return(self.lines[0]["theme"])

	@cached_property
	def clusterConfig(self):
		return(self._eventRaw['src'][self._srcIndx]['clustering'][self._flavor])

	@cached_property
	def QSConfig(self):
		return(self._runRaw['qs'])

	@cached_property
	def flavor(self):
		return(self._flavor)

	@cached_property
	def overwrite(self):
		return(self._runRaw['overwrite'])

	@cached_property
	def runnerConfig(self):
		return(self._runRaw['config'])
	
	@cached_property
	def datasetID(self):
		return(self.runnerConfig['src'])

	@cached_property
	def directoryDate(self):
		"""The datestring directory"""
		return("".join(self._eventRaw['date'].split("-")))
		
	@cached_property
	def directoryFlavor(self):
		return("{}_{}".format(self.directoryDate, self.flavor))
	@property
	def blueEdge(self):
		"""int containing the index for the beginning of the spectral window used for clustering"""
		blueEdge = self.lines[0]['window'][0]
		if not (type(blueEdge) == int):
			raise TypeError("Window indexes must be integers")
		return(blueEdge)

	@property
	def redEdge(self):
		"""int containing the index for the end of the spectral window used for clustering"""
		redEdge = self.lines[0]['window'][1]
		if not (type(redEdge) == int):
			raise TypeError("Window indexes must be integers")
		return(redEdge)

	@property
	def lineCenter(self):
		"""The index for a center position in the window. This may coinside with the line center of the spectrum"""
		center = self.lines[0]['center']
		if not (type(center) == int):
			raise TypeError("lineCenter index must be an integer")
		return(center)
	
	@cached_property
	def lineContinuum(self):
		"""The index of the continuum for the spectrum. This may be used for normalization"""
		continuum = self._eventRaw['src'][self._srcIndx]['spectralParams']['continuum']
		if not (type(continuum) == int):
			raise TypeError("lineContinuum index must be an integer")
		return(continuum)

	@property
	def timeFrames(self):
		if 'timeFrames' not in list(self.runnerConfig.keys()):
			return(0)
		
		startFrame = self.runnerConfig['timeFrames'][0]
		endFrame = self.runnerConfig['timeFrames'][1]
		return(np.arange(startFrame, endFrame+1).astype(int))

	# @property
	# def clusterConfig(self):
	# 	return(self.srcLst.srcCluster[self._runRaw.runnerInput['line']])

	def _load(self, fname):
		with open(fname) as configFile:
			try:
				configInput = yaml.safe_load(configFile)
				return(configInput) 
			except yaml.YAMLError as error:
				print(error)


		# if 'clustering' in list(srcInput.keys()):
		# 	self.srcCluster 	= srcInput['clustering']
		# else:
		# 	self.srcCluster = {'main': {'intrinsic': [{'label': 'window', 'layerConfig': {'bins': [-1, 999]}}], 
		# 				'optimized': [{'layerGroups': [30], 'layerConfig': {'converge': 1e-6, 'similarity': 'dist'}}]}}

			


		#self.lines = srcInput['spectralParams']['lineList']
		#self.continuum = srcInput['spectralParams']['continuum']
		#print(list(srcInput.keys()))
		# if "axisFit" in list(srcInput.keys()):


	# def loadSource(self):
	# 	"""
	# 	Loads source configuration from eventManager.yml

	# 	Parameters
	# 	----------
	# 	eventInput : dict
	# 		dictionary containing event specific configuration from eventManager.yml
		
	# 	Attributes
	# 	----------
	# 	srcLst : :class:`~queso_cluster.loaders.event.srcMeta`
	# 		Specific source metadata referenced in the active runner 
	# 	srcLabelLst : str
	# 		string identifier for a listed source set by the active runner
	# 	clusterConfig : dict
	# 		dictionary of the clustering configuration for the listed source set by the active runner

	# 	"""

# class srcMeta:
# 	"""
# 		:param srcInput:
# 		:type srcInput:

# 	"""
# 	def __init__(self, srcInput):

# class runnerMeta:
# 	def __init__(self, runnerInput):
# 		self.label = runnerInput['label']
# 		self.config = runnerInput['config']
# 		self.overwrite = runnerInput['overwrite']

# 		if 'alignment_dir' in list(runnerInput.keys()):
# 			self.alignmentDir = runnerInput['alignment_dir']

# 		if 'qs' in list(runnerInput.keys()):
# 			self.qs_config = runnerInput['qs']

# class eventInput:
# 	def __init__(self, fname, eventIndx=0, runIndx=0):
# 		configLst = self._load(fname)
# 		self.event = eventRunner(configLst[eventIndx], runIndx)


# 	def _load(self, fname):
# 		with open(fname) as configFile:
# 			try:
# 				configInput = yaml.safe_load(configFile)
# 				return(configInput) 
# 			except yaml.YAMLError as error:
# 				print(error)
