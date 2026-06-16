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

.. py:class:: Products(quesoOut)

   
   Detail

   :param quesoOut: Analysis object that stores all of the configuration
   :type quesoOut: :class:`~queso_cluster.ti.timeIndependent` or :class:`~queso_cluster.td.timeDependent`















   ..
       !! processed by numpydoc !!

   .. py:method:: clusterMapCompound(compoundLabels, timeAxis=False)

      
      Creates a figure showing all of the distinct sequences of spectra

      :param compoundLabels: Character array for all sequence labels
      :type compoundLabels: char.array
      :param timeAxis: Boolean to add an extra axis for time
      :type timeAxis: bool

      :returns: **fig** -- Figure showing the distribution of cluster sequences
      :rtype: mpl.Figure















      ..
          !! processed by numpydoc !!


   .. py:method:: clusterMapSequence(timeAxis=False)

      
      :param timeAxis: Boolean to add an extra axis for time
      :type timeAxis: bool, optional

      :returns: * **figA** (*mpl.Figure*) -- Map of the cluster results for individual time steps
                * **figB** (*mpl.Figure*) -- Map of all distinct sequences















      ..
          !! processed by numpydoc !!


   .. py:method:: clusterMapSequenceHorizontal(timeAxis)

      
      Horizontal oriented maps of the cluster results for individual time steps

      :param compoundLabels:
      :type compoundLabels: char.array
      :param timeAxis: Boolean to add an extra axis for time
      :type timeAxis: bool

      :returns: * **fig** (*mpl.figure*) -- Map of the cluster results for individual time steps
                * **compoundLabels** (*np.char.array*) -- Character array for all sequence labels















      ..
          !! processed by numpydoc !!


   .. py:method:: clusterMapSequenceVertical(timeAxis)

      
      Vertically oriented maps of the cluster results for individual time steps

      :param compoundLabels:
      :type compoundLabels: char.array
      :param timeAxis: Boolean to add an extra axis for time
      :type timeAxis: bool

      :returns: * **fig** (*mpl.figure*) -- Map of the cluster results for individual time steps
                * **compoundLabels** (*np.char.array*) -- Character array for all sequence labels















      ..
          !! processed by numpydoc !!


   .. py:method:: clusterProfiles(dev=False, showContinuum=True)

      
      Figure showing the representative profiles of each of the clusters and the raw data histogram

      :param showContinuum: Adds a horizontal line at the continuum. Useful only if normalized to continuum
      :type showContinuum: bool, optional
      :param dev: secret testing
      :type dev: bool

      :returns: **fig** -- Figure
      :rtype: mpl.figure















      ..
          !! processed by numpydoc !!


   .. py:method:: clusterProfilesCompound(compoundLabels)


   .. py:method:: load()


   .. py:method:: spectralEntry(ax, indx, showContinuum, scores=None, dev=False)

      
      Calculation function for :func:`~queso_cluster.addon.products.Products.clusterProfiles`

      :param ax: matplotlib axes to add content to
      :type ax: mpl.Axes
      :param indx: 1D array of data indexes for a given cluster
      :type indx: ndarray
      :param color: color string for 2D histogram of raw data. gradient goes as white -> color
      :type color: str
      :param wavelambda: 1D array containing the wavelength
      :type wavelambda: ndarray
      :param extent: List containing the left, right, bottom, top of the content
      :type extent: list
      :param showContinuum: Adds a horizontal line at the continuum. Useful only if normalized to continuum
      :type showContinuum: bool
      :param scores: Validation score to be shown in the figure window
      :type scores: float, optional
      :param dev: secret testing
      :type dev: bool, optional

      :returns: **ax** -- Updated axis with all the content added
      :rtype: mpl.Axes















      ..
          !! processed by numpydoc !!


   .. py:attribute:: aspect


   .. py:attribute:: clusterCmap


   .. py:attribute:: mapMake


   .. py:attribute:: vfindx


   .. py:attribute:: vindx


   .. py:attribute:: xlim


   .. py:attribute:: ylim


