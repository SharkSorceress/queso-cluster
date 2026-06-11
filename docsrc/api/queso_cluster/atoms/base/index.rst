queso_cluster.atoms.base
========================

.. py:module:: queso_cluster.atoms.base

.. autoapi-nested-parse::

   :file: queso_cluster/atoms/base.py
   :lang:  python
   :synopsis:
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Functions
---------

.. autoapisummary::

   queso_cluster.atoms.base.calcOptimization
   queso_cluster.atoms.base.compute_bin
   queso_cluster.atoms.base.concatSpectra
   queso_cluster.atoms.base.curvature
   queso_cluster.atoms.base.get_bin_edges
   queso_cluster.atoms.base.labelGluer
   queso_cluster.atoms.base.labelReorder
   queso_cluster.atoms.base.maximize
   queso_cluster.atoms.base.minimize
   queso_cluster.atoms.base.np_all_axis0
   queso_cluster.atoms.base.np_all_axis1
   queso_cluster.atoms.base.np_gradient
   queso_cluster.atoms.base.numba_histogram
   queso_cluster.atoms.base.rotateArray
   queso_cluster.atoms.base.similarityMetric
   queso_cluster.atoms.base.startMax
   queso_cluster.atoms.base.startPlusPlus


Module Contents
---------------

.. py:function:: calcOptimization(k, data, decision, threshold=1e-06)

   
   Calculates the set of k decisions with a convergence threshold

   :param k: The number of groups
   :type k: int
   :param data: The data to be clustered
   :type data: ndarray
   :param decision: The previous iteration's decisions
   :type decision: ndarray
   :param threshold: The convergence threshold
   :type threshold: float, optional

   :raises ConvergenceError: If the convergence criteria cannot be evaulated or if the convergence criterion is not met after :obj:`~queso_cluster.atoms.error.covergeLimit`

   :returns: * **decision** (*ndarray*) -- The current iteration's representative profiles
             * **data_label** (*ndarray*) -- The labels for the data















   ..
       !! processed by numpydoc !!

.. py:function:: compute_bin(x, bin_edges)

.. py:function:: concatSpectra(dataSquareLst)

   
   Function to concatenate several channels of data into one array for clustering

   :param dataSquareLst: dask arrays containing spectral data to be concatenated
   :type dataSquareLst: dask.array

   :returns: Concatenated spectral profiles
   :rtype: dask.array















   ..
       !! processed by numpydoc !!

.. py:function:: curvature(y)

.. py:function:: get_bin_edges(bins, lim)

.. py:function:: labelGluer(labels)

.. py:function:: labelReorder(labels)

.. py:function:: maximize(data, decisions, size)

.. py:function:: minimize(data, decisions, size)

.. py:function:: np_all_axis0(x)

.. py:function:: np_all_axis1(x)

.. py:function:: np_gradient(f)

.. py:function:: numba_histogram(a, bins, lim)

   
   Numba accelerated histogram function

   :param a: detail
   :type a: int
   :param bins: the number of bins in the histogram
   :type bins: int
   :param lim: the top and bottom of the histogram
   :type lim: ndarray

   :returns: * **hist** (*ndarray*) -- the histogram
             * **bin_edges** (*ndarray*) -- 1D array of the bin edges















   ..
       !! processed by numpydoc !!

.. py:function:: rotateArray(image, turns)

   
   Rotates an array

   :param image: 2D array to be rotated
   :type image: ndarray
   :param turns: Number of pi/2 turns to rotate
   :type turns: int

   :returns: Rotated array
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: similarityMetric(x, y, type='dist', ref=0)

.. py:function:: startMax(data, k, decisions)

   
   Heuristic k-means++.
   Rather than selecting from a distribution around the furtherest datapoint, this initialization simply selects the furtherest datapoint as the next representative

   :param data: data pool for finding the initial representative profiles
   :type data: ndarray
   :param k: The number of clusters
   :type k: int
   :param decisions: Array containing the initial, randomly selected representative profile and empty slots for remaining profiles
   :type decisions: ndarray

   :returns: **decisions** -- Array containing a full set of representative profiles
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: startPlusPlus(data, k, decisions)

   
   k-means++ initialization

   :param data: data pool for finding the initial representative profiles
   :type data: ndarray
   :param k: The number of clusters
   :type k: int
   :param decisions: Array containing the initial, randomly selected representative profile and empty slots for remaining profiles
   :type decisions: ndarray

   :returns: **decisions** -- Array containing a full set of representative profiles
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

