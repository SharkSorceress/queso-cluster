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
	ViSPobj = visp(dataDirectory=dkistDir + 
				config.directoryDate + '/' + config.datasetID + '/')

	tiDev = ti.timeIndependent(config, ViSPobj)
	tiDev.dataSquare = ViSPobj.dataPrism[config.timeFrames, ...].reshape((ViSPobj.dataPrism.shape[1]*config.timeFrames.size, ViSPobj.dataPrism.shape[-1]))

	if config.overwrite:
		tiDev.prepSquare = runBase.runPrep(tiDev.dataSquare,
										norm=normAtom.normContinuum, 
										continuumIndx=config.lineContinuum)

		#> Note: Creates a mask for data within a specific coordinate range
		tiDev.maskLine = np.ones(tiDev.prepSquare.shape[0]).astype(bool)
		if 'bbox' in list(config.runnerConfig.keys()):
			tiDev.maskLine = maskAtom.maskCoordinate(config.runnerConfig['bbox'], 
											(config.timeFrames.size, 
											ViSPobj.dimInfo['rasterSize'], 
											ViSPobj.dimInfo['alongSlitSize']))

		labelLine, scoreTuple = tiDev.cluster(kLst=config.clusterConfig['optimized'])
		labelSquare = labelLine.reshape((config.timeFrames.size, 
								   ViSPobj.dimInfo['rasterSize'], 
								   ViSPobj.dimInfo['alongSlitSize']))

		logger.info("Save start")
		np.savez("./{}.npz".format(config.flavor), labelSquare=labelSquare, maskLine=tiDev.maskLine, prepSquare=tiDev.prepSquare.compute())
		logger.info("Save end")
	return(tiDev)

if __name__ == '__main__':
	from queso_cluster.loaders.event import eventRunner
	eventManager = eventRunner("./eventManager.yml", eventIndx=2, runIndx=0)
	tiDev  = main_time(eventManager)

	geoLst = list(tiDev.geometry.keys())

	for g in range(len(geoLst)):
		print("{}: {}".format(geoLst[g], tiDev.geometry[geoLst[g]]))

	exit()


	print(tiDev._instrumentObj.dimInfo)

	from queso_cluster.addon import products
	p = products.Products(tiDev, eventManager)
	#p.figure03()
	fig3a = p.clusterMapSequence(timeAxis=False)
	fig3a.savefig("./figure03_sequence.png")

	fig4 = p.clusterProfiles()
	fig4.savefig("./clusterLabels.png")


	hiIntMask = np.zeros(p.optLabels.shape[1:])
	for t in range(p.optLabels.shape[0]):
		hiIntMask = np.logical_or(hiIntMask, p.optLabels[t, ...] == 311)

	hiIntMask = hiIntMask.astype(float)
	hiIntMask[hiIntMask == 0] = np.nan
	hiIntMask = np.broadcast_to(hiIntMask, p.optLabels.shape)

	compoundLabels = tiDev.clusterCompoundLabels(p.optLabels*hiIntMask)
	fig3c = p.clusterMapCompound(compoundLabels)
	fig3c.savefig("./figure03_compound_peak.png")

	p.clusterProfilesCompound(compoundLabels)

	compoundLabels = tiDev.clusterCompoundLabels(p.optLabels)
	fig3b = p.clusterMapCompound(compoundLabels)
	fig3b.savefig("./figure03_compound.png")

	# #plt.close()


