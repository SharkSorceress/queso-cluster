import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from . import style as sty
def figureBackup01(analysisObj, mode, dataSquare=None, mask=True):
	
	if dataSquare is None:
		dataSquare = analysisObj.dataSquare

	moment0Lst = []

	if type(mode) == str:
		mode = [mode]

	for m in range(len(mode)):
		match mode[m]:
			case 'continuum':
				dataLine = dataSquare[:, analysisObj._config.lineContinuum]
				if mask:
					dataLine *= analysisObj.maskLine
				moment0Lst.append(dataLine.compute())
			case 'window':
				ii, jj = [analysisObj._config.blueEdge, analysisObj._config.redEdge]
				dataLine = dataSquare[:, ii:jj+1].mean(axis=-1)
				if mask:
					dataLine *= analysisObj.maskLine
				moment0Lst.append(dataLine.compute())



	#i0_layerCount = len(analysisObj._config.clusterConfig['intrinsic'])

	fig = plt.figure(layout='constrained', figsize=(5*len(mode), 5), dpi=300)

	#moment0 = {'window': moment0_integrated, 'continuum': moment0_continuum}
	#binWidth = {'window': 0.01, 'continuum': 0.01}

	for i in range(len(mode)):
		#label = analysisObj._config.clusterConfig['intrinsic'][i]['label']
		#bins  = analysisObj._config.clusterConfig['intrinsic'][i]['layerConfig']['bins']

		ax = fig.add_subplot(1, len(mode), i+1)
		histBins = np.arange(0, np.ceil(np.nanmax(moment0Lst[i])*10)/10, step=0.01)
		ax.hist(moment0Lst[i][moment0Lst[i] > 0], bins=histBins, range=histBins, rwidth=1, fill=False, histtype='step', color='black')
		#_, color_pallet =  sty._genColorPallet(len(np.diff(bins)))

		# for j in range(len(bins)-2):
		# 	ax.axvline(x = bins[j+1], color='red') 
		ax.set_title(mode[i])
		#ax.set_yscale("log")


		ax.annotate("Min={:.3f}".format(float(np.nanmin(moment0Lst[i]))),
            		xy=(0.01, 1-0.1), xycoords='axes fraction',
					xytext=(0.01, 1-0.1), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')	
		
		ax.annotate("Max={:.3f}".format(float(np.nanmax(moment0Lst[i]))),
            		xy=(0.01, 1-0.15), xycoords='axes fraction',
					xytext=(0.01, 1-0.15), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')	
				   #color=mpl.colors.rgb2hex(color_pallet[j+1]))
		ax.set_xlim([np.nanmin(moment0Lst[i][moment0Lst[i] > 0]), np.nanmax(moment0Lst[i][moment0Lst[i] > 0])])
	return(fig)