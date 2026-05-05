*************
API Reference
*************

---------
writer.py
---------

.. function:: exportFITS(spectralDataset,labelLine,fname)


------
aux.py
------

.. function:: _gen_dataID(Input)


.. function:: pick_jth_label(labelLst,j)


.. function:: density_2channel(x,y,dy,xsize,top,bottom)


.. function:: density_hist2d(data,dy,top,bottom)


.. function:: close_factors(number)


.. function:: almost_factors(number)


.. function:: common_elements(ar1,ar2,ar3)


-------
base.py
-------

.. function:: normZ(dataSquare)


.. function:: normMaximum(dataSquare)


.. function:: normContinuum(dataSquare,continuumIndx)


.. function:: concatSpectra(dataSquareLst)


.. function:: numba_histogram(a,bins,lim)


.. function:: rotateArray(image,turns)


.. function:: get_bin_edges(bins,lim)


.. function:: compute_bin(x,bin_edges)


.. function:: np_gradient(f)


.. function:: minimize(data,decisions,size)


.. function:: maximize(data,decisions,size)


.. function:: np_all_axis0(x)


.. function:: np_all_axis1(x)


.. function:: similarityMetric(x,y,type='dist',ref=0)


.. function:: curvature(y)


.. function:: startMax(data,k,decisions)


.. function:: startPlusPlus(data,k,decisions)


.. function:: _calcMoment(waveAxis,ii,jj,lineCore,dataCube,order,ref,counter=0)


.. function:: _calcFeatureDensity(data,converge,zindx,func1)


.. function:: _calcOptimization(k,data,decision,threshold)


.. function:: _calcElbowEntry(data,labels)


.. function:: _calcVarianceScore(data)


.. function:: _criteriaInertiaScore(score)


.. function:: _calcInertiaScore(dataSquare,labelLine)


.. function:: _criteriaSilhouetteScore(score)


.. function:: _calcSilhouetteScore(dataSquare,labelLine)


.. function:: _calcSingleSilhouetteScore(data,labels,lab)


.. function:: _calcCHindex(data,labels)


.. function:: labelGluer(labels)


.. function:: labelReorder(labels)


.. function:: _calcQuiescentFrame(spectralData,spectralParams,contIndxs,progress=None)


.. function:: _calcDynamicFrame(spectralData,dynamicScanNum,progress=None,delta=0)


-----------
approach.py
-----------

.. function:: __init__(self,config,catalogName,instrumentObj)


.. function:: __getattr__(self,name)


.. function:: cluster(self,prepSquare,maskLine


.. function:: __init__(self,catalogBase)


.. function:: clustering(self,prepCube,tlst,groups,intrinsicSquare=None)

	:detail: low temporal resolution clustering

-------
logg.py
-------

.. function:: loggTimer(func)


.. function:: wrapper(*args,**kwargs)


.. function:: logg(tag,val=None,_time=None,_log=None)


.. function:: duration_string(dur)


------
aia.py
------

.. function:: delayAIA(fname,epochDev)


--------
style.py
--------

.. function:: cbar_bounds(bounds)


.. function:: _genColorPallet(n)


.. function:: rainbow_cmap(nrange,discrete=False,nan=False)


.. function:: cmap_discretize(cmap,N)


.. function:: __init__(self,spaceInfo,deltas)


.. function:: _mapGen(self,fig,pos,arr,flareContour=None,timeAxis=None,**kwargsDict)


------------
multiline.py
------------

-----------
products.py
-----------

.. function:: __init__(self,epochObj,optLabels)


.. function:: figure03(self)


.. function:: figure04_template(self)


.. function:: spectralEntry(self,ax,indx,color,wavelambda,extent,scores=None)


---------
loader.py
---------

.. function:: __init__(self,data,home,fig)


.. function:: _loadEventConfig(self,eventRunnerFname,args)


.. function:: __init__(self,dataPath)


.. function:: vispLoad(self,stokes=0)


.. function:: irisLoad(self)


.. function:: fissLoad(self,labels)


.. function:: __init__(self,config1,config2)


.. function:: visp2visp(self)


.. function:: fiss2fiss(self)


.. function:: __init__(self,dataPath,labels)


.. function:: __init__(self,dataPath,stokes=0)


.. function:: __init__(self,inputLst,runIndx)


.. function:: loadSource(self,eventInput)


.. function:: __init__(self,srcInput)


.. function:: __init__(self,runnerInput)


.. function:: __init__(self,fname,eventIndx,runIndx)


.. function:: _load(self,fname)


-------
base.py
-------

.. function:: _mainIntrinsic(config,prepSquare,lineIndx,intrinsicSkip=False)


.. function:: _mainOptimization(prepSquare,labelLine,kLst=None,stageMax=2)


-------
base.py
-------

.. function:: _runOptimalKSearch(dataSquare,funcLst,checkLst)


.. function:: runPrep(dataSquare,norm='continuum',keepI0=None,maskLine=None,quSquare=None,**kwargs)


.. function:: _runIntrinsic(nbins,data,edgeOverride=None)


.. function:: runStart(k,data,start='max')


.. function:: _runOptimization(k,sub_data,converge)


.. function:: _findOptimalK(dataSquare,funcLst,criteriaLst,converge=1e-6)


.. function:: _runLabelSort(dataSquare,labelLine)

