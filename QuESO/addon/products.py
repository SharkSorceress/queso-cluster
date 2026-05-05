#> file:  ./QuESO/addon/products
#> lang:  python
#> synopsis: 
#> author:   <>
from ..atoms import base as baseAtom
from ..atoms import aux as auxAtom
from . import style as sty
from  ..runners import base as baseRun
from .logg import loggTimer

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap



class Products:

	def __init__(self, epochObj, optLabels):
#> detail: 
#> param type self:
#> param type epochObj:
#> param type optLabels:
#> return (type): 
#> test-method:
		self.epochObj = epochObj
		self.config 			= self.epochObj.config
		self.keepI0 = self.config.runners.config['keepI0']
		self.ii, self.jj = self.epochObj.spectralWindow
		self.lineCenter = self.epochObj.lineCenter
		self.continuum = self.epochObj.continuum
		

		self.waveFit 	= self.epochObj.waveFit 
		self.optLabels 	= optLabels
		self.optLabels[self.optLabels == 0] = np.nan
		self.vindx 	= np.where(~np.isnan(self.optLabels))[0]

		self.mapMake = sty.mapMaker(self.epochObj.spaceInfo, self.epochObj.deltas)


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
						moment0 = self.epochObj.instrumentObj.dataSquare[:, self.ii:self.jj+1].mean(axis=-1).compute()
						bins = intrinsicConfig[i]['layerConfig']['bins']
						cbar_label = "Mean Window Intensity"
					case 'continuum':
						moment0 = self.epochObj.instrumentObj.dataSquare[:, self.epochObj.continuum].compute()
						bins = intrinsicConfig[i]['layerConfig']['bins']
						cbar_label = "Continuum Intensity"

				intrinsicLayerMap = baseRun._runIntrinsic(len(np.diff(bins)), np.floor(moment0*100)/100., 
											  edgeOverride=np.array(bins).astype(float))
				_, color_pallet = sty._genColorPallet(len(np.unique(intrinsicLayerMap)))

				match types[t]:
					case 'intensity':
						present = moment0
						cmap = 'Greys_r'
					case 'labels':
						present = intrinsicLayerMap
						cmap = mpl.colors.ListedColormap(color_pallet)
						norm = mpl.colors.BoundaryNorm(np.array(bins).astype(float), cmap.N)

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
				cbar = fig.colorbar(im_cbar, cax=cax, spacing='proportional', label=cbar_label)

			intrinsicLayerMap_oldCount = auxAtom.pick_jth_label(self.optLabels[self.vindx], 0).astype(float)
			intrinsicLayerMap = np.zeros(self.optLabels.shape) + np.nan
			recountLst = np.unique(intrinsicLayerMap_oldCount)
			for rc in range(recountLst.size):
				lindx = np.where(intrinsicLayerMap_oldCount == recountLst[rc])[0]
				intrinsicLayerMap[self.vindx[lindx]] = rc+1

			actual_bounds, bound_ticks, color_pallet = sty.cbar_bounds(list(np.unique(intrinsicLayerMap[self.vindx])))
			cmap = mpl.colors.ListedColormap(color_pallet)
			norm = mpl.colors.BoundaryNorm(actual_bounds, cmap.N+1)

			kwargsDict = {'cmap': cmap}
			ax, im, tax = self.mapMake._mapGen(fig, gs[-1, 0], 
												intrinsicLayerMap,
												timeAxis=True, 
												#flareContour=self.mask_map, 
												**kwargsDict)
			cax = fig.add_subplot(gs[-1, 1])
			ax.set_aspect("equal")

			#cbar = fig.colorbar(im, cax=cax, ticks=bounds_ticks)#, label='Binned Intensity')
			cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), spacing='proportional',
									ticks=bound_ticks,
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
	def figure04_template(self):
