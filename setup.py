from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'Readme.md')) as f:
    long_description = f.read()

setup(name='kron',
      version='1.0',
      description='Kron, the command line companion for Kronbute',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/healthcarecom/kron',
      author='Healthcare.com Inc.',
      packages=find_packages(),
      python_requires=">=3.7",
      install_requires=[
          'jsonpickle',
          'requests',
          'colorama',
          'click',
          'coloredlogs',
          'terminaltables'
      ],
      package_data={},
      entry_points={
          'console_scripts': ['kron = main:cli']
      }
)