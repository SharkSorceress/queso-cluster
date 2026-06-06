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

	Attributes
	----------
	cmap : ListedColormap
		The matplotlib colormap to use
	norm : BoundaryNorm
		The matplotlib normalization to use
	bound_ticks : ndarray
		Tick locations for plt.colorbar
	"""

	def __init__(self, nbounds, tolColorLabel='rainbow_PuRd'):
		self.tolColorLabel = tolColorLabel
		self.nbounds = nbounds
		#cleanLst = list(labelLst[~np.isnan(labelLst)])
		
		color_palette = self.genColorPalette()
		actual_bounds, self.bound_ticks = self.cbar_bounds()

		self.cmap = mpl.colors.ListedColormap(color_palette)
		self.cmap.set_bad("#FFFFFF")
		self.norm = mpl.colors.BoundaryNorm(actual_bounds, self.cmap.N+1)	


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
	
	Attributes
	----------
	flatten : lambda function
		creates a 1D array from a spatial 2D array
	unflatten : lambda function
		creates a spatial 2D array from a flattened 1D array
	bbox : ndarray
		1D array containing the extent of the region in pixel units
	extent : ndarray
		1D array containing the extent of the region in arcseconds
	correct : lambda function
		Flattens a transposed array (for IDL maps only)

	"""
	def __init__(self, spaceInfo, deltas):
		self.spaceInfo 	= spaceInfo
		self.deltas 	= deltas
		self.cadence 	= 15.667

		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 

	
		# if bbox is None:
		self.bbox = np.array([0, self.spaceInfo['rasterSize'], 0, self.spaceInfo['alongSlitSize']])
		# else:
		# 	self.bbox = np.array(bbox)
		self.extent = self.bbox * (0, self.deltas['pxlSlitWidth'].magnitude, 0, self.deltas['pxlAlongSlit'].magnitude)

		self.correct = lambda x: x.reshape(self.spaceInfo['alongSlitSize'], self.spaceInfo['rasterSize']).T.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])


	def _mapGen(self, fig, pos, arr, flareContour=None, timeAxis=None, **kwargsDict):		
		if mpl.axes._axes.Axes == type(pos):
			ax = pos
		else:
			ax = fig.add_subplot(pos)

		ax.set_anchor('NW')

		yScale = self.deltas['pxlAlongSlit'].magnitude
		xScale = self.deltas['pxlSlitWidth'].magnitude

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