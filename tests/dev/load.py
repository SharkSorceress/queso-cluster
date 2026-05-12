
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
