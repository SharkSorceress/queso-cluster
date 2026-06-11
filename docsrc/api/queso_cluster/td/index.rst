queso_cluster.td
================

.. py:module:: queso_cluster.td

.. autoapi-nested-parse::

   :file:  queso_cluster/td.py
   :lang:  python
   :synopsis:
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   queso_cluster.td.timeDependent


Module Contents
---------------

.. py:class:: timeDependent(config, instrumentObj)

   
   Time dependent clustering framework

   :param config: object containing yaml configuration
   :type config: :class:`~queso_cluster.loaders.event.eventInput`
   :param catalogBase: base string for catalog name
   :type catalogBase: str
   :param instrumentObj: A `loader` object for specific instruments
   :type instrumentObj: :class:`~queso_cluster.loaders.visp.visp`, :class:`~queso_cluster.loaders.fiss.fiss`, :class:`~queso_cluster.loaders.iris.iris`















   ..
       !! processed by numpydoc !!

   .. py:method:: cluster(prepSquare, maskLine, intrinsicLine=None, kLst=None)


   .. py:method:: clusterSequence(prepCube, maskLine, klst, intrinsicLine=None)


   .. py:method:: prepSequence(timeFrames, **kwargs)


   .. py:method:: timeFrames(nframes=5, peakTime=None)


