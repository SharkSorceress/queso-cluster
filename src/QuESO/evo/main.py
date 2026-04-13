class EvolutionDriven:
	def __init__(self, events, alignmentDir, catalogBase):

		self.catalogBase = catalogBase
		self.figDir 	 = './fig/{}/'.format(self.catalogBase)

		configsIDs = [events.runners.config['primary']['src']]
		
		lineSelect = {}
		if 'lines' in list(events.runners.config['primary'].keys()):
			lineSelect[events.runners.config['primary']['src']] = events.runners.config['primary']['lines'][events.runners.config['primary']['src']]


		if 'support' in list(events.runners.config.keys()):
			configsIDs.append(events.runners.config['support']['src'])
			if 'lines' in list(events.runners.config['support'].keys()):
				lineSelect[events.runners.config['support']['src']] = events.runners.config['support']['lines'][events.runners.config['support']['src']]
			# else:
			# 	lineSelect.append(0)

		self.events = events

		self.lineSelect = lineSelect
		print(self.lineSelect)

		self.resolution = [0.02, 0.01]

		self.configs = events.srcLst

		self.alignmentDir = alignmentDir
		self.catalogBase = catalogBase 
		self.dataIDLst = events.srcLabelLst

		self.bbox = np.array(events.runners.config['bbox'])

		timeSeqParam = events.runners.config['frames']
		self.timeSeqLst = np.arange(timeSeqParam[0], timeSeqParam[1]+timeSeqParam[2], timeSeqParam[2])
		
		self.dynamicIndx = np.where(self.timeSeqLst == 0)[0]

		#self.configIndxSort = sorted(range(len(self.roleLst)), key=lambda k: self.roleLst[k])
		self.dirid   		= ''.join(events.date.split('-'))


		__coalignLog__ = util.logg("start", val="Coalignment")
		self.coalignment()
		util.logg("stop", _log=__coalignLog__)

	def coalignment(self):

		waveInfo = {"AEVEG_I": {"lineCenter": 854.21, "lineBand": 0.1},
				   		"BZNNG_I_D1": {'lineCenter': 589.5940, "lineBand": 0.05},
						"BZNNG_I_D2": {'lineCenter': 588.9973, "lineBand": 0.05}, 
						"BZNNG_I_Ni": {'lineCenter': 589.2883, "lineBand": 0.05}}
		dirFits = globalVars.dkist_dir + self.dirid + '/' + self.alignmentDir

		self.dataLst = []
		self.spectralParamsLst = []
		self.waveAxisLst = []
		#fname_wave 	= ["AEVEG_CaII(854.21nm)", "BZNNG_NaID1(589.59nm)", "BZNNG_NaID1(589.59nm)"]

		files = glob.glob(dirFits + '/ViSP_{}_*.fits'.format(self.dataIDLst[0].split("-")[0]))

		file_trunc = np.sort(np.array([int(x.split('_')[-1].split(".")[0]) for x in files]))
		nfiles = len(files)

		initialFName = glob.glob(dirFits + '/ViSP_{}_*_{}.fits'.format(self.dataIDLst[0].split("-")[0], file_trunc[0]))[0]
		initial = fits.open(initialFName)

		pullSpaceInfo = vispDataset(globalVars.dkist_dir + self.dirid + "/" + self.dataIDLst[0].split("-")[0] + "/")
		#pullSpaceInfo = vispDataset(globalVars.dkist_dir + self.dirid + "/BZNNG/")

		spaceInfo = pullSpaceInfo.spaceInfo

		nbins = np.floor(pullSpaceInfo.shape[2]/initial[0].data.shape[3])

		#int(125/2)
