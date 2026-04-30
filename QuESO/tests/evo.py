import QuESO.base as base
import QuESO.evo as evo
import QuESO.imports as imports
import QuESO.loader as loader

def main(config):


	srcUse = config.runners.config['primary']['src']
	srcConfigPrimary 	= config.srcLst[config.srcLabelLst.index(srcUse)]

	srcUse = config.runners.config['support']['src']
	srcConfigSecondary 	= config.srcLst[config.srcLabelLst.index(srcUse)]

	config.srcLst = [srcConfigPrimary, srcConfigSecondary]
#	catalogName = 'alt'

	evoDev = evo.EvolutionDriven(config, config.runners.alignmentDir, config.runners.label)

	if not config.runners.overwrite:
		frameLst, _, timeLst = evoDev.clustering()
		try:
			dataFile = Dataset(evoDev.figDir + '/evoCCS_{}_sorted.nc'.format(config.runners.label), 'r', format="NETCDF4")	
		except FileNotFoundError:
			dataFile = Dataset(evoDev.figDir + '/evoCCS_{}.nc'.format(config.runners.label), 'r', format="NETCDF4")	

		labelEntry = np.zeros((5, 125*89))
		for t in range(5):
			print(dataFile.variables['labels_full'][t, ...].data.shape)
			labelEntry[t, :] = dataFile.variables['labels_full'][t, ...].data.astype(float).reshape(125*89)

		labelLst = [labelEntry]
	else:
		frameLst, labelLst, timeLst = evoDev.clustering()
	
	return(labelLst)



if __name__ == '__main__':
	from paper02 import paper02_products
	eventManager = loader.QuESO("./eventRunners.yml")

	evoDev, labelLine, noMaskLabelLine = main(eventManager)
	p02 = paper02.paper02_products(evoDev, labelLst, frameLst)
	p02.run()