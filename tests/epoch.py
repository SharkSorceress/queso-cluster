from QuESO import approach, base, loader
from QuESO.aux import writer
from QuESO.runners import base as runBase
from QuESO.addon import aia

# import sys
import argparse
from netCDF4 import Dataset
import numpy as np

def main(config):

	srcUse = config.runners.config['src']
	aiaUse = config.runners.config['aia']

	srcConfig 	= config.srcLst[config.srcLabelLst.index(srcUse)]
	config.srcLst = srcConfig

	c = config.runners.label + '-' + aiaUse
	ViSPobj = loader.instrument('/disk/data/DKIST/20221227/CSYRML/')
	ViSPobj.vispLoad()

	epochDev = approach.timeIndependent(config, c, ViSPobj)
	if not config.runners.overwrite:
		#__loadLog__ = util.logg("start", 'Reading from file...')
		try:
			saveFile = Dataset(epochDev.figDir + '/epochCCS_{}_sorted.nc'.format(c), 'r', format="NETCDF4")	
		except FileNotFoundError:
			saveFile = Dataset(epochDev.figDir + '/epochCCS_{}.nc'.format(c), 'r', format="NETCDF4")
		
		labelLine = saveFile.variables['labelMap'][...].data.astype(float)
		noMasklabelLine = saveFile.variables['noMask_labels'][...].data.astype(float)

		writer.exportFITS(epochDev, labelLine)
		#util.logg('stop', _log=__loadLog__)
	else:
	
		prepSquare = runBase.runPrep(epochDev.dataSquare,
							   norm='continuum', continuumIndx=epochDev.continuum)#maskSquare=epochDev.maskSquare)
		#noMaskLabelLine, _ = epochDev.clustering(epochDev.dataSquare)#

		maskLine = np.ones(prepSquare.shape[0]).astype(bool)
		if False:
			_, _, _, maskLine = aia.delayAIA("/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(aiaUse), epochDev)
	
		keepI0 = None
		if "keepI0" in list(config.runners.config.keys()):
			keepI0 = config.runners.config['keepI0']
		
		#epochDev.prepSquare = prepSquare
		labelLine, scoreTuple,  = epochDev.cluster(prepSquare, maskLine, 
											 keepI0=keepI0, kLst=config.srcLst.clusterConfig['optimized'])
		print(epochDev.prepSquare)
		print(labelLine.shape)
		#writer.exportFITS(epochDev, labelLine, c)
	return(epochDev, labelLine)


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--event')
	parser.add_argument('-r', '--run')
	args = parser.parse_args()	


	#from paper01 import paper01_products
	quesoInstance = loader.QuESO("/disk/data/DKIST/" ,
							 	"/disk/data/sriley/",
							 	"./dev/fig/")
	
	eventManager = quesoInstance._loadEventConfig("./eventRunners.yml", args)


	#quesoInstance.aiaFname 	=  "/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(eventManager.event.runners.config['aia'])
	#quesoInstance.instrumentDir = quesoInstance.datDir + '/20221227/CSYRML/'


	epochDev, labelLine = main(eventManager.event)

	from QuESO.addon import products
	p = products.Products(epochDev, labelLine)
	p.figure03()
	#p.figure04_template()

	#p01 = paper01_products(epochDev, labelLine.astype(float), 
	#						keepI0=keepI0, noMask_labels=noMaskLabelLine.astype(float))
	#p01.run()