from lib.util.imports import *

def _gen_dataID(Input):
	stokes_lst 		= ['I', 'Q', 'U', 'V']
	coreIndex, coreLabel = [None, '']
	if hasattr(Input, 'manualOverride'):
		if 'coreOrder' in Input.manualOverride.keys():
			coreOrder = Input.manualOverride['coreOrder']
			coreLabel = '_' + list(coreOrder)[0]
			coreIndex = coreOrder[list(coreOrder)[0]]  
	data_id = Input.data['id'] + "_" + stokes_lst[Input.data['stokes']] + coreLabel 
	return(data_id, coreIndex)


def pick_jth_label(labelLst, j):
	return(np.array([str(x)[j] for x in labelLst.astype(int)]).astype(int))

# def leadDigit(num):
# 	out = np.floor(10**(np.log10(num) - np.floor(np.log10(num))))
# 	# if np.isnan(out).any():
# 	# 	#print(np.where(np.isnan(np.log10(num))))
# 	# 	out[np.where(np.isnan(out))[0]] = 0
#	return(out)

def rotateArray(image, turns):
	
	for i in range(turns):
		image = np.array(list(zip(*image[::-1])))

	return(image[::-1])

@nb.njit(cache=True)
def get_bin_edges(bins, lim):
	bin_edges = np.zeros((bins+1,), dtype=np.float64)
	a_min = lim.min()
	a_max = lim.max()
	delta = (a_max - a_min) / bins
	for i in range(bin_edges.shape[0]):
		bin_edges[i] = a_min + i * delta

	bin_edges[-1] = a_max  # Avoid roundoff error on last point
	return bin_edges


@nb.njit()
def compute_bin(x, bin_edges):
	# assuming uniform bins for now
	n = bin_edges.shape[0] - 1
	a_min = bin_edges[0]
	a_max = bin_edges[-1]

	# special case to mirror NumPy behavior for last bin
	if x == a_max:
		return n - 1 # a_max always in last bin

	bin = int(n * (x - a_min) / (a_max - a_min))

	if bin < 0 or bin >= n:
		return None
	else:
		return bin


@nb.njit()
def numba_histogram(a, bins, lim):
	hist = np.zeros((bins,), dtype=np.intp)
	bin_edges = get_bin_edges(bins, lim)

	for x in a.flat:
		bin = compute_bin(x, bin_edges)
		if bin is not None:
			hist[int(bin)] += 1

	return hist, bin_edges


# @numba.extending.overload(np.gradient)
@nb.njit()
def np_gradient(f):
    # def np_gradient_impl(f):
	out = np.empty_like(f, np.float64)
	out[1:-1] = (f[2:] - f[:-2]) / 2.0
	out[0] = f[1] - f[0]
	out[-1] = f[-1] - f[-2]
	return out

#    return np_gradient_impl


@nb.njit()
def density_2channel(x, y, dy, xsize, top, bottom):
	NbinY   = nb.int32((top-bottom)/dy)
	centerRaster = np.zeros((xsize, NbinY))
	for i in range(len(x)):
		xx = nb.int32(x[i])
		for j in range(len(y)):
			yy = nb.int32(np.floor((y[j] - bottom) / dy))
			centerRaster[xx, yy] += 1
	return(centerRaster)

@nb.njit()
def density_hist2d(data, dy, top, bottom):
	NbinY   = nb.int32((top-bottom)/dy)
	hist    = np.zeros((data.shape[1], NbinY))
	for i in range(data.shape[0]):
		for j in range(data.shape[1]):
			k = nb.int32(np.floor((data[i,j]-bottom)/ dy))
			hist[j,k] += 1
	return(hist)

@nb.njit(cache=True)
def np_all_axis0(x):
	"""Numba compatible version of np.all(x, axis=0)."""
	out = np.ones(x.shape[1], dtype=np.bool8)
	for i in range(x.shape[0]):
		out = np.logical_and(out, x[i, :])
	return out
@nb.njit(cache=True)
def np_all_axis1(x):
	"""Numba compatible version of np.all(x, axis=1)."""
	out = np.ones(x.shape[0], dtype=np.bool8)
	for i in range(x.shape[1]):
		out = np.logical_and(out, x[:, i])
	return out

@nb.njit(cache=True)
def close_factors(number):
	''' 
	find the closest pair of factors for a given number
	'''
	factor1 = 0
	factor2 = number
	while factor1 +1 <= factor2:
		factor1 += 1
		if number % factor1 == 0:
			factor2 = number // factor1
		
	return factor1, factor2

@nb.njit(cache=True)
def almost_factors(number):
	'''
	find a pair of factors that are close enough for a number that is close enough
	'''
	while True:
		factor1, factor2 = close_factors(number)
		if 1/2 * factor1 <= factor2: # the fraction in this line can be adjusted to change the threshold aspect ratio
			break
		number += 1
	return factor1, factor2

@nb.njit()
def common_elements(ar1, ar2, ar3):
    n1, n2, n3 = len(ar1), len(ar2), len(ar3)
    i, j, k = 0, 0, 0
    common = []
    while i < n1 and j < n2 and k < n3:
        if ar1[i] == ar2[j] == ar3[k]:
            common.append(ar1[i])
            i += 1
            j += 1
            k += 1
        elif ar1[i] < ar2[j]:
            i += 1
        elif ar2[j] < ar3[k]:
            j += 1
        else:
            k += 1
    return common


