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
		self._runRaw 	= self._eventRaw['run'][runIndx]

		for s in range(len(self._eventRaw['src'])):
			self.srcMeta(self._eventRaw['src'][s])
			id_mod = ('-' + self.id_mod)*(bool(self.id_mod))
			if (self.id + id_mod) == self._runRaw['config']['src']:
				self.lines = [x for x in self.lines if x['label'] == self._runRaw['config']['line']]
				#self.srcLabelLst = srcObj.id + id_mod
				self.clusterConfig = self.srcCluster[self._runRaw['config']['line']]
				break
		print(self.lines)
		print(self.clusterConfig)
		# self._flavor = None
		# self._overwrite = None
		# self._runnerConfig = None
		# self._datasetID = None
		# self._directoryDate = None
		# self._blueEdge = None
		# self._redEdge = None
		# self._lineCenter = None
		# self._lineContinuum = None
		# self._timeFrames = None

	@cached_property
	def QSConfig(self):
		return(self._runRaw['qs'])

	@cached_property
	def flavor(self):
		return(self._runRaw['label'])

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
		
	@property
	def blueEdge(self):
		"""int containing the index for the beginning of the spectral window used for clustering"""
		return(self.lines[0]['window'][0])

	@property
	def redEdge(self):
		"""int containing the index for the end of the spectral window used for clustering"""
		return(self.lines[0]['window'][1])

	@property
	def lineCenter(self):
		"""The index for a center position in the window. This may coinside with the line center of the spectrum"""
		return(self.lines[0]['center'])
	
	@cached_property
	def lineContinuum(self):
		"""The index of the continuum for the spectrum. This may be used for normalization"""
		return(self.continuum)

	@property
	def timeFrames(self):
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

	def srcMeta(self, srcInput):
		self.id = srcInput['id']['data']
		self.instrument = srcInput['id']['instrument']
		if 'mod' in list(srcInput['id'].keys()):
			self.id_mod = srcInput['id']['mod']
		else:
			self.id_mod = ""
						
		# if 'theme' in list(srcInput.keys()):
		# 	self.theme = srcInput['theme']
		# else:
		# 	self.theme = '#0000FF'

		if 'clustering' in list(srcInput.keys()):
			self.srcCluster 	= srcInput['clustering']
		else:
			self.srcCluster = {'main': {'S0': [{'label': 'window', 'layerConfig': {'bins': [-1, 999]}}], 
						'S1': [{'layerGroups': [30], 'layerConfig': {'converge': 1e-6, 'similarity': 'dist'}}]}}


		if 'residual' in list(srcInput.keys()):
			self.residual = bool(srcInput['residual'])

		# self.clusterConfig = {'intrinsic': srcCluster['S0'],
		# 						'optimized': srcCluster['S1']}


		self.lines = srcInput['spectralParams']['lineList']
		self.continuum = srcInput['spectralParams']['continuum']

		if "axisFit" in list(srcInput.keys()):
			waveCoeff = np.array(srcInput['axisFit']['coeff'])
			#self.waveUnit = srcInput['axisFit']['unit']
			self.waveFitFunc = lambda N: np.poly1d(waveCoeff)(np.arange(N))*pint.Unit(srcInput['axisFit']['unit'])


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
