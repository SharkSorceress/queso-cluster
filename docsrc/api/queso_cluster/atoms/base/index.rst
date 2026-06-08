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


   :Parameters:

       **k** : int
           The number of groups

       **data** : ndarray
           The data to be clustered

       **decision** : ndarray
           The previous iteration's decisions

       **threshold** : float, optional
           The convergence threshold



   :Returns:

       **decision** : ndarray
           The current iteration's representative profiles

       **data_label** : ndarray
           The labels for the data




   :Raises:

       ConvergenceError
           If the convergence criteria cannot be evaulated or if the convergence criterion is not met after :obj:`~queso_cluster.atoms.error.covergeLimit`







   ..
       !! processed by numpydoc !!

.. py:function:: compute_bin(x, bin_edges)

.. py:function:: concatSpectra(dataSquareLst)

   
   Function to concatenate several channels of data into one array for clustering


   :Parameters:

       **dataSquareLst** : dask.array
           dask arrays containing spectral data to be concatenated



   :Returns:

       dask.array
           Concatenated spectral profiles











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


   :Parameters:

       **a** : int
           detail

       **bins** : int
           the number of bins in the histogram

       **lim** : ndarray
           the top and bottom of the histogram             



   :Returns:

       **hist** : ndarray
           the histogram

       **bin_edges** : ndarray
           1D array of the bin edges











   ..
       !! processed by numpydoc !!

.. py:function:: rotateArray(image, turns)

   
   Rotates an array


   :Parameters:

       **image** : ndarray
           2D array to be rotated

       **turns** : int
           Number of pi/2 turns to rotate



   :Returns:

       ndarray
           Rotated array











   ..
       !! processed by numpydoc !!

.. py:function:: similarityMetric(x, y, type='dist', ref=0)

.. py:function:: startMax(data, k, decisions)

   
   Heuristic k-means++. 
   Rather than selecting from a distribution around the furtherest datapoint, this initialization simply selects the furtherest datapoint as the next representative


   :Parameters:

       **data** : ndarray
           data pool for finding the initial representative profiles

       **k** : int
           The number of clusters

       **decisions** : ndarray
           Array containing the initial, randomly selected representative profile and empty slots for remaining profiles



   :Returns:

       **decisions** : ndarray
           Array containing a full set of representative profiles











   ..
       !! processed by numpydoc !!

.. py:function:: startPlusPlus(data, k, decisions)

   
   k-means++ initialization


   :Parameters:

       **data** : ndarray
           data pool for finding the initial representative profiles

       **k** : int
           The number of clusters

       **decisions** : ndarray
           Array containing the initial, randomly selected representative profile and empty slots for remaining profiles



   :Returns:

       **decisions** : ndarray
           Array containing a full set of representative profiles











   ..
       !! processed by numpydoc !!

