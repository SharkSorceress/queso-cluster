import yaml
import numpy as np

class eventRunner:
	def __init__(self, inputLst, runIndx):
		stokes_lst 		= ['I', 'Q', 'U', 'V']

		eventRaw 	= inputLst['event']
		runRaw 		= eventRaw['run'][runIndx]

		# if not runRaw['override']:
		# 	exit()

		self.date = eventRaw['date']

		self.runners = runnerMeta(runRaw)
		self.loadSource(eventRaw)

		srcUse = self.runners.config['src']
		self.srcLst = self.srcLst[self.srcLabelLst.index(srcUse)]

	def loadSource(self, eventInput):
		#> detail: 
		#> param type self:
		#> param type eventInput:
		#> return (type): 
		#> test-method:

		self.srcLst = []
		self.srcLabelLst = []
		for s in range(len(eventInput['src'])):
			srcInput = eventInput['src'][s]
			srcObj = srcMeta(srcInput)
			self.srcLst.append(srcObj)
			self.srcLabelLst.append(srcObj.id + '-' + srcObj.id_mod)

class srcMeta:
	def __init__(self, srcInput):
		self.id = srcInput['id']['data']
		self.instrument = srcInput['id']['instrument']
		if 'mod' in list(srcInput['id'].keys()):
			self.id_mod = srcInput['id']['mod']
		else:
			self.id_mod = ""
						
		if 'theme' in list(srcInput.keys()):
			self.theme = srcInput['theme']
		else:
			self.theme = '#0000FF'

		if 'clustering' in list(srcInput.keys()):
			srcCluster 	= srcInput['clustering']
		else:
			srcCluster = {'S0': [{'label': 'window', 'layerConfig': {'bins': [-1, 999]}}], 
						'S1': [{'layerGroups': [1], 'layerConfig': {'converge': 0}}]}


		if 'residual' in list(srcInput.keys()):
			self.residual = bool(srcInput['residual'])

		self.clusterConfig = {'intrinsic': srcCluster['S0'],
								'optimized': srcCluster['S1']}


		self.lines = srcInput['lines']

		if "axis_fit" in list(srcInput.keys()):
			self.waveCoeff = np.array(srcInput['axis_fit']['coeff'])
			self.waveUnit = srcInput['axis_fit']['unit']
			self.waveFitFunc = lambda N: np.poly1d(self.waveCoeff)(np.arange(N))*pint.Unit(self.waveUnit)

		print(self.waveCoeff)

class runnerMeta:
	def __init__(self, runnerInput):
		self.label = runnerInput['label']
		self.approach = runnerInput['approach']
		self.config = runnerInput['config']
		self.overwrite = runnerInput['overwrite']

		if 'alignment_dir' in list(runnerInput.keys()):
			self.alignmentDir = runnerInput['alignment_dir']

		if 'qs' in list(runnerInput.keys()):
			self.qs_config = runnerInput['qs']

class eventInput:
	def __init__(self, fname, eventIndx, runIndx):
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
