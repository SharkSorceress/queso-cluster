"""
	:file:  queso_cluster/atom/error.py
	:lang:  python
	:synopsis: 
	:author: Sarah Riley <academic@sriley.dev>

"""
import numpy as np

convergeLimit = int(1000)
"""Maximum number of interations before ConvergenceError is raised"""

class ConvergenceError(Warning):
    """
    Create an Exception for when convergence doesn't occur after :obj:`~queso_cluster.atoms.error.convergeLimit` iterations
    """
    def __init__(self, msg):
        self.msg = msg
        super().__init__(self.msg)

    def __str__(self):
        return(self.msg)



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

class RPConflictWarning(Warning):

    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return("Something occured and the number of labels is no longer equal to the input k")

class ClusterError(Exception):
    """
    Creates an Exception to handle the case when the user uses a value of k which is strictly less than one
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        return("Value of k must be positive and at least 1.")

class OopsAllNan(Exception):
    """
    Creates an Exception to raise an error when all data has been NaN'd
    """
    def __init__(self):
        super().__init__()

    def __str__(self):
        return("No valid indexes. All data is NaN or masked out. Check clustering configuration")