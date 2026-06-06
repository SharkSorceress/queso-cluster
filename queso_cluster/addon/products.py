"""
	:file:  queso_cluster/addon/products.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>
"""

from . import style as sty
from .logg import loggTimer, logger
from ..atoms import aux as auxAtom
from ..atoms import scores as scoresAtom
from  ..runners import base as baseRun

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap


class Products:
	"""
	Detail

	Parameters
	----------
	quesoOut : type
		summary
	optLabels : type
		summary

	Attributes
	----------
	vindx : ndarray
		tuple of the indicies corresponding to non-nan labels
	vfindx : ndarray
		1D array containing the indicies of non-nan labels
	xlim : ndarray
		The physical minimum and maximum of the raster direction
	ylim : ndarray
		The physical minimum and maximum of the along slit direction
	aspect : float
		Half of the aspect ratio
	clusterCmap : :class:`~queso_cluster.addon.style.clusterColormap`
		default color configuration for cluster maps
	mapMake : :class:`~queso_cluster.addon.style.mapMaker`
		A map object to plot the data
		
	"""
	
	def __init__(self, quesoOut):

		self.quesoOut = quesoOut
		self.keepI0 = self.config.runners.config['keepI0']
		#self.ii, self.jj = self.quesoOut.spectralWindow
		
		self.load()

		#self.optLabels 	= optLabels
		self.optLabels[self.optLabels == 0] = np.nan
		self.vindx 	= np.where(~np.isnan(self.optLabels))#[0]
		#print(self.vindx.type)

		self.vfindx = np.ravel_multi_index(self.vindx, self.optLabels.shape)

		self.xlim = np.array([self.vindx[1].min(), self.vindx[1].max()])*self.quesoOut.deltas['pxlSlitWidth'].magnitude
		self.ylim = np.array([self.vindx[2].min(), self.vindx[2].max()])*self.quesoOut.deltas['pxlAlongSlit'].magnitude

		self.aspect = (np.diff(self.ylim)[0]/np.diff(self.xlim)[0])/2.
	
		self.clusterCmap = sty.clusterColormap(np.unique(self.optLabels[self.vindx]).astype(int).size)

		self.mapMake = sty.mapMaker(self.quesoOut.dimInfo, self.quesoOut.deltas)


	def load(self):
		loading = np.load("./{}.npz".format(self.flavor))
		print(loading)
		self.optLabels 				= loading['labelSquare']
		self.quesoOut.maskLine 		= loading['maskLine']
		self.quesoOut.prepSquare 	= loading['prepSquare']
		loading.close()

	def __getattr__(self, name):
		parentLst = [self.quesoOut]
		for p in parentLst:
			if hasattr(p, name):
				return getattr(p, name)
			else:
				continue
		raise AttributeError("No parents have object with attribute '%s'" % name)
	
	@loggTimer
	def clusterMapSequence(self, timeAxis=False):
		"""
		

		Parameters
		----------
		timeAxis : bool, optional
			Boolean to add an extra axis for time
		
		Returns
		-------
		figA : mpl.Figure
			Map of the cluster results for individual time steps
		figB : mpl.Figure
			Map of all distinct sequences

		"""
		
		if np.abs(np.diff(self.ylim)) > np.abs(np.diff(self.xlim)):
			figA, compoundLabels = self.clusterMapSequenceHorizontal(timeAxis)
		else:
			figA, compoundLabels = self.clusterMapSequenceVertical(timeAxis)
			
		figB = self.clusterMapCompound(compoundLabels, timeAxis)
		return(figA, figB)

	def clusterMapCompound(self, compoundLabels, timeAxis):	
		"""
		Creates a figure showing all of the distinct sequences of spectra

		Parameters
		----------
		compoundLabels : char.array
			Character array for all sequence labels
		timeAxis : bool
			Boolean to add an extra axis for time
		
		Returns
		-------
		fig : mpl.Figure
			Figure showing the distribution of cluster sequences

		"""	

		compoundLabels[~np.char.isalnum(compoundLabels)] = np.nan

		recountedCompoundLabels = np.zeros(compoundLabels.shape) + np.nan
		labelLst = np.unique(compoundLabels[:-1])
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			lindx = np.where(compoundLabels == labelLst[l])
			recountedCompoundLabels[lindx] = l+1
		
		labelLst = np.unique(recountedCompoundLabels)
		labelLst = labelLst[~np.isnan(labelLst)]

		if self.aspect < 1:
			fig = plt.figure(layout='compressed', figsize=(10, 5*self.aspect), dpi=300)
		else:
			fig = plt.figure(layout='compressed', figsize=(10, 10*self.aspect), dpi=300)

		gs = GridSpec(1, 2, figure=fig,  width_ratios=[1, 0.025], hspace=0, wspace=0)	
		compoundClusterCmap = sty.clusterColormap(np.unique(labelLst).astype(int).size)	
		#_, color_pallet = sty._genColorPallet(len(np.unique(labelLst)))
		#cmap = mpl.colors.ListedColormap(color_pallet)
		#cmap.set_bad("#FFFFFF")
		kwargsDict = {'cmap': compoundClusterCmap.cmap, 'norm': compoundClusterCmap.norm}
		ax, im  = self.mapMake._mapGen(fig, gs[0, 0], 
												recountedCompoundLabels,
												timeAxis=timeAxis, 
												#flareContour=self.mask_map, 
												**kwargsDict)
		ax.set_xlim(self.xlim)
		ax.set_ylim(self.ylim)
		ax.set_aspect("equal")

		cax = fig.add_subplot(gs[0, 1])
		cbar = fig.colorbar(im, spacing='uniform', 
					  ticks=compoundClusterCmap.bound_ticks,
					  orientation="vertical", cax=cax)
		return(fig)
	
	@loggTimer
	def clusterMapSequenceVertical(self, timeAxis):
		"""
		Vertically oriented maps of the cluster results for individual time steps
		
		Parameters
		----------
		compoundLabels : char.array
		timeAxis : bool
			Boolean to add an extra axis for time

		Returns
		-------
		fig : mpl.figure
			Map of the cluster results for individual time steps
		compoundLabels : np.char.array
			Character array for all sequence labels

		"""			
		ncols = self.optLabels.shape[0]
		#> Error?: Maximum number of clients reached		
		fig = plt.figure(layout='compressed', figsize=(2*ncols, 2*ncols/self.aspect), dpi=300)
		
		
		nrows = ncols
		ncols = 2
		height_ratios = [1 for x in range(nrows)]
		width_ratios = [1, 0.025]		
		gs = GridSpec(nrows, ncols, figure=fig, 
				height_ratios=height_ratios, width_ratios=width_ratios, hspace=0, wspace=0)



		labelLst = np.unique(self.optLabels[self.vindx]).astype(int)#.astype(str)
		# tLabels = np.unique(self.optLabels)
		

		#actual_bounds, bound_ticks, color_pallet = sty.cbar_bounds()
		#cmap = mpl.colors.ListedColormap(color_pallet)
		#norm = mpl.colors.BoundaryNorm(actual_bounds, cmap.N+1)

		compoundLabels = np.zeros(self.optLabels.shape[1:], dtype=str)

		recountedLabels = np.zeros(self.optLabels.shape) + np.nan
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			lindx = np.where(self.optLabels == labelLst[l])
			recountedLabels[lindx] = l+1

		for t in range(self.optLabels.shape[0]):
			kwargsDict = {'cmap': self.clusterCmap.cmap, 'norm': self.clusterCmap.norm}
			ax, im  = self.mapMake._mapGen(fig, gs[t, 0], 
												recountedLabels[t, ...],
												timeAxis=timeAxis, 
												#flareContour=self.mask_map, 
												**kwargsDict)
			ax.set_xlim(self.xlim)
			ax.set_ylim(self.ylim)

			ax.set_aspect("equal")

			if not gs[t, 0].is_last_row():
				ax.set_xticklabels([])

			#cbar = fig.colorbar(im, cax=cax, ticks=bounds_ticks)#, label='Binned Intensity')
				#
			# cbar.ax.set_yticklabels(["{}XX".format(int(x)) for x in recountLst])
			compoundLabels = np.char.add(compoundLabels, np.char.zfill(recountedLabels[t, ...].astype(np.uint).astype(str), 2))
		
		cax = fig.add_subplot(gs[:, 1])
		cbar = fig.colorbar(im, spacing='uniform',
									ticks=self.clusterCmap.bound_ticks, orientation="vertical",
									cax=cax)
		cbar.ax.set_yticklabels(["{}".format(int(x)) for x in np.unique(labelLst)])
		return(fig, compoundLabels)
	
	@loggTimer
	def clusterMapSequenceHorizontal(self, timeAxis):
		"""
		Horizontal oriented maps of the cluster results for individual time steps
		
		Parameters
		----------
		compoundLabels : char.array
		timeAxis : bool
			Boolean to add an extra axis for time

		Returns
		-------
		fig : mpl.figure
			Map of the cluster results for individual time steps
		compoundLabels : np.char.array
			Character array for all sequence labels
			
		"""	
			
		ncols = self.optLabels.shape[0]
		#> Error?: Maximum number of clients reached		
		fig = plt.figure(layout='compressed', figsize=(2*ncols, ncols*self.aspect), dpi=300)
		
		nrows = 2
		height_ratios=[0.025, 1]
		width_ratios = [1 for x in range(ncols)]
		gs = GridSpec(nrows, ncols, figure=fig, 
				height_ratios=height_ratios, width_ratios=width_ratios, hspace=0, wspace=0)


		labelLst = np.unique(self.optLabels[self.vindx]).astype(int)#.astype(str)
		# tLabels = np.unique(self.optLabels)
		# actual_bounds, bound_ticks, color_pallet = sty.cbar_bounds(list(labelLst[~np.isnan(labelLst)]))
		# cmap = mpl.colors.ListedColormap(color_pallet)
		# norm = mpl.colors.BoundaryNorm(actual_bounds, cmap.N+1)

		compoundLabels = np.zeros(self.optLabels.shape[1:], dtype=str)

		recountedLabels = np.zeros(self.optLabels.shape) + np.nan
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			lindx = np.where(self.optLabels == labelLst[l])
			recountedLabels[lindx] = l+1

		for t in range(self.optLabels.shape[0]):
			kwargsDict = {'cmap': self.clusterCmap.cmap, 'norm': self.clusterCmap.norm}
			ax, im  = self.mapMake._mapGen(fig, gs[1, t], 
												recountedLabels[t, ...],
												timeAxis=timeAxis, 
												#flareContour=self.mask_map, 
												**kwargsDict)
			ax.set_xlim(self.xlim)
			ax.set_ylim(self.ylim)
			ax.set_aspect("equal")

			if not gs[0, t].is_first_col():
				ax.set_yticklabels([])

			#cbar = fig.colorbar(im, cax=cax, ticks=bounds_ticks)#, label='Binned Intensity')
				#
			# cbar.ax.set_yticklabels(["{}XX".format(int(x)) for x in recountLst])
			compoundLabels = np.char.add(compoundLabels, np.char.zfill(recountedLabels[t, ...].astype(np.uint).astype(str), 2))
		
		cax = fig.add_subplot(gs[0, :])
		cbar = fig.colorbar(im, spacing='uniform',
									ticks=self.clusterCmap.bound_ticks, orientation="horizontal",
									cax=cax)
		cbar.ax.set_xticklabels(["{}".format(int(x)) for x in np.unique(labelLst)])
		

		return(fig, compoundLabels)

	@loggTimer
	def figure03(self):
