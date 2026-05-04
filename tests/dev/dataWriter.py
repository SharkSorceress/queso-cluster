


def exportNetCDF(config, vispDataset, label_map, spectralParams):
	coreIndex, coreLabel = [None, '']
	if hasattr(config, 'manualOverride'):
		if 'coreOrder' in config.manualOverride.keys():
			coreOrder = config.manualOverride['coreOrder']
			coreLabel = '_' + list(coreOrder)[0]#.keys()
			coreIndex = coreOrder[list(coreOrder)[0]]  
	visp_id = config.data['id'] 
	data_id = visp_id + coreLabel

	alongSlitSize   = int(np.max(vispDataset.shape))
	maxRasters      = label_map.shape[0]#vispDataset.spaceInfo['maxRasters']
	rasterSize      = int((vispDataset.dataCube.shape[0] / alongSlitSize) / vispDataset.spaceInfo['maxRasters'])

	deltas = [vispDataset.spaceInfo['pxlSlitWidth'], 
			  vispDataset.spaceInfo['pxlAlongSlit']]
	aspect = deltas[1]/deltas[0]
	scales = [alongSlitSize, rasterSize, aspect]

	delta_time = 15.667

	# aia_lgt = readsav(globalVars.home_dir + '20221227/results/transformed_lgtcube_' + visp_id + '.sav')['transformed_lgtcube'].astype(np.int32)

	# aia_lgtcube, mask_map = epoch.transformed_lgtcube(aia_lgt, vispDataset.dataCube, scales, deltas)
	dirid   = ''.join(config.date.split('-'))
	fname = globalVars.home_dir + dirid + '/' + dirid + '_catalog/' + ''.join(config.date.split('-')) + '_catalog_test.nc'
	mode = 'r+'

	overwrite = True
	if overwrite:
		mode = 'w'
	dataFile = Dataset(fname, mode, format="NETCDF4")


	print(list(dataFile.groups.keys()))
	if 'DKIST-' + data_id not in list(dataFile.groups.keys()):
		print('check')

		print(data_id)
		sourceGroup 	= dataFile.createGroup('DKIST-' + data_id)

		if len(list(sourceGroup.dimensions.keys())) != 4:
			raster_dim 	= sourceGroup.createDimension("raster", rasterSize)
			slit_dim 	= sourceGroup.createDimension("slit", alongSlitSize)
			time_dim 	= sourceGroup.createDimension("time", maxRasters)
			wave_dim 	= sourceGroup.createDimension("wave", vispDataset.shape[-1])

		sourceGroup.instrument 	= "DKIST/ViSP"
		sourceGroup.wavelength 	= vispDataset.waveInfo['lineLabel']
		sourceGroup.dataID 		= data_id
		sourceGroup.version 	= '0'
		sourceGroup.spectralParams = spectralParams
		#ValueError: multi-dimensional array attributes not supported
		#print(extrema.shape)
		#sys.exit()
		#sourceGroup.extrema 	= extrema

		clusterGroup 	= sourceGroup.createGroup("catalog")
