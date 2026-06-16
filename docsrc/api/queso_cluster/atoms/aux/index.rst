queso_cluster.atoms.aux
=======================

.. py:module:: queso_cluster.atoms.aux

.. autoapi-nested-parse::

   :file: queso_cluster/atoms/aux
   :lang:  python
   :synopsis:
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Functions
---------

.. autoapisummary::

   queso_cluster.atoms.aux.almost_factors
   queso_cluster.atoms.aux.close_factors
   queso_cluster.atoms.aux.common_elements
   queso_cluster.atoms.aux.convertTime
   queso_cluster.atoms.aux.density_hist2d
   queso_cluster.atoms.aux.pick_jth_label


Module Contents
---------------

.. py:function:: almost_factors(number)

.. py:function:: close_factors(number)

.. py:function:: common_elements(ar1, ar2, ar3)

.. py:function:: convertTime(dates, baseFormat='%Y-%m-%dT%H:%M:%S', ref=False)

   
   Converts time stamps into seconds

   :param dates: list containing the datetime stamps from header information
   :type dates: list
   :param baseFormat: String format for the datetime without microseconds
   :type baseFormat: str, optional
   :param ref: Boolean to decide if you want to use the initial datetime stamp as a reference
   :type ref: boolean, optional

   :returns: 1D array containing time in units of seconds since 1970 Jan 01
   :rtype: ndarray















   ..
       !! processed by numpydoc !!

.. py:function:: density_hist2d(data, dy, top, bottom)

.. py:function:: pick_jth_label(labelLst, j)

