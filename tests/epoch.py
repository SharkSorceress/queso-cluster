#> file:  ./tests/ti
#> lang:  python
#> synopsis: 
#> author:   <>

import numpy as np

from queso_cluster import writer, ti
from queso_cluster import base as baseMain
from queso_cluster.addon import prep, aia
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
	#writer.dirCleanUp(config.directoryFlavor)

	aiaUse = config.runnerConfig['aia']

	ViSPobj = visp(dataDirectory=dkistDir + 
				config.directoryDate + '/' + config.datasetID + '/')

	tiDev = ti.timeIndependent(config, ViSPobj)
	tiDev.dataSquare = ViSPobj.dataPrism

	if config.overwrite:
		tiDev.prepSquare = baseMain.runPrep(tiDev.dataSquare, **config.normConfig)
		#noMaskLabelLine, _ = tiDev.clustering(tiDev.dataSquare)#

		fig_std = prep.profileVariation(tiDev)
		fig_std.savefig("./{}/profileVariation.png".format(config.directoryFlavor))

		tiDev.maskLine = np.ones(tiDev.prepSquare.shape[0]).astype(bool)
		if True:
			_, _, _, tiDev.maskLine = aia.delayAIA("/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(aiaUse), tiDev)

		if 'bbox' in list(config.runnerConfig.keys()):
			tiDev.maskLine = maskAtom.maskCoordinate(config.runnerConfig['bbox'], 
											(ViSPobj.dimInfo['rasterSize'], 
											ViSPobj.dimInfo['alongSlitSize']))

		fig = prep.intrinsicHistogram(tiDev, ["window", "continuum"])
		fig.savefig("./{}/histogram.png".format(config.directoryFlavor))

		labelLine = tiDev.cluster(kLst=config.clusterConfig['optimized'], 
									initialize=config.clusterConfig['prep']['initialize'])
		labelSquare = labelLine.reshape((ViSPobj.dimInfo['rasterSize'], 
									ViSPobj.dimInfo['alongSlitSize']))

		logger.info("Save start")
		np.savez("./{}/{}.npz".format(config.directoryFlavor, config.flavor), 
		   labelSquare=labelSquare, maskLine=tiDev.maskLine, 
		   prepSquare=tiDev.prepSquare.compute())
		logger.info("Save end")
	return(tiDev)


def main_time(config):
	ViSPobj = visp(dataDirectory=dkistDir + 
				config.directoryDate + '/' + config.datasetID + '/')

	tiDev = ti.timeIndependent(config, ViSPobj)
	tiDev.dataSquare = ViSPobj.dataPrism[config.timeFrames, ...].reshape((ViSPobj.dataPrism.shape[1]*config.timeFrames.size, 
																	   ViSPobj.dataPrism.shape[-1]))


	if config.overwrite:
		tiDev.prepSquare = baseMain.runPrep(tiDev.dataSquare, **config.normConfig)

		#> Note: Creates a mask for data within a specific coordinate range
		tiDev.maskLine = np.ones(tiDev.prepSquare.shape[0]).astype(bool)
		if 'bbox' in list(config.runnerConfig.keys()):
			tiDev.maskLine = maskAtom.maskCoordinate(config.runnerConfig['bbox'], 
											(config.timeFrames.size, 
											ViSPobj.dimInfo['rasterSize'], 
											ViSPobj.dimInfo['alongSlitSize']))
	
		fig = prep.intrinsicHistogram(tiDev, ["window", "continuum"])
		fig.savefig("./{}/histogram.png".format(config.directoryFlavor))


		labelLine = tiDev.cluster(kLst=config.clusterConfig['optimized'], 
									initialize=config.clusterConfig['prep']['initialize'])
		labelSquare = labelLine.reshape((config.timeFrames.size, 
								   ViSPobj.dimInfo['rasterSize'], 
								   ViSPobj.dimInfo['alongSlitSize']))

		logger.info("Save start")
		np.savez("./{}/{}.npz".format(config.directoryFlavor, config.flavor), 
		   labelSquare=labelSquare, maskLine=tiDev.maskLine, 
		   prepSquare=tiDev.prepSquare.compute())
		logger.info("Save end")
	return(tiDev)

if __name__ == '__main__':
	from queso_cluster.loaders.event import eventRunner
	eventManager = eventRunner("./eventManager_AH.yml", eventIndx=0, runIndx=0)
	tiDev = main_time(eventManager)

	from queso_cluster.addon import products
	p = products.Products(tiDev)
	# fig3a = p.clusterMapSequence(timeAxis=False)
	# fig3a.savefig("./{}/clusterSequence.png".format(tiDev._config.directoryFlavor))

	# fig3b = p.clusterMapSequence(timeAxis=False, intrinsic=True)
	# fig3b.savefig("./{}/intrinsicSequence.png".format(tiDev._config.directoryFlavor))

	# kwargDict = {"vmin": 0.2} #sets the minimum for the intensity
	# fig3c = p.intensityMapSequence(timeAxis=False, **kwargDict)
	# fig3c.savefig("./{}/intensitySequence.png".format(tiDev._config.directoryFlavor))

	# fig4 = p.clusterProfiles()
	# fig4.savefig("./{}/clusterLabels.png".format(tiDev._config.directoryFlavor))

	from queso_cluster.atoms import flare as flareAtom
	hiIntMask = flareAtom.kernelClusterMask(p.optLabels)

	compoundLabels = tiDev.clusterCompoundLabels(p.optLabels*hiIntMask)
	fig3c = p.clusterMapCompound(compoundLabels)
	fig3c.savefig("./{}/figure03_compound_peak.png".format(tiDev._config.directoryFlavor))

	p.clusterProfilesCompound(compoundLabels)

	# compoundLabels = tiDev.clusterCompoundLabels(p.optLabels)
	# fig3b = p.clusterMapCompound(compoundLabels)
	# fig3b.savefig("./{}/figure03_compound.png".format(tiDev._config.directoryFlavor))


