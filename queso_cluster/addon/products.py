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
from ..atoms import error as errorAtom
from ..atoms import norm as normAtom

from  .. import base as baseMain

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap

from sklearn import metrics

import copy

class Products:
	"""
	Detail

	Parameters
	----------
	quesoOut : :class:`~queso_cluster.ti.timeIndependent` or :class:`~queso_cluster.td.timeDependent`
		Analysis object that stores all of the configuration
		
		
	"""
	
	def __init__(self, quesoOut):

		self._quesoOut 	= quesoOut


		self.load()


		self.optLabels[self.optLabels == 0] = np.nan
		self.vindx 	= np.where(~np.isnan(self.optLabels))#[0]

		self.vfindx = np.ravel_multi_index(self.vindx, self.optLabels.shape)

		ii, jj = [self._quesoOut._config.blueEdge, self._quesoOut._config.redEdge]

		#print(self.vfindx)

		if self.vfindx.size == 0:
			raise errorAtom.OopsAllNan()
	
		self._raw_max = (np.ceil(np.nanmax(self._quesoOut.prepSquare[self.vfindx, self._quesoOut.waveGrid[:, None]])*100)/100.)
		self._raw_min = (np.floor(np.nanmin(self._quesoOut.prepSquare[self.vfindx, self._quesoOut.waveGrid[:, None]])*100)/100.)	

		if hasattr(self._quesoOut._config, "waveFitFunc"):
			waveFit	= self._quesoOut._config.waveFitFunc(self._quesoOut._instrumentObj.nSpectral+1).to('angstrom')
			self._wavelambda = waveFit.magnitude
			self._wavelambda -= self._wavelambda[self._quesoOut._config.lineCenter]
			if waveFit.units == "angstrom":
				self._waveUnit = r"\textrm{\AA}"
			#print(self._waveUnit)
		else:
			self._wavelambda = np.arange(self._quesoOut._instrumentObj.dataPrism.shape[2])
			self._waveUnit = "index"


		self._extent  = self._wavelambda[ii], self._wavelambda[jj], self._raw_min, self._raw_max

		# if len(self.vindx) == 2:
		self.xlim = np.array(self._quesoOut._config.runnerConfig['bbox'][:2])*self._quesoOut._instrumentObj.pxlDelta['pxlSlitWidth'].magnitude
		self.ylim = np.array(self._quesoOut._config.runnerConfig['bbox'][2:])*self._quesoOut._instrumentObj.pxlDelta['pxlAlongSlit'].magnitude
		# elif len(self.vindx) == 3:
		# 	self.xlim = np.array([self.vindx[1].min(), self.vindx[1].max()])*self._quesoOut._instrumentObj.pxlDelta['pxlSlitWidth'].magnitude
		# 	self.ylim = np.array([self.vindx[2].min(), self.vindx[2].max()])*self._quesoOut._instrumentObj.pxlDelta['pxlAlongSlit'].magnitude



		print([self.xlim, self.ylim])

		self.aspect = np.diff(self.xlim)[0]/np.diff(self.ylim)[0]
	
		self.clusterCmap = sty.clusterColormap(np.unique(self.optLabels[self.vindx]).astype(int))

		self.mapMake = sty.mapMaker(self._quesoOut._instrumentObj)


	def load(self):
		loading = np.load("./{}/{}.npz".format(self._quesoOut._config.directoryFlavor, self._quesoOut._config.flavor))
		logger.info(loading)
		self.optLabels 				= loading['labelSquare']
		self._quesoOut.maskLine 	= loading['maskLine']
		self._quesoOut.prepSquare 	= loading['prepSquare']
		loading.close()
	
	@loggTimer
	def clusterMapSequence(self, timeAxis=False, intrinsic=False):
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
			figA = self.clusterMapSequenceHorizontal(timeAxis, intrinsic)
		else:
			figA = self.clusterMapSequenceVertical(timeAxis, intrinsic)
			
		#figB = self.clusterMapCompound(compoundLabels, timeAxis)
		return(figA)
	

	@loggTimer
	def intensityMapSequence(self, timeAxis=False, **kwargs):

		if np.abs(np.diff(self.ylim)) > np.abs(np.diff(self.xlim)):
			figA = self.intensityMapSequenceHorizontal(timeAxis, **kwargs)
		else:
			figA = self.intensityMapSequenceVertical(timeAxis)
			
		#figB = self.clusterMapCompound(compoundLabels, timeAxis)
		return(figA)
	

	def intensityMapSequenceHorizontal(self, timeAxis, **kwargs):
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
		fig = plt.figure(layout='compressed', figsize=(3*ncols, (3*ncols*self.aspect) * 1.2), dpi=300)
		
		nrows = 2
		height_ratios=[0.025, 1]
		width_ratios = [1 for x in range(ncols)]
		gs = GridSpec(nrows, ncols, figure=fig, 
				height_ratios=height_ratios, width_ratios=width_ratios, hspace=0, wspace=0)


		intensitySequence = np.nanmean(self._quesoOut._instrumentObj.dataPrism[self._quesoOut._config.timeFrames, ..., 
																		 self._quesoOut._config.blueEdge:self._quesoOut._config.redEdge], axis=-1)
		intensitySequence = intensitySequence.reshape(self._quesoOut._config.timeFrames.size, 
														self._quesoOut.geometry['rasterSize'], 
														self._quesoOut.geometry['alongSlitSize'])
		print(intensitySequence.shape)

		for t in range(self.optLabels.shape[0]):
			kwargs['cmap'] = "Greys_r"
			ax, im  = self.mapMake._mapGen(fig, gs[1, t], 
												intensitySequence[t, ...],
												timeAxis=timeAxis, 
												#xlim=self.xlim,
												#ylim=self.ylim,
												#flareContour=self.mask_map, 
												**kwargs)
			if not gs[0, t].is_first_col():
				ax.set_yticklabels([])

		cax = fig.add_subplot(gs[0, :])
		cbar = fig.colorbar(im, spacing='uniform',
									orientation="horizontal",
									cax=cax)

		#cbar.minorticks_off()
		

		return(fig)#, compoundLabels)		



	def intensityMapSequenceVertical(self, timeAxis, **kwargs):
		"""
		Vertical oriented maps of the cluster results for individual time steps
		
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
		fig = plt.figure(layout='constrained', figsize=((3*self.aspect)*1.2, 3*ncols), dpi=300)
		
		
		nrows = ncols
		ncols = 2
		height_ratios = [1 for x in range(nrows)]
		width_ratios = [1, 0.025]		
		gs = GridSpec(nrows, ncols, figure=fig, 
				height_ratios=height_ratios, width_ratios=width_ratios, hspace=0, wspace=0)


		intensitySequence = np.nanmean(self._quesoOut._instrumentObj.dataPrism[self._quesoOut._config.timeFrames, ..., 
																		 self._quesoOut._config.blueEdge:self._quesoOut._config.redEdge], axis=-1)
		intensitySequence = intensitySequence.reshape(self._quesoOut._config.timeFrames.size, 
														self._quesoOut.geometry['rasterSize'], 
														self._quesoOut.geometry['alongSlitSize'])
		print(intensitySequence.shape)

		for t in range(self.optLabels.shape[0]):
			kwargs['cmap'] = "Greys_r"
			ax, im  = self.mapMake._mapGen(fig, gs[t, 0], 
												intensitySequence[t, ...],
												timeAxis=timeAxis, 
												#xlim=self.xlim,
												#ylim=self.ylim,
												#flareContour=self.mask_map, 
												**kwargs)
			if not gs[t, 0].is_last_row():
				ax.set_xticklabels([])

		cax = fig.add_subplot(gs[:, 1])
		cbar = fig.colorbar(im, spacing='uniform',
									orientation="horizontal",
									cax=cax)

		#cbar.minorticks_off()
		

		return(fig)#, compoundLabels)		


	def clusterMapCompound(self, compoundLabels, timeAxis=False):	
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

		#compoundLabels[~np.char.isalnum(compoundLabels)] = np.nan

		maskSquare = self._quesoOut.maskLine.reshape((self.optLabels.shape[0], *compoundLabels.shape)).sum(axis=0)
		maskSquare[maskSquare > 0] = True
		maskSquare[maskSquare == 0] = False
		compoundLabels[maskSquare] = 'X'
		#compoundLabels *= maskSquare


		recountedCompoundLabels = np.zeros(compoundLabels.shape) + np.nan
		labelLst = np.unique(compoundLabels)
		lcounter = 1
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			if labelLst[l] == 'X':
				continue

			lindx = np.where(compoundLabels == labelLst[l])
			if len(lindx[0]) > 3:
				recountedCompoundLabels[lindx] = lcounter
				lcounter += 1
		
		boxNew = np.where(np.isfinite(recountedCompoundLabels))
		xlim = np.array([np.max([self.xlim[0], (boxNew[0].min())*self._quesoOut._instrumentObj.pxlDelta['pxlSlitWidth'].magnitude]), 
				   		 np.min([self.xlim[1], (boxNew[0].max())*self._quesoOut._instrumentObj.pxlDelta['pxlSlitWidth'].magnitude])])
		ylim = np.array([np.max([self.ylim[0], (boxNew[1].min())*self._quesoOut._instrumentObj.pxlDelta['pxlAlongSlit'].magnitude]), 
				   		 np.min([self.ylim[1], (boxNew[1].max())*self._quesoOut._instrumentObj.pxlDelta['pxlAlongSlit'].magnitude])])

		boxAspect = np.diff(xlim)[0]/np.diff(ylim)[0]

		#self.clusterProfilesCompound(recountedCompoundLabels)
		labelLst = np.unique(recountedCompoundLabels)
		labelLst = labelLst[~np.isnan(labelLst)]

		# if self.aspect <= 1:
		# 	fig = plt.figure(layout='compressed', figsize=(10, 10*self.aspect), dpi=300)
		# else:
		fig = plt.figure(layout='compressed', figsize=(10*boxAspect, 10), dpi=300)

		gs = GridSpec(1, 2, figure=fig,  width_ratios=[1, 0.025], hspace=0, wspace=0)
		compoundClusterCmap = sty.clusterColormap(np.unique(labelLst).astype(int))	
		kwargsDict = {'cmap': compoundClusterCmap.cmap, 'norm': compoundClusterCmap.norm}
		ax, im  = self.mapMake._mapGen(fig, gs[0, 0], 
												recountedCompoundLabels,
												timeAxis=timeAxis, 
												xlim=xlim,
												ylim=ylim,
												#flareContour=self.mask_map, 
												**kwargsDict)

		cax = fig.add_subplot(gs[0, 1])
		cbar = fig.colorbar(im, spacing='uniform', 
					  orientation="vertical", cax=cax)
		cbar.minorticks_off()
		cbar.set_ticks(compoundClusterCmap.bound_ticks, labels=compoundClusterCmap.tickLabels) 
		return(fig)
	
	@loggTimer
	def clusterProfilesCompound(self, compoundLabels):
		labelLst = np.unique(compoundLabels)

		ncols = self.optLabels.shape[0]
		lcounter = 1
		for ll in range(labelLst.size):
			if labelLst[ll] == "X":
				continue
			indx2D = np.where(compoundLabels == labelLst[ll])

			if indx2D[0].size > 3:

				fig = plt.figure(layout='constrained', figsize=((ncols + 0.2)*3, 1*3), dpi=300)
			
				gs  = GridSpec(1, ncols + 1, 
						left=0, right=1, top=1, bottom=0, 
						width_ratios=[1 for x in range(ncols)] + [0.2],
						height_ratios=[1 for x in range(1)],
						figure=fig)		

				ymin = np.inf
				ymax = -np.inf
				for oo in range(ncols):
					indx = np.ravel_multi_index((oo*np.ones(indx2D[0].size, dtype=int), *indx2D), 
									self.optLabels.shape)
					ymin = np.nanmin([ymin, np.nanmin(self._quesoOut.prepSquare[indx,self._quesoOut._config.blueEdge:self._quesoOut._config.redEdge])])
					ymax = np.nanmax([ymax, np.nanmax(self._quesoOut.prepSquare[indx,self._quesoOut._config.blueEdge:self._quesoOut._config.redEdge])])


				print([ymin, ymax])

				for oo in range(ncols):
					indx = np.ravel_multi_index((oo*np.ones(indx2D[0].size, dtype=int), *indx2D), 
									self.optLabels.shape)


					ax  = plt.subplot(gs[0, oo])
					
					ax  = self.spectralEntry(ax, indx, scale=np.ceil((ymax-ymin)/50 * 1000)/1000)


					if not gs[0, oo].is_first_col():
						ax.set_yticklabels([])
					ax.set_xlabel(r"$\lambda-\lambda_{0}$" +  " [{}]".format(self._waveUnit))	
					ax.set_ylim([np.floor(ymin*1000)/1000., np.ceil(ymax*1000)/1000])
					

				fig.savefig("./{}/sequences/labelTest_{}.pdf".format(self._quesoOut._config.directoryFlavor, int(lcounter)))
				lcounter += 1
			plt.close()

	def clusterMapSequenceVertical(self, timeAxis, intrinsic):
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
		fig = plt.figure(layout='constrained', figsize=((3*self.aspect)*1.2, 3*ncols), dpi=300)
		
		
		nrows = ncols
		ncols = 2
		height_ratios = [1 for x in range(nrows)]
		width_ratios = [1, 0.025]		
		gs = GridSpec(nrows, ncols, figure=fig, 
				height_ratios=height_ratios, width_ratios=width_ratios, hspace=0, wspace=0)


		labelArr = copy.copy(self.optLabels)
		clusterCmap = copy.copy(self.clusterCmap)
		if intrinsic:
			labelArr[self.vindx] = auxAtom.pick_jth_label(self.optLabels[self.vindx], 0)
			clusterCmap = sty.clusterColormap(np.unique(labelArr[self.vindx]).astype(int))

		labelLst = np.unique(labelArr[self.vindx]).astype(int)
		

		#actual_bounds, bound_ticks, color_pallet = sty.cbar_bounds()
		#cmap = mpl.colors.ListedColormap(color_pallet)
		#norm = mpl.colors.BoundaryNorm(actual_bounds, cmap.N+1)

		#compoundLabels = np.zeros(self.optLabels.shape[1:], dtype=str)

		recountedLabels = np.zeros(labelArr.shape) + np.nan
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			if not np.isnan(labelLst[l]):
				lindx = np.where(labelArr == labelLst[l])
				recountedLabels[lindx] = l+1

		for t in range(self.optLabels.shape[0]):
			kwargsDict = {'cmap': clusterCmap.cmap, 'norm': clusterCmap.norm}
			ax, im  = self.mapMake._mapGen(fig, gs[t, 0], 
												recountedLabels[t, ...],
												timeAxis=timeAxis, 
												xlim=self.xlim,
												ylim=self.ylim,
												#flareContour=self.mask_map, 
												**kwargsDict)

			if not gs[t, 0].is_last_row():
				ax.set_xticklabels([])

			#cbar = fig.colorbar(im, cax=cax, ticks=bounds_ticks)#, label='Binned Intensity')
				#
			# cbar.ax.set_yticklabels(["{}XX".format(int(x)) for x in recountLst])
			#compoundLabels = np.char.add(compoundLabels, np.char.zfill(recountedLabels[t, ...].astype(np.uint).astype(str), 2))
		
		cax = fig.add_subplot(gs[:, 1])
		cbar = fig.colorbar(im, spacing='uniform',
									ticks=clusterCmap.bound_ticks, orientation="vertical",
									cax=cax)
		cbar.ax.set_yticklabels(["{}".format(int(x)) for x in np.unique(labelLst)])
		cbar.minorticks_off()
		return(fig)
	
	def clusterMapSequenceHorizontal(self, timeAxis, intrinsic):
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
		fig = plt.figure(layout='compressed', figsize=(3*ncols, (3*ncols*self.aspect) * 1.2), dpi=300)
		
		nrows = 2
		height_ratios=[0.025, 1]
		width_ratios = [1 for x in range(ncols)]
		gs = GridSpec(nrows, ncols, figure=fig, 
				height_ratios=height_ratios, width_ratios=width_ratios, hspace=0, wspace=0)

		labelArr = copy.copy(self.optLabels)
		clusterCmap = copy.copy(self.clusterCmap)
		if intrinsic:
			labelArr[self.vindx] = auxAtom.pick_jth_label(self.optLabels[self.vindx], 0)
			clusterCmap = sty.clusterColormap(np.unique(labelArr[self.vindx]).astype(int))

		labelLst = np.unique(labelArr[self.vindx]).astype(int)
		#labelLst = np.unique(self.optLabels[self.vindx]).astype(int)#.astype(str)
		# tLabels = np.unique(self.optLabels)
		# actual_bounds, bound_ticks, color_pallet = sty.cbar_bounds(list(labelLst[~np.isnan(labelLst)]))
		# cmap = mpl.colors.ListedColormap(color_pallet)
		# norm = mpl.colors.BoundaryNorm(actual_bounds, cmap.N+1)


		#compoundLabels = np.zeros(self.optLabels.shape[1:], dtype=str)

		recountedLabels = np.zeros(labelArr.shape) + np.nan
		for l in range(labelLst.size):
			#for t in range(self.optLabels.shape[0]):
			lindx = np.where(labelArr == labelLst[l])
			recountedLabels[lindx] = l+1

		print(recountedLabels.shape)

		for t in range(self.optLabels.shape[0]):
			kwargsDict = {'cmap': clusterCmap.cmap, 'norm': clusterCmap.norm}
			ax, im  = self.mapMake._mapGen(fig, gs[1, t], 
												recountedLabels[t, ...],
												timeAxis=timeAxis, 
												xlim=self.xlim,
												ylim=self.ylim,
												#flareContour=self.mask_map, 
												**kwargsDict)
			if not gs[0, t].is_first_col():
				ax.set_yticklabels([])

			#cbar = fig.colorbar(im, cax=cax, ticks=bounds_ticks)#, label='Binned Intensity')
				#
			# cbar.ax.set_yticklabels(["{}XX".format(int(x)) for x in recountLst])
			# compoundLabels = np.char.add(compoundLabels, 
			# 					np.char.zfill(recountedLabels[t, ...].astype(np.uint).astype(str), 2))
		
		cax = fig.add_subplot(gs[0, :])
		cbar = fig.colorbar(im, spacing='uniform',
									ticks=clusterCmap.bound_ticks, orientation="horizontal",
									cax=cax)
		cbar.ax.set_xticklabels(["{}".format(int(x)) for x in np.unique(labelLst)])
		cbar.minorticks_off()
		

		return(fig)

	@loggTimer
	def intrinsicMap(self):
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
						moment0 = self._quesoOut._instrumentObj.dataSquare[:, self.ii:self.jj+1].mean(axis=-1).compute()
						bins = intrinsicConfig[i]['layerConfig']['bins']
						cbar_label = "Mean Window Intensity"
					case 'continuum':
						moment0 = self._quesoOut._instrumentObj.dataSquare[:, self._quesoOut.lineContinuum].compute()
						bins = intrinsicConfig[i]['layerConfig']['bins']
						cbar_label = "Continuum Intensity"

				intrinsicLayerMap = baseMain.runIntrinsic(len(np.diff(bins)), np.floor(moment0*100)/100., 
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
		
		ii, jj = [self._quesoOut._config.blueEdge, 
					self._quesoOut._config.redEdge]

		# if hasattr(self._quesoOut._config, "waveFit"):
		# 	wavelambda  = self._quesoOut._config.waveFit.magnitude
		# 	wavelambda -= wavelambda[self._quesoOut._config.lineCenter]
		# 	waveUnit = self._quesoOut._config.waveFit.units
		# else:
		# 	wavelambda = np.arange(self._quesoOut._instrumentObj.dataPrism.shape[2])
		# 	waveUnit = "index"

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

		#raw_max = (np.ceil(np.nanmax(self._quesoOut.prepSquare[self.vfindx, self._quesoOut._config.waveGrid])*100)/100.)#.compute()
		#raw_min = (np.floor(np.nanmin(self._quesoOut.prepSquare[self.vfindx, self._quesoOut._config.waveGrid])*100)/100.)#.compute()	
		#extent  	= self._wavelambda[ii], self._wavelambda[jj], raw_min, raw_max

		panel_bounds = []
		bounds_ticker = int(str(i0o1Lst[0])[0])
		for j in range(len(i0o1Lst)):
			i0_indx = np.where(i0o1Arr == i0o1Lst[j])[0]

			if i0_indx.size <= 1:
				continue
			ax0      = plt.subplot(gs[j, 0])

			sindx = np.where(i0Arr == i0Arr[i0_indx[0]])[0].astype(np.uint32)
			print([i0Arr[i0_indx[0]]])

			subFrame = self._quesoOut.prepSquare[self.vfindx[sindx], :]

			# dbScore = None
			# if np.unique(validLabels[sindx]).size > 1:
			# 	#dbScore = scoresAtom.calcDaviesBouldin(self._quesoOut.prepSquare[self.vfindx[sindx], ii:jj+1], validLabels[sindx])
			# 	dbScore = metrics.davies_bouldin_score(subFrame[:, self._quesoOut.waveGrid], validLabels[sindx])
			# 	print(dbScore)

			ax0 = self.spectralEntry(ax0, self.vfindx[i0_indx])#, scores=dbScore)
			if gs[j,0].is_last_row():
				#ax0.set_xlabel(r"$\lambda-\lambda_{0}$ [$\mathrm{\AA}$]")
				ax0.set_xlabel(r"$\lambda-\lambda_{0}$" +  " [{}]".format(self._waveUnit))
			ax0.tick_params(labelleft=True)
			#axR0.tick_params(labelright=False)
			if not gs[j, 0].is_last_row():
				ax0.tick_params(labelbottom=False)
		
			if bounds_ticker != int(str(i0o1Lst[j])[0]):
				trans = mpl.transforms.blended_transform_factory(ax0.transData, fig.transFigure)
				panel_bounds.append([-self._extent[0], ax0.get_position().bounds[2], j, trans])

			bounds_ticker = int(str(i0o1Lst[j])[0])

			o2Arr = auxAtom.pick_jth_label(validLabels[i0_indx], 2).astype(int)					
			o2Lst = np.unique(o2Arr).astype(int)
			
			for k in range(len(o2Lst)):
				ax      	= plt.subplot(gs[j, k+1])
				o2_indx 	= i0_indx[np.where(o2Arr == o2Lst[k])[0]]

				#sArr = auxAtom.pick_jth_label(validLabels[o2_indx], 0)
				#print(sindx)

				score = None
				#print(np.unique(validLabels[sindx]))
				#if np.unique(validLabels[sindx]).size > 1:
					# score = scoresAtom.calcNeighborSilhouetteScore(self._quesoOut.prepSquare[self.vfindx[sindx], ii:jj+1], 
				 	# 							   validLabels[sindx], 
					# 							   point=validLabels[o2_indx[0]])
					#score = metrics.silhouette_samples(subFrame[:, self._quesoOut.waveGrid], validLabels[sindx], metric='euclidean')
					#print(validLabels[o2_indx[0]])
					#score = score[validLabels[sindx] == validLabels[o2_indx[0]]].mean()
					#print([scikitScore[validLabels[sindx] == validLabels[o2_indx[0]]].mean(), np.median(scikitScore[validLabels[sindx] == validLabels[o2_indx[0]]])])

				ax = self.spectralEntry(ax,self.vfindx[o2_indx.astype(np.uint32)], scores=score)
				if gs[j,k+1].is_last_row():
					ax.set_xlabel(r"$\lambda-\lambda_{0}$" +  " [{}]".format(self._waveUnit))	
				else:
					ax.tick_params(labelbottom=False)				
										
				ax.tick_params(labelleft=False)
				# if dev and not gs[j, k+1].is_last_col():
				# 	axR.tick_params(labelright=False)
		return(fig)

	def spectralEntry(self, ax, indx, scores=None, dev=False, scale=0.01):
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
		ii, jj = [self._quesoOut._config.blueEdge, self._quesoOut._config.redEdge]

		# 
		raw_dat = self._quesoOut.prepSquare[indx,:]
		raw_dat = raw_dat[:, ii:jj+1]
		centroid_i = raw_dat.sum(axis=0)/raw_dat.shape[0]	


		ax.plot(self._wavelambda[self._quesoOut.waveGrid]-self._wavelambda[self._quesoOut._config.lineCenter], centroid_i[self._quesoOut.waveGrid - ii], color='black', linewidth=0.75)

		# im = ax.hist2d(raw_dat, bins=[0.01, wavelambda[ii:jj+1]-wavelambda[self.lineCenter]])
		temp_im 	= auxAtom.density_hist2d(raw_dat, scale, self._extent[3], self._extent[2])
		if self._quesoOut._config.normConfig['norm'] == normAtom.normMaximum:
			temp_im[temp_im > 0] = np.log10(temp_im[temp_im > 0])

		#ww_grid = self._wavelambda[self._quesoOut._config.waveGrid].tolist() + [self._wavelambda[self._quesoOut._config.redEdge + 1]]
		ww_grid = self._wavelambda[ii:jj+1+1]
		ww, insty = np.meshgrid(np.asarray(ww_grid)-self._wavelambda[self._quesoOut._config.lineCenter], np.arange(self._extent[2], self._extent[3]+scale, scale))
		#print([ww.shape, insty.shape, temp_im.shape])
		im = ax.pcolormesh(ww, insty, temp_im.T, cmap=LinearSegmentedColormap.from_list('', ['white', self._quesoOut._config.lineTheme]))

		ax.axvline(x = 0, linestyle='dashed', color='black')


		labelLst = np.unique(self.optLabels[np.unravel_index(indx, self.optLabels.shape)]).astype(int).astype(str)
		
		commonLabel = [labelLst[0][j] for j in range(len(labelLst[0])) if np.unique([a[j] for a in [list(x) for x in labelLst]]).size == 1]

		label = "{}{}".format(int("".join(commonLabel)), "X"*(len(labelLst[0]) - len(commonLabel)))
		ax.annotate("{}".format(label),
			xy=(0.01, 1-0.05), xycoords='axes fraction',
			xytext=(0.01, 1-0.05), textcoords='axes fraction', fontfamily='sans-serif',
			va='center', ha='left')
		
		ax.annotate("N={}".format(len(indx)),
            		xy=(0.01, 1-0.1), xycoords='axes fraction',
					xytext=(0.01, 1-0.1), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')

		ax.annotate(r"m={:.3f}$\pm${:.3f}".format(centroid_i.mean(), np.std(raw_dat.mean(axis=1))),
            		xy=(0.01, 1-0.15), xycoords='axes fraction',
					xytext=(0.01, 1-0.15), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')	


		# unnorm = self._quesoOut.dataSquare[indx, ii:jj].mean(axis=1)
		# ax.annotate(r"u={:.3f}$\pm${:.3f}".format(unnorm.mean().compute(), np.std(unnorm).compute()),
        #     		xy=(0.01, 1-0.2), xycoords='axes fraction',
		# 			xytext=(0.01, 1-0.2), textcoords='axes fraction', fontfamily='sans-serif',
        #     		va='center', ha='left')	


		if not (scores is None):
			ax.annotate("S={:.3f}".format(float(scores)),
            		xy=(0.01, 1-0.25), xycoords='axes fraction',
					xytext=(0.01, 1-0.25), textcoords='axes fraction', fontfamily='sans-serif',
            		va='center', ha='left')			



		if self._quesoOut._config.normConfig['norm'] == normAtom.normContinuum:
			ax.axhline(y = 1, color='black', linestyle='dotted')



		wdiff = np.floor(np.abs(self._wavelambda[jj] - self._wavelambda[ii]))
		wMajor = 10**np.floor(np.log10(wdiff))
		wMajor *= np.ceil(wdiff/wMajor)/4.


		ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=wMajor))
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=wMajor/2.))
		

		return(ax)
