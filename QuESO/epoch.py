import QuESO.base as base
import QuESO.atoms.aux as auxAtom

class EpochDriven:
	def __init__(self, config, catalogName, instrumentObj):
		self.catalogBase = catalogName
		self.instrumentObj = instrumentObj

		self.figDir 	 = './fig/{}/'.format(self.catalogBase)
		self.qsBase 	= config.runners.qs_config + '-' + config.runners.config['aia']
		self.qsFigDir 	 = './fig/{}/'.format(self.qsBase) 
		os.makedirs(self.figDir, exist_ok=True)


		self.config = config 
		self.dirid = ''.join(config.date.split('-'))


		spectralConfig 		= self.config.srcLst.lines[0]
		self.spectralWindow = spectralConfig['window']
		self.lineCore 		= spectralConfig['core']
		self.continuum 		= spectralConfig['continuum']
		waveCoeff		= self.config.srcLst.waveCoeff

		self.waveFit = np.poly1d(waveCoeff)(np.arange(self.spectralData.shape[-1]))

	def __getattr__(self, name):
		parentLst = [self.config, self.instrumentObj]
		for p in parentLst:
			if hasattr(p, name):
				return getattr(p, name)
			else:
				continue
		raise AttributeError("No parents have object with attribute '%s'" % name)

	def clustering(self, prepSquare, fullFOVlabels=None):
		if fullFOVlabels is None:
			fullintrinsic = base._mainIntrinsic(self.config.srcLst, self.dataCube, True, np.arange(self.dataCube.shape[0]), 0)
			fullFOVlabels = auxAtom.pick_jth_label(fullintrinsic, 0).astype(int)
			
		labelLine, scoreTuple = base._mainOptimization(self.config.srcLst, prepSquare, fullFOVlabels)
		return(labelLine, scoreTuple)

	def delayAIA(self, fname):
		
		self.jq_delayFile = readsav(fname)

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

		self.aia_correct =  lambda x: x.reshape((295, 514)).T.reshape(514*295)

		jq_AIAMask 	= np.zeros(jq_AIAFrame.shape) + np.nan
		jq_indxMap 	= np.zeros(jq_AIAFrame.shape) + np.nan
		jq_AIABright = np.zeros(jq_AIAFrame.shape) + np.nan

		#print([0.01937, self.deltas['pxlAlongSlit']])
		#print([0.21420, self.deltas['pxlSlitWidth']])

		dy = 0.01937
		dx = 0.214167


		for i in range(len(jq_delayCube['arr'][:, 4])):
			xx = int(np.floor(jq_delayCube['arr'][int(i), 4]*dx*6))
			yy = int(np.floor(jq_delayCube['arr'][int(i), 5]*dy*6))

			if jq_delayCube['arr'][i, 7] > 0:
				jq_AIAFrame[xx, yy] = jq_delayCube['arr'][i, 3] - jq_delayCube['arr'][i, 7] 
				jq_AIAMask[xx, yy] = 1

				jq_AIABright[xx, yy] = jq_delayCube['arr'][i, 2]
			if jq_delayCube['arr'][i, 9] > 0:
				jq_AIAFrame[xx, yy] = jq_delayCube['arr'][i, 3] - jq_delayCube['arr'][i, 9]
				jq_AIAMask[xx, yy] = 1

				jq_AIABright[xx, yy] = jq_delayCube['arr'][i, 2]

			jq_indxMap[xx, yy] = i

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

			if ~(np.isnan(jq_AIAMask[xx, yy])):
				visp_jqMaskFrame[i] = jq_AIAMask[xx, yy]
				visp_aiaIndx[i] = jq_indxMap[xx, yy]
				visp_aiaBright[i] = jq_AIABright[xx, yy]
				visp_jqDelayFrame[i] = jq_AIAFrame[xx, yy]

		self.delayCube 	= self.correct(visp_jqDelayFrame)/60.
		self.aiaATvisp  = self.correct(visp_aiaBright)
		self.aiaIndxMap = self.correct(visp_aiaIndx)

		self.mask_map = np.zeros(self.delayCube.shape)
		self.mask_map[np.where(~np.isnan(self.delayCube))] = 1