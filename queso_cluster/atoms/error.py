"""
	:file:  queso_cluster/atom/error.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>

"""
import numpy as np

convergeLimit = int(1000)
"""Maximum number of interations before ConvergenceError is raised"""

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


class IntrinsicLabelError(Exception):
    """
    Creates an Exception to handle the case when the instrinic label is incorrect
    """
    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return("Invalid intrinsic layer selection. Allowed labels include lineCenter, window, and lineContinuum")


class ClusterError(Exception):
    """
    Creates an Exception to handle the case when the user uses a value of k which is strictly less than one
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        return("Value of k must be positive and at least 1.")