"""
	:file:  queso_cluster/atom/error.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>


    Attributes
    ----------
    convergeLimit : int
        Maximum number of interations before ConvergenceError is raised
"""
import numpy as np

convergeLimit = int(1000)

class ConvergenceError(Exception):
    """
    Create an Exception for when convergence doesn't occur after :obj:`~queso_cluster.atoms.error.convergeLimit` iterations
    """
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        # if np.isnan(self.killCounter):
        #     return("Convergence condition is nan.")
        #else:
        return(self.msg)
        #return("Convergence condition not met after 1000 steps")


class LoadError(Exception):
    """
    Creates an Exception for overwrite contradiction
    """

    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return("Overwrite is set to False. Cannot run.")