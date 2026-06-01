#> file:  ./QuESO/addon/style
#> lang:  python
#> synopsis: 
#> author:   <>
import numpy as np
import tol_colors as tc
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import LinearSegmentedColormap


plt.rcParams.update({'font.size': 12})
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'serif'
#	mpl.rcParams["font.monospace"] = ["FreeMono"]
def cbar_bounds(bounds):
#> detail: 
#> param type bounds:
#> return (type): 
#> test-method:
	actual_bounds = []
	for b in range(len(bounds)):
		actual_bounds.append((b+1)-0.5)
		actual_bounds.append((b+1)+0.5)
	actual_bounds = np.unique(actual_bounds)
	bound_ticks = [b+1 for b in range(len(bounds))]
	_, color_pallet = _genColorPallet(len(bounds))
	return(actual_bounds, bound_ticks, color_pallet)

def _genColorPallet(n):
#> detail: 
#> param type n:
#> return (type): 
#> test-method:
	# from . import  tol_colors as tol

	cmap = tc.tol_cmap(colormap='rainbow_PuRd')
	color_pallet = [cmap(i) for i in np.linspace(0, cmap.N, n).astype(int)]
	color_pallet.reverse()
	return(cmap, color_pallet)


def rainbow_cmap(nrange, discrete=False, nan=False):
#> detail: 
#> param type nrange:
#> param type [False] discrete:
#> param type [False] nan:
#> return (type): 
#> test-method:

	# from .tol_colors import tol_cmap

	if nan:
		return(tc.tol_cmap(colormap='rainbow_discrete', lut=nrange))

	schemes = tc.tol_cmap(colormap='rainbow_PuRd').reversed()

	if discrete:
		final_cmap = cmap_discretize(schemes, nrange)
	else:
		final_cmap = schemes
	return(final_cmap)

def cmap_discretize(cmap, N):
#> detail: 
#> param type cmap:
#> param type N:
#> return (type): 
#> test-method:
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
#> detail: 
#> param type self:
#> param type spaceInfo:
#> param type deltas:
#> return (type): 
#> test-method:
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

		if ((not (timeAxis is None)) or timeAxis) and pos.is_last_row():
			f = lambda x: (x*self.cadence/xScale)/3600.
			g = lambda x: (x/self.cadence*xScale)*3600.
			#-0.15
			ax.secondary_xaxis(-0.17, functions=(f, g))
			return(ax, im)

		return(ax, im)