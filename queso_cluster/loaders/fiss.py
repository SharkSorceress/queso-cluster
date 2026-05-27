import glob
from astropy.io import fits
import numpy as np

class fiss:
	def __init__(self, dataPath):
		self.dataPath = dataPath

	def fissLoad(self, labels):
		#> detail: 
		#> param type self:
		#> param type labels:
		#> return (type): 
		#> test-method:

		biasDarkLst = glob.glob(self.dataPath + "*_{}_BiasDark.fts".format(labels))
		flatLst 	= glob.glob(self.dataPath + "*_{}_Flat.fts".format(labels))
		fitsLst 	= glob.glob(self.dataPath + "*_{}.fts".format(labels))

		initial = fits.open(fitsLst[0])

		self.rasterSize = initial[0].header['NAXIS2']
		self.alongSlitSize = initial[0].header['NAXIS3']


		self.waveInfo = {
			"lineLabel": initial[0].header['GRATWVLN'],#dataset.headers['WAVEBAND'][0],
		}

		print(self.waveInfo)

		self.spaceInfo = {
			"maxRasters": len(fitsLst),
			"pxlAlongSlit": 512,
			'pxlSlitWidth': 512
		}



		self.dataCube =  np.zeros((len(fitsLst), self.alongSlitSize, self.rasterSize, initial[0].header['NAXIS1']))

		for f in range(len(fitsLst)):
			file = fits.open(fitsLst[f])
			self.dataCube[f, ...] = file[0].data#.reshape(self.rasterSize*self.alongSlitSize, initial[0].header['NAXIS1'])
			print(file[0].data.shape)

			file.close()

		self.dataCube = np.moveaxis(self.dataCube, 1, 2)
		self.shape = self.dataCube.shape