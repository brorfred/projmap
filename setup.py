"""Setup file to generate a distribution of projmap

use as python setup.py sdist"""


from setuptools import setup, find_packages

setup(name='projmap',
      version='0.81',
      description='High level wrapper of matplotlibs mapping package',
      author='Bror Jonsson',
      author_email='brorfred@gmail.com',
      url='https://github.com/brorfred/projmap',
      requires=["numpy(>=1.5)", "matplotlib(>=2.0)", "six",
                "cartopy(>=0.16)"],
      packages=['projmap'],
      package_data={'projmap': ['data/*.txt', 'map_regions.cfg']},
     )
