#> file:  ./queso-cluster/loader
#> lang:  python
#> synopsis: 
#> author: Sarah Olivia Riley  <academic@sriley.dev>

import dkist
import yaml
import numpy as np

from astropy.io import fits
import glob

import pint

# ureg = pint.UnitRegistry()
# Q_ = ureg.Quantity
# ureg.define(Q_(None, 'intensity'))

import datetime
from  datetime import datetime as dt

class QuESO:
	def __init__(self, data, home, fig):
		self.datDir = data
		self.homDir = home
		self.figDir = fig

	def _loadEventConfig(self, eventRunnerFname, event=0, runner=0):
		#> detail: 
		#> param type self:
		#> param type eventRunnerFname:
		#> param type args:
		#> return (type): 
		#> test-method:
		eventObj = eventInput(eventRunnerFname, int(event), int(runner))
		return(eventObj)


def convertTime(dates, ref=False):
	calc_diff_wF = lambda t: (dt.strptime(t, "%Y-%m-%dT%H:%M:%S.%f") - datetime.datetime(1970, 1, 1)) / datetime.timedelta(microseconds=1)

	calc_diff_woF = lambda t: (dt.strptime(t, "%Y-%m-%dT%H:%M:%S") - datetime.datetime(1970, 1, 1)) / datetime.timedelta(microseconds=1)
	#print([dates, len(dates)])
	if type(dates) != np.str_:
		unixTime = np.zeros(len(dates))
		for T in range(len(dates)):
	#		print(dates[T])
			try:
				unixTime[T] = calc_diff_wF(dates[T]) * 1e-6
			except:
				unixTime[T] = calc_diff_woF(dates[T]) * 1e-6	

		#print("duration: {}".format(unixTime[-1]-unixTime[0]))
		if ref:
			reference_time = dates[0]
			unixTime -= unixTime[0]
			return(unixTime, reference_time)

	else:
		try:
			unixTime = calc_diff_wF(dates) * 1e-6
		except:
			unixTime = calc_diff_woF(dates) * 1e-6	


	return(unixTime)

class instrument:
	def __init__(self, dataPath):
		self.dataPath = dataPath

	def vispLoad(self, stokes=0):
		#> detail: 
		#> param type self:
		#> param type [0] stokes:
		#> return (type): 
		#> test-method:
		dataset = dkist.load_dataset(self.dataPath)
		dataCube = dataset.data
		if 'polarization state' in dataset.wcs.pixel_axis_names:
			dataCube = dataCube[stokes, ...] 
		#axisInfo = [dataset.wcs.pixel_axis_names[::-1], dataset.data.shape]
		flat_axis = 1
		numRaster = 1
		test = []
		crval = []
		
		for n in range(dataset.headers['DNAXIS'][0]):
			dnaxis_entry = dataset.headers['DNAXIS' + str(n+1)][0]
			
			#print([dataset.headers['DTYPE' + str(n+1)][0], dnaxis_entry])
			match dataset.headers['DTYPE' + str(n+1)][0]: 
				case 'SPECTRAL':
						spectral_len = dnaxis_entry
						spectral_loc = int(np.where(np.asarray(dataCube.shape) == dnaxis_entry)[0])
				case 'TEMPORAL':
						numRaster = dnaxis_entry
						flat_axis *= numRaster
				case 'SPATIAL':
						crval.append(dataset.headers['CRVAL' + str(n+1)][0])
						flat_axis *= dnaxis_entry
						test.append(dnaxis_entry)


		pxlSize = [[], []]
		for m in range(dataset.headers['WCSAXES'][0]):
			match dataset.headers['CTYPE' + str(m+1)][0]:
				case 'HPLT-TAN':                     
					pxlSize[0].append(dataset.headers['CDELT' + str(m+1)][0])   
					pxlSize[1].append(m)
				case 'AWAV':
						waveAxisDelta = dataset.headers['CDELT' + str(m+1)][0]


		self.deltas = {	
			"pxlAlongSlit": min(pxlSize[0]) * pint.Unit("arcsecond"),
			'pxlSlitWidth': dataset.headers['VSPWID'][0] * pint.Unit("arcsecond")
		}

		self.dataCube = np.moveaxis(dataCube, spectral_loc, -1)
		self.shape = self.dataCube.shape
		if numRaster == 1:
			self.shape = self.dataCube.shape
			self.dataSquare = self.dataCube.reshape(flat_axis, spectral_len)#.rechunk('auto')
		else:
			self.dataSquare = self.dataCube.reshape(numRaster, flat_axis//numRaster, spectral_len)

		self.alongSlitSize 	= np.max(test)
		print(self.dataSquare.shape)
		self.rasterSize 	= (flat_axis // self.alongSlitSize) // numRaster

		self.spaceInfo = {
			"maxRasters": numRaster,
			"rasterSize": self.rasterSize,
			"alongSlitSize": self.alongSlitSize,
		}
		print(self.spaceInfo)

		self.waveInfo = {
			"waveDelta": waveAxisDelta,
			"waveExtrema": (dataset.headers['WAVEMIN'][0], 
							dataset.headers['LINEWAV'][0], 
							dataset.headers['WAVEMAX'][0])
		}

		datetime = convertTime(dataset.headers['DATE-BEG'])

		self.zeroDate = dataset.headers['DATE-BEG'][0]

		stepCadence = np.diff(datetime[0:self.rasterSize])
		stepCadence = stepCadence[stepCadence > 0]
		self.stepCadence = stepCadence.mean() * pint.Unit("second")

		mapCadence = np.diff(datetime[::self.rasterSize])
		mapCadence = mapCadence[mapCadence > 0]

		resetTime = datetime[self.rasterSize-1:self.rasterSize+1]
		print(resetTime)

		if len(np.unique(mapCadence)) > 0: 
			self.mapCadence = mapCadence.mean() * pint.Unit("second")

	def irisLoad(self):
		#> detail: 
		#> param type self:
		#> return (type): 
		#> test-method:
			dataset = fits.open(self.dataPath, memmap=True, do_not_scale_image_data=True)

	def fissLoad(self, labels):
		#> detail: 
		#> param type self:
		#> param type labels:
		#> return (type): 
		#> test-method:

		biasDarkLst = glob.glob(self.dataPath + "*_{}_BiasDark.fts".format(labels))
		flatLst 	= glob.glob(self.dataPath + "*_{}_Flat.fts".format(labels))
		fitsLst 	= glob.glob(self.dataPath + "*_{}.fts".format(labels))

		initial = fits.open(fitsLst[0])

		self.rasterSize = initial[0].header['NAXIS2']
		self.alongSlitSize = initial[0].header['NAXIS3']


		self.waveInfo = {
			"lineLabel": initial[0].header['GRATWVLN'],#dataset.headers['WAVEBAND'][0],
		}

		print(self.waveInfo)

		self.spaceInfo = {
			"maxRasters": len(fitsLst),
			"pxlAlongSlit": 512,
			'pxlSlitWidth': 512
		}



		self.dataCube =  np.zeros((len(fitsLst), self.alongSlitSize, self.rasterSize, initial[0].header['NAXIS1']))

		for f in range(len(fitsLst)):
			file = fits.open(fitsLst[f])
			self.dataCube[f, ...] = file[0].data#.reshape(self.rasterSize*self.alongSlitSize, initial[0].header['NAXIS1'])
			print(file[0].data.shape)

			file.close()

		self.dataCube = np.moveaxis(self.dataCube, 1, 2)
		self.shape = self.dataCube.shape

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
