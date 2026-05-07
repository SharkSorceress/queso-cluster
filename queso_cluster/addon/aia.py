#> file:  ./QuESO/addon/aia
#> lang:  python
#> synopsis: 
#> author:   <>

from scipy.io import readsav
import numpy as np

from .logg import loggTimer


@loggTimer
def delayAIA(fname, epochDev):
#> detail: 
#> param type fname:
#> param type epochDev:
#> return (type): 
#> test-method:
	
	eD = epochDev

	jq_delayCube = readsav(fname)

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

	moment_compare = eD.dataSquare[:, eD.spectralWindow[0]:eD.spectralWindow[1]].mean(axis=-1).reshape(eD.shape[0], eD.shape[1])

	#aia_correct =  lambda x: x.reshape((295, 514)).T.reshape(514*295)
	correct = lambda x: x.reshape(eD.shape[1], eD.shape[0]).T.reshape(eD.shape[0]*eD.shape[1])

	jq_AIAMask 	= np.zeros(jq_AIAFrame.shape) + np.nan
	jq_indxMap 	= np.zeros(jq_AIAFrame.shape) + np.nan
	jq_AIABright = np.zeros(jq_AIAFrame.shape) + np.nan

	#print([0.01937, eD.deltas['pxlAlongSlit']])
	#print([0.21420, eD.deltas['pxlSlitWidth']])

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

	aia_mask_raw = jq_AIAMask

	visp_jqDelayFrame = np.zeros(eD.dataSquare.shape[0]) + np.nan
	visp_jqMaskFrame = np.zeros(eD.dataSquare.shape[0]) + np.nan
	visp_aiaIndx 		= np.zeros(eD.dataSquare.shape[0]) + np.nan
	visp_aiaBright 		= np.zeros(eD.dataSquare.shape[0]) + np.nan
	# visp_aialgt 	= np.zeros((eD.dataCube.shape[0], jq_delayCube['nuvlgt'].shape[0])) + np.nan
	for i in range(eD.dataCube.shape[0]):
		yy = int(np.floor((i / eD.shape[0])*dy*6))
		xx = int(np.floor(np.mod(i, eD.shape[0])*dx*6))

		if ~(np.isnan(jq_AIAMask[xx, yy])):
			visp_jqMaskFrame[i] = jq_AIAMask[xx, yy]
			visp_aiaIndx[i] = jq_indxMap[xx, yy]
			visp_aiaBright[i] = jq_AIABright[xx, yy]
			visp_jqDelayFrame[i] = jq_AIAFrame[xx, yy]

	delayCube 	= correct(visp_jqDelayFrame)/60.
	aiaATvisp  = correct(visp_aiaBright)
	aiaIndxMap = correct(visp_aiaIndx)

	mask_map = np.zeros(delayCube.shape, dtype=bool)
	mask_map[np.where(~np.isnan(delayCube))] = True

	print(mask_map.shape)


	return(delayCube, aiaATvisp, aiaIndxMap, mask_map)