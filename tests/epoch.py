#> file:  ./tests/ti
#> lang:  python
#> synopsis: 
#> author:   <>

import numpy as np

from queso_cluster import writer, ti
from queso_cluster.runners import base as runBase
from queso_cluster.addon import aia, prep
from queso_cluster.loaders.visp import visp
from queso_cluster.atoms import norm as normAtom
from queso_cluster.atoms import mask as maskAtom


import logging
logger = logging.getLogger("queso_cluster")
logging.basicConfig(format="!> [%(asctime)s]%(message)s", level=logging.INFO)

dkistDir = '/disk/data/DKIST/'


def main(config):
#> detail: 
#> param type config:
#> return (type): 
#> test-method:
	aiaUse = config.runners.config['aia']

	c = config.runners.label + '-' + aiaUse
	ViSPobj = visp(dkistDir + config.dirid + '/CSYRML/')
	ViSPobj.load()

	tiDev = ti.timeIndependent(config, c, ViSPobj)

	prepSquare = runBase.runPrep(tiDev.dataSquare,
									norm=normAtom.normContinuum, 
									continuumIndx=tiDev.continuum)
	#noMaskLabelLine, _ = tiDev.clustering(tiDev.dataSquare)#

	tiDev.maskLine = np.ones(prepSquare.shape[0]).astype(bool)
	if True:
		_, _, _, tiDev.maskLine = aia.delayAIA("/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(aiaUse), tiDev)

	labelLine, scoreTuple,  = tiDev.cluster(prepSquare, kLst=config.clusterConfig['optimized'])
	#writer.exportFITS(tiDev, labelLine, c)
	return(tiDev, labelLine)


def main_time(config):
	c = config.runners.label
	ViSPobj = visp(dkistDir + config.dirid + '/' + config.runners.config['src'] + '/')
	ViSPobj.load()

	tiDev = ti.timeIndependent(config, c, ViSPobj)
	startFrame = config.runners.config['timeFrames'][0]
	endFrame = config.runners.config['timeFrames'][1]

	tiDev.timeFrames = np.arange(startFrame, endFrame+1).astype(int)
	tiDev.dataSquare = ViSPobj.dataSquare[tiDev.timeFrames, ...].reshape((ViSPobj.dataSquare.shape[1]*tiDev.timeFrames.size, ViSPobj.shape[-1]))

	fig1 = prep.figureBackup01(tiDev)
	fig1.savefig("./intrinsicHist.png")


	if config.runners.overwrite:
		tiDev.prepSquare = runBase.runPrep(tiDev.dataSquare,
										norm=normAtom.normContinuum, 
										continuumIndx=tiDev.continuum)

		#> Note: Creates a mask for data within a specific coordinate range
		tiDev.maskLine = np.ones(tiDev.prepSquare.shape[0]).astype(bool)
		if 'bbox' in list(config.runners.config.keys()):
			tiDev.maskLine = maskAtom.maskCoordinate(config.runners.config['bbox'], (tiDev.timeFrames.size, tiDev.dimInfo['rasterSize'], tiDev.dimInfo['alongSlitSize']))

		#fig1 = prep.figureBackup01(tiDev, dataSquare=tiDev.dataSquare[tiDev.maskLine, :])
		#fig1.savefig("./intrinsicHist_flare.png")

		labelLine, scoreTuple  = tiDev.cluster(kLst=config.clusterConfig['optimized'])
		labelSquare = labelLine.reshape((tiDev.timeFrames.size, tiDev.dimInfo['rasterSize'], tiDev.dimInfo['alongSlitSize']))

		logger.info("Save start")
		np.savez("./{}.npz".format(c), labelSquare=labelSquare, maskLine=tiDev.maskLine, prepSquare=tiDev.prepSquare.compute())
		logger.info("Save end")
		
	return(tiDev)

if __name__ == '__main__':
	from queso_cluster.loaders.event import eventInput
	eventManager = eventInput("./eventManager.yml", eventIndx=2, runIndx=0)
	tiDev  = main_time(eventManager.event)

	from queso_cluster.addon import products
	p = products.Products(tiDev)
	#p.figure03()
	fig3a, fig3b = p.clusterMapSequence(timeAxis=False)
	fig3a.savefig("./figure03_sequence.png")
	fig3b.savefig("./figure03_compound.png")
	# #plt.close()

	fig4 = p.clusterProfiles()
	fig4.savefig("./clusterLabels.png")

