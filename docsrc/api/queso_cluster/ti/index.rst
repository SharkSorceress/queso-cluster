queso_cluster.ti
================

.. py:module:: queso_cluster.ti

.. autoapi-nested-parse::

   :file:  queso_cluster/ti.py
   :lang:  python
   :synopsis:
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   queso_cluster.ti.timeIndependent


Module Contents
---------------

.. py:class:: timeIndependent(config, instrumentObj)

   
   Time independent clustering framework

   :param config: object containing yaml configuration
   :type config: :class:`~queso_cluster.loaders.event.eventInput`
   :param instrumentObj: A `loader` object for specific instruments
   :type instrumentObj: :class:`~queso_cluster.loaders.visp.visp`, :class:`~queso_cluster.loaders.fiss.fiss`, :class:`~queso_cluster.loaders.iris.iris`















   ..
       !! processed by numpydoc !!

   .. py:method:: cluster(intrinsicLine=None, kLst=None, initialize='max')

      
      Primary clustering function
















      ..
          !! processed by numpydoc !!


   .. py:method:: clusterCompoundLabels(optLabels)

      
      Concatenates the labels by time to form a sequence cluster

      :param optLabels: 3D array containing the finalized cluster labels
      :type optLabels: ndarray

      :returns: **compoundLabels** -- 2D array containing the cluster *sequence* labels
      :rtype: ndarray















      ..
          !! processed by numpydoc !!


   .. py:property:: geometry

      
      Imports spatial and temporal properties from instrumentObj

      :returns: Dictionary containing the geometry and cadence of the observations
      :rtype: dict















      ..
          !! processed by numpydoc !!