#> detail: 
#> param type self:
#> return (type): 
#> test-method:

		width = [2, 0.025]
		types = ['intensity', 'labels']
		for t in range(len(types)):

			fig = plt.figure(layout='compressed', figsize=(2*4, 3.25*4), dpi=300)

			gs = GridSpec(3,2, figure=fig, width_ratios=width, height_ratios=[1, 1, 1], hspace=0, wspace=0)


			intrinsicConfig = self.config.srcLst.clusterConfig['intrinsic']
			for i in range(len(intrinsicConfig)):
				match intrinsicConfig[i]['label']:
					case 'window':
						moment0 = self.quesoOut.instrumentObj.dataSquare[:, self.ii:self.jj+1].mean(axis=-1).compute()
						bins = intrinsicConfig[i]['layerConfig']['bins']
						cbar_label = "Mean Window Intensity"
					case 'continuum':
						moment0 = self.quesoOut.instrumentObj.dataSquare[:, self.quesoOut.continuum].compute()
						bins = intrinsicConfig[i]['layerConfig']['bins']
						cbar_label = "Continuum Intensity"

				intrinsicLayerMap = baseRun.runIntrinsic(len(np.diff(bins)), np.floor(moment0*100)/100., 
											  edgeOverride=np.array(bins).astype(float))

				
				match types[t]:
					case 'intensity':
						present = moment0
						cmap = 'Greys_r'
					case 'labels':
						instrinsicCmap = sty.clusterColormap(np.unique(intrinsicLayerMap).size)
						present = intrinsicLayerMap
						cmap = instrinsicCmap.cmap
						norm = instrinsicCmap.norm
						#cmap = mpl.colors.ListedColormap(color_pallet)
						#norm = mpl.colors.BoundaryNorm(np.array(bins).astype(float), cmap.N)

				kwargsDict = {'cmap': cmap}
				# if i > np.inf:
				# 	ax, im, tax = self.mapMake._mapGen(fig, gs[i, 0], 
				# 									present,
				# 									timeAxis=True,
				# 									#flareContour=self.mask_map, 
				# 									**kwargsDict)

				# 	ax.set_xlabel("Raster Direction [arcseconds]")
				# 	tax.set_xlabel('Time  [hours after 20:02:42 UTC]')	
				# else:
				ax, im = self.mapMake._mapGen(fig, gs[i, 0], 
												present,
												#flareContour=self.mask_map, 
												**kwargsDict)

				ax.set_xticklabels([])
				ax.set_aspect("equal")
				ax.set_ylabel("Along Slit Direction [arcseconds]")

				#ax.text(20, 2250, " ({})".format(self.alphaLst[i]), va="center", ha="center", bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25', alpha=0.3), font='monospace')
				# ax.annotate('({})'.format(self.alphaLst[i]),
            	# 	xy=(0.035, 1-0.05), xycoords='axes fraction',
				# 	xytext=(0.035, 1-0.05), textcoords='axes fraction', fontfamily='sans-serif',
            	# 	va='center', ha='center', bbox=dict(boxstyle='square', facecolor='white', edgecolor='black', alpha=0.4))
				
				cax = fig.add_subplot(gs[i, 1])
				match types[t]:
					case 'intensity':
						im_cbar = im
					case 'labels':
						im_cbar = mpl.cm.ScalarMappable(norm=norm, cmap=cmap)
				cbar = fig.colorbar(im_cbar, cax=cax, spacing='uniform', label=cbar_label)

			intrinsicLayerMap_oldCount = auxAtom.pick_jth_label(self.optLabels[self.vindx], 0).astype(float)
			intrinsicLayerMap = np.zeros(self.optLabels.shape) + np.nan
			recountLst = np.unique(intrinsicLayerMap_oldCount)
			for rc in range(recountLst.size):
				lindx = np.where(intrinsicLayerMap_oldCount == recountLst[rc])[0]
				intrinsicLayerMap[self.vindx[lindx]] = rc+1


			compoundInstrinsicColor = sty.clusterColormap(np.unique(intrinsicLayerMap[self.vindx]).size)
			# actual_bounds, bound_ticks, color_pallet = sty.cbar_bounds(list())
			# cmap = mpl.colors.ListedColormap(color_pallet)
			# norm = mpl.colors.BoundaryNorm(actual_bounds, cmap.N+1)

			kwargsDict = {'cmap': compoundInstrinsicColor.cmap, "norm": compoundInstrinsicColor.norm}
			ax, im, tax = self.mapMake._mapGen(fig, gs[-1, 0], 
												intrinsicLayerMap,
												timeAxis=True, 
												#flareContour=self.mask_map, 
												**kwargsDict)
			cax = fig.add_subplot(gs[-1, 1])
			ax.set_aspect("equal")

			#cbar = fig.colorbar(im, cax=cax, ticks=bounds_ticks)#, label='Binned Intensity')
			cbar = fig.colorbar(im, spacing='proportional',
									ticks=compoundInstrinsicColor.bound_ticks,
									cax=cax, label='Intrinsic bins')
			cbar.ax.set_yticklabels(["{}XX".format(int(x)) for x in recountLst])

			ax.set_xlabel("Raster Direction [arcseconds]")
			tax.set_xlabel('Time  [hours after 20:02:42 UTC]')
			ax.set_ylabel("Along Slit Direction [arcseconds]")

			#ax.text(20, 2250, " ({})".format(self.alphaLst[2]), va="center", ha="center", bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.25', alpha=0.3))
			# ax.annotate('({})'.format(self.alphaLst[2]),
            # 		xy=(0.035, 1-0.05), xycoords='axes fraction',
			# 		xytext=(0.035, 1-0.05), textcoords='axes fraction', fontfamily='sans-serif',
            # 		va='center', ha='center', bbox=dict(boxstyle='square', facecolor='white', edgecolor='black', alpha=0.4))

			#print(self.figDir + 'figure03_{}.pdf'.format(types[t]))
			fig.savefig('./figure03_{}.png'.format(types[t]))
			#fig.savefig(self.figDir + 'figure03_{}.pdf'.format(types[t]))


	@loggTimer
	def clusterProfiles(self, dev=False, showContinuum=True):
		"""
		Figure showing the representative profiles of each of the clusters and the raw data histogram
		
		Parameters
		----------
		showContinuum : bool, optional
			Adds a horizontal line at the continuum. Useful only if normalized to continuum
		dev : bool
			secret testing

		Returns
		-------
		fig : mpl.figure
			Figure 		
			
		"""	
		
		ii, jj = [self.ii, self.jj]
		#self.quesoOut.prepSquare = self.quesoOut.prepSquare.persist()

		if hasattr(self.quesoOut, "waveFit"):
			wavelambda  = self.quesoOut.waveFit.magnitude
			wavelambda -= wavelambda[self.lineCenter]
			waveUnit = self.quesoOut.waveFit.units
		else:
			print(self.quesoOut.shape)
			wavelambda = np.arange(self.quesoOut.shape[3])
			waveUnit = "index"

		validLabels = self.optLabels[self.vindx]

		i0Arr = auxAtom.pick_jth_label(validLabels, 0)

		i0o1Arr = auxAtom.pick_jth_label(validLabels, 0)*10 + auxAtom.pick_jth_label(validLabels, 1)

		i0o1Lst = np.unique(i0o1Arr)
		nrows = len(i0o1Lst)
		ncols = 1 + auxAtom.pick_jth_label(validLabels, 2).max()

		fig = plt.figure(layout='constrained', figsize=((ncols + 0.2)*3, nrows*3), dpi=300)
		
		gs  = GridSpec(nrows, ncols + 1, 
					left=0, right=1, top=1, bottom=0, 
					width_ratios=[1 for x in range(ncols)] + [0.2],
					height_ratios=[1 for x in range(nrows)],
					figure=fig)			

		print(self.quesoOut.prepSquare.shape)
		raw_max = (np.ceil(np.nanmax(self.quesoOut.prepSquare[self.vfindx, ii:jj+1])*10)/10.)#.compute()
		raw_min = (np.floor(np.nanmin(self.quesoOut.prepSquare[self.vfindx, ii:jj+1])*10)/10.)#.compute()	
		extent  	= wavelambda[ii], wavelambda[jj], raw_min, raw_max



		color = "black"
		panel_bounds = []
		bounds_ticker = int(str(i0o1Lst[0])[0])
		for j in range(len(i0o1Lst)):
			i0_indx = np.where(i0o1Arr == i0o1Lst[j])[0]

			ax0      = plt.subplot(gs[j, 0])
			ax0 = self.spectralEntry(ax0, i0_indx, color, wavelambda, extent, showContinuum)
			if gs[j,0].is_last_row():
				#ax0.set_xlabel(r"$\lambda-\lambda_{0}$ [$\mathrm{\AA}$]")
				ax0.set_xlabel(r"$\lambda-\lambda_{0}$" +  " [{}]".format(waveUnit))
			ax0.tick_params(labelleft=True)
			#axR0.tick_params(labelright=False)
			if not gs[j, 0].is_last_row():
				ax0.tick_params(labelbottom=False)
		
			if bounds_ticker != int(str(i0o1Lst[j])[0]):
				trans = mpl.transforms.blended_transform_factory(ax0.transData, fig.transFigure)
				panel_bounds.append([-extent[0], ax0.get_position().bounds[2], j, trans])

			bounds_ticker = int(str(i0o1Lst[j])[0])

			o2Arr = auxAtom.pick_jth_label(validLabels[i0_indx], 2).astype(int)					
			o2Lst = np.unique(o2Arr).astype(int)
			for k in range(len(o2Lst)):
				ax      	= plt.subplot(gs[j, k+1])
				o2_indx 	= i0_indx[np.where(o2Arr == o2Lst[k])[0]]

				#sArr = auxAtom.pick_jth_label(validLabels[o2_indx], 0)
				#sindx = np.where(i0Arr == sArr[0])[0]

				score = 0#scoresAtom.calcSingleSilhouetteScore(self.quesoOut.prepSquare[sindx.astype(np.uint32), ii:jj+1].compute(), validLabels[sindx.astype(np.uint32)], validLabels[o2_indx[0]])
				ax = self.spectralEntry(ax, o2_indx, color, wavelambda, extent, showContinuum, scores=score)
				if gs[j,k+1].is_last_row():
					ax.set_xlabel(r"$\lambda-\lambda_{0}$" +  " [{}]".format(waveUnit))	
				else:
					ax.tick_params(labelbottom=False)				
										
				ax.tick_params(labelleft=False)
				# if dev and not gs[j, k+1].is_last_col():
				# 	axR.tick_params(labelright=False)



		return(fig)

	def spectralEntry(self, ax, indx, color, wavelambda, extent, showContinuum, scores=None, dev=False):
		"""
		Calculation function for :func:`~queso_cluster.addon.products.Products.clusterProfiles`
		
		Parameters
		----------
		ax : mpl.Axes
			matplotlib axes to add content to
		indx : ndarray
			1D array of data indexes for a given cluster
		color : str
			color string for 2D histogram of raw data. gradient goes as white -> color
		wavelambda : ndarray
			1D array containing the wavelength
		extent : list
			List containing the left, right, bottom, top of the content
		showContinuum : bool
			Adds a horizontal line at the continuum. Useful only if normalized to continuum
		scores : float, optional
			Validation score to be shown in the figure window
		dev : bool, optional
			secret testing

		Returns
		-------
		ax : mpl.Axes
			Updated axis with all the content added
			
		"""	
		ii, jj = [self.ii, self.jj]
		raw_dat = self.quesoOut.prepSquare[self.vfindx[indx.astype(np.uint32)], ii:jj+1]
		centroid_i = raw_dat.sum(axis=0)/raw_dat.shape[0]	

		if dev:
			resolvingIndex = scoresAtom.calcSingleResolvingIndex(raw_dat)
			centroid_min, centroid_max = np.quantile(raw_dat, [0.25, 0.75], axis=0)			
			axR = ax.twinx()
			axR.set_ylim([-1, 1])
			axR.plot(wavelambda[ii:jj+1], resolvingIndex, color='red', linestyle='dashed', linewidth=0.75)
			ax.plot(wavelambda[ii:jj+1], centroid_min, color='blue', linewidth=0.75)
			ax.plot(wavelambda[ii:jj+1], centroid_max, color='blue', linewidth=0.75)
			logger.debug("Resolving Index: {}".format(np.mean(np.abs(resolvingIndex))))
		ax.plot(wavelambda[ii:jj+1], centroid_i, color='black', linewidth=0.75)

		# im = ax.hist2d(raw_dat, bins=[0.01, wavelambda[ii:jj+1]-wavelambda[self.lineCenter]])
		temp_im 	= auxAtom.density_hist2d(raw_dat, 0.01, extent[3], extent[2])

		ww, insty = np.meshgrid(wavelambda[ii:jj+1+1], np.arange(extent[2], extent[3], 0.01))
		im = ax.pcolormesh(ww, insty, temp_im.T, cmap=LinearSegmentedColormap.from_list('', ['white', color]))

		ax.axvline(x = wavelambda[self.lineCenter], linestyle='dashed', color='black')

		tindx = self.vindx[0][indx]
		xindx = self.vindx[1][indx]
		yindx = self.vindx[2][indx]
		labelLst = np.unique(self.optLabels[tindx, xindx, yindx]).astype(int).astype(str)
		commonLabel = [labelLst[0][j] for j in range(len(labelLst[0])) if np.unique([a[j] for a in [list(x) for x in labelLst]]).size == 1]
		#print(commonLabel)
		label = "{}{}".format(int("".join(commonLabel)), "X"*(len(labelLst[0]) - len(commonLabel)))
		ax.annotate("{}".format(label),
			xy=(0.01, 1-0.05), xycoords='axes fraction',
			xytext=(0.01, 1-0.05), textcoords='axes fraction', fontfamily='sans-serif',
			va='center', ha='left')
		
		ax.annotate("N={}".format(len(indx)),
            		xy=(0.01, 1-0.1), xycoords='axes fraction',
					xytext=(0.01, 1-0.1), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')

		if not (scores is None):
			ax.annotate("S={:.3f}".format(float(scores)),
            		xy=(0.01, 1-0.15), xycoords='axes fraction',
					xytext=(0.01, 1-0.15), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')				

			
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=1))
		

		return(ax)
