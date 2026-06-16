"""
	:file:  queso_cluster/addon/style
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>
"""

import numpy as np
import tol_colors as tc
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap


plt.rcParams.update({'font.size': 12})
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'serif'


class clusterColormap:
	"""
	Creates a colormap to be used with the cluster maps

	Parameters
	----------
	nbounds : int
		the number of labels to use
	tolColorLabel : str, optional
		the name of the TOL colormap to use

	"""

	def __init__(self, bounds, tolColorLabel='rainbow_PuRd'):
		self.tolColorLabel = tolColorLabel
		self.nbounds = bounds.size
		#cleanLst = list(labelLst[~np.isnan(labelLst)])
		
		color_palette = self.genColorPalette()
		actual_bounds, self.bound_ticks = self.cbar_bounds()

		self.tickLabels = bounds

		self.cmap = mpl.colors.ListedColormap(color_palette)
		self.cmap.set_bad("#FFFFFF")
		self.norm = mpl.colors.BoundaryNorm(actual_bounds, self.cmap.N)	


	def cbar_bounds(self):
		"""
		Creates a list of uniform spaced tick locations 


		Returns
		-------
		actual_bounds : ndarray
			The edges of the bins to be used with mpl.colors.BoundaryNorm
		bound_ticks : ndarray
			Tick locations for plt.colorbar
		
		"""

		actual_bounds = []
		for b in range(self.nbounds):
			actual_bounds.append((b+1)-0.5)
			actual_bounds.append((b+1)+0.5)
		actual_bounds = np.unique(actual_bounds)
		bound_ticks = [b+1 for b in range(self.nbounds)]
		return(actual_bounds, bound_ticks)

	def genColorPalette(self):
		"""
		Creates a list of uniform spaced tick locations 

		Returns
		-------
		color_palette : list
			The hexcodes for the colors to be used in the colormap

		"""
		cmap = tc.tol_cmap(colormap=self.tolColorLabel)
		color_palette = [cmap(i) for i in np.linspace(0, cmap.N, self.nbounds).astype(int)]
		color_palette.reverse()
		return(color_palette)



class mapMaker:
	"""
	A class to format maps in a consistent way.

	Parameters
	----------
	spaceInfo : dict
		dictionary containing number of pixels in each spatial dimension 
	deltas : dict
		dictinary containing the raster pixel scale as 'pxlSlitWidth' and the along slit pixel scale as 'pxlAlongSlit'
	

	"""
	def __init__(self, instrumentObj):
		self.spaceInfo 		= instrumentObj.dimInfo#spaceInfo
		self.deltas 		= instrumentObj.pxlDelta#deltas
		self.stepCadence 	= instrumentObj.stepCadence

		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 

	
		# if bbox is None:
		self.bbox = np.array([0, self.spaceInfo['rasterSize'], 0, self.spaceInfo['alongSlitSize']])
		# else:
		# 	self.bbox = np.array(bbox)
		self.extent = self.bbox * (0, self.deltas['pxlSlitWidth'].magnitude, 0, self.deltas['pxlAlongSlit'].magnitude)

		self.correct = lambda x: x.reshape(self.spaceInfo['alongSlitSize'], self.spaceInfo['rasterSize']).T.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])


	def _mapGen(self, fig, pos, arr, flareContour=None, xlim=None, ylim=None, timeAxis=None, **kwargsDict):		
		if mpl.axes._axes.Axes == type(pos):
			ax = pos
		else:
			ax = fig.add_subplot(pos)

		ax.set_anchor('NW')

		yScale = self.deltas['pxlAlongSlit'].magnitude
		xScale = self.deltas['pxlSlitWidth'].magnitude

		dat = self.unflatten(arr)

		x = (np.arange(np.array(dat.shape)[0]+1))*xScale
		y = (np.arange(np.array(dat.shape)[1]+1))*yScale
		XX, YY = np.meshgrid(x, y)

		im = ax.pcolormesh(XX, YY, dat.T, 
					 rasterized=True, snap=True, 
					 shading='flat', **kwargsDict)

		if ylim is None:
			ydiff = np.floor(np.abs(y[-1]-y[0]))
		else:
			ydiff = np.floor(np.abs(ylim[1]-ylim[0]))
			ax.set_ylim(ylim)

		if xlim is None:
			xdiff = np.floor(np.abs(x[-1]-x[0]))
		else:
			xdiff = np.floor(np.abs(xlim[1]-xlim[0]))
			ax.set_xlim(xlim)


		if ydiff > 0:
			yMajor = 10**np.floor(np.log10(ydiff))
			yMajor *= np.ceil(ydiff//yMajor)/4.
		else:
			yMajor = yScale*2

		if xdiff > 0:
			xMajor = 10**np.floor(np.log10(xdiff))
			xMajor *= np.ceil(xdiff//xMajor)/4.
		else:
			xMajor = xScale*2
		
		ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(base=yMajor))
		ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=xMajor))

		ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=yMajor/2.))
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=xMajor/2.))

		fmtr = mpl.ticker.StrMethodFormatter('{x:,g}\"')

		ax.xaxis.set_major_formatter(fmtr)
		ax.yaxis.set_major_formatter(fmtr)

		ax.set_aspect('equal')

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

		if (timeAxis) and pos.is_last_row():
			f = lambda x: (x*self.cadence/xScale)/3600.
			g = lambda x: (x/self.cadence*xScale)*3600.
			#-0.15
			ax.secondary_xaxis(-0.17, functions=(f, g))
			return(ax, im)

		return(ax, im)