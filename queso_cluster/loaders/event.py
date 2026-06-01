import yaml
import pint
import numpy as np

from ..atoms import aux as auxAtom

class eventRunner:
	def __init__(self, inputLst, runIndx):
		stokes_lst 		= ['I', 'Q', 'U', 'V']

		eventRaw 	= inputLst['event']
		runRaw 		= eventRaw['run'][runIndx]

		# if not runRaw['override']:
		# 	exit()

		self.date = eventRaw['date']
		self.dirid = "".join(self.date.split("-"))

		self.runners = runnerMeta(runRaw)
		self.loadSource(eventRaw)

		# srcUse = self.runners.config['src']
		# print(srcUse)
		# print(self.srcLabelLst)
		# print(self.srcLst)
		# self.srcLst = self.srcLst[self.srcLabelLst.index(srcUse)]

	def loadSource(self, eventInput):
		#> detail: 
		#> param type self:
		#> param type eventInput:
		#> return (type): 
		#> test-method:

		for s in range(len(eventInput['src'])):
			srcInput = eventInput['src'][s]
			srcObj = srcMeta(srcInput)
			id_mod = ('-' + srcObj.id_mod)*(bool(srcObj.id_mod))
			if (srcObj.id + id_mod) == self.runners.config['src']:
				srcObj.lines = [x for x in srcObj.lines if x['label'] == self.runners.config['line']]
				self.srcLst = srcObj
				self.srcLabelLst = srcObj.id + id_mod
				self.clusterConfig = srcObj.srcCluster[self.runners.config['line']]
				break

class srcMeta:
	def __init__(self, srcInput):
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

class runnerMeta:
	def __init__(self, runnerInput):
		self.label = runnerInput['label']
		self.config = runnerInput['config']
		self.overwrite = runnerInput['overwrite']

		if 'alignment_dir' in list(runnerInput.keys()):
			self.alignmentDir = runnerInput['alignment_dir']

		if 'qs' in list(runnerInput.keys()):
			self.qs_config = runnerInput['qs']

class eventInput:
	def __init__(self, fname, eventIndx=0, runIndx=0):
		self.configList = []
		configLst = self._load(fname)
		self.event = eventRunner(configLst[eventIndx], runIndx)


	def _load(self, fname):
		with open(fname) as configFile:
			try:
				configInput = yaml.safe_load(configFile)
				return(configInput) 
			except yaml.YAMLError as error:
				print(error)
