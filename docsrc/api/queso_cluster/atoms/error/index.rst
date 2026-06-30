queso_cluster.atoms.error
=========================

.. py:module:: queso_cluster.atoms.error

.. autoapi-nested-parse::

   :file:  queso_cluster/atom/error.py
   :lang:  python
   :synopsis:
   :author: Sarah Riley <academic@sriley.dev>

   ..
       !! processed by numpydoc !!


Attributes
----------

.. autoapisummary::

   queso_cluster.atoms.error.convergeLimit


Exceptions
----------

.. autoapisummary::

   queso_cluster.atoms.error.ClusterError
   queso_cluster.atoms.error.ConvergenceError
   queso_cluster.atoms.error.IntrinsicLabelError
   queso_cluster.atoms.error.LoadError
   queso_cluster.atoms.error.OopsAllNan
   queso_cluster.atoms.error.RPConflictWarning


Module Contents
---------------

.. py:exception:: ClusterError

   Bases: :py:obj:`Exception`


   
   Creates an Exception to handle the case when the user uses a value of k which is strictly less than one
















   ..
       !! processed by numpydoc !!

.. py:exception:: ConvergenceError(msg)

   Bases: :py:obj:`Warning`


   
   Create an Exception for when convergence doesn't occur after :obj:`~queso_cluster.atoms.error.convergeLimit` iterations
















   ..
       !! processed by numpydoc !!

   .. py:attribute:: msg


.. py:exception:: IntrinsicLabelError

   Bases: :py:obj:`Exception`


   
   Creates an Exception to handle the case when the instrinic label is incorrect
















   ..
       !! processed by numpydoc !!

.. py:exception:: LoadError

   Bases: :py:obj:`Exception`


   
   Creates an Exception for overwrite contradiction
















   ..
       !! processed by numpydoc !!

.. py:exception:: OopsAllNan

   Bases: :py:obj:`Exception`


   
   Creates an Exception to raise an error when all data has been NaN'd
















   ..
       !! processed by numpydoc !!

.. py:exception:: RPConflictWarning

   Bases: :py:obj:`Warning`


   
   Base class for warning categories.
















   ..
       !! processed by numpydoc !!

.. py:data:: convergeLimit
   :value: 1000


   
   Maximum number of interations before ConvergenceError is raised
















   ..
       !! processed by numpydoc !!

