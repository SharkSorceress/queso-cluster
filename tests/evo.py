#> file:  ./tests/evo
#> lang:  python
#> synopsis: 
#> author:   <>
from queso_cluster import base, approach, base, loader
from queso_cluster import writer
from queso_cluster.atoms import aux as auxAtom
from queso_cluster.runners import base as runBase

import numpy as np

def main(config):
#> detail: 
#> param type config:
#> return (type): 
#> test-method:


	srcUse = config.runners.config['primary']['src']
	srcConfigPrimary 	= config.srcLst[config.srcLabelLst.index(srcUse)]

	# srcUse = config.runners.config['support']['src']
	# srcConfigSecondary 	= config.srcLst[config.srcLabelLst.index(srcUse)]

	config.srcLst = srcConfigPrimary
	# config.srcLst = [srcConfigPrimary, srcConfigSecondary]
#	catalogName = 'alt'

	ViSPobj = loader.instrument('/disk/data/DKIST/20230503/AEVEG/')
	ViSPobj.vispLoad()

	#config.runners.alignmentDir
	#print(config.srcLst)
	evoDev = approach.timeDependent(config, config.runners.label, ViSPobj)
	# if not config.runners.overwrite:
	# 	frameLst, _, timeLst = evoDev.clustering()
	# 	try:
	# 		dataFile = Dataset(evoDev.figDir + '/evoCCS_{}_sorted.nc'.format(config.runners.label), 'r', format="NETCDF4")	
	# 	except FileNotFoundError:
	# 		dataFile = Dataset(evoDev.figDir + '/evoCCS_{}.nc'.format(config.runners.label), 'r', format="NETCDF4")	

	# 	labelEntry = np.zeros((5, 125*89))
	# 	for t in range(5):
	# 		print(dataFile.variables['labels_full'][t, ...].data.shape)
	# 		labelEntry[t, :] = dataFile.variables['labels_full'][t, ...].data.astype(float).reshape(125*89)

	# 	labelLst = [labelEntry]
	# else:
	timeFrames, tLst = evoDev.timeFrames(peakTime=2, nframes=4)
	
	keepI0 = None
	if "keepI0" in list(config.runners.config.keys()):
		keepI0 = config.runners.config['keepI0']


	intrinsicLine = base._mainIntrinsic(config.srcLst, 
										np.floor(evoDev.dataSquare[tLst[1], ...]*100)/100., 0, intrinsicSkip=False)
	intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)

	klst = config.runners.config['primary']['S1']
	for t in range(timeFrames.shape[0]):
		prepSquare = runBase.runPrep(timeFrames[t,...], norm='continuum', continuumIndx=evoDev.continuum)
		print(prepSquare.shape)
		maskLine = np.ones(prepSquare.shape[0]).astype(bool)
		print(maskLine.shape)
		print(intrinsicLine.shape)
		if not (keepI0 is None):
			i0Mask = np.zeros(prepSquare.shape[0], dtype=bool)
			for i in keepI0:
				#print(np.unique(intrinsicLine[(intrinsicLine == i)]))
				#print(np.unique(intrinsicLine[(intrinsicLine == i)*maskLine]))
				i0Mask[(intrinsicLine == i)] = 1
			maskLine *= i0Mask

		print(maskLine.shape)
		
		frameLst, labelLst = evoDev.clusterPerFrame(prepSquare, maskLine, kLst=[klst[t]], intrinsicLine=intrinsicLine)
	
	return(evoDev, labelLst)



if __name__ == '__main__':
	#from paper02 import paper02_products
	quesoInstance = loader.QuESO("/disk/data/DKIST/" ,
							 	"/disk/data/sriley/",
							 	"./dev/fig/")
	
	eventManager = quesoInstance._loadEventConfig("./eventRunners.yml", event=1, runner=2)

	evoDev, labelLine = main(eventManager.event)
	#p02 = paper02.paper02_products(evoDev, labelLst, frameLst)
	#p02.run()