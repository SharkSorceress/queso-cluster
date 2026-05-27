import numpy as np
import dask.array as da
import numba as nb


def normFunc(dataSquare, func):
	#> detail: 
	#> param type dataSquare:
    #> param type func:
	#> return (type): 
	#> test-method:    
    return(func(dataSquare))

def normZ(dataSquare):
	#> detail: 
	#> param type dataSquare:
	#> return (type): 
	#> test-method:
	print("TBD")
	return(dataSquare)

def normMaximum(dataSquare):
	#> detail: 
	#> param type dataSquare:
	#> return (type): 
	#> test-method:
	norm_func = lambda x: x/(x.max(axis=1))[:,None]
	normSquare = da.blockwise(norm_func, 'ij', dataSquare, 'ij', dtype=np.float32)
	return(normSquare)

def normContinuum(dataSquare, continuumIndx):
	#> detail: 
	#> param type dataSquare:
	#> param type continuumIndx:
	#> return (type): 
	#> test-method:
	norm_func = lambda x: x/(x[:, int(continuumIndx)])[:,None]
	normSquare = da.blockwise(norm_func, 'ij', dataSquare, 'ij', dtype=np.float32)
	return(normSquare)