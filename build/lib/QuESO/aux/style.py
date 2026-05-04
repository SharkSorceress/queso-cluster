from lib.util.imports import *

accentColor = "#527A00"
plt.rcParams.update({'font.size': 12})
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'serif'
#	mpl.rcParams["font.monospace"] = ["FreeMono"]


def _genColorPallet(n, show=None):
	import lib.util.tol_colors as tol
	cmap = tol.tol_cmap(colormap='rainbow_PuRd')
	color_pallet = [cmap(i) for i in np.linspace(0, cmap.N+1, n).astype(int)]
	color_pallet.reverse()
	return(cmap, color_pallet)


def rainbow_cmap(nrange, discrete=False, nan=False):

	from lib.util.tol_colors import tol_cmap

	if nan:
		return(tol_cmap(colormap='rainbow_discrete', lut=nrange))

	schemes = tol_cmap(colormap='rainbow_PuRd').reversed()

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


def cbar_bounds(bounds):
	actual_bounds = []
	for b in range(len(bounds)):
		actual_bounds.append((b+1)-0.5)
		actual_bounds.append((b+1)+0.5)
	actual_bounds = np.unique(actual_bounds)
	bound_ticks = [b+1 for b in range(len(bounds))]
	_, color_pallet = _genColorPallet(len(bounds))
	return(actual_bounds, bound_ticks, color_pallet)


class mapMaker:
	def __init__(self, spaceInfo, deltas):
		# self.dataArr 	= arr
		self.spaceInfo 	= spaceInfo
		self.deltas 	= deltas
		self.cadence 	= 15.667
		print(deltas)

		self.aspect = self.deltas['pxlAlongSlit']/self.deltas['pxlSlitWidth']

		self.flatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])  
		self.unflatten = lambda arr: arr.reshape(self.spaceInfo['rasterSize'], self.spaceInfo['alongSlitSize']) 

		self.bbox = np.array([0, self.spaceInfo['rasterSize'], 0, self.spaceInfo['alongSlitSize']])

		self.extent = self.bbox * (0, self.deltas['pxlSlitWidth'], 0, self.deltas['pxlAlongSlit'])

		self.correct = lambda x: x.reshape(self.spaceInfo['alongSlitSize'], self.spaceInfo['rasterSize']).T.reshape(self.spaceInfo['rasterSize']*self.spaceInfo['alongSlitSize'])




	def _helperAxisSetup(self, ax, swap, aspectCheck):
		ax.set_xlim([self.bbox[0], self.bbox[1]])
		ax.set_ylim([self.bbox[2], self.bbox[3]])


		yScale = self.deltas['pxlAlongSlit']
		xScale = self.deltas['pxlSlitWidth']

		xShift = self.bbox[0]
		yShift = self.bbox[2]

		if swap:
			xScale = self.deltas['pxlAlongSlit']
			yScale = self.deltas['pxlSlitWidth']

			xShift = self.bbox[2]
			yShift = self.bbox[0]
			ax.invert_xaxis()



		def _ticksPhysical(ticks, shift, scale):
			return(np.round((np.array(ticks)+shift)*scale, decimals=1).astype(int))

		unitSqX = 10**np.floor(np.log10(_ticksPhysical(self.bbox[1], xShift, xScale)-_ticksPhysical(self.bbox[0], xShift, xScale)))
		unitSqY = 10**np.floor(np.log10(_ticksPhysical(self.bbox[3], yShift, yScale)-_ticksPhysical(self.bbox[2], yShift, yScale)))

		unitSqX = 10#5
		unitSqY = 5#2
		print((unitSqX, unitSqY))

		ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=unitSqX/xScale))
		ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=(unitSqX/2.)/xScale))

		ticks_loc = ax.get_xticks().tolist()
		ticks_loc = list(np.array(ticks_loc)[np.where(_ticksPhysical(ticks_loc, xShift, xScale) % unitSqX == 0)[0]])
		ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))
		ax.set_xticklabels(["{:d}\"".format(int(_ticksPhysical(x, xShift, xScale))) for x in ticks_loc])


		ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(base=unitSqY/yScale))
		ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=(unitSqY/2.)/yScale))

		ticks_loc = ax.get_yticks().tolist()
		ticks_loc = list(np.array(ticks_loc)[np.where(_ticksPhysical(ticks_loc, yShift, yScale) % unitSqY == 0)[0]])
		ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))

		ax.set_yticklabels(["{:d}\"".format(int(_ticksPhysical(y, yShift, yScale))) for y in ticks_loc])

		if aspectCheck:
			minUnitSq = np.min([unitSqX, unitSqY])
			ax.axhline(y = self.bbox[2] + (minUnitSq/yScale), color='black')
			ax.axvline(x = self.bbox[0] + (minUnitSq/xScale), color='black')

			# ax.set_xlim([self.bbox[0], self.bbox[0] + (minUnitSq/xScale)])
			# ax.set_ylim([self.bbox[2], self.bbox[2] + (minUnitSq/yScale)])

		return(ax)

	def verifyAspect(self, fig, ax, arr, aspect, swap, **kwargsDict):
		old_bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

		fig2 = plt.figure(layout='compressed', dpi=fig.get_dpi(), figsize=(old_bbox.width, old_bbox.height))
		ax_check = fig2.add_subplot(111)

		im_check = ax_check.imshow(self.unflatten(arr).T, origin='lower', aspect=aspect, 
							**kwargsDict)
		
		ax_check = self._helperAxisSetup(ax_check, swap, True)
		ax_check.axis("off")
		import string, random
		checkName = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
		fig2.tight_layout()
		print([fig.get_dpi(), checkName, fig2.get_figwidth(), fig2.get_figheight()])
		fig2.savefig("./fig/aspectCheck/{}.png".format(checkName))

	def _mapGen(self, fig, pos, arr, aspect=None, swap=False, aspectCheck=False, flareContour=None, timeAxis=None, **kwargsDict):
		if type(aspect) == type(None): 
			aspect = self.aspect
		

		ax = fig.add_subplot(pos)
		ax.set_anchor('NW')

		im = ax.imshow(self.unflatten(arr).T, origin='lower', aspect=aspect, 
				 #extent=self.extent, 
				 interpolation='nearest',
				 **kwargsDict)

		if type(flareContour) != type(None):
		
			f = lambda x,y: flareContour[int(y),int(x)]
			g = np.vectorize(f)

			x = np.linspace(0,flareContour.shape[1], flareContour.shape[1]*10)
			y = np.linspace(0,flareContour.shape[0], flareContour.shape[0]*10)
			X, Y 	= np.meshgrid(x[:-1],y[:-1])
			Z 		= g(X[:-1],Y[:-1]).T

			cs = ax.contour(Z, 
					origin='lower', levels=[0],
						#extent=self.extent,
						corner_mask=True,
						antialiased=False,
						extent=[0-0.5, flareContour.shape[0]-0.5, 0-0.5, flareContour.shape[1]-0.5],
						colors='black', 
						linewidths=1)		

		ax = self._helperAxisSetup(ax, swap, aspectCheck)

		# if aspectCheck:
		# 	self.verifyAspect(fig, ax, arr, aspect, swap, **kwargsDict)


		if (type(timeAxis) != type(None)) or timeAxis:
			f = lambda x: (x*self.cadence)/3600.
			g = lambda x: (x/self.cadence)*3600.
			#-0.15
			tax = ax.secondary_xaxis(-0.17, functions=(f, g))
			return(ax, im, self.extent, tax)

		return(ax, im, self.extent)



