queso_cluster.base
==================

.. py:module:: queso_cluster.base


Classes
-------

.. autoapisummary::

   queso_cluster.base.interface


Functions
---------

.. autoapisummary::

   queso_cluster.base.mainIntrinsic
   queso_cluster.base.mainOptimization


Module Contents
---------------

.. py:class:: interface(config, instrument, framework)

   .. py:method:: load()


   .. py:method:: run(prepConfig)


   .. py:method:: write(labelSquare)


   .. py:attribute:: config


   .. py:attribute:: flavor


   .. py:attribute:: framework


.. py:function:: mainIntrinsic(config, prepSquare)

.. py:function:: mainOptimization(prepSquare, labelLine, initialize, kLst=None, stageMax=2)

