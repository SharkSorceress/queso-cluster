queso_cluster.atoms.error
=========================

.. py:module:: queso_cluster.atoms.error

.. autoapi-nested-parse::

       :file:  queso_cluster/atom/error.py
       :lang:  python
       :synopsis: 
       :author: Sarah Riley <academic@sriley.dev>


   Attributes
   ----------
   convergeLimit : int
       Maximum number of interations before ConvergenceError is raised

   ..
       !! processed by numpydoc !!


Attributes
----------

.. autoapisummary::

   queso_cluster.atoms.error.convergeLimit


Exceptions
----------

.. autoapisummary::

   queso_cluster.atoms.error.ConvergenceError
   queso_cluster.atoms.error.LoadError


Module Contents
---------------

.. py:exception:: ConvergenceError(msg)

   Bases: :py:obj:`Exception`


   
   Create an Exception for when convergence doesn't occur after :obj:`~queso_cluster.atoms.error.convergeLimit` iterations
















   ..
       !! processed by numpydoc !!

   .. py:attribute:: msg


.. py:exception:: LoadError

   Bases: :py:obj:`Exception`


   
   Creates an Exception for overwrite contradiction
















   ..
       !! processed by numpydoc !!

.. py:data:: convergeLimit
   :value: 1000


