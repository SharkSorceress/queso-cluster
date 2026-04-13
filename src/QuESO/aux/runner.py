from lib.util.imports import *
import lib.util.ViSP_tools as vt
import scipy.io.idl as idl

def axis_calibrate(config, datStruct, quiescent):
	# vispCube = numba.float32(vispDataset.dataCube.astype(np.float16).compute())    
	# #lineCore, ii, jj, quiescent, quiescent_indx    = pre.linecore_range(vispCube)
	# data_id, coreIndex = util._gen_dataID(config)
	# dirid   = ''.join(config.date.split('-'))
	#quiescent       = pre.four_corners([vispDataset.dataCube.blocks[0, 0], vispDataset.dataCube.blocks[-1, 0]], 
	#									   data_id)
	#lineCore, ii, jj = pre.search_linecore(quiescent, data_id, dirid, coreIndex)
	#lineCore, ii, jj = [544,484, 604]
	vispDataset = datStruct.spectralData
	lineCore = datStruct.lineCore

	wavemin, wavemax = [vispDataset.waveInfo['waveExtrema'][0], 
						vispDataset.waveInfo['waveExtrema'][2]]
	dc = np.loadtxt('./dat/solar_merged_20200720_600_33300_100.out.gz',skiprows =3) 
	wvair_telluric = np.load('./dat/telluric_atlas_mainMol_USstd_wv_air_angstrom_v20240307.npy')  /10. 
	trans_telluric = np.load('./dat/telluric_atlas_mainMol_USstd_CO2_416ppm-Base_3km-PWV_3__mm-Airmass_1___v20240307.npy')
	solar_spectra = dc[:,1][::-1] 
	wvair_solar = vt.vacuum_to_air(1e8/dc[:,0])[::-1]/10.
	align_lst = []
	#ii = 0



	ww          = (wvair_solar > 853)*( wvair_solar < 855)  
	ww_telluric = (wvair_telluric > 853) * (wvair_telluric < 855)  

	atlas = wvair_solar[ww][np.where(solar_spectra[ww] == np.min(solar_spectra[ww]))[0]]

	waveAxis = np.arange(wavemin, wavemax, step=vispDataset.waveInfo['waveDelta'])
	visp  = waveAxis[lineCore]


#	for i in range(2):
		# print(atlas)
		# print(visp)
		# if atlas != visp:
		# 	align_lst.append(atlas - visp)        
		# 	# print(atlas - visp)
		# wavemin += (atlas - visp)
		# wavemax += (atlas - visp)

	visp_peaks, _       = find_peaks(1-quiescent, prominence=0.01)
#	print(visp_peaks)
	# visp_peaks 			= peakSearch(1 - quiescent)
	# print(visp_peaks)

	atlas_peaks, _      = find_peaks(1-solar_spectra[ww], prominence=0.01)
#	atlas_peaks 		= peakSearch(1 - solar_spectra[ww])

	telluric_peaks, _   = find_peaks(1-trans_telluric[ww_telluric], prominence=0.01)
