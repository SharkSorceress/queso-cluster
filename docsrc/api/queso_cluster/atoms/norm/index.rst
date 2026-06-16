queso_cluster.atoms.norm
========================

.. py:module:: queso_cluster.atoms.norm


Functions
---------

.. autoapisummary::

   queso_cluster.atoms.norm.normContinuum
   queso_cluster.atoms.norm.normFunc
   queso_cluster.atoms.norm.normMaximum
   queso_cluster.atoms.norm.normZ


Module Contents
---------------

.. py:function:: normContinuum(dataSquare, continuumIndx)

   
   Normalizes the data to the intensity of a reference position

   :param dataSquare: 2D array containing the spectral data
   :type dataSquare: ndarray
   :param continuumIndx: Integer index of the position to normalize with respect to
   :type continuumIndx: int

   :returns: 2D array of normalized spectral data
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: normFunc(dataSquare, func)

   
   Normalizes the data with a user-defined function

   :param dataSquare: 2D array containing the spectral data
   :type dataSquare: ndarray
   :param func: user function which accepts an array and outputs an array of the same shape
   :type func: function

   :returns: 2D array of normalized spectral data
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: normMaximum(dataSquare, windowIndx=None)

   
   Normalizes the data to the maximum value in a given range

   :param dataSquare: 2D array containing the spectral data
   :type dataSquare: ndarray
   :param windowIndx: List containing the beginning and end (inclusive) of the desired range to find maximum.
                      If not set, this function will use the full avaliable range of the data
   :type windowIndx: list, optional

   :returns: 2D array of normalized spectral data
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: normZ(dataSquare)

   
   Z-Normalization

   .. todo:: I have to write this function.

   :param dataSquare: 2D array containing the spectral data
   :type dataSquare: ndarray

   :returns: 2D array of normalized spectral data
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

