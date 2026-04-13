
class EpochProducts:
	def __init__(self, epochObj):
		self.epochObj 	= epochObj
		self.version 	= datetime.now(timezone.utc)
		self.catalogBase=self.epochObj.catalogBase

		self.fpath = globalVars.home_dir + self.epochObj.dirid + '/' + self.epochObj.dirid + '_catalog/'
		self.figDir = './fig/paper01_{}/'.format(self.catalogBase)

		self.config 		= self.epochObj.config
		self.alongSlitSize = self.epochObj.spaceInfo['alongSlitSize']
		self.rasterSize 	  = self.epochObj.spaceInfo['rasterSize']
		self.aspect 		  = self.epochObj.aspect
		# self.lineCore, self.ii, self.jj = self.epochObj.spectralParams

		self.spectralWindow = self.epochObj.spectralWindow
		self.lineCore = self.epochObj.lineCore
		self.continuum = self.epochObj.continuum

		self.deltas = self.epochObj.deltas

		self.waveFit 	= self.epochObj.waveFit 


		self.bbox = [0, self.rasterSize, 0, self.alongSlitSize]

		self.mapMake = util.mapMaker(self.epochObj.spaceInfo, self.deltas)

	def catalogTemplate(self, labels, sscore, noMask_labels, catalogType):
		ii, jj = self.spectralWindow

		lineLabel   = self.epochObj.spectralData.waveInfo['lineLabel']
		
		wavelambda  = self.epochObj.waveFit
		valid_indx 	= np.where(~np.isnan(labels))[0]

		i0ArrFull = _calc.pick_jth_label(noMask_labels, 0).astype(int)
		i0Lst = np.unique(i0ArrFull).astype(int)
		i0Arr 	= _calc.pick_jth_label(labels[valid_indx], 0).astype(int)

		ngroups = np.array(self.epochObj.config.srcLst.clusterConfig['optimized'][0]['layerGroups'])

		nrows = []
		gCounter = 0
		entryCounter = 0

		for n in range(len(ngroups)):
				nrows.append(self.epochObj.config.srcLst.clusterConfig['optimized'][1]['layerGroups'][gCounter:gCounter+ngroups[n]])
				gCounter += ngroups[n]
				entryCounter += np.array(nrows[n]).sum()

		_, color_pallet = util._genColorPallet(len(i0Lst))

		keyProgress =ProgressBar(total=entryCounter, 
							ascii=False, leave=True, 
							bar_format=catalogType + ' Catalog Key: {percentage:3.3f}%|{bar}| {n} [{elapsed}]')

		with PdfPages(self.fpath + self.epochObj.visp_id + '_catalog_' + catalogType + "-" + self.catalogBase + '.pdf') as pdf:
			for j in range(len(i0Lst)):
				i0Search = np.where(i0Arr == i0Lst[j])[0]
				if len(i0Search) < 1:
					keyProgress.update(np.array(nrows[i0Lst[j]-1]).sum())
					continue

				i0_indx 	= valid_indx[i0Search]

				raw_max = (np.ceil(self.epochObj.normCube[i0_indx, ii:jj].max()*10)/10.).compute()
				raw_min = (np.floor(self.epochObj.normCube[i0_indx, ii:jj].min()*10)/10.).compute()	
				extent  	= wavelambda[ii]-wavelambda[self.lineCore], wavelambda[jj]-wavelambda[self.lineCore], raw_min, raw_max

				o1Arr = _calc.pick_jth_label(labels[i0_indx], 1).astype(int)
				o1Lst = np.unique(o1Arr).astype(int)

				fig = plt.figure(layout="constrained", figsize=(int(np.max(nrows[i0Lst[j]-1])+1)*3, int(len(o1Lst))*3))
				
				gs  = GridSpec(int(len(o1Lst)), int(np.max(nrows[i0Lst[j]-1])+1), 
							left=0, right=1, top=1, bottom=0, 
							width_ratios=[1 for x in range(int(np.max(nrows[i0Lst[j]-1])+1))],
							height_ratios=[1 for x in range(int(len(o1Lst)))],
							figure=fig)			

				color = color_pallet[int(i0Lst[j])-1]
				print(o1Lst)
				for i in range(len(o1Lst)):
					ax      = plt.subplot(gs[i, 0])
					o1_indx = i0_indx[np.where(o1Arr == o1Lst[i])[0]]

					if catalogType == "spectral":
						ax = self.spectralEntry(ax, o1_indx, color, wavelambda, extent)
						ax.set_title("N = {} | {}X".format(len(o1_indx), int(i0Lst[j])*10 + (i+1)))
					elif catalogType == "timeDelay":
						ax, aia_hist = self.timeDelayEntry(ax, o1_indx, color)
						ax.set_title("N = {} | {}X".format(len(aia_hist), int(i0Lst[j])*10 + (i+1)))
					
					if not gs[o1Lst[i]-1, 0].is_last_row():
						ax.tick_params(labelbottom=False)
					
					o2Arr = _calc.pick_jth_label(labels[o1_indx], 2).astype(int)					
					o2Lst = np.unique(o2Arr).astype(int)
					print(o2Lst)
					for k in range(len(o2Lst)):
						ax      	= plt.subplot(gs[i, k+1])
						o2_indx 	= o1_indx[np.where(o2Arr == o2Lst[k])[0]]

						if catalogType == "spectral":
							ax = self.spectralEntry(ax, o2_indx, color, wavelambda, extent)
						elif catalogType == "timeDelay":
							ax, aia_hist = self.timeDelayEntry(ax, o2_indx, color)

						ax.set_title('N = {} | {}'.format(len(o2_indx), int(labels[o2_indx[0]])))
						ax.tick_params(labelleft=False)
						if not gs[o1Lst[i]-1,1+k].is_last_row():
							ax.tick_params(labelbottom=False)

						keyProgress.update(1)
			
				fig.suptitle("k-means results ({} {} || {}XX)".format(self.epochObj.visp_id, lineLabel, i0Lst[j]))   

				if catalogType == "spectral":
					fig.savefig(self.figDir + "/cluster_{}.png".format(i0Lst[j]))
				elif catalogType == "timeDelay":
					fig.savefig(self.figDir + "/timeDelay_{}.png".format(i0Lst[j]))

				pdf.savefig()
		keyProgress.close()
		util.logg("msg", "Catalog Key Saved")	

	def spectralEntry(self, ax, indx, color, wavelambda, extent):
		ii, jj = self.spectralWindow
		raw_dat = self.epochObj.normCube[indx.astype(np.uint32), ii:jj]
		centroid_i = raw_dat.sum(axis=0)/raw_dat.shape[0]		
		ax.plot(wavelambda[ii:jj]-wavelambda[self.lineCore], centroid_i, color='black')

		temp_im 	= _calc.density_hist2d(raw_dat.compute(), 0.01, extent[3], extent[2])
		im = ax.imshow(temp_im.T, 
		extent=extent, aspect='auto', origin='lower')    
		im.set_cmap(LinearSegmentedColormap.from_list('', ['white', color]))

		ax.axvline(x = 0, linestyle='dashed', color='black')
		ax.set_ylim([extent[2], extent[3]])
		return(ax)

	def timeDelayEntry(self,ax, indx, color):
		binRate = 2
		xmax = np.ceil(np.max(np.abs(np.array([np.nanmin(self.epochObj.delayCube), np.nanmax(self.epochObj.delayCube)]))))
		xmax += (1-(xmax % 2))
		nbins = int(2*xmax/binRate)#int((np.ceil(aia_hist.max()) - np.


		indexs 	= self.epochObj.delayCube[indx]
		aia_hist = indexs[np.where(~np.isnan(indexs))[0]]		

		if len(aia_hist) > 0:
			hist, edges = _calc.numba_histogram(aia_hist, nbins, 
														lim=np.array([-xmax, xmax]))
					
			max_val = np.max(hist)
			ax.bar(edges[:-1], hist, 
					width=np.diff(edges), 
					edgecolor=None, align="edge", color=color,
					linewidth=0.25)  
			ax.set_ylim([0, max_val])
			ax.set_xlim([-xmax, xmax])	
		return(ax, aia_hist)

	def catalogKey(self, labels, sscore, noMask_labels):
		ii, jj = self.spectralWindow

		lineLabel   = self.epochObj.spectralData.waveInfo['lineLabel']
		
		wavelambda  = self.epochObj.waveFit
		valid_indx 	= np.where(~np.isnan(labels))[0]

		i0ArrFull = _calc.pick_jth_label(noMask_labels, 0).astype(int)
		i0Lst = np.unique(i0ArrFull).astype(int)
		i0Arr 	= _calc.pick_jth_label(labels[valid_indx], 0).astype(int)

		ngroups = np.array(self.epochObj.config.srcLst.clusterConfig['optimized'][0]['layerGroups'])

		nrows = []
		gCounter = 0
		entryCounter = 0
		for n in range(len(ngroups)):
			nrows.append(self.epochObj.config.srcLst.clusterConfig['optimized'][1]['layerGroups'][gCounter:gCounter+ngroups[n]])
			gCounter += ngroups[n]
			entryCounter += np.array(nrows[n]).sum()

		_, color_pallet = util._genColorPallet(len(i0Lst))

		keyProgress = ProgressBar(total=entryCounter, 
							ascii=False, leave=True, 
						bar_format='Catalog Key: {percentage:3.3f}%|{bar}| {n} [{elapsed}]')

		with PdfPages(self.fpath + self.epochObj.visp_id + '_catalog_' + self.catalogBase + '.pdf') as pdf:
			firstPage = plt.figure(figsize=(11.69,8.27))
			firstPage.clf()
			txt = 'Spectral Catalog Key ({} {})\nv{}'.format(self.epochObj.visp_id, self.epochObj.spectralData.waveInfo['lineLabel'], self.version)
			firstPage.text(0.5,0.5,txt, transform=firstPage.transFigure, size=24, ha="center")
			pdf.savefig()
			plt.close()
			J = 0
			for j in range(len(i0Lst)):

				i0Search = np.where(i0Arr == i0Lst[j])[0]
				if len(i0Search) < 1:
					keyProgress.update(np.array(nrows[i0Lst[j]-1]).sum())
					continue

				i0_indx 	= valid_indx[i0Search]

				raw_max = (np.ceil(self.epochObj.normCube[i0_indx, ii:jj].max()*10)/10.).compute()
				raw_min = (np.floor(self.epochObj.normCube[i0_indx, ii:jj].min()*10)/10.).compute()	
				extent  	= wavelambda[ii]-wavelambda[self.lineCore], wavelambda[jj]-wavelambda[self.lineCore], raw_min, raw_max

				o1Arr = _calc.pick_jth_label(labels[i0_indx], 1).astype(int)
				o1Lst = np.unique(o1Arr).astype(int)


				fig = plt.figure(layout="constrained", figsize=(int(np.max(nrows[i0Lst[j]-1])+1)*3, int(len(o1Lst))*3))
				
				gs  = GridSpec(int(len(o1Lst)), int(np.max(nrows[i0Lst[j]-1])+1), 
							left=0, right=1, top=1, bottom=0, 
							width_ratios=[1 for x in range(int(np.max(nrows[i0Lst[j]-1])+1))],
							height_ratios=[1 for x in range(int(len(o1Lst)))],
							figure=fig)


				for i in range(len(o1Lst)):
					ax      = plt.subplot(gs[i, 0])
					o1_indx = i0_indx[np.where(o1Arr == o1Lst[i])[0]]
				
					raw_dat = self.epochObj.normCube[o1_indx.astype(np.uint32), ii:jj]
					centroid_i = raw_dat.sum(axis=0)/raw_dat.shape[0]

					ax.set_title('N = {} | {}X'.format(len(o1_indx), (int(i0Lst[j])*10) + (i+1)))
					ax.plot(wavelambda[ii:jj]-wavelambda[self.lineCore], centroid_i, color=color_pallet[int(i0Lst[j])-1])
					ax.axvline(x = 0, linestyle='dashed', color=color_pallet[int(i0Lst[j])-1])
					ax.set_ylim([raw_min, raw_max])
					if not gs[i,0].is_last_row():
						ax.tick_params(labelbottom=False)

					o2Arr = _calc.pick_jth_label(labels[o1_indx], 2).astype(int)
					o2Lst = np.unique(o2Arr).astype(int)
					for k in range(len(o2Lst)):
						#print([i0Lst[j], o1Lst[i], o2Lst[k]])
						ax      	= plt.subplot(gs[i, 1+k])
						o2_indx 	= o1_indx[np.where(o2Arr == o2Lst[k])[0]]
						raw_dat 	=  self.epochObj.normCube[o2_indx.astype(np.uint32), ii:jj]
						centroid_i 	= raw_dat.sum(axis=0)/raw_dat.shape[0]

						temp_im 	= _calc.density_hist2d(raw_dat.compute(), 0.01, raw_max, raw_min)
						im = ax.imshow(temp_im.T, 
									extent=extent, aspect='auto', origin='lower')    
						im.set_cmap(LinearSegmentedColormap.from_list('', ['white', color_pallet[int(i0Lst[j])-1]]))
						ax.set_title('N = {} | {}'.format(len(o2_indx), int(labels[o2_indx[0]])))
						#ax.set_title('N = {} | {} | ISS = {:.2f} | OSS = {:.2f}'.format(len(o2_indx), int(labels[o2_indx[0]]), sscore[0][J][i][k], sscore[1][J][0][len(o2Lst)*i + k]))
						ax.plot(wavelambda[ii:jj]-wavelambda[self.lineCore], centroid_i, color='black')
						ax.axvline(x = 0, linestyle='dashed', color='black')
						ax.set_ylim([raw_min, raw_max])
						ax.tick_params(labelleft=False)
						if not gs[i,1+k].is_last_row():
							ax.tick_params(labelbottom=False)
						keyProgress.update(1)

				J += 1
				#print("check7-{}".format(j))
						
				fig.suptitle("k-means results ({} {} || {}XX)".format(self.epochObj.visp_id, lineLabel, i0Lst[j]))   
				fig.savefig(self.figDir + "/cluster_{}.png".format(i0Lst[j]))
				pdf.savefig()
				plt.close()
		keyProgress.close()
		util.logg("msg", "Catalog Key Saved")	

	def catalogDelayKey(self, labels, noMask_labels):
		# dir_mod, i1, i2 = self.config.intensityBins

		# labels = Labels

		#	labels = self.correct(Labels)

		# aia_lgtcube = self.correct(self.epochObj.aia_lgtcube)

		ii, jj = self.epochObj.spectralWindow
		# lineCore = self.epochObj.lineCore
		
		lineLabel   = self.epochObj.spectralData.waveInfo['lineLabel']
		
		wavelambda  = self.epochObj.waveFit
		valid_indx 	= np.where(~np.isnan(labels))[0]

		#i0Lst = np.unique(i0Arr)
		i0ArrFull = _calc.pick_jth_label(noMask_labels, 0).astype(int)
		i0Lst = np.unique(i0ArrFull).astype(int)
		i0Arr 	= _calc.pick_jth_label(labels[valid_indx], 0).astype(int)

		ngroups = np.array(self.epochObj.config.srcLst.clusterConfig['optimized'][0]['layerGroups'])

		nrows = []
		gCounter = 0
		entryCounter = 0
		for n in range(len(ngroups)):
			nrows.append(self.epochObj.config.srcLst.clusterConfig['optimized'][1]['layerGroups'][gCounter:gCounter+ngroups[n]])
			gCounter += ngroups[n]
			entryCounter += np.array(nrows[n]).sum()

		_, color_pallet = util._genColorPallet(len(i0Lst))


		fig 	= plt.figure(layout='constrained', figsize=(10, 5))
		ax1 	= fig.add_subplot(121)
		im		= ax1.imshow(labels.reshape(self.rasterSize, self.alongSlitSize).T, cmap='rainbow_r', aspect=self.aspect, origin='lower')
		ax2 	= fig.add_subplot(122)
		im 	= ax2.imshow(self.epochObj.delayCube.reshape(self.rasterSize, self.alongSlitSize).T, aspect=self.aspect, origin='lower')
		fig.savefig('./index_test.png') 

		keyProgress = ProgressBar(total=entryCounter, 
							ascii=False, leave=True, 
						bar_format='Catalog Key: {percentage:3.3f}%|{bar}| {n} [{elapsed}]')

		binRate = 2
		
		xmax = np.ceil(np.max(np.abs(np.array([np.nanmin(self.epochObj.delayCube), np.nanmax(self.epochObj.delayCube)]))))
		xmax += (1-(xmax % 2))
		nbins = int(2*xmax/binRate)#int((np.ceil(aia_hist.max()) - np.floor(aia_hist.min()))/2.)

		with PdfPages(self.fpath + self.epochObj.visp_id + '_timeDelay_' + self.catalogBase + '.pdf') as pdf:
			firstPage = plt.figure(figsize=(11.69,8.27))
			firstPage.clf()
			txt = 'Spectral Catalog Key ({} {})\nv{}'.format(self.epochObj.visp_id, self.epochObj.spectralData.waveInfo['lineLabel'], self.version)
			firstPage.text(0.5,0.5,txt, transform=firstPage.transFigure, size=24, ha="center")
			pdf.savefig()
			plt.close()

			for j in range(len(i0Lst)):

				i0Search = np.where(i0Arr == i0Lst[j])[0]
				if len(i0Search) < 1:
					keyProgress.update(np.array(nrows[i0Lst[j]-1]).sum())
					continue

				i0_indx 	= valid_indx[i0Search]

				raw_max = (np.ceil(self.epochObj.normCube[i0_indx, ii:jj].max()*10)/10.).compute()
				raw_min = (np.floor(self.epochObj.normCube[i0_indx, ii:jj].min()*10)/10.).compute()	
				extent  	= wavelambda[ii]-wavelambda[self.lineCore], wavelambda[jj]-wavelambda[self.lineCore], raw_min, raw_max

				# print([(raw_min, full_data[intrinsic_indx, ii:jj].min().compute()), (raw_max, full_data[intrinsic_indx, ii:jj].max().compute())])	
				o1Arr = _calc.pick_jth_label(labels[i0_indx], 1).astype(int)
				o1Lst = np.unique(o1Arr).astype(int)

				fig = plt.figure(layout="constrained", figsize=(int(np.max(nrows[i0Lst[j]-1])+1)*3, int(len(o1Lst))*3))
				
				gs  = GridSpec(int(len(o1Lst)), int(np.max(nrows[i0Lst[j]-1])+1), 
							left=0, right=1, top=1, bottom=0, 
							width_ratios=[1 for x in range(int(np.max(nrows[i0Lst[j]-1])+1))],
							height_ratios=[1 for x in range(int(len(o1Lst)))],
							figure=fig)


				for i in range(len(o1Lst)):
					ax      = plt.subplot(gs[o1Lst[i]-1, 0])
					o1_indx = i0_indx[np.where(o1Arr == o1Lst[i])[0]]
					indexs 	= self.epochObj.delayCube[o1_indx]
					aia_hist = indexs[np.where(~np.isnan(indexs))[0]]

					if len(aia_hist) > 0:
						# print(np.ceil(np.max(np.abs(np.array([aia_hist.min(), aia_hist.max()])))))
						
						hist, edges = _calc.numba_histogram(aia_hist, nbins, 
														lim=np.array([-xmax, xmax]))
					
						max_val = np.max(hist)
						ax.bar(edges[:-1], hist, 
								width=np.diff(edges), 
								edgecolor=None, align="edge", color=color_pallet[int(i0Lst[j])-1],
								linewidth=0.25)  
						ax.set_ylim([0, max_val])
						ax.set_title("N = {} | {}X".format(len(aia_hist), int(i0Lst[j])*10 + (i+1)))
						ax.set_xlim([-xmax, xmax])	

						if not gs[o1Lst[i]-1, 0].is_last_row():
							ax.tick_params(labelbottom=False)

						o2Arr = _calc.pick_jth_label(labels[o1_indx], 2).astype(int)					
						o2Lst = np.unique(o2Arr).astype(int)
						for k in range(len(o2Lst)):
							#print([j, i, k])
							# I, J    = [int(np.floor(k/nrows)), int(k % nrows)]
							ax      	= plt.subplot(gs[o1Lst[i]-1, k+1])
							o2_indx 	= o1_indx[np.where(o2Arr == o2Lst[k])[0]]
							indexs 		= self.epochObj.delayCube[o2_indx]
							aia_hist 	= indexs[np.where(~np.isnan(indexs))[0]]

							if len(aia_hist) > 0:
								hist, edges = _calc.numba_histogram(aia_hist, nbins, 
																lim=np.array([-xmax, xmax]))
								ax.bar(edges[:-1], hist, 
										width=np.diff(edges), edgecolor=None, color="black",
										linewidth=0.25, align='edge')    
								ax.set_ylim(0, max_val)
								ax.set_title("N = {} | {}".format(len(aia_hist), int(labels[o2_indx[0]])))
								
								ax.set_xlim([-xmax, xmax])
								ax.tick_params(labelleft=False)
								if not gs[o1Lst[i]-1,1+k].is_last_row():
									ax.tick_params(labelbottom=False)

								self.spectra_maps_time(o2_indx, labels, int(labels[o2_indx[0]]), [hist, edges], i0Lst)
							keyProgress.update(1)
						
				fig.suptitle("k-means results ({} {} || {}XX)".format(self.epochObj.visp_id, lineLabel, i0Lst[j]))   
				fig.savefig(self.figDir + "/timeDelay_{}.png".format(i0Lst[j]))

				pdf.savefig()
				plt.close()

		keyProgress.close()
		util.logg("msg", "Catalog Key Saved")	


	def spectra_maps_time(self, indx, labelFrame, label, time, i0Lst):
		hist, edges = time
		ii, jj = self.epochObj.spectralWindow
		wavelambda  = self.epochObj.waveFit

		raw_dat 	=  self.epochObj.normCube[indx.astype(np.uint32), ii:jj]
		centroid_i 	= raw_dat.sum(axis=0)/raw_dat.shape[0]

		mask_map = self.epochObj.unflatten(self.epochObj.mask_map)

		_, color_pallet = util._genColorPallet(len(i0Lst))

		color = color_pallet[int(int(str(label)[0])-1)]

		frameCube = self.epochObj.dataCube[..., ii:jj].sum(axis=-1)

		width =  [1./(self.aspect*self.alongSlitSize/self.rasterSize) + 0.25 , 0.5]

		fig = plt.figure(layout='constrained', figsize=(np.array(width).sum()*3, (1.2 + 1.2 + 1.2 + 0.75)*3))
		gs = fig.add_gridspec(4, 2,  width_ratios=width, height_ratios=(1, 0.5, 1, 1),
							left=0, right=1, top=1, bottom=0,
							wspace=0, hspace=0)
		
		raw_max = (np.ceil(self.epochObj.normCube[indx, ii:jj].max()*10)/10.).compute()
		raw_min = (np.floor(self.epochObj.normCube[indx, ii:jj].min()*10)/10.).compute()	


		ax1 = fig.add_subplot(gs[0, 0])
		temp_im 	= _calc.density_hist2d(raw_dat.compute(), 0.01, raw_max, raw_min)
		im = ax1.imshow(temp_im.T, 
					extent=[wavelambda[ii]-wavelambda[self.lineCore], wavelambda[jj]-wavelambda[self.lineCore], raw_min, raw_max], aspect='auto', origin='lower')    
		im.set_cmap(LinearSegmentedColormap.from_list('', ['white', color]))

		ax1.plot(wavelambda[ii:jj]-wavelambda[self.lineCore], centroid_i, color='black')
		ax1.axvline(x = 0, linestyle='dashed', color='black')

		ax1.set_xlabel(r"$\lambda - \lambda_{0}$ [$\AA$]")

		# ax2 = fig.add_subplot(132)

		kwargsDict = {"cmap": LinearSegmentedColormap.from_list('', ['white', 'white'])}
		ax2, im_chrom, _, = self.mapMake._mapGen(fig, gs[2, 0], np.ones(frameCube.shape), 
										  		aspect='auto',
												flareContour=mask_map, 
												aspectCheck=None, **kwargsDict)

		xx, yy = np.where(self.epochObj.unflatten(labelFrame) == label)

		ax2.scatter(xx,yy, zorder=0, color=color, s=1, marker='s')

		ax2.set_xlabel("Raster Direction [arcsec]")
		ax2.set_ylabel("Along Slit Direction [arcsec]")


		ax_histx = fig.add_subplot(gs[1, 0], sharex=ax2)
		ax_histy = fig.add_subplot(gs[2, 1], sharey=ax2)
		ax_histx.tick_params(axis="x", labelbottom=False)
		ax_histy.tick_params(axis="y", labelleft=False)
		ax_histy.tick_params(axis='x', labelbottom=True)

		ax_histx.hist(xx, bins=self.rasterSize, 
				range=[0, self.rasterSize], 
				rwidth=1, 
				histtype='step', 
				fill=False, color=color)
		ax_histy.hist(yy, bins=self.alongSlitSize, histtype='step', 
					range=[0, self.alongSlitSize], 
					rwidth=1, 
					orientation='horizontal', 
					color=color, fill=False)#, color=config.theme['primary'])   


		ax3 = fig.add_subplot(gs[3, 0])
		ax3.bar(edges[:-1], hist, 
				width=np.diff(edges), edgecolor=None, color=color,
				linewidth=0.25, align='edge')    
		ax3.set_ylim(0, hist.max())
		ax3.set_xlabel("$\Delta t$ [min]")
		# ax3.set_title("N = {} | {}".format(len(aia_hist), int(labels[o2_indx[0]])))
		
		ax3.set_xlim([-np.abs(edges).max(), np.abs(edges).max()])

		fig.savefig(self.figDir + "/3panel_summary_{}.png".format(label))
		plt.close()