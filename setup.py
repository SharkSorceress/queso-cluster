from distutils.core import setup

from queso_cluster import __version__

setup(
    name='queso_cluster',
    version=__version__,
    author='Sarah Olivia Riley',
    author_email='sarah.riley1@montana.edu',
    packages=['queso_cluster', 'queso_cluster.atoms', 'queso_cluster.runners', 'queso_cluster.addon', 'queso_cluster.loaders', 'tests'],
    url='https://queso.sriley.dev',
    description='Quantifying the Evolution of Spectra with Optimization',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy>=1.25",
        "dkist ",
		"scipy",
		"numba",
		"astropy",
		"numba_progress",
		"dask",
		"pyyaml",
		"tol-colors",
		"pint"
    ],
)