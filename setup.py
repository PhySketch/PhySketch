#!/usr/bin/env python

from setuptools import setup

setup(name='PhySketch',
      version='1.0',
      description='Physics Sketch Recognition Kit',
      author='Adriana Andrijauskas, Eric Grassl, Fernando de Moraes, Rafael Zulli',
      url='https://github.com/rzulli/PhySketch/',
      packages=['physketch','physketch.prediction'],
      install_requires=[
            'numpy>=1.14.2',
            'opencv-python>=3.2.0',
            'matplotlib>=2.2.2',
            'darkflow>=1.0.0',
            'tensorflow>=1.7.0',
            'lxml>=4.2.0']
     )