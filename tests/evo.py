#> file:  ./tests/evo
#> lang:  python
#> synopsis: 
#> author:   <>
from queso_cluster import base, writer, td
from queso_cluster.atoms import aux as auxAtom
from queso_cluster.atoms import norm as normAtom
from queso_cluster.runners import base as runBase
from queso_cluster.loaders.visp import visp

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

	ViSPobj = visp('/disk/data/DKIST/20230503/AEVEG/')
	ViSPobj.load()

	#config.runners.alignmentDir
	#print(config.srcLst)
	evoDev = approach.timeDependent(config, config.runners.label, ViSPobj)
	bboxMask = np.zeros((evoDev.rasterSize, evoDev.alongSlitSize))


	bEx = config.runners.config['bbox']
	bboxMask[bEx[0]:bEx[1], bEx[2]:bEx[3]] = 1

	bboxMask = bboxMask.reshape(bboxMask.shape[0]*bboxMask.shape[1])

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
										np.floor(timeFrames[1, ...]*100)/100., 0, intrinsicSkip=False)
	intrinsicLine = auxAtom.pick_jth_label(intrinsicLine, 0).astype(int)

	maskLine = bboxMask.astype(bool)#np.ones(prepSquare.shape[0]).astype(bool)
	if not (keepI0 is None):
		i0Mask = np.zeros(timeFrames.shape[1], dtype=bool)
		print(i0Mask.shape)
		for i in keepI0:
			i0Mask[(intrinsicLine == i)] = 1
		maskLine *= i0Mask

	print(np.unique(intrinsicLine))

	klst = config.runners.config['primary']['S1']
	labelSquare = np.zeros((timeFrames.shape[0], timeFrames.shape[1]))
	for t in range(timeFrames.shape[0]):
		prepSquare = runBase.runPrep(timeFrames[t,...], norm=normAtom.normContinuum, continuumIndx=evoDev.continuum)
		print(prepSquare.shape)
		
		labelLine, scores = evoDev.cluster(prepSquare, maskLine, kLst=[klst[t]], intrinsicLine=intrinsicLine)
		labelSquare[t, :] = labelLine
	
	return(evoDev, labelSquare)



if __name__ == '__main__':
	#from paper02 import paper02_products
	from queso_cluster.loaders.event import eventInput
	eventManager = eventInput("./eventManager.yml", 1, 0)

	evoDev, labelSquare= main(eventManager.event)

	from queso_cluster.addon import products
	p = products.Products(evoDev, labelSquare)
	p.figure03_sequence()