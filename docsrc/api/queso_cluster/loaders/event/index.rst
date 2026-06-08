queso_cluster.loaders.event
===========================

.. py:module:: queso_cluster.loaders.event

.. autoapi-nested-parse::

   :file:  queso_cluster/loaders/event.py
   :lang:  python
   :synopsis: 
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   queso_cluster.loaders.event.eventRunner


Module Contents
---------------

.. py:class:: eventRunner(fname, eventIndx, runIndx)

   
   Detail


   :Parameters:

       **fname** : str
           File path of the eventManager.yml

       **eventIndx** : list
           integer for the order of the event in the eventManager.yml

       **runIndx** : int
           integer for the order of the runner in the eventManager.yml














   ..
       !! processed by numpydoc !!

   .. py:method:: srcMeta(srcInput)


   .. py:property:: blueEdge

      
      int containing the index for the beginning of the spectral window used for clustering
















      ..
          !! processed by numpydoc !!


   .. py:property:: datasetID


   .. py:property:: directoryDate

      
      The datestring directory
















      ..
          !! processed by numpydoc !!


   .. py:property:: flavor


   .. py:property:: lineCenter

      
      The index for a center position in the window. This may coinside with the line center of the spectrum
















      ..
          !! processed by numpydoc !!


   .. py:property:: lineContinuum

      
      The index of the continuum for the spectrum. This may be used for normalization
















      ..
          !! processed by numpydoc !!


   .. py:property:: overwrite


   .. py:property:: redEdge

      
      int containing the index for the end of the spectral window used for clustering
















      ..
          !! processed by numpydoc !!


   .. py:property:: runnerConfig


   .. py:property:: timeFrames


