#> file:  ./QuESO/atoms/aux
#> lang:  python
#> synopsis: 
#> author:   <>
import numpy as np
import numba as nb


def _gen_dataID(Input):
#> detail: 
#> param type Input:
#> return (type): 
#> test-method:
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
#> detail: 
#> param type labelLst:
#> param type j:
#> return (type): 
#> test-method:
	return(np.array([str(x)[j] for x in labelLst.astype(int)]).astype(int))


@nb.njit()
def density_2channel(x, y, dy, xsize, top, bottom):
#> detail: 
#> param type x:
#> param type y:
#> param type dy:
#> param type xsize:
#> param type top:
#> param type bottom:
#> return (type): 
#> test-method:
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
#> detail: 
#> param type data:
#> param type dy:
#> param type top:
#> param type bottom:
#> return (type): 
#> test-method:
	NbinY   = nb.int32((top-bottom)/dy)
	hist    = np.zeros((data.shape[1], NbinY))
	for i in range(data.shape[0]):
		for j in range(data.shape[1]):
			k = nb.int32(np.floor((data[i,j]-bottom)/ dy))
			hist[j,k] += 1
	return(hist)



@nb.njit(cache=True)
def close_factors(number):
#> detail: 
#> param type number:
#> return (type): 
#> test-method:
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
#> detail: 
#> param type number:
#> return (type): 
#> test-method:
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
#> detail: 
#> param type ar1:
#> param type ar2:
#> param type ar3:
#> return (type): 
#> test-method:
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


