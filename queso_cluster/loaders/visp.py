import dkist
import numpy as np
import pint

from ..atoms import aux as auxAtom

from . import event as eventLoad

from functools import cached_property

class visp(eventLoad.eventRunner):

	stokes_lst 		= ['I', 'Q', 'U', 'V']

	def __init__(self, dataDirectory=None, stokes='I'):
		

		self._dataset = dkist.load_dataset(dataDirectory)
		self._datetime = auxAtom.convertTime(self._dataset.headers['DATE-BEG'])


		# print(self._dataset.wcs.pixel_axis_names)


		# flat_axis = 1
		# numRasters = 1
		#test = []
		#crval = []

		# for n in range(self._dataset.headers['DNAXIS'][0]):
		# 	dnaxis_entry = self._dataset.headers['DNAXIS' + str(n+1)][0]
			
		# 	match self._dataset.headers['DTYPE' + str(n+1)][0]: 
		# 		case 'SPECTRAL':
		# 				spectral_len = dnaxis_entry
		# 				spectral_loc = int(np.where(np.asarray(dataCube.shape) == dnaxis_entry)[0])
		# 		case 'TEMPORAL':
		# 				numRasters = dnaxis_entry
		# 				#flat_axis *= numRasters
		# 		case 'SPATIAL':
		# 				#crval.append(dataset.headers['CRVAL' + str(n+1)][0])
		# 				flat_axis *= dnaxis_entry
		# 				#test.append(dnaxis_entry)


		#self.shape = self._dataset.data.shape
		#if numRasters == 1:
		#	self.shape = self.dataCube.shape
		#	self.dataSquare = self.dataCube.reshape(flat_axis, spectral_len)#.rechunk('auto')
		#else:
		# self.dataPrism = 

		# self.dimInfo = {
		# 	"numRasters" : numRasters,
		# 	"alongSlitSize" : np.max(test),
		# 	"rasterSize" : (flat_axis // np.max(test)) // numRasters,
		# }

	@cached_property
	def dataPrism(self):
		if 'polarization state' in self._dataset.wcs.pixel_axis_names:
			dataCube = self._dataset.data[0, ...] 
		else:
			dataCube = self._dataset.data

		n = self._dataset.wcs.pixel_axis_names.index('dispersion axis')
		dataCube = np.moveaxis(dataCube, n+1, -1)
		return(dataCube.reshape(self.dimInfo['numRasters'], 
						  self.dimInfo['rasterSize']*self.dimInfo['alongSlitSize'], dataCube.shape[-1]))
	@cached_property
	def pxlDelta(self):
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
		labels = ['rasterSize', 'alongSlitSize', 'numRasters']
		dimLst = ['raster scan step number', 'spatial along slit', 'raster map repeat number']

		dimInfo = {}
		for d in range(len(dimLst)):
			n = self._dataset.wcs.pixel_axis_names.index(dimLst[d])
			dimInfo[labels[d]] = self._dataset.headers['DNAXIS' + str(n+1)][0]
		return(dimInfo)
			

	@cached_property
	def nSpectral(self):
		"""If a wavelength calibration is present in the eventManager.yml, this attribute will store the physical wavelength axis in Angstroms"""	
		n = self._dataset.wcs.pixel_axis_names.index('dispersion axis')
		return(self._dataset.headers['DNAXIS' + str(n+1)][0])
