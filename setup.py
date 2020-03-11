# coding=utf-8
from covid_micro import __version__ as version
from setuptools import setup

setup(name='covid_micro',
      version=version,
      description='Small microservice for plotting current corona virus spread',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          "Operating System :: OS Independent",
      ],

      url='https://github.com/gluap/covid_micro',
      author='Paul Görgen',
      author_email='pypi@pgoergen.de',
      license='MIT',

      packages=['covid_micro'],

      install_requires=["flask", "numpy", "matplotlib", "scipy", "requests"],

      zip_safe=False,
      include_package_data=False,

      tests_require=[
          'tox', 'pytest'
      ],

      entry_points={'console_scripts': ['app=covid_micro.app:main']},
      long_description=open('readme.rst', 'r').read()
      )
