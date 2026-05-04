from ..atoms import base as baseAtom
from ..atoms import aux as auxAtom
from .. import loader


from astropy.io import fits
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap

from  ..runners import base as baseRun
from ..aux.logg import loggTimer

import tol_colors as tol

def cbar_bounds(bounds):
	actual_bounds = []
	for b in range(len(bounds)):
		actual_bounds.append((b+1)-0.5)
		actual_bounds.append((b+1)+0.5)
	actual_bounds = np.unique(actual_bounds)
	bound_ticks = [b+1 for b in range(len(bounds))]
	_, color_pallet = _genColorPallet(len(bounds))
	return(actual_bounds, bound_ticks, color_pallet)

def _genColorPallet(n):
	# from . import  tol_colors as tol

	cmap = tol.tol_cmap(colormap='rainbow_PuRd')
	color_pallet = [cmap(i) for i in np.linspace(0, cmap.N, n).astype(int)]
	color_pallet.reverse()
	return(cmap, color_pallet)


def rainbow_cmap(nrange, discrete=False, nan=False):

	# from .tol_colors import tol_cmap

	if nan:
		return(tol.tol_cmap(colormap='rainbow_discrete', lut=nrange))

	schemes = tol.tol_cmap(colormap='rainbow_PuRd').reversed()

	if discrete:
		final_cmap = cmap_discretize(schemes, nrange)
	else:
		final_cmap = schemes
	return(final_cmap)

def cmap_discretize(cmap, N):
	"""Return a discrete colormap from the continuous colormap cmap.

		cmap: colormap instance, eg. cm.jet. 
		N: number of colors.
	"""
	

	if type(cmap) == str:
		cmap = mpl.get_cmap(cmap)
	colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
	colors_rgba = cmap(colors_i)
	indices = np.linspace(0, 1., N+1)
	cdict = {}
	for ki, key in enumerate(('red','green','blue')):
		cdict[key] = [(indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in range(N+1)]
	# Return colormap object.
	return LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)

class mapMaker:
	def __init__(self, spaceInfo, deltas):
		# self.dataArr 	= arr
		self.spaceInfo 	= spaceInfo
		self.deltas 	= deltas
		self.cadence 	= 15.667
		print(deltas)

		#self.aspect = self.deltas['pxlAlongSlit']/self.deltas['pxlSlitWidth']

		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 

	
		# if bbox is None:
		self.bbox = np.array([0, self.spaceInfo['rasterSize'], 0, self.spaceInfo['alongSlitSize']])
		# else:
		# 	self.bbox = np.array(bbox)
		self.extent = self.bbox * (0, self.deltas['pxlSlitWidth'], 0, self.deltas['pxlAlongSlit'])

		self.correct = lambda x: x.reshape(self.spaceInfo['alongSlitSize'], self.spaceInfo['rasterSize']).T.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])


	# def _helperAxisSetup(self, ax, swap, aspectCheck):
	# 	ax.set_xlim([self.bbox[0], self.bbox[1]])
	# 	ax.set_ylim([self.bbox[2], self.bbox[3]])


	# 	yScale = self.deltas['pxlAlongSlit']
	# 	xScale = self.deltas['pxlSlitWidth']

	# 	xShift = self.bbox[0]
	# 	yShift = self.bbox[2]

	# 	if swap:
	# 		xScale = self.deltas['pxlAlongSlit']
	# 		yScale = self.deltas['pxlSlitWidth']

	# 		xShift = self.bbox[2]
	# 		yShift = self.bbox[0]
	# 		ax.invert_xaxis()



	# 	def _ticksPhysical(ticks, shift, scale):
	# 		return(np.round((np.array(ticks)+shift)*scale, decimals=1).astype(int))

	# 	unitSqX = 10**np.floor(np.log10(_ticksPhysical(self.bbox[1], xShift, xScale)-_ticksPhysical(self.bbox[0], xShift, xScale)))
	# 	unitSqY = 10**np.floor(np.log10(_ticksPhysical(self.bbox[3], yShift, yScale)-_ticksPhysical(self.bbox[2], yShift, yScale)))

	# 	unitSqX = 10#5
	# 	unitSqY = 5#2
	# 	print((unitSqX, unitSqY))

	# 	ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=unitSqX/xScale))
	# 	ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=(unitSqX/2.)/xScale))

	# 	ticks_loc = ax.get_xticks().tolist()
	# 	ticks_loc = list(np.array(ticks_loc)[np.where(_ticksPhysical(ticks_loc, xShift, xScale) % unitSqX == 0)[0]])
	# 	ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))
	# 	ax.set_xticklabels(["{:d}\"".format(int(_ticksPhysical(x, xShift, xScale))) for x in ticks_loc])


	# 	ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(base=unitSqY/yScale))
	# 	ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=(unitSqY/2.)/yScale))

	# 	ticks_loc = ax.get_yticks().tolist()
	# 	ticks_loc = list(np.array(ticks_loc)[np.where(_ticksPhysical(ticks_loc, yShift, yScale) % unitSqY == 0)[0]])
	# 	ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))

	# 	ax.set_yticklabels(["{:d}\"".format(int(_ticksPhysical(y, yShift, yScale))) for y in ticks_loc])

	# 	if aspectCheck:
	# 		minUnitSq = np.min([unitSqX, unitSqY])
	# 		ax.axhline(y = self.bbox[2] + (minUnitSq/yScale), color='black')
	# 		ax.axvline(x = self.bbox[0] + (minUnitSq/xScale), color='black')

	# 		# ax.set_xlim([self.bbox[0], self.bbox[0] + (minUnitSq/xScale)])
	# 		# ax.set_ylim([self.bbox[2], self.bbox[2] + (minUnitSq/yScale)])

	# 	return(ax)

	def _mapGen(self, fig, pos, arr, flareContour=None, timeAxis=None, **kwargsDict):		
		if mpl.axes._axes.Axes == type(pos):
			ax = pos
		else:
			ax = fig.add_subplot(pos)

		ax.set_anchor('NW')

		yScale = self.deltas['pxlAlongSlit']
		xScale = self.deltas['pxlSlitWidth']

		# if bbox is None:
		# 	xShift = self.bbox[0]
		# 	yShift = self.bbox[2]
		# else:
		# 	xShift = bbox[0]
		# 	yShift = bbox[2]

		dat = self.unflatten(arr)

		x = (np.arange(np.array(dat.shape)[0]+1))*xScale
		y = (np.arange(np.array(dat.shape)[1]+1))*yScale
		XX, YY = np.meshgrid(x, y)

		im = ax.pcolormesh(XX, YY, dat.T, 
					 rasterized=True, snap=True, 
					 shading='flat', **kwargsDict)
		
		ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(base=5))
		ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=10))

		ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=2.5))
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=5))

		fmtr = mpl.ticker.StrMethodFormatter('{x:,g}\"')
		ax.xaxis.set_major_formatter(fmtr)
		ax.yaxis.set_major_formatter(fmtr)

		ax.set_aspect("equal")
		# im = ax.imshow(self.unflatten(arr).T, origin='lower', aspect=aspect, 
		# 		 #extent=self.extent, 
		# 		 interpolation='nearest',
		# 		 **kwargsDict)

		if not (flareContour is None):
		
			f = lambda x,y: flareContour[int(x),int(y)]
			g = np.vectorize(f)

			y = np.linspace(0,flareContour.shape[1]-1, flareContour.shape[1]*10)
			x = np.linspace(0,flareContour.shape[0]-1, flareContour.shape[0]*10)
			X, Y 	= np.meshgrid(x,y)

			cs = ax.contour(((X-0.5)*xScale), (Y*yScale), g(X,Y), 
						origin='lower', levels=[0],
						corner_mask=True,
						antialiased=False,
						colors='black', 
						linewidths=1)

		if (not (timeAxis is None)) or timeAxis:
			f = lambda x: (x*self.cadence/xScale)/3600.
			g = lambda x: (x/self.cadence*xScale)*3600.
			#-0.15
			tax = ax.secondary_xaxis(-0.17, functions=(f, g))
			return(ax, im, tax)

		return(ax, im)

