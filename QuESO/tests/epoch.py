import QuESO.base as base
import QuESO.epoch as epoch
import QuESO.imports as imports
import QuESO.loader as loader
from QuESO.main import QuESO_main



@loggTimer
def main(config):

	imports.dkist_dir = "/disk/data/DKIST/"
	imports.home_dir = "/disk/data/sriley/"
	imports.fig_dir = "./fig/"
	

	srcUse = config.runners.config['src']
	aiaUse = config.runners.config['aia']

	imports.aia_fname = "/disk/data/SDO/qiuj/sarah/20221227/data/aia_lgtcv_visptime_{}.sav".format(aiaUse)


	srcConfig 	= config.srcLst[config.srcLabelLst.index(srcUse)]
	config.srcLst = srcConfig

	c = config.runners.label + '-' + aiaUse
	ViSPobj = loader.instrument(imports.dkist_dir + "/" + ''.join(config.date.split('-')) + "/" + self.visp_id + "/").vispLoad()

	epochDev = ep.EpochDriven(config, c, ViSPobj)
	if not config.runners.overwrite:
		__loadLog__ = util.logg("start", 'Reading from file...')
		try:
			saveFile = Dataset(epochDev.figDir + '/epochCCS_{}_sorted.nc'.format(c), 'r', format="NETCDF4")	
		except FileNotFoundError:
			saveFile = Dataset(epochDev.figDir + '/epochCCS_{}.nc'.format(c), 'r', format="NETCDF4")
		
		labelLine = dataFile.variables['labelMap'][...].data.astype(float)
		noMasklabelLine = dataFile.variables['noMask_labels'][...].data.astype(float)
		util.logg('stop', _log=__loadLog__)
	else:
		prepSquare = base.prep(epochDev.dataSquare, norm='continuum', maskSquare=epochDev.maskSquare)
		noMaskLabelLine, sscore = epochDev.clustering(epochDev.dataSquare)#
		labelLine, scoreTuple  = epochDev.clustering(prepSquare)
	return(epochDev, labelLine, noMaskLabelLine)


if __name__ == '__main__':
	from paper01 import paper01_products
	eventManager = QuESO_main("./eventRunners.yml")

	epochDev, labelLine, noMaskLabelLine = main(eventManager)
	p01 = paper01_products(epochDev, labelLine.astype(float), 
							keepI0=keepI0, noMask_labels=noMaskLabelLine.astype(float))
	p01.run()