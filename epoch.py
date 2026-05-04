from QuESO import approach, base, loader
from QuESO.aux import writer

# import sys
import argparse

def main(config):

	srcUse = config.runners.config['src']
	aiaUse = config.runners.config['aia']

	srcConfig 	= config.srcLst[config.srcLabelLst.index(srcUse)]
	config.srcLst = srcConfig

	c = config.runners.label + '-' + aiaUse
	ViSPobj = loader.instrument(imports.dkist_dir + "/" + ''.join(config.date.split('-')) + "/" + self.visp_id + "/").vispLoad()

	epochDev = approach.timeIndependent(config, c, ViSPobj)
	if not config.runners.overwrite:
		__loadLog__ = util.logg("start", 'Reading from file...')
		try:
			saveFile = Dataset(epochDev.figDir + '/epochCCS_{}_sorted.nc'.format(c), 'r', format="NETCDF4")	
		except FileNotFoundError:
			saveFile = Dataset(epochDev.figDir + '/epochCCS_{}.nc'.format(c), 'r', format="NETCDF4")
		
		labelLine = dataFile.variables['labelMap'][...].data.astype(float)
		noMasklabelLine = dataFile.variables['noMask_labels'][...].data.astype(float)

		writer.exportFITS(epochDev, labelLine, noMasklabelLine)
		util.logg('stop', _log=__loadLog__)
	else:
		prepSquare = base.prep(epochDev.dataSquare, norm='continuum', maskSquare=epochDev.maskSquare)
		noMaskLabelLine, sscore = epochDev.clustering(epochDev.dataSquare)#
		labelLine, scoreTuple  = epochDev.clustering(prepSquare)

		writer.exportFITS()
	return(epochDev, labelLine, noMaskLabelLine)


if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--event')
	parser.add_argument('-r', '--run')
	args = parser.parse_args()	


	#from paper01 import paper01_products
	quesoInstance = loader.QuESO()
	eventManager = quesoInstance._loadEventConfig("./eventRunners.yml", args)


	quesoInstance.datDir 	= "/disk/data/DKIST/" 
	quesoInstance.homDir 	= "/disk/data/sriley/"
	quesoInstance.figDir 	= "./fig/"
	quesoInstance.aiaFname 	=  "/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(eventManager.runners.config['aia'])



	epochDev, labelLine, noMaskLabelLine = main(eventManager)
	#p01 = paper01_products(epochDev, labelLine.astype(float), 
	#						keepI0=keepI0, noMask_labels=noMaskLabelLine.astype(float))
	#p01.run()