import dkist
import numpy as np
import pint

from ..atoms import aux as auxAtom

class visp:
	def __init__(self, dataPath):
		self.dataPath = dataPath

	def load(self, stokes=0, flattenTime=False):
		#> detail: 
		#> param type self:
		#> param type [0] stokes:
		#> return (type): 
		#> test-method:
		dataset = dkist.load_dataset(self.dataPath)
		dataCube = dataset.data
		if 'polarization state' in dataset.wcs.pixel_axis_names:
			dataCube = dataCube[stokes, ...] 
		print(dataCube.shape)
		#axisInfo = [dataset.wcs.pixel_axis_names[::-1], dataset.data.shape]
		flat_axis = 1
		numRaster = 1
		test = []
		crval = []

		
		for n in range(dataset.headers['DNAXIS'][0]):
			dnaxis_entry = dataset.headers['DNAXIS' + str(n+1)][0]
			
			#print([dataset.headers['DTYPE' + str(n+1)][0], dnaxis_entry])
			match dataset.headers['DTYPE' + str(n+1)][0]: 
				case 'SPECTRAL':
						spectral_len = dnaxis_entry
						spectral_loc = int(np.where(np.asarray(dataCube.shape) == dnaxis_entry)[0])
				case 'TEMPORAL':
						numRaster = dnaxis_entry
						flat_axis *= numRaster
				case 'SPATIAL':
						crval.append(dataset.headers['CRVAL' + str(n+1)][0])
						flat_axis *= dnaxis_entry
						test.append(dnaxis_entry)


		pxlSize = [[], []]
		for m in range(dataset.headers['WCSAXES'][0]):
			match dataset.headers['CTYPE' + str(m+1)][0]:
				case 'HPLT-TAN':                     
					pxlSize[0].append(dataset.headers['CDELT' + str(m+1)][0])   
					pxlSize[1].append(m)
				case 'AWAV':
						waveAxisDelta = dataset.headers['CDELT' + str(m+1)][0]


		self.deltas = {	
			"pxlAlongSlit": min(pxlSize[0]) * pint.Unit("arcsecond"),
			'pxlSlitWidth': dataset.headers['VSPWID'][0] * pint.Unit("arcsecond")
		}

		self.dataCube = np.moveaxis(dataCube, spectral_loc, -1)
		self.shape = self.dataCube.shape
		if numRaster == 1 or flattenTime:
			self.shape = self.dataCube.shape
			self.dataSquare = self.dataCube.reshape(flat_axis, spectral_len)#.rechunk('auto')
		else:
			self.dataSquare = self.dataCube.reshape(numRaster, flat_axis//numRaster, spectral_len)

		self.alongSlitSize 	= np.max(test)
		self.rasterSize 	= (flat_axis // self.alongSlitSize) // numRaster

		self.spaceInfo = {
			"maxRasters": numRaster,
			"rasterSize": self.rasterSize,
			"alongSlitSize": self.alongSlitSize,
		}
		self.waveInfo = {
			#"waveDelta": waveAxisDelta,
			"waveExtrema": (dataset.headers['WAVEMIN'][0], 
							dataset.headers['LINEWAV'][0], 
							dataset.headers['WAVEMAX'][0])
		}

		datetime = auxAtom.convertTime(dataset.headers['DATE-BEG'])

		#> Note: The start datetime of the observations
		self.zeroDate = dataset.headers['DATE-BEG'][0]

		#> Note: slit spectrographs have three relavant time scales:
		#> Note: step cadence -- the time between slit positions 
		#> Note: map cadence -- the time between rasters
		#> Note: reset time -- the time it takes to go from the end of the raster to the start of a new raster
		stepCadence = np.diff(datetime[0:self.rasterSize])
		stepCadence = stepCadence[stepCadence > 0]
		self.stepCadence = stepCadence.mean() * pint.Unit("second")

		mapCadence = np.diff(datetime[::self.rasterSize])
		mapCadence = mapCadence[mapCadence > 0]

		self.resetTime = datetime[self.rasterSize-1:self.rasterSize+1] * pint.Unit("second")

		if len(np.unique(mapCadence)) > 0: 
			self.mapCadence = mapCadence.mean() * pint.Unit("second")