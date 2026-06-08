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


   :Parameters:

       **nbounds** : int
           the number of labels to use

       **tolColorLabel** : str, optional
           the name of the TOL colormap to use

   :Attributes:

       **cmap** : ListedColormap
           The matplotlib colormap to use

       **norm** : BoundaryNorm
           The matplotlib normalization to use

       **bound_ticks** : ndarray
           Tick locations for plt.colorbar













   ..
       !! processed by numpydoc !!

   .. py:method:: cbar_bounds()

      
      Creates a list of uniform spaced tick locations 





      :Returns:

          **actual_bounds** : ndarray
              The edges of the bins to be used with mpl.colors.BoundaryNorm

          **bound_ticks** : ndarray
              Tick locations for plt.colorbar











      ..
          !! processed by numpydoc !!


   .. py:method:: genColorPalette()

      
      Creates a list of uniform spaced tick locations 





      :Returns:

          **color_palette** : list
              The hexcodes for the colors to be used in the colormap











      ..
          !! processed by numpydoc !!


   .. py:attribute:: cmap


   .. py:attribute:: nbounds


   .. py:attribute:: norm


   .. py:attribute:: tolColorLabel
      :value: 'rainbow_PuRd'



.. py:class:: mapMaker(spaceInfo, deltas)

   
   A class to format maps in a consistent way.


   :Parameters:

       **spaceInfo** : dict
           dictionary containing number of pixels in each spatial dimension 

       **deltas** : dict
           dictinary containing the raster pixel scale as 'pxlSlitWidth' and the along slit pixel scale as 'pxlAlongSlit'

   :Attributes:

       **flatten** : lambda function
           creates a 1D array from a spatial 2D array

       **unflatten** : lambda function
           creates a spatial 2D array from a flattened 1D array

       **bbox** : ndarray
           1D array containing the extent of the region in pixel units

       **extent** : ndarray
           1D array containing the extent of the region in arcseconds

       **correct** : lambda function
           Flattens a transposed array (for IDL maps only)













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


