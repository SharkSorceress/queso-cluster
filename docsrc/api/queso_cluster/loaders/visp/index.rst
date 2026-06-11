queso_cluster.loaders.visp
==========================

.. py:module:: queso_cluster.loaders.visp


Classes
-------

.. autoapisummary::

   queso_cluster.loaders.visp.visp


Module Contents
---------------

.. py:class:: visp(dataDirectory=None, stokes='I')

   Bases: :py:obj:`queso_cluster.loaders.event.eventRunner`


   
   Detail

   :param fname: File path of the eventManager.yml
   :type fname: str
   :param eventIndx: integer for the order of the event in the eventManager.yml
   :type eventIndx: list
   :param runIndx: integer for the order of the runner in the eventManager.yml
   :type runIndx: int















   ..
       !! processed by numpydoc !!

   .. py:property:: dataPrism


   .. py:property:: dimInfo


   .. py:property:: fitWavelength

      
      If a wavelength calibration is present in the eventManager.yml, this attribute will store the physical wavelength axis in Angstroms
















      ..
          !! processed by numpydoc !!


   .. py:property:: mapCadence

      
      the time between rasters
















      ..
          !! processed by numpydoc !!


   .. py:property:: pxlDelta


   .. py:property:: resetDuration

      
      the time it takes to go from the end of the raster to the start of a new raster
















      ..
          !! processed by numpydoc !!


   .. py:property:: stepCadence

      
      the time between slit positions
















      ..
          !! processed by numpydoc !!


   .. py:attribute:: stokes_lst
      :value: ['I', 'Q', 'U', 'V']