#	telluric_peaks 		= peakSearch(1 - trans_telluric[ww_telluric])

	indxAxis = np.arange(len(waveAxis))

	# print([len(waveAxis), len(quiescent)])
	fig = plt.figure(layout='constrained', figsize=(10, 5))
	ax1 = fig.add_subplot(121)
	ax2 = fig.add_subplot(122)
	
	ax1.plot(wvair_solar[ww], 1-solar_spectra[ww])
	ax1.plot(wvair_solar[ww][atlas_peaks], 1-solar_spectra[ww][atlas_peaks], "x")
	ax2.plot(indxAxis, 1-quiescent)
	ax2.plot(indxAxis[visp_peaks], 1-quiescent[visp_peaks], "x")
	ax1.plot(wvair_telluric[ww_telluric], 1-trans_telluric[ww_telluric])
	ax1.plot(wvair_telluric[ww_telluric][telluric_peaks], 
			1-trans_telluric[ww_telluric][telluric_peaks], "x")
	#plt.show()
	plt.savefig('./fig/testing_atlas_1.png')
	sys.exit()


	fit_arr = 		[[None, 0, 0],
					[2, None, 1],
					[None, 1, 2],
					[3, None, 3],
					[None, 2, 4],
					[None, 3, 5],
					[4, None, 6],
					[None, 4, 7],
					[5, None, 8]]

	fit_peaks = []
	fit_visp  = []
	for l in range(len(fit_arr)):
		for k in range(len(fit_arr[l])):
			indx = fit_arr[l][k]
			if indx != None:
				match k:
					case 0:
						fit_peaks.append(wvair_solar[ww][atlas_peaks[int(indx)]])
					case 1:
						fit_peaks.append(wvair_telluric[ww_telluric][telluric_peaks[int(indx)]])
					case 2:
						fit_visp.append(indxAxis[visp_peaks][int(indx)])


	test_fit_d3 = np.polyfit(fit_visp, fit_peaks, deg=3)
	test_fit_d2 = np.polyfit(fit_visp, fit_peaks, deg=2)
	test_fit_d1 = np.polyfit(fit_visp, fit_peaks, deg=1)


	fig = plt.figure(layout='constrained', figsize=(10, 5))
	ax1 = fig.add_subplot(121)
	ax2 = fig.add_subplot(122)
	#plt.scatter(waveAxis[visp_peaks], wvair_solar[ww][atlas_peaks])
	ax1.scatter(fit_visp, fit_peaks)
	ax1.plot(indxAxis, np.poly1d(test_fit_d3)(indxAxis))
	ax1.plot(indxAxis, np.poly1d(test_fit_d2)(indxAxis))
	ax1.plot(indxAxis, np.poly1d(test_fit_d1)(indxAxis))
	ax1.set_ylabel("atlas")
	ax1.set_xlabel("ViSP")

	ax2.scatter(fit_visp, fit_peaks - np.poly1d(test_fit_d3)(fit_visp), label='cubic')
	ax2.scatter(fit_visp, fit_peaks - np.poly1d(test_fit_d2)(fit_visp), label='quad')
	ax2.scatter(fit_visp, fit_peaks - np.poly1d(test_fit_d1)(fit_visp), label='linear')
	ax2.set_xlabel("ViSP")
	ax2.set_ylabel("residual [real - fit]")
	ax2.legend()
	plt.savefig("./fig/fitting_test.png")


	plt.figure(figsize=(12, 4))
	plt.subplot(131)
	plt.plot(wvair_solar[ww], solar_spectra[ww]/solar_spectra[ww].max())
	plt.plot(np.poly1d(test_fit_d3)(indxAxis), quiescent/quiescent.max())
	plt.plot(wvair_telluric[ww_telluric], trans_telluric[ww_telluric])
	plt.title("Cubic")
	print('$({})x^3+({})x^2 + ({})x + ({})$'.format(*test_fit_d3))
	plt.subplot(132)
	plt.plot(wvair_solar[ww], solar_spectra[ww]/solar_spectra[ww].max())
	plt.plot(np.poly1d(test_fit_d2)(indxAxis), quiescent/quiescent.max())
	plt.plot(wvair_telluric[ww_telluric], trans_telluric[ww_telluric])
	plt.title("Quadratic")
	print('$({})x^2 + ({})x + ({})$'.format(*test_fit_d2))
	plt.subplot(133)
	plt.plot(wvair_solar[ww], solar_spectra[ww]/solar_spectra[ww].max())
	plt.plot(np.poly1d(test_fit_d1)(indxAxis), quiescent/quiescent.max())   
	plt.plot(wvair_telluric[ww_telluric], trans_telluric[ww_telluric])
	print('$({})x + ({})$'.format(*test_fit_d1))
	plt.title("Linear")
	plt.savefig('./fig/fitting_result.png')




### Adopted from STiC, courtesy Jaime de la Cruz. Gratefully acknowledged!

class satlas:
    def __init__(self):
        # Check dir where this class is stored
        this_dir, this_filename = os.path.split(__file__)
        DATA_PATH = os.path.join(this_dir, "fts_disk_center.idlsave")

        # Load data file
        fts = idl.readsav(DATA_PATH)
        self.cont = fts["ftscnt"]
        self.sp   = fts["ftsint"]
        self.wav  = fts["ftswav"]


    def tocgs(self, w, s):
        clight=2.99792458e10         #speed of light [cm/s]
        joule_2_erg=1e7
        aa_to_cm=1e-8
        s *=joule_2_erg/aa_to_cm # from Watt /(cm2 ster AA) to erg/(s cm2 ster cm)
        s *=(w*aa_to_cm)**2/clight   # to erg/
        return s

    def tosi(self, wav, s):
        clight=2.99792458e8      #speed of light [m/s]                                  
        aa_to_m=1e-10                                                                        
        cm_to_m=1e-2                       
        s /= cm_to_m**2 * aa_to_m # from from Watt /(s cm2 ster AA) to Watt/(s m2 ster m) 
        s *= (wav*aa_to_m)**2 / clight # to Watt/(s m2 Hz ster)
        return s
    
    def getatlas(self, w0, w1, cgs = False, si = False, nograv = False):
        idx = (np.where((self.wav >= w0) & (self.wav <= w1)))[0]

        wav =  np.copy(self.wav[idx[0]:idx[-1]])
        sp =   np.copy(self.sp[idx[0]:idx[-1]])
        cont = np.copy(self.cont[idx[0]:idx[-1]])

        if(not nograv):
            wav *=  (1.0-633.0/2.99792458e8) # grav reddening

        # convert to CGS units
        if(cgs):
            sp =   self.tocgs(wav, sp)
            cont = self.tocgs(wav, cont)

        # convert to IS units
        elif(si):
            sp =   self.tosi(wav, sp)
            cont = self.tosi(wav, cont)

        # Normalize by the continuum (default)
        else:
            sp /= cont
            cont[:] = 1.0
            
        return wav, sp, cont

    def nmsiatlas(self, wnm0, wnm1):
        # Easy shortcut for wavelengths in nm and SI units.
        # HU, Jul  9 2021 
        
        NM_TO_ANGSTROM = 10.0

        w0 = wnm0 * NM_TO_ANGSTROM
        w1 = wnm1 * NM_TO_ANGSTROM

        atl = self.getatlas(w0, w1, si=True)

        return atl[0] / NM_TO_ANGSTROM, atl[1], atl[2]