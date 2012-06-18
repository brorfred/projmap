"""Setup file to generate a distribution of projmap

use as python setup.py sdist"""


from distutils.core import setup

setup(name='projmap',
      version='0.5',
      description='Higher level version of matplotlibs Basemap',
      author='Bror Jonsson',
      author_email='brorfred@gmail.com',
      url='http://brorfred.org/python_dists/projmap/',
      requires=["numpy(>=1.5)", "matplotlib(>=1.1.0)"],
      packages=['projmap'],
      package_data={'projmap': ['data/*.txt', 'map_regions.cfg']},
      #data_files=[('projmap', ['projmap/map_regions.cfg',])]
     )
