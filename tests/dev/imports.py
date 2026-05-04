import numba
import numpy as np
from numba import jit
import numba as nb
from numba_progress import ProgressBar

from scipy import interpolate
from scipy.io import readsav
from scipy.signal import find_peaks
import scipy.interpolate
import scipy.ndimage

import timeit
import time
import datetime as dt
from datetime import datetime, timezone

import os, sys, gc
import os.path
import requests
import dill, pickle
import yaml
import glob
#from multiprocessing import Pool

import logging

import dask.array as da
from netCDF4 import Dataset

import matplotlib.style as mplstyle
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec, GridSpecFromSubplotSpec
import matplotlib.colors as colors
import matplotlib.dates as mdates				

import dkist
import dkist.net
from sunpy.net import Fido, attrs as a
from astropy import units as u
import astropy.io.fits as fits
from astropy.time import Time
import astropy

import sunpy
from sunpy.visualization import drawing
from sunpy.coordinates import frames
from sunpy.map.header_helper import make_fitswcs_header

# import lib.util.utility as util
# from lib.util.tol_colors import tol_cmap
# import lib.prep as pre
# #import lib.util.Global as globalVars
# import lib.analysis as analysis
# from lib.util.datClass import Input, vispDataset, hiKObj, fissDataset
# from lib.util.dataWriter import exportNetCDF
# import lib.util.style as sty

# import lib.util.ViSP_tools as vt

#www_catalog  = "https://solar.physics.montana.edu/sriley/catalog"
#www_catkey   = "https://solar.physics.montana.edu/sriley/catalog_key"
#www_main     = "https://solar.physics.montana.edu/sriley" 

dkist_dir = ""
home_dir  = "" 

# match os.uname()[1]:
#     case 'filament':
#         home_dir = '/disk/data/sriley/'
#         #www_dir  = '/www/sriley'
#     case 'mandjetcola13':
#         home_dir = '/hdd/filament/'
#         #globus_dir = '/hdd/globusconnectpersonal-*/'
#     case 'neothothcola13':
#         home_dir = '/media/pharaohcola13/USB DISK/filament/'
        

__version__ = "0.0.0"
__versionLongName__ = "mild"