# 	epochGroup 		= dataFile.createGroup("epoch") 
# #	evolutionGroup	= dataFile.createGroup("evolution")

		raster 		= sourceGroup.createVariable("raster", np.uint, ('raster',))
		raster.units = "pixels"
		raster.long_name = "raster position"
		raster.delta = vispDataset.spaceInfo['pxlSlitWidth']
		raster[:] = np.arange(rasterSize)

		slit 		= sourceGroup.createVariable("slit", np.uint, ('slit', ))
		slit.units = "pixels"
		slit.long_name = "along slit position"
		slit.delta = vispDataset.spaceInfo['pxlAlongSlit'] 
		slit[:] = np.arange(alongSlitSize)

		time 		= sourceGroup.createVariable("time", np.uint, ('time', ))
		time.units = "seconds since reference"
		time.long_name = "time"
		time.reference = 0
		time.delta = delta_time
		time[:] = np.arange(maxRasters) * delta_time

		# clusterGroup.total = len(list(dict.fromkeys([tuple(x) for x in label_map[:,:]])))

		#layer_map = label_map[:, 0].copy()
		# max_layer = int(np.log10(layer_map[0]))+1

		labels 		= clusterGroup.createVariable("Catalog Label Layer", np.uint, ('time', 'raster', 'slit'))
		labels[...] =  label_map[0].reshape((maxRasters, rasterSize, alongSlitSize))


	# 	depth 		= sourceGroup.createDimension("odepth", label_map[1].shape[0])
	# 	labels 		= clusterGroup.createVariable("Optimization", np.uint,  ('odepth', 'time', 'raster', 'slit'))
	# # labels.mode = long_name[layer != 0]
	# 	print(label_map[1].shape)
	# 	for olayer in range(label_map[1].shape[0]):
	# 		labels[olayer,...] =  label_map[1][olayer, :].reshape((maxRasters, rasterSize, alongSlitSize))
		


			# layer_map 	-=  (np.floor(layer_map/(10**(max_layer - 1 - layer)))*10**(max_layer - 1 - layer)).astype(np.uint16)
			# layer += 1
		#print(label_map[2].shape)
		# depth 	= sourceGroup.createDimension("ddepth", label_map[1].shape[0])
		# labels 	= clusterGroup.createVariable("Discrimination", np.uint, ('ddepth', 'time', 'raster', 'slit'))
		# for dlayer in range(label_map[2].shape[0]):
		# 	labels[dlayer,...] =  label_map[2][dlayer, :].reshape((maxRasters, rasterSize, alongSlitSize))

		# test = clusterGroup.createVLType(np.int32, "extremaType")
		# exShape = extrema.shape
		# x = clusterGroup.createDimension("x", exShape[0])
		# y = clusterGroup.createDimension("y", exShape[1])
		# z = clusterGroup.createDimension("z", exShape[2])
		# minMax 		= clusterGroup.createVariable("extrema", np.float32, ('x', 'y', 'z'))
		# minMax[...] = extrema

# 	# print(dataFile.groups['catalog'])
# 	# print(dataFile.groups['catalog']['Lvl0'].mode)
# 	# print(dataFile.groups['catalog']['Lvl1'].mode)
# 	# print(dataFile.groups['catalog']['Lvl2'].mode)
# 	# print(dataFile.groups['catalog']['Lvl3'].mode)

# 	epochDelay = epochGroup.createVariable("epochDelay", np.float32, ('time', 'raster', 'slit'))
# 	epochDelay.units = 'seconds'
# 	epochDelay[...] = aia_lgtcube.reshape((maxRasters, rasterSize, alongSlitSize))

# 	flareMask = epochGroup.createVariable("flareMask", np.float32, ('time', 'raster', 'slit'))
# 	flareMask.source = 'AIA 1600'
# 	flareMask[...] = mask_map.reshape((maxRasters, rasterSize, alongSlitSize))



	# plt.figure()
	# map_test = dataFile.groups['DKIST-' + data_id].groups['catalog']['Lvl0'][0,...]*100 + dataFile.groups['DKIST-' + data_id].groups['catalog']['Lvl1'][0,...]*10 + dataFile.groups['DKIST-' + data_id].groups['catalog']['Lvl2'][0,...]

	# print(np.where((label_map[:,0].reshape((maxRasters, rasterSize, alongSlitSize))[0,...] - map_test).astype(int) != 0))
	# plt.imshow(map_test.T, aspect='auto', origin='lower')
	# plt.savefig('./fig/netcdf_layerTest1.png')

# 	import lib.dev.quiescent as qs
# 	qs_spectrum, contribution, waveFit = qs.quiescent() 

# 	wave = dataFile.createVariable("wave", np.float32, ('wave', ))
# 	wave.units = 'nanometers'
# 	wave.long_name = "corrected wavelength"
# 	wave[:] = waveFit

# 	quiescent = dataFile.createVariable("qs", np.float32, ('wave', ))
# 	quiescent.units = 'normalized intensity'
# 	quiescent.long_name = "quiescent spectrum estimate"
# 	quiescent[:] = qs_spectrum

	print(dataFile)
	print(dataFile.groups['DKIST-' + data_id])
	print(dataFile.groups['DKIST-' + data_id].groups['catalog'])

# 	# print(dataFile.groups['cluster'])
# 	# print(dataFile.groups['epoch'])
# 	# print(dataFile.variables)
# 	# print(dataFile.variables['raster'][...])
	dataFile.close()

