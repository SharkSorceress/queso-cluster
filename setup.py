from distutils.core import setup

setup(
    name='QuESO',
    version='0.0.0',
    author='Sarah Olivia Riley',
    author_email='sarah.riley1@montana.edu',
    packages=['QuESO', 'QuESO.atoms', 'QuESO.runners', 'QuESO.addon', 'tests'],
    url='https://queso.sriley.dev',
    license='LICENSE.txt',
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