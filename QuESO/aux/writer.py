from astropy.io import fits
import numpy as np

# from globals import __version__

def exportFITS(spectralDataset, labelLine, fname):


	#[t, x, y, lambda]
	data = spectralDataset.dataSquare.reshape(spectralDataset.shape)
	#[t, x, y, lambda, label]
	# > TODO: Add mask

	labelSquare = labelLine.reshape(data.shape[:-1])


	#hdu1 = fits.PrimaryHDU(data=data)
	hdu2 = fits.PrimaryHDU(data=labelSquare)

	fileFormat = ['results']
	h = 0
	for hdu in [hdu2]:
		hdr = hdu.header
		hdr["CAXISY"] 	= ("Along Slit Direction") 
		hdr["CDELTY"] 	=  (spectralDataset.spaceInfo['pxlAlongSlit'])

		hdr['CAXISX'] 	= ("Raster Direction")
		hdr["CDELTX"] 	= (spectralDataset.spaceInfo['pxlSlitWidth']) 

		if hasattr(spectralDataset, "stepCadence"):
			hdr["STEPCAD"] = (spectralDataset.stepCadence)
		#hdr["cadence"] 			= (spectralDataset.spaceInfo['cadence'])

		if hasattr(spectralDataset, "mapCadence"):
			hdr["CAXIST"] = ("Time")
			hdr["CDELTT"] = (spectralDataset.mapCadence)


		for a in range(2):
			hdr["WINDOW{}".format(a+1)] 	= (spectralDataset.spectralWindow[a])
	
		hdr["CONTIN"] 	= (spectralDataset.continuum)
		hdr["CENTER"]	= (spectralDataset.lineCenter)

		if hasattr(spectralDataset, "waveCoeff"):
			for a in range(len(spectralDataset.waveCoeff)):
				hdr["WAVEFIT{}".format(a+1)] = (spectralDataset.waveCoeff[a])

		#hdu.set("normalization", config.normalization)

		#hdu.set("QuESO version", __version__)

		hdul = fits.HDUList([hdu])
		hdul.writeto("./{}-{}.fits".format(fileFormat[h], fname))
		h += 1
	