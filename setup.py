from distutils.core import setup

setup(
    name='queso-cluster',
    version='0.0.0',
    author='Sarah Olivia Riley',
    author_email='sarah.riley1@montana.edu',
    packages=['queso-cluster', 'queso-cluster.atoms', 'queso-cluster.runners', 'queso-cluster.addon', 'tests'],
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
		"argparse",
		"tol-colors",
    ],
)