#> file:  ./queso-cluster/loader
#> lang:  python
#> synopsis: 
#> author: Sarah Olivia Riley  <academic@sriley.dev>

import argparse
import dkist
import yaml
import numpy as np

class QuESO:
	def __init__(self, data, home, fig):
		global datDir
		datDir = data
		global homDir
		homDir = home
		global figDir
		figDir = fig

	def _loadEventConfig(self, eventRunnerFname, event=0, runner=0):
		#> detail: 
		#> param type self:
		#> param type eventRunnerFname:
		#> param type args:
		#> return (type): 
		#> test-method:
		eventObj = eventInput(eventRunnerFname, int(event), int(runner))
		return(eventObj)


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
		axisInfo = [dataset.wcs.pixel_axis_names[::-1], dataset.data.shape]
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
			"pxlAlongSlit": min(pxlSize[0]),
			'pxlSlitWidth': dataset.headers['VSPWID'][0]
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
			"lineLabel": "Ca II IRT",#dataset.headers['WAVEBAND'][0],
			"waveDelta": waveAxisDelta,
			"waveExtrema": (dataset.headers['WAVEMIN'][0], 
							dataset.headers['LINEWAV'][0], 
							dataset.headers['WAVEMAX'][0])
		}

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

class coalignment:
	def __init__(self, config1, config2):
		self.config_src = config1
		self.config_des = config2



	def visp2visp(self):
		#> detail: 
		#> param type self:
		#> return (type): 
		#> test-method:
		waveInfo = {"AEVEG_I": {"lineCenter": 854.21, "lineBand": 0.1},
				   		"BZNNG_I_D1": {'lineCenter': 589.5940, "lineBand": 0.05},
						"BZNNG_I_D2": {'lineCenter': 588.9973, "lineBand": 0.05}, 
						"BZNNG_I_Ni": {'lineCenter': 589.2883, "lineBand": 0.05}}
		dirFits = globalVars.dkist_dir + self.dirid + '/' + self.alignmentDir


		self.dataLst = []
		self.spectralParamsLst = []
		self.waveAxisLst = []
		#fname_wave 	= ["AEVEG_CaII(854.21nm)", "BZNNG_NaID1(589.59nm)", "BZNNG_NaID1(589.59nm)"]

		files = glob.glob(dirFits + '/ViSP_{}*.fits'.format(self.dataIDLst[0]))
		file_trunc = np.sort(np.array([int(x.split('_')[-1].split(".")[0]) for x in files]))
		#print(file_trunc)
		nfiles = len(files)

		initialFName = glob.glob(dirFits + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[self.configIndxSort[0]], file_trunc[0]))[0]
		initial = fits.open(initialFName)


		pullSpaceInfo = vispDataset(globalVars.dkist_dir + self.dirid + "/{}/".format(self.dataIDLst[self.configIndxSort[0]]))
		spaceInfo = pullSpaceInfo.spaceInfo

		nbins = np.floor(pullSpaceInfo.shape[2]/initial[0].data.shape[3])
		print(nbins)

		#int(125/2)
		self.bbox = [0, 125, int(np.floor(1188/nbins)), int(np.ceil((1629)/nbins))]
		print(self.bbox)


		for d in range(len(self.dataIDLst)):
			indx = self.configIndxSort[d]
			#dataset = dkist.load_dataset(globalVars.home_dir + "/" + self.dirid + "/raw/dkist/" + self.configs[indx].data['id'] + "/")
			#fname_wave = self.dataIDLst[indx] + "_" + ''.join(dataset.headers['VSPWID'][0])

			initialFName = glob.glob(dirFits + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[indx], file_trunc[0]))[0]
			initial = fits.open(initialFName)
			initial_shape = initial[0].data[0, :, self.bbox[0]:self.bbox[1], self.bbox[2]:self.bbox[3]].shape
			data_entry = np.zeros((nfiles, *initial_shape))
			waveAxis_entry = np.zeros((nfiles, *initial[1].data.shape))
			for f in range(nfiles):
				findx = file_trunc[f]
				# print(globalVars.home_dir + "/" + self.dirid + '/' + dirAlignment + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[indx], f+1))
				nxtFName = glob.glob(dirFits + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[indx], findx))[0]
				print(nxtFName)
				hdul = fits.open(nxtFName)   

				if (len(hdul[1].data) != len(initial[1].data)):
					waveAxisMod = np.min(np.array([len(hdul[1].data), len(initial[1].data)]))
					data_entry[f, 0:waveAxisMod, ...]  = hdul[0].data[0, 0:waveAxisMod, self.bbox[0]:self.bbox[1], self.bbox[2]:self.bbox[3]]
					waveAxis_entry[f,0:waveAxisMod, ...] 	= hdul[1].data[0:waveAxisMod]
				else:
					data_entry[f, ...]  = hdul[0].data[0, :, self.bbox[0]:self.bbox[1], self.bbox[2]:self.bbox[3]]
					waveAxis_entry[f, ...] 	= hdul[1].data

				hdul.close()
			data_entry = np.moveaxis(data_entry, 1, -1)		
			I0_config = self.configs[indx].clusterConfig['intrinsic']
			if np.array(I0_config).sum() == 0:
				lineCenter 	= waveInfo[util._gen_dataID(self.configs[indx])[0]]['lineCenter']
				lineBand 	= waveInfo[util._gen_dataID(self.configs[indx])[0]]['lineBand']

				lineCore = np.abs(waveAxis_entry[0, ...] - lineCenter).argmin()
				ii 		 = np.abs(waveAxis_entry[0, ...] - lineCenter + lineBand).argmin()
				jj 		 = np.abs(waveAxis_entry[0, ...] - lineCenter - lineBand).argmin()

				print([ii, jj, lineCore])
				print([waveAxis_entry[0, ii], waveAxis_entry[0, jj], waveAxis_entry[0, lineCore]])
				print([waveAxis_entry[0, jj] - waveAxis_entry[0, ii]])
			else:
				ii, jj = self.configs[indx].spectralParams['window']
				lineCore = self.configs[indx].spectralParams['core']
			
			self.spectralParamsLst.append([lineCore, ii, jj])

			self.dataLst.append(data_entry)
			self.waveAxisLst.append(waveAxis_entry*10)
		

		self.spaceInfo = {'rasterSize': self.dataLst[0].shape[1], 'alongSlitSize': self.dataLst[0].shape[2], 
						'pxlAlongSlit': spaceInfo['pxlAlongSlit']*nbins, 'pxlSlitWidth': spaceInfo['pxlSlitWidth']}
		
		self.timeInfo  = {"maxRasters": nfiles, "stepCadence": 1.5, "scanCadence": 3.11*60}
		self.aspect 	= self.spaceInfo['pxlAlongSlit']/self.spaceInfo['pxlSlitWidth']


		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 		



	def fiss2fiss(self):
		#> detail: 
		#> param type self:
		#> return (type): 
		#> test-method:
		self.dataLst = []
		self.spectralParamsLst = []
		self.waveAxisLst = []
		for c in self.configs:
			fData = fissDataset(globalVars.home_dir + "fissSample/", c.data['id'])
			self.dataLst.append(fData.dataCube[:, 0:250, :])
			self.spectralParamsLst.append([c.spectralParams["core"]]+c.spectralParams["window"])

			waveEntry = np.zeros((fData.dataCube.shape[0], fData.dataCube.shape[-1]))
			print(fData.dataCube.shape[-1])
			for t in range(fData.dataCube.shape[0]):
				waveEntry[t, :] = np.arange(0, fData.dataCube.shape[-1])
			self.waveAxisLst.append(waveEntry)

		self.spaceInfo = {'rasterSize': self.dataLst[0].shape[1], 'alongSlitSize': self.dataLst[0].shape[2], 
						'pxlAlongSlit': .1, 'pxlSlitWidth': .1}
		
		self.timeInfo  = {"maxRasters": self.dataLst[0].shape[0], "stepCadence": 1.5, "scanCadence": 3.11*60}
		self.aspect 	= 1#self.spaceInfo['pxlAlongSlit']/self.spaceInfo['pxlSlitWidth']


		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 

		self.bbox = [0, self.dataLst[0].shape[1], 0, self.dataLst[0].shape[2]]

class fissDataset:
	def __init__(self, dataPath, labels):

		biasDarkLst = glob.glob(dataPath + "*_{}_BiasDark.fts".format(labels))
		flatLst 	= glob.glob(dataPath + "*_{}_Flat.fts".format(labels))
		fitsLst 	= glob.glob(dataPath + "*_{}.fts".format(labels))

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

		self.waveCoeff = np.array(srcInput['axis_fit']['coeff'])
		if srcInput['axis_fit']['unit'] == 'nm':
			self.waveCoeff *= 10


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