def _helperAxisSetup(ax, bbox, deltas, aspectCheck=False, swap=False):
	ax.set_xlim([bbox[0], bbox[1]])
	ax.set_ylim([bbox[2], bbox[3]])


	yScale = deltas['pxlAlongSlit']
	xScale = deltas['pxlSlitWidth']
	xShift = bbox[0]

	yShift = bbox[2]

	if swap:
		xScale = deltas['pxlAlongSlit']
		yScale = deltas['pxlSlitWidth']

		xShift = bbox[2]
		yShift = bbox[0]
		ax.invert_xaxis()

	if yShift != 0:
		yShift *= -1

	if xShift != 0:
		xShift *= -1

	def _ticksPhysical(ticks, shift, scale):
		return(np.round((np.array(ticks)+shift)*scale, decimals=1).astype(int))

	unitSqX = 10**np.floor(np.log10(_ticksPhysical(bbox[1], xShift, xScale)-_ticksPhysical(bbox[0], xShift, xScale)))
	unitSqY = 10**np.floor(np.log10(_ticksPhysical(bbox[3], yShift, yScale)-_ticksPhysical(bbox[2], yShift, yScale)))


	ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(base=unitSqX/xScale))
	ax.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=(unitSqX/2.)/xScale))

	ticks_loc = ax.get_xticks().tolist()
	ticks_loc = list(np.array(ticks_loc)[np.where(_ticksPhysical(ticks_loc, xShift, xScale) % unitSqX == 0)[0]])
	ax.xaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))
	ax.set_xticklabels(["{:d}\"".format(int(_ticksPhysical(x, xShift, xScale))) for x in ticks_loc])
	print(["{:d}\"".format(int(_ticksPhysical(x, xShift, xScale))) for x in ticks_loc])


	ax.yaxis.set_major_locator(mpl.ticker.MultipleLocator(base=unitSqY/yScale))
	ax.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(base=(unitSqY/2.)/yScale))
	ticks_loc = ax.get_yticks().tolist()
	ticks_loc = list(np.array(ticks_loc)[np.where(_ticksPhysical(ticks_loc, yShift, yScale) % unitSqY == 0)[0]])

	ax.yaxis.set_major_locator(mpl.ticker.FixedLocator(ticks_loc))
	ax.set_yticklabels(["{:d}\"".format(int(_ticksPhysical(y, yShift, yScale))) for y in ticks_loc])
	print(["{:d}\"".format(int(_ticksPhysical(y, yShift, yScale))) for y in ticks_loc])

	if aspectCheck:
		minUnitSq = np.min([unitSqX, unitSqY])
		ax.axhline(y = bbox[2] + (minUnitSq/yScale), color='black')
		ax.axvline(x = bbox[0] + (minUnitSq/xScale), color='black')

		# ax.set_xlim([self.bbox[0], self.bbox[0] + (minUnitSq/xScale)])
		# ax.set_ylim([self.bbox[2], self.bbox[2] + (minUnitSq/yScale)])

	return(ax)
