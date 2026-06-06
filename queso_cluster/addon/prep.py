import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from . import style as sty
def figureBackup01(analysisObj, dataSquare=None):
    ii, jj = [analysisObj.ii, analysisObj.jj]
    if dataSquare is None:
        dataSquare = analysisObj.dataSquare
    
    moment0_integrated = dataSquare[:, ii:jj+1].mean(axis=-1).compute()
    print(moment0_integrated.shape)
    moment0_continuum = dataSquare[:, analysisObj.continuum].compute()
    print(moment0_continuum.shape)

    i0_layerCount = len(analysisObj.clusterConfig['intrinsic'])

    fig = plt.figure(layout='constrained', figsize=(5*i0_layerCount, 5), dpi=300)

    moment0 = {'window': moment0_integrated, 'continuum': moment0_continuum}
    binWidth = {'window': 0.01, 'continuum': 0.01}

    for i in range(i0_layerCount):
        label = analysisObj.clusterConfig['intrinsic'][i]['label']
        bins  = analysisObj.clusterConfig['intrinsic'][i]['layerConfig']['bins']

        ax = fig.add_subplot(1, i0_layerCount, i+1)
        histBins = np.arange(0, np.ceil(np.nanmax(moment0[label])*10)/10, step=binWidth[label])
        ax.hist(moment0[label], bins=histBins, range=histBins, rwidth=1, fill=False, histtype='step', color='black')
        #_, color_pallet =  sty._genColorPallet(len(np.diff(bins)))

        #for j in range(len(bins)-2):
        #   ax.axvline(x = bins[j+1] , color=mpl.colors.rgb2hex(color_pallet[j+1]))


    return(fig)