queso_cluster.addon.style
=========================

.. py:module:: queso_cluster.addon.style

.. autoapi-nested-parse::

   :file:  queso_cluster/addon/style
   :lang:  python
   :synopsis:
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   queso_cluster.addon.style.clusterColormap
   queso_cluster.addon.style.mapMaker


Module Contents
---------------

.. py:class:: clusterColormap(nbounds, tolColorLabel='rainbow_PuRd')

   
   Creates a colormap to be used with the cluster maps

   :param nbounds: the number of labels to use
   :type nbounds: int
   :param tolColorLabel: the name of the TOL colormap to use
   :type tolColorLabel: str, optional















   ..
       !! processed by numpydoc !!

   .. py:method:: cbar_bounds()

      
      Creates a list of uniform spaced tick locations

      :returns: * **actual_bounds** (*ndarray*) -- The edges of the bins to be used with mpl.colors.BoundaryNorm
                * **bound_ticks** (*ndarray*) -- Tick locations for plt.colorbar















      ..
          !! processed by numpydoc !!


   .. py:method:: genColorPalette()

      
      Creates a list of uniform spaced tick locations

      :returns: **color_palette** -- The hexcodes for the colors to be used in the colormap
      :rtype: list















      ..
          !! processed by numpydoc !!


   .. py:attribute:: cmap


   .. py:attribute:: nbounds


   .. py:attribute:: norm


   .. py:attribute:: tolColorLabel
      :value: 'rainbow_PuRd'



.. py:class:: mapMaker(spaceInfo, deltas)

   
   A class to format maps in a consistent way.

   :param spaceInfo: dictionary containing number of pixels in each spatial dimension
   :type spaceInfo: dict
   :param deltas: dictinary containing the raster pixel scale as 'pxlSlitWidth' and the along slit pixel scale as 'pxlAlongSlit'
   :type deltas: dict















   ..
       !! processed by numpydoc !!

   .. py:attribute:: bbox


   .. py:attribute:: cadence
      :value: 15.667



   .. py:attribute:: correct


   .. py:attribute:: deltas


   .. py:attribute:: extent


   .. py:attribute:: flatten


   .. py:attribute:: spaceInfo


   .. py:attribute:: unflatten


