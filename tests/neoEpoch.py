import numpy as np

from queso_cluster import writer, ti
from queso_cluster import base as baseMain
from queso_cluster.runners import base as runBase
from queso_cluster.addon import aia, prep
from queso_cluster.loaders.visp import visp
from queso_cluster.atoms import norm as normAtom
from queso_cluster.atoms import mask as maskAtom


import logging
logger = logging.getLogger("queso_cluster")
logging.basicConfig(format="!> [%(asctime)s]%(message)s", level=logging.INFO)

dkistDir = '/disk/data/DKIST/'



def main_time(config):
	
	ViSPobj = visp(dkistDir + config.dirid + '/' + config.runners.config['src'] + '/')
	ViSPobj.load()
	
	qObj = baseMain.interface(config, ViSPobj, ti.timeIndependent)

	##> Slight modification to the data format
	qObj.framework.timeFrames = np.arange(config.runners.config['timeFrames'][0], config.runners.config['timeFrames'][1]+1).astype(int)
	qObj.framework.dataSquare = ViSPobj.dataSquare[qObj.framework.timeFrames, ...].reshape((ViSPobj.dataSquare.shape[1]*qObj.framework.timeFrames.size, ViSPobj.shape[-1]))

	##> Normalization configuration
	prepConfig = {"norm": normAtom.normContinuum, "continuumIndx": config.srcLst.continuum}
	##> Running QuESO
	#labelSquare = qObj.run(prepConfig)
	qObj.framework, labelSquare = qObj.load()

	return(qObj.framework, labelSquare)

if __name__ == '__main__':
	from queso_cluster.loaders.event import eventInput
	eventManager = eventInput("./eventManager.yml", eventIndx=2, runIndx=0)
	tiDev, labelLine = main_time(eventManager.event)

	from queso_cluster.addon import products
	p = products.Products(tiDev, labelLine)
	#p.figure03()
	fig3a, fig3b = p.clusterMapSequence(timeAxis=False)
	fig3a.savefig("./figure03_sequence.png")
	fig3b.savefig("./figure03_compound.png")
	# #plt.close()

	fig4 = p.clusterProfiles()
	fig4.savefig("./clusterLabels.png")