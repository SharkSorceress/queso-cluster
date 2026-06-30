queso_cluster.atoms.scores
==========================

.. py:module:: queso_cluster.atoms.scores


Functions
---------

.. autoapisummary::

   queso_cluster.atoms.scores.calcDaviesBouldin
   queso_cluster.atoms.scores.calcNeighborSilhouetteScore
   queso_cluster.atoms.scores.findSampleNeighbor
   queso_cluster.atoms.scores.speedTest
   queso_cluster.atoms.scores.speedTest2


Module Contents
---------------

.. py:function:: calcDaviesBouldin(data, labels, q=2)

.. py:function:: calcNeighborSilhouetteScore(dataSquare, labelLine, point)

   
   Calculates the Silhouette Score for a specific cluster

   :param dataSquare: 2D array (nsamples, nfeatures) containing the pool of data
   :type dataSquare: ndarray
   :param labelLine: 1D array (nsamples,) for the labels on the data
   :type labelLine: ndarray
   :param point: cluster label to evaluate
   :type point: int

   :returns: Silhouette Score
   :rtype: int















   ..
       !! processed by numpydoc !!

.. py:function:: findSampleNeighbor(dataSquare, labelLine, pointIndx)

   
   Calculates the nearest label to a given sample

   :param dataSquare: 2D array (nsamples, nfeatures) containing the pool of data
   :type dataSquare: ndarray
   :param labelLine: 1D array (nsamples,) for the labels on the data
   :type labelLine: ndarray
   :param pointIndx: sample index
   :type pointIndx: int

   :returns: The label of the nearest cluster to that point
   :rtype: int















   ..
       !! processed by numpydoc !!

.. py:function:: speedTest(interSamples, intraSample, interIndxSize)

.. py:function:: speedTest2(intraSamples, intraIndxSize, i)