#		self.bbox = [0, 125, int(np.floor(1188/nbins)), int(np.ceil((1629)/nbins))]
		self.bbox = np.floor((self.bbox * np.array([1, 1, 1./nbins, 1./nbins]))).astype(int)
		self.spectralParamsLst = {}

		for d in range(len(self.dataIDLst)):
			indx = d#self.configIndxSort[d]
			#dataset = dkist.load_dataset(globalVars.home_dir + "/" + self.dirid + "/raw/dkist/" + self.configs[indx].data['id'] + "/")
			#fname_wave = self.dataIDLst[indx] + "_" + ''.join(dataset.headers['VSPWID'][0])

			initialFName = glob.glob(dirFits + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[indx].split("-")[0], file_trunc[0]))[0]
			initial = fits.open(initialFName)
			initial_shape = initial[0].data[0, :, self.bbox[0]:self.bbox[1]+1, self.bbox[2]:self.bbox[3]+1].shape
			data_entry = np.zeros((nfiles, *initial_shape))
			waveAxis_entry = np.zeros((nfiles, *initial[1].data.shape))
			for f in range(nfiles):
				findx = file_trunc[f]
				# print(globalVars.home_dir + "/" + self.dirid + '/' + dirAlignment + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[indx], f+1))
				nxtFName = glob.glob(dirFits + '/ViSP_{}*_{}.fits'.format(self.dataIDLst[indx].split("-")[0], findx))[0]
				hdul = fits.open(nxtFName)   

				if (len(hdul[1].data) != len(initial[1].data)):
					waveAxisMod = np.min(np.array([len(hdul[1].data), len(initial[1].data)]))
					data_entry[f, 0:waveAxisMod, ...]  = hdul[0].data[0, 0:waveAxisMod, self.bbox[0]:self.bbox[1]+1, self.bbox[2]:self.bbox[3]+1]
					waveAxis_entry[f,0:waveAxisMod, ...] 	= hdul[1].data[0:waveAxisMod]
				else:
					data_entry[f, ...]  = hdul[0].data[0, :, self.bbox[0]:self.bbox[1]+1, self.bbox[2]:self.bbox[3]+1]
					waveAxis_entry[f, ...] 	= hdul[1].data

				hdul.close()
			data_entry = np.moveaxis(data_entry, 1, -1)		
			# I0_config = self.configs[indx].clusterConfig['intrinsic']

			# print(self.configs[indx].lines)
			# print(len(self.configs[indx].lines))

			line_config = self.configs[indx].lines


			# for l in range(len(self.lineSelect[self.dataIDLst[indx]])):
			if self.dataIDLst[indx] in list(self.lineSelect):
				linesLst 		= [line['label'] for line in line_config]
				linesSelectLst = [line for line in self.lineSelect[self.dataIDLst[indx]]]
				# print(line_config)
				for l in range(len(linesSelectLst)):
					# line_indx = linesLst.index(linesLst[q])
					# ii, jj = line_config[linesLst.index(linesSelectLst[l])]['window']
					# lineCore = line_config[linesLst.index(linesSelectLst[l])]['core']

					self.spectralParamsLst[self.dataIDLst[indx] + "_" + linesSelectLst[l]] = line_config[linesLst.index(linesSelectLst[l])]

			else:

				self.spectralParamsLst[self.dataIDLst[indx]] = self.configs[indx].lines
			print(self.dataIDLst[indx])

			self.dataLst.append(data_entry)
			self.waveAxisLst.append(waveAxis_entry*10)
		
		self.spaceInfo = {'rasterSize': self.dataLst[0].shape[1], 'alongSlitSize': self.dataLst[0].shape[2], 
						'pxlAlongSlit': spaceInfo['pxlAlongSlit']*nbins, 'pxlSlitWidth': spaceInfo['pxlSlitWidth']}	

		self.timeInfo  = {"maxRasters": nfiles, "stepCadence": 1.5, "scanCadence": 3.11*60}
		self.aspect 	= self.spaceInfo['pxlAlongSlit']/self.spaceInfo['pxlSlitWidth']


		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 

	def clustering(self):
		frameLst 	= []
		labelLst 	= []
		timeLst 	= []
		spectralLst = list(self.spectralParamsLst.keys())
		# print(spectralLst)
		# print(self.spectralParamsLst)
		for c in range(len(spectralLst)):
			indx = c
			dataID = spectralLst[c].split("_")[0]
			dataID_indx = self.dataIDLst.index(dataID)

			support, TarrSupport = [(dataID == self.events.runners.config['support']['src']), None]
			if support:
				TarrSupport = timeLst[0]

			__clusterLog__ = util.logg('start', val='{} | Support: {}'.format(spectralLst[c], support))

			# print(self.spectralParamsLst[spectralLst[c]])
			#if (x in  [0, -1, np.max(self.timeSeqLst)]) else 0
			clusterThis = (not support) * np.array([1 for x in self.timeSeqLst])
			print(clusterThis)
			s0s1_labels, frame_combine, time_dist = main(self.configs[dataID_indx], self.dataLst[dataID_indx], self.spectralParamsLst[spectralLst[c]], self.timeSeqLst, clusterThis, 
															support=support, TarrSupport=TarrSupport)
			util.logg('stop', _log=__clusterLog__)
			frameLst.append(frame_combine)
			labelLst.append(s0s1_labels)
			timeLst.append(time_dist)


		return(frameLst, labelLst, timeLst)
	
	def _labelFilter(self, labelLst, **kwargs):
		peakIntrinsicLabels = kwargs['base']
		print(np.where(peakIntrinsicLabels != 3))
		labelLst[0][self.dynamicIndx, np.where(peakIntrinsicLabels != 3)[0]] = np.nan




def _mainEvo(config, spectralData, spectralParams, tlst, clusterThis, support=False, TarrSupport=None):
	#for concat 
	ii, jj = 0, spectralData.shape[-1]
	iii, jjj = spectralParams['window']

	residual = config.residual

	labelFrame 		= np.zeros((len(tlst), spectralData.shape[1]*spectralData.shape[2])) + np.nan
	dataFrame 		= np.zeros((len(tlst) + int(residual), spectralData.shape[1]*spectralData.shape[2], spectralData.shape[-1])) 
	quiescentFrame 	= np.zeros((spectralData.shape[1]*spectralData.shape[2], spectralData.shape[3]))

	try:
		dataCube = spectralData.dataCube.reshape(spectralData.shape).astype(np.float32).compute()
	except AttributeError:
		dataCube = spectralData

	if support:
		dynamicScanNum = TarrSupport
		peakIntrinsicLabels = np.ones(spectralData.shape[1]*spectralData.shape[2])
	else:
		dynamicScanNum = dataCube[...,iii:jjj].sum(axis=-1).argmax(axis=0)

		layerOverride = None
		nbins = 1
		if 'layerConfig' in list(config.clusterConfig['intrinsic'][0].keys()):
			if 'bins' in list(config.clusterConfig['intrinsic'][0]['layerConfig'].keys()):
				layerOverride = np.array(config.clusterConfig['intrinsic'][0]['layerConfig']['bins']).astype(float)
				nbins = len(np.diff(layerOverride))

			if 'nbins' in list(config.clusterConfig['intrinsic'][0]['layerConfig'].keys()):
				nbins = int(config.clusterConfig['intrinsic'][0]['layerConfig']['nbins'])

		intrinsic_frame = EVcalc._calcDynamicFrame(dataCube, dynamicScanNum).reshape(dataFrame.shape[1:])
		s0_no_nan 	= analysis._runIntrinsic(nbins, 
									intrinsic_frame[:,iii:jjj].sum(axis=-1), 
									edgeOverride=layerOverride)
		peakIntrinsicLabels = s0_no_nan.astype(float)/3.0
				# print(np.unique(peakIntrinsicLabels))
		# print(np.where(peakIntrinsicLabels < 3))
		peakIntrinsicLabels[np.where(peakIntrinsicLabels < 1)] = np.nan


	if residual:
		__qsframeLog__ = util.logg("start", "Quiescent Frame Generated")
		with ProgressBar(total=int(dataCube.shape[1]*dataCube.shape[2]), ascii=False, leave=True, desc='Quiescent Frame', bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as qsProgress:	
			quiescentFrame = EVcalc._calcQuiescentFrame(dataCube, [jjj-iii+50, jjj-iii, jj], spectralParams['continuum'], progress=qsProgress)
			dataFrame[0, ...] = quiescentFrame
		util.logg("stop", _log=__qsframeLog__)

		# labelLst[0][self.dynamicIndx, np.where(peakIntrinsicLabels < peakIntrinsicLabels.max())[0]] = np.nan
	# Parameters used for SPD
	groups = [1, 5, 2, 4, 1]

	#groups = [3, 5]

	# groups = np.ones(len(tlst), dtype=int)
	# groups[np.where(tlst == 0)[0]] = 5
	for dt in range(len(tlst)):
		epochLabel 	= np.ones(labelFrame.shape[1]) * 111
		#__frameLog__ = util.logg("start", "{:+} Frame Generated".format(tlst[dt]))
		with ProgressBar(total=int(dataCube.shape[1]*dataCube.shape[2]), ascii=False, leave=True, desc='Epoch Frame {:+}'.format(tlst[dt]),
						bar_format='{desc}: {percentage:3.3f}%|{bar}| {n} [{elapsed}]') as epochProgress:	
			epochFrame 	= EVcalc._calcDynamicFrame(dataCube, dynamicScanNum, progress=epochProgress, delta=tlst[dt]).reshape(dataFrame.shape[1:]) 
		#util.logg("stop", _log=__frameLog__)
		if clusterThis[dt]:
			intrinsicPass = True
			if tlst[dt] != 0:
				intrinsicPass = False

			if groups[dt] > 1:
				util.logg("msg", "Time delta Runner (peak{:+})".format(tlst[dt]))
				epochLabel, sscore 	= analysis.main(config, epochFrame*peakIntrinsicLabels[:, None], [100, ii, jj], 
								quiescentFrame=quiescentFrame, intrinsicPass=intrinsicPass, optimalGroups=groups[dt])

		filter_indx = np.where(np.logical_not(np.isnan(epochFrame.sum(axis=-1))))[0]
		dataFrame[dt+int(residual), ...] 	= epochFrame
		labelFrame[dt, filter_indx] 		= epochLabel.reshape(labelFrame.shape[1:])[filter_indx]	
				
	return(labelFrame, dataFrame, dynamicScanNum)




