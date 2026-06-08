queso_cluster.addon.products
============================

.. py:module:: queso_cluster.addon.products

.. autoapi-nested-parse::

   :file:  queso_cluster/addon/products.py
   :lang:  python
   :synopsis: 
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Classes
-------

.. autoapisummary::

   queso_cluster.addon.products.Products


Module Contents
---------------

.. py:class:: Products(quesoOut, config)

   
   Detail


   :Parameters:

       **quesoOut** : type
           summary

       **optLabels** : type
           summary

   :Attributes:

       **vindx** : ndarray
           tuple of the indicies corresponding to non-nan labels

       **vfindx** : ndarray
           1D array containing the indicies of non-nan labels

       **xlim** : ndarray
           The physical minimum and maximum of the raster direction

       **ylim** : ndarray
           The physical minimum and maximum of the along slit direction

       **aspect** : float
           Half of the aspect ratio

       **clusterCmap** : :class:`~queso_cluster.addon.style.clusterColormap`
           default color configuration for cluster maps

       **mapMake** : :class:`~queso_cluster.addon.style.mapMaker`
           A map object to plot the data













   ..
       !! processed by numpydoc !!

   .. py:method:: clusterMapCompound(compoundLabels, timeAxis=False)

      
      Creates a figure showing all of the distinct sequences of spectra


      :Parameters:

          **compoundLabels** : char.array
              Character array for all sequence labels

          **timeAxis** : bool
              Boolean to add an extra axis for time



      :Returns:

          **fig** : mpl.Figure
              Figure showing the distribution of cluster sequences











      ..
          !! processed by numpydoc !!


   .. py:method:: clusterMapSequence(timeAxis=False)

      



      :Parameters:

          **timeAxis** : bool, optional
              Boolean to add an extra axis for time



      :Returns:

          **figA** : mpl.Figure
              Map of the cluster results for individual time steps

          **figB** : mpl.Figure
              Map of all distinct sequences











      ..
          !! processed by numpydoc !!


   .. py:method:: clusterMapSequenceHorizontal(timeAxis)

      
      Horizontal oriented maps of the cluster results for individual time steps


      :Parameters:

          **compoundLabels** : char.array
              ..

          **timeAxis** : bool
              Boolean to add an extra axis for time



      :Returns:

          **fig** : mpl.figure
              Map of the cluster results for individual time steps

          **compoundLabels** : np.char.array
              Character array for all sequence labels











      ..
          !! processed by numpydoc !!


   .. py:method:: clusterMapSequenceVertical(timeAxis)

      
      Vertically oriented maps of the cluster results for individual time steps


      :Parameters:

          **compoundLabels** : char.array
              ..

          **timeAxis** : bool
              Boolean to add an extra axis for time



      :Returns:

          **fig** : mpl.figure
              Map of the cluster results for individual time steps

          **compoundLabels** : np.char.array
              Character array for all sequence labels











      ..
          !! processed by numpydoc !!


   .. py:method:: clusterProfiles(dev=False, showContinuum=True)

      
      Figure showing the representative profiles of each of the clusters and the raw data histogram


      :Parameters:

          **showContinuum** : bool, optional
              Adds a horizontal line at the continuum. Useful only if normalized to continuum

          **dev** : bool
              secret testing



      :Returns:

          **fig** : mpl.figure
              Figure          











      ..
          !! processed by numpydoc !!


   .. py:method:: clusterProfilesCompound(compoundLabels)


   .. py:method:: figure03()


   .. py:method:: load()


   .. py:method:: spectralEntry(ax, indx, color, wavelambda, extent, showContinuum, scores=None, dev=False)

      
      Calculation function for :func:`~queso_cluster.addon.products.Products.clusterProfiles`


      :Parameters:

          **ax** : mpl.Axes
              matplotlib axes to add content to

          **indx** : ndarray
              1D array of data indexes for a given cluster

          **color** : str
              color string for 2D histogram of raw data. gradient goes as white -> color

          **wavelambda** : ndarray
              1D array containing the wavelength

          **extent** : list
              List containing the left, right, bottom, top of the content

          **showContinuum** : bool
              Adds a horizontal line at the continuum. Useful only if normalized to continuum

          **scores** : float, optional
              Validation score to be shown in the figure window

          **dev** : bool, optional
              secret testing



      :Returns:

          **ax** : mpl.Axes
              Updated axis with all the content added











      ..
          !! processed by numpydoc !!


   .. py:attribute:: aspect


   .. py:attribute:: clusterCmap


   .. py:attribute:: keepI0


   .. py:attribute:: mapMake


   .. py:attribute:: vfindx


   .. py:attribute:: vindx


   .. py:attribute:: xlim


   .. py:attribute:: ylim


