from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(name='kron',
      version='1.4',
      description='Kron, the command line companion for Kronbute',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/healthcarecom/kron',
      author='Healthcare.com Inc.',
      py_modules=['main', 'job', 'kronbute', 'util', 'info', 'runs'],
      python_requires=">=3.6.5",
      install_requires=[
          'jsonpickle',
          'requests',
          'colorama',
          'click',
          'coloredlogs',
          'terminaltables',
          'pyfiglet',
          'pyyaml'
      ],
      package_data={},
      entry_points={
          'console_scripts': ['kron = main:cli']
      }
)
