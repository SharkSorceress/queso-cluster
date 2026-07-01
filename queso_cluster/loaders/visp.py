import dkist
import numpy as np
import pint

from ..atoms import aux as auxAtom
from . import event as eventLoad

from functools import cached_property

class visp(eventLoad.eventRunner):
	"""
	Creates an object to store ViSP data, scales, and other properties

	Parameters
	----------
	dataDirectory : str
		absolute filepath to where the ViSP data for a runner is stored
	stokes : str, optional
		The stokes vector to use ['I', 'Q', 'U', 'V']

	"""

	stokes_lst 		= ['I', 'Q', 'U', 'V']

	def __init__(self, dataDirectory=None, stokes='I'):
		self._stokesIndx = self.stokes_lst.index(stokes)

		self._dataset = dkist.load_dataset(dataDirectory)
		self._datetime = auxAtom.convertTime(self._dataset.headers['DATE-BEG'])

	@cached_property
	def dataPrism(self):
		"""
		Stores the data in (t, xy, lambda) or (xy, lambda)

		Returns
		-------
		ndarray
			2D or 3D array containing the spectral data
		"""
		if 'polarization state' in self._dataset.wcs.pixel_axis_names:
			dataCube = self._dataset.data[self._stokesIndx, ...] 
		else:
			dataCube = self._dataset.data

		n = np.where(dataCube.shape == self.dimInfo['spectralSize'])[0]
		dataCube = np.moveaxis(dataCube, n, -1)
		if self.dimInfo['numRasters'] > 1:
			return(dataCube.reshape(self.dimInfo['numRasters'], 
						  self.dimInfo['rasterSize']*self.dimInfo['alongSlitSize'], self.dimInfo['spectralSize']))
		else:
			return(dataCube.reshape(self.dimInfo['rasterSize']*self.dimInfo['alongSlitSize'], self.dimInfo['spectralSize']))

	@cached_property
	def seeing(self):
		r0 = self._dataset.headers['R0']
		print(r0)

	@cached_property
	def pxlDelta(self):
		"""
		Collects the spatial plate scale in both directions

		Returns
		-------
		dict
			Dictionary with the slit width as 'pxlSlitWidth' and the along pixel scale as 'pxlAlongSlit'
		"""
		labels = ['pxlSlitWidth', 'pxlAlongSlit']		
		dimLst = ['raster scan step number', 'spatial along slit']

		deltaInfo = {}
		for d in range(len(dimLst)):
			n = self._dataset.wcs.pixel_axis_names.index(dimLst[d])
			deltaInfo[labels[d]] = self._dataset.headers['CDELT' + str(n+1)][0] * pint.Unit("arcsecond")
		
		return(deltaInfo)


	@cached_property
	def stepCadence(self):
		"""the time between slit positions"""
		stepCadence = np.diff(self._datetime[0:self.dimInfo['rasterSize']])
		stepCadence = stepCadence[stepCadence > 0]
		return(stepCadence.mean() * pint.Unit("second"))

	@cached_property
	def mapCadence(self):
		"""the time between rasters"""
		mapCadence = np.diff(self._datetime[::self.dimInfo['rasterSize']])
		mapCadence = mapCadence[mapCadence > 0]
		return(mapCadence.mean() * pint.Unit("second"))	
	
	@cached_property
	def resetDuration(self):
		"""the time it takes to go from the end of the raster to the start of a new raster"""
		return(np.diff(self._datetime[self.dimInfo['rasterSize']-1:self.dimInfo['rasterSize']+1]) * pint.Unit("second"))

	@cached_property
	def dimInfo(self):
		labels = ['rasterSize', 'alongSlitSize', 'numRasters', "spectralSize"]
		dimLst = ['raster scan step number', 'spatial along slit', 'raster map repeat number', 'dispersion axis']

		dimInfo = {}
		for d in range(len(dimLst)):
			if dimLst[d] not in self._dataset.wcs.pixel_axis_names:
				dimInfo[labels[d]] = 1
			else:
				n = self._dataset.wcs.pixel_axis_names.index(dimLst[d])
				dimInfo[labels[d]] = self._dataset.headers['DNAXIS' + str(n+1)][0]
			
		return(dimInfo)
			
	@cached_property
	def nSpectral(self):
		"""If a wavelength calibration is present in the eventManager.yml, this attribute will store the physical wavelength axis in Angstroms"""	
		n = self._dataset.wcs.pixel_axis_names.index('dispersion axis')
		return(self._dataset.headers['DNAXIS' + str(n+1)][0])
