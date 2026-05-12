from distutils.core import setup

setup(
    name='queso_cluster',
    version='0.0.0',
    author='Sarah Olivia Riley',
    author_email='sarah.riley1@montana.edu',
    packages=['queso_cluster', 'queso_cluster.atoms', 'queso_cluster.runners', 'queso_cluster.addon', 'tests'],
    url='https://queso.sriley.dev',
    license='LICENSE',
    description='Quantifying the Evolution of Spectra with Optimization',
    long_description=open('README.md').read(),
    install_requires=[
        "numpy ",
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