#> detail: 
#> param type self:
#> return (type): 
#> test-method:
		ii, jj = [self.ii, self.jj]
		
		wavelambda  = self.epochObj.waveFit


		validLabels = self.optLabels[self.vindx]
		print(np.unique(validLabels))

		# selectiveIndx = []
		# for k in range(len(self.keepI0)):
		# 	selectiveIndx += vindx[np.where(auxAtom.pick_jth_label(self.optLabels[vindx], 0) == self.keepI0[k])[0]].tolist()


		# valid_indx = np.array(selectiveIndx).astype(int)


		i0Arr = auxAtom.pick_jth_label(validLabels, 0)
		i0Lst = np.unique(i0Arr)

		print(np.unique(self.optLabels))
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

		raw_max = (np.ceil(self.epochObj.prepSquare[:, ii:jj+1].max()*10)/10.).compute()
		raw_min = (np.floor(self.epochObj.prepSquare[:, ii:jj+1].min()*10)/10.).compute()	
		extent  	= wavelambda[ii]-wavelambda[self.lineCenter], wavelambda[jj]-wavelambda[self.lineCenter], raw_min, raw_max

		x0 = extent[0]

		color = "black"
		panel_bounds = []
		bounds_ticker = int(str(i0o1Lst[0])[0])
		for j in range(len(i0o1Lst)):
			i0_indx = np.where(i0o1Arr == i0o1Lst[j])[0]

			ax0      = plt.subplot(gs[j, 0])
			ax0 = self.spectralEntry(ax0, i0_indx, color, wavelambda, extent)
			if gs[j,0].is_last_row():
				ax0.set_xlabel(r"$\lambda-\lambda_{0}$ [\AA]")									
			
			ax0.tick_params(labelleft=True)

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

				sArr = auxAtom.pick_jth_label(validLabels[o2_indx], 0)
				sindx = np.where(i0Arr == sArr[0])[0]

				score = baseAtom._calcSingleSilhouetteScore(self.epochObj.prepSquare[sindx.astype(np.uint32), ii:jj+1].compute(), validLabels[sindx.astype(np.uint32)], validLabels[o2_indx[0]])
			
				ax = self.spectralEntry(ax, o2_indx, color, wavelambda, extent, scores=score)
				if gs[j,k+1].is_last_row():
					ax.set_xlabel(r"$\lambda-\lambda_{0}$ [\AA]")					
										
				ax.tick_params(labelleft=False)
				if not gs[j, k+1].is_last_row():
					ax.tick_params(labelbottom=False)		


		#fig.savefig(self.figDir + "{}_alt.pdf".format(catalogType))
		fig.savefig("./clusterLabels.png")

	def spectralEntry(self, ax, indx, color, wavelambda, extent, scores=None):
#> detail: 
#> param type self:
#> param type ax:
#> param type indx:
#> param type color:
#> param type wavelambda:
#> param type extent:
#> param type [None] scores:
#> return (type): 
#> test-method:
		ii, jj = [self.ii, self.jj]
		raw_dat = self.epochObj.prepSquare[indx.astype(np.uint32), ii:jj+1]
		centroid_i = raw_dat.sum(axis=0)/raw_dat.shape[0]		
		ax.plot(wavelambda[ii:jj+1]-wavelambda[self.lineCenter], centroid_i, color='black')

		temp_im 	= auxAtom.density_hist2d(raw_dat.compute(), 0.01, extent[3], extent[2])
		im = ax.imshow(temp_im.T, 
		extent=extent, aspect='auto', origin='lower')    
		im.set_cmap(LinearSegmentedColormap.from_list('', ['white', color]))

		ax.axvline(x = 0, linestyle='dashed', color='black')
		ax.set_ylim([extent[2], extent[3]])

		label = int(np.unique(self.optLabels[self.vindx[indx]])[0])
		if len(np.unique(self.optLabels[self.vindx[indx]])) > 1:
			print(np.unique(self.optLabels[self.vindx[indx]]))
			tmp = np.unique(auxAtom.pick_jth_label(self.optLabels[self.vindx[indx]], 0))*10 + np.unique(auxAtom.pick_jth_label(self.optLabels[self.vindx[indx]], 1))
			label = "{}X".format(int(tmp[0]))

		if scores == None:
			ax.text(0.9*(wavelambda[ii]-wavelambda[self.lineCenter]), 0.8*extent[3],
						"{}\nN={}\n".format(label, len(indx)),
						fontname='Times New Roman')
		else:
			ax.text(0.9*(wavelambda[ii]-wavelambda[self.lineCenter]), 0.8*extent[3],
					"{}\nN={}\nS={:.3f}".format(label, len(indx), float(scores)),
					fontname='Times New Roman')
			
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=0.2))

		return(ax)