class Products:

	def __init__(self, epochObj, optLabels):

		# self.iObj = loader.instrument('/disk/data/DKIST/20221227/CSYRML/')
		# self.iObj.vispLoad()


		self.epochObj = epochObj

		self.config 			= self.epochObj.config

		self.keepI0 = self.config.runners.config['keepI0']

		#self.alongSlitSize 		= self.epochObj.spaceInfo['alongSlitSize']
		#self.rasterSize 	  	= self.epochObj.spaceInfo['rasterSize']
		#self.aspect 		  	= self.epochObj.aspect


		self.ii, self.jj = self.epochObj.spectralWindow
		self.lineCenter = self.epochObj.lineCenter
		self.continuum = self.epochObj.continuum
		

		self.waveFit 	= self.epochObj.waveFit 
		# optLabels[optLabels == 0] = np.nan
		# valid_indx = np.where(~np.isnan(optLabels))[0]
		self.optLabels 	= optLabels#[valid_indx]#[valid_indx]#.reshape(optLabels.shape[0]*optLabels.shape[1])
		self.optLabels[self.optLabels == 0] = np.nan
		# self.optLabels[self.optLabels > 600] = np.nan
		self.vindx 	= np.where(~np.isnan(self.optLabels))[0]

		#self.optLabels 	= self.epochObj.flatten(optLabels)
		#self.optLabels[self.optLabels == 0] = np.nan


	# def load(self, fname):
	# 	hdul = fits.open(fname)

	# 	self.optLabels = hdul[1].data


	# 	self.

		self.mapMake = mapMaker(self.epochObj.spaceInfo, self.epochObj.deltas)


	@loggTimer
	def figure03(self):

		# fig2 = plt.figure(layout='constrained', figsize=(8.5/1.5, 5/1.5), dpi=300)
		width = [2, 0.025]#, 0, 3*self.aspect*self.alongSlitSize/self.rasterSize + 0.25, 0.075]

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
				_, color_pallet = _genColorPallet(len(np.unique(intrinsicLayerMap)))

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

			actual_bounds, bound_ticks, color_pallet = cbar_bounds(list(np.unique(intrinsicLayerMap[self.vindx])))
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