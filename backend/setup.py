#!/usr/bin/env python
from setuptools import find_packages,setup

setup(name='heart-risk-predictor',
      version='0.0.1',
      description='Python Distribution Utilities',
      author='Ritu Arora',
      author_email='arora0824@gmail.com',
      packages=['pandas', 'numpy', 'seaborn', 'flask', 'flask_restful', 'gunicorn', 'scikit-learn', 'xgboost', 'category-encoders', 'pydantic', 'pytest' ],
     )