class EpochDriven:
	def __init__(self, config, catalogName):
		self.catalogBase = catalogName

		self.figDir 	 = './fig/{}/'.format(self.catalogBase)
		self.qsBase 	= config.runners.qs_config + '-' + config.runners.config['aia']
		self.qsFigDir 	 = './fig/{}/'.format(self.qsBase) 
		# os.removedirs(self.figDir)
		os.makedirs(self.figDir, exist_ok=True)


		self.config = config 
		self.dirid = ''.join(config.date.split('-'))
		# self.dataID, self.coreIndx = util._gen_dataID(config)
		self.visp_id = self.config.srcLst.id


		spectralConfig 		= self.config.srcLst.lines[0]
		self.spectralWindow = spectralConfig['window']
		self.lineCore 		= spectralConfig['core']
		self.continuum 		= spectralConfig['continuum']
		self.waveCoeff		= self.config.srcLst.waveCoeff

		#lineCore, ii, jj


		__loadLog__ = util.logg("start", val="Load")
		self.loadViSP()
		self.delayAIA()
	#		self.loadAIA()
		util.logg("stop", _log=__loadLog__)

	def loadViSP(self):
		self.spectralData = vispDataset(globalVars.dkist_dir + "/" + self.dirid + "/" + self.visp_id + "/")
		
		self.dataCube = self.spectralData.dataCube.compute()
		norm_func = lambda x: x/(x[:, int(self.continuum)])[:,None]
		self.normCube = da.blockwise(norm_func, 'ij', self.dataCube, 'ij', dtype=np.float32)


		alongSlitSize   = int(np.max(self.spectralData.shape))
		maxRasters      = self.spectralData.spaceInfo['maxRasters']
		rasterSize      = int((self.dataCube.shape[0] / alongSlitSize) / maxRasters)

		self.spaceInfo = {'alongSlitSize': alongSlitSize,
							'rasterSize': rasterSize,
							'maxRasters': maxRasters}

		self.deltas = {'pxlSlitWidth': self.spectralData.spaceInfo['pxlSlitWidth'],
						'pxlAlongSlit': self.spectralData.spaceInfo['pxlAlongSlit']}

		
		self.waveFit = np.poly1d(self.waveCoeff)(np.arange(self.spectralData.shape[-1]))

		print(self.waveFit[self.spectralWindow[0]:self.spectralWindow[1]+1] - self.waveFit[self.lineCore])
		print(self.waveFit[self.lineCore])
		# sys.exit()

		self.aspect = self.deltas['pxlAlongSlit']/self.deltas['pxlSlitWidth']

		self.correct = lambda x: x.reshape(self.spaceInfo['alongSlitSize'], self.spaceInfo['rasterSize']).T.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])

		self.correct_3d = lambda x,y: x.reshape(self.spaceInfo['alongSlitSize'], self.spaceInfo['rasterSize'], y).T.reshape((self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'], y))

		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 


	def clustering(self, frame, altLabels=None):
		if type(altLabels) == type(None):
		# 	return(analysis.main(self.config.srcLst, frame, [self.lineCore]+self.spectralWindow, intrinsicPass=False, altLabels=altLabels))
		# else:
			fullintrinsic = analysis._mainIntrinsic(self.config.srcLst, self.dataCube, True, np.arange(self.dataCube.shape[0]), 0)
			altLabels = _calc.pick_jth_label(fullintrinsic, 0).astype(int)
			
		labels, scores = analysis.main(self.config.srcLst, frame, [self.lineCore]+self.spectralWindow, intrinsicPass=False, altLabels=altLabels)

		return(altLabels, labels, scores)

	def _writeMask(self, labels, noMask_labels, mod=""):

		dataFile = Dataset(self.figDir + '/epochCCS_' + "_".join([x for x in [self.catalogBase, mod]]) + '.nc', 'w', format="NETCDF4")

		dataFile.createDimension("raster", self.spaceInfo['rasterSize'])
		dataFile.createDimension("slit", self.spaceInfo['alongSlitSize'])
		# dataFile.createDimension("label", len(scores[1]))


		raster 				= dataFile.createVariable("raster", np.uint, ('raster',))
		raster.units 		= "pixels"
		raster.long_name 	= "raster position"
		raster[:] 			= np.arange(self.spaceInfo['rasterSize'])

		slit 				= dataFile.createVariable("slit", np.uint, ('slit', ))
		slit.units 			= "pixels"
		slit.long_name 		= "along slit position"
		slit[:] 			= np.arange(self.spaceInfo['alongSlitSize'])

		labelMap 			= dataFile.createVariable("labelMap", int, ('raster', 'slit'))
		labelMap[...] 		= self.unflatten(labels)

		noMaskMap 			= dataFile.createVariable("noMask_labels", int, ('raster', 'slit'))
		noMaskMap[...]		= self.unflatten(noMask_labels)

		delayMap 			= dataFile.createVariable("delayMap", float, ('raster', 'slit'))
		delayMap[...] 		= self.unflatten(self.delayCube)

		# scoreArr			= dataFile.createVariable("scoreArr", float, ('label', ))
		# scoreArr[:]			= scores[1]

		# labelArr			= dataFile.createVariable("labelArr", float, ('label', ))
		# labelArr[:]			= scores[0]

		dataFile.close()

	def _sortFile(self, labels):

	#		file2jq = Dataset(self.figDir + '/profiles_2025oct20.nc', 'w', format="NETCDF4")


	#	noMask_labels = dataFile.variables['noMask_labels'][...].data.astype(float)
	#	labels = dataFile.variables['labelMap'][...].data.astype(float)
	#	sscores = dataFile.variables['scoreArr'][...].data.astype(float)

		ii, jj = self.spectralWindow

		lmap = self.flatten(labels)
		valid_indx = np.where(lmap > 0)[0]
		labelMap = lmap[valid_indx]

		# file2jq.createDimension("wave", jj - ii + 1)
		# file2jq.createDimension("label", len(np.unique(labelMap)))

		# wavelength 			= file2jq.createVariable("wavelength", np.float64, ('wave', ))
		# wavelength[:] 		= self.waveFit[ii:jj+1]


		# profile				= file2jq.createVariable("profile", np.float64, ('label', 'wave', ))
		# profileLabel		= file2jq.createVariable("label", np.uint, ('label', ))
		# profileVelo			= file2jq.createVariable("velocity", np.float64, ('label', ))


		sortedLabel = np.zeros(lmap.shape) + np.nan
		i0Lst = np.unique(_calc.pick_jth_label(labelMap, 0))
		label_counter = 0
		for i0 in range(len(i0Lst)):
			i0indx = np.where(_calc.pick_jth_label(labelMap, 0) == i0Lst[i0])[0]
			o1Lst = np.unique(_calc.pick_jth_label(labelMap[i0indx], 1))
			sortedLst_o1 = [[], []]
			for o1 in range(len(o1Lst)):
				o1indx = i0indx[np.where(_calc.pick_jth_label(labelMap[i0indx], 1) == o1Lst[o1])[0]]
				o1_centroid = self.normCube[valid_indx[o1indx], ii:jj+1].sum(axis=0)/len(o1indx)

				# tmp_thing = _calc.pick_jth_label(labelMap[o1indx[0]], 0)*10 + _calc.pick_jth_label(labelMap[o1indx[0]], 1)

				sortedLst_o1[0].append(int(str(labelMap[o1indx[0]])[0:2]))
				sortedLst_o1[1].append(o1_centroid.sum().compute())

			sorted_indx_o1 = np.argsort(np.array(sortedLst_o1[1])).astype(int)[::-1]
			o1Lst = np.array(sortedLst_o1[0])[sorted_indx_o1]
			for s1 in range(len(sorted_indx_o1)):
				# s1indx = valid_indx[o1indx[np.where(labelMap[o1indx] == sortedLst_o2[0][sorted_indx[s2]])[0]]]

				tmp_thing = _calc.pick_jth_label(labelMap[i0indx], 0)*10 + _calc.pick_jth_label(labelMap[i0indx], 1)

				o1indx = i0indx[np.where(tmp_thing == o1Lst[s1])[0]]
				#o1Lst[o1])[0]]
				o1_centroid = self.normCube[valid_indx[o1indx], ii:jj+1].sum(axis=0)/len(o1indx)

				# sortedLst_o1[0].append(np.unique(labelMap[o1indx[0]]))
				# sortedLst_o1[1].append(o1_centroid.sum().compute())

				sortedLst_o2 = [[], []]
				o2Lst = np.unique(_calc.pick_jth_label(labelMap[o1indx], 2))
				for o2 in range(len(o2Lst)):
					o2indx = o1indx[np.where(_calc.pick_jth_label(labelMap[o1indx], 2) == o2Lst[o2])[0]]
					o2_centroid = self.normCube[valid_indx[o2indx], ii:jj+1].sum(axis=0)/len(o2indx)

					# print([labelMap[o2indx[0]], o2_centroid.sum().compute()], o2_centroid.max().compute())
					sortedLst_o2[0].append(labelMap[o2indx[0]])
					sortedLst_o2[1].append(o2_centroid.sum().compute())

			
				sorted_indx = np.argsort(np.array(sortedLst_o2[1])).astype(int)[::-1]
				for s2 in range(len(sorted_indx)):
					s2indx = valid_indx[o1indx[np.where(labelMap[o1indx] == sortedLst_o2[0][sorted_indx[s2]])[0]]]
					sortedLabel[s2indx] = int(i0Lst[i0]*100 + (s1 + 1)*10 + (s2 + 1))

					s2_centroid = (self.normCube[s2indx, ii:jj+1].sum(axis=0)/len(s2indx)).compute()
					#					print([sortedLst_o2[0][sorted_indx[s2]], int(i0Lst[i0]*100 + (s1 + 1)*10 + (s2 + 1)), s2_centroid.sum()])


					#profile[label_counter, :] = s2_centroid
					#profileLabel[label_counter] = sortedLabel[s2indx[0]]
					#profileVelo[label_counter] = (3e5/(self.waveFit[self.lineCore])) * np.sum(s2_centroid * (self.waveFit[ii:jj+1] - self.waveFit[self.lineCore])) / s2_centroid.sum()			
					label_counter += 1


			#				print(np.array(sortedLst_o2[0])[np.argsort(np.array(sortedLst_o2[1])).astype(int)[::-1]])

			# print(np.argsort(np.array(sortedLst_o1[1])).astype(int)[::-1])
			# print(np.array(sortedLst_o1[0])[np.argsort(np.array(sortedLst_o1[1])).astype(int)[::-1]])
			# print(np.sort(np.array(sortedLst[1])))					
		#file2jq.close()
		return(sortedLabel)


		# dataFile = Dataset(self.figDir + '/epochCCS_' + self.catalogBase + '_sorted.nc', 'w', format="NETCDF4")

		# dataFile.createDimension("raster", self.spaceInfo['rasterSize'])
		# dataFile.createDimension("slit", self.spaceInfo['alongSlitSize'])
		# dataFile.createDimension("label", len(sscores[1]))


		# raster 				= dataFile.createVariable("raster", np.uint, ('raster',))
		# raster.units 		= "pixels"
		# raster.long_name 	= "raster position"
		# raster[:] 			= np.arange(self.spaceInfo['rasterSize'])

		# slit 				= dataFile.createVariable("slit", np.uint, ('slit', ))
		# slit.units 			= "pixels"
		# slit.long_name 		= "along slit position"
		# slit[:] 			= np.arange(self.spaceInfo['alongSlitSize'])

		# labelMap 			= dataFile.createVariable("labelMap", int, ('raster', 'slit'))
		# labelMap[...] 		= self.unflatten(labels)

		# noMaskMap 			= dataFile.createVariable("noMask_labels", int, ('raster', 'slit'))
		# noMaskMap[...]		= self.unflatten(noMask_labels)

		# delayMap 			= dataFile.createVariable("delayMap", float, ('raster', 'slit'))
		# delayMap[...] 		= self.unflatten(self.delayCube)

		# scoreArr			= dataFile.createVariable("scoreArr", float, ('label', ))
		# scoreArr[:]			= sscores[1]



	def prep(self):
		__prepLog__ = util.logg("start", val="Preparations")
		prepped_frame 	= np.zeros(self.spectralData.shape[1:])
		mask_map = self.unflatten(self.mask_map)
		#self.unflatten(self.correct(self.mask_map))#self.unflatten(self.mask_map)

		expanded_dataCube = self.dataCube.reshape(self.spectralData.shape[1:])
		if self.config.runners.config['useMask']:	
			for x in range(self.spaceInfo['rasterSize']):
				for y in range(self.spaceInfo['alongSlitSize']):
					if mask_map[x, y]:
						prepped_frame[x, y, :] = expanded_dataCube[x, y, :]
					else:
						prepped_frame[x, y, :] = np.nan
	
		else:
			for x in range(self.spaceInfo['rasterSize']):
				for y in range(self.spaceInfo['alongSlitSize']):			
					prepped_frame[x, y, :] = expanded_dataCube[x, y, :]

		util.logg("stop", _log=__prepLog__)
		return(prepped_frame)

	def delayAIA(self):
		# aiaCube = readsav(globalVars.home_dir + self.dirid + '/results/transformed_lgtcube_' + self.visp_id + '.sav')['transformed_lgtcube'].astype(np.int32)

		# visp_aia = readsav("/disk/data/sriley/20221227/mask_map_2025feb24.sav")
		# mask_map = visp_aia['mask_map']['data'][0]

		# dataCube_delay  = np.zeros(self.dataCube.shape[0]) + np.nan
		# aiaPeak  		= np.zeros(self.dataCube.shape[0]) + np.nan
		# vispAIAindx 	= np.zeros((self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize'])) + np.nan


		jq_delayCube = readsav("/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(self.config.runners.config['aia']))
		self.jq_delayFile = jq_delayCube

		#jq_delayCube['arr'][0] --> background of pixel
		#jq_delayCube['arr'][1] --> background noise of pixel (standard deviation)
		#jq_delayCube['arr'][2] --> AIA brightness at ViSP slit time
		#jq_delayCube['arr'][3] --> time of the ViSP slit
		#jq_delayCube['arr'][4] --> xpos
		#jq_delayCube['arr'][5] --> ypos
		#jq_delayCube['arr'][6] --> brightness of peak (before ViSP time)
		#jq_delayCube['arr'][7] --> time of peak before ViSP time
		#jq_delayCube['arr'][8] --> brightness of peak (after ViSP time)
		#jq_delayCube['arr'][9] --> time of peak after ViSP time


		jq_AIAFrame = np.zeros((514, 295)) + np.nan
		momentFrame = np.zeros(len(jq_delayCube['arr'][:, 4])) + np.nan

		moment_compare = self.unflatten(self.dataCube[:, self.spectralWindow[0]:self.spectralWindow[1]].sum(axis=-1))

		# for i in range(10):
		# 	print([i, jq_delayCube['arr'][:, i].max(), jq_delayCube['arr'][:, i].min()])
	
		self.aia_correct =  lambda x: x.reshape((295, 514)).T.reshape(514*295)

	#		counter = 0
		jq_AIAMask 	= np.zeros(jq_AIAFrame.shape) + np.nan
		jq_indxMap 	= np.zeros(jq_AIAFrame.shape) + np.nan
		jq_AIABright = np.zeros(jq_AIAFrame.shape) + np.nan

		print([0.01937, self.deltas['pxlAlongSlit']])
		print([0.21420, self.deltas['pxlSlitWidth']])

		dy = 0.01937
		dx = 0.214167


		for i in range(len(jq_delayCube['arr'][:, 4])):
			xx = int(np.floor(jq_delayCube['arr'][int(i), 4]*dx*6))
			yy = int(np.floor(jq_delayCube['arr'][int(i), 5]*dy*6))

			# xx1 = xx+1 #int(np.ceil(int(jq_delayCube['arr'][int(i), 4])*self.deltas['pxlSlitWidth']*6))+1
			# yy1 = yy+1 #int(np.ceil(int(jq_delayCube['arr'][int(i), 5])*self.deltas['pxlAlongSlit']*6))+1


			if jq_delayCube['arr'][i, 7] > 0:
				jq_AIAFrame[xx, yy] = jq_delayCube['arr'][i, 3] - jq_delayCube['arr'][i, 7] 
				jq_AIAMask[xx, yy] = 1

				jq_AIABright[xx, yy] = jq_delayCube['arr'][i, 2]
	#				jq_AIAMask[xx+1, yy] = 1
			
			if jq_delayCube['arr'][i, 9] > 0:
				jq_AIAFrame[xx, yy] = jq_delayCube['arr'][i, 3] - jq_delayCube['arr'][i, 9]
				jq_AIAMask[xx, yy] = 1

				jq_AIABright[xx, yy] = jq_delayCube['arr'][i, 2]


			# if jq_delayCube['arr'][i, 9] > 0 and jq_delayCube['arr'][i, 7] > 0:
			# 	print([jq_delayCube['arr'][i, 3] - jq_delayCube['arr'][i, 9], jq_delayCube['arr'][i, 3] - jq_delayCube['arr'][i, 7]])
				# jq_AIAMask[xx, yy] = np.nan
				# jq_AIAFrame[xx, yy] = np.nan
	#				jq_AIAMask[xx+1, yy] = 1
			# else:
			# 	jq_AIAMask[xx, yy] = np.nan



			jq_indxMap[xx, yy] = i
	#			jq_AIALgt[xx, yy, :] = jq_delayCube['nuvlgt'][:, i]

			momentFrame[int(i)] = moment_compare[int(jq_delayCube['arr'][int(i), 4]), int(jq_delayCube['arr'][int(i), 5])]




		self.aia_mask_raw = jq_AIAMask

		visp_jqDelayFrame = np.zeros(self.dataCube.shape[0]) + np.nan
		visp_jqMaskFrame = np.zeros(self.dataCube.shape[0]) + np.nan
		visp_aiaIndx 		= np.zeros(self.dataCube.shape[0]) + np.nan
		visp_aiaBright 		= np.zeros(self.dataCube.shape[0]) + np.nan
		# visp_aialgt 	= np.zeros((self.dataCube.shape[0], jq_delayCube['nuvlgt'].shape[0])) + np.nan
		for i in range(self.dataCube.shape[0]):
			yy = int(np.floor((i / self.spaceInfo['rasterSize'])*dy*6))
			xx = int(np.floor(np.mod(i, self.spaceInfo['rasterSize'])*dx*6))
	#			indx = int(np.floor(np.mod(i, self.spaceInfo['rasterSize'])))

			if ~(np.isnan(jq_AIAMask[xx, yy])):
				visp_jqMaskFrame[i] = jq_AIAMask[xx, yy]

	#			if ~(np.isnan(jq_indxMap[xx, yy])):
				visp_aiaIndx[i] = jq_indxMap[xx, yy]

				visp_aiaBright[i] = jq_AIABright[xx, yy]
			# 	visp_aialgt[i, :] 		= jq_AIALgt[xx, yy, :]

			# if ~(np.isnan(jq_ViSPTime[xx, yy])):
			# 	visp_time[i] = jq_ViSPTime[xx, yy]

	#			if ~(np.isnan(jq_AIAFrame[xx, yy])):
				visp_jqDelayFrame[i] = jq_AIAFrame[xx, yy]

		# corrected_jqFrame = self.unflatten(self.correct(jq_AIAFrame))

		# print([counter, np.nanmin(jq_AIAFrame), np.nanmax(jq_AIAFrame), np.nanmedian(jq_AIAFrame)])

	#		fig = plt.figure(layout='constrained', figsize=(5, 5))
		# ax = fig.add_subplot(121)

		# vmax = np.ceil(np.nanmax(visp_jqDelayFrame/60))

		# im = ax.imshow((self.unflatten(self.correct(visp_jqDelayFrame))/60.).T, aspect=self.aspect, origin='lower', cmap='bwr', vmin=-vmax, vmax=vmax)
		# fig.colorbar(im, ax=ax, orientation='horizontal')

		# ax.set_ylim([jq_delayCube['arr'][:, 5].min(), jq_delayCube['arr'][:, 5].max()])
		# ax.set_xlim([jq_delayCube['arr'][:, 4].min(), jq_delayCube['arr'][:, 4].max()])


		# ax2 = fig.add_subplot(111)
		# ax2.scatter(jq_delayCube['arr'][:, 2], momentFrame)
		# ax2.set_ylabel("Window integrated ViSP Intensity")
		# ax2.set_xlabel("AIA Brightness at ViSP Time")

		# fig.savefig('./fig/jq_delayTest.png')

	#		self.aiaLgt 	= visp_aialgt
		self.delayCube 	= self.correct(visp_jqDelayFrame)/60.
		self.aiaATvisp  = self.correct(visp_aiaBright)
	#		self.vispTim 	= self.correct(visp_time)
		self.aiaIndxMap = self.correct(visp_aiaIndx)

		self.mask_map = np.zeros(self.delayCube.shape)
		self.mask_map[np.where(~np.isnan(self.delayCube))] = 1

		# fig = plt.figure(layout='constrained', figsize=(10, 5), dpi=300)
		# ax1 = fig.add_subplot(111)
		# # vispAIAindx = vispAIAindx.reshape(alongSlitSize, rasterSize).T.reshape(rasterSize*alongSlitSize)

		# im = ax1.imshow(vispAIAindx.T, cmap='Greys_r', origin='lower', aspect=self.aspect)
		# fig.colorbar(im, ax=ax1)
		# fig.savefig('./fig/vispAIAraster.png')


		# fig = plt.figure(layout='constrained', figsize=(10,15), dpi=300)

		# ax3 = fig.add_subplot(313)
		# im = ax3.imshow(self.unflatten(dataCube_delay).T, cmap='rainbow',
		# 		aspect=self.aspect, origin='lower')
		# fig.colorbar(im, ax=ax3)

		# decay_map = self.delayCube.copy()
		# decay_map[decay_map <= 0] = np.nan

		# rise_map = self.delayCube.copy()
		# rise_map[rise_map > 0] = np.nan 


		# ax1 = fig.add_subplot(311)
		# decay_cmap = LinearSegmentedColormap.from_list('', ['#FF0000', '#000000'])
		# decay_cmap.set_bad("#FFFFFF")

		# im = ax1.imshow(self.unflatten(decay_map).T, cmap=decay_cmap,
		# 		aspect=self.aspect, origin='lower')
		# fig.colorbar(im, ax=ax1)

		# rise_cmap = LinearSegmentedColormap.from_list('', ['#000000', '#0000FF'])
		# rise_cmap.set_bad("#FFFFFF")

		# ax1 = fig.add_subplot(312)
		# im = ax1.imshow(self.unflatten(rise_map).T, cmap=rise_cmap,
		# 		aspect=self.aspect, origin='lower')
		# fig.colorbar(im, ax=ax1)

		# fig.savefig('./fig/delayTesting.png')
		# sys.exit()
		# return([dataCube_delay, raw_mask])
