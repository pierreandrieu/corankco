from setuptools import setup, find_packages
from distutils.extension import Extension

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='corankcolight',
      version='1.0.1',
      description='Kemeny-Youg method for rank aggregation of incomplete rankings with ties',
      long_description=readme(),
      url='https://github.com/pierreandrieu/corankcolight',
      author='Pierre Andrieu',
      author_email='pierre.andrieu@lilo.org',
      license='MIT',
      packages=find_packages(include=['corankcolight', 'corankcolight.*']),
      ext_modules=[Extension("bioconsertcimpl", ["bioconsertcimpl.c"])],
      python_requires='>=3',
      zip_safe=False,
      install_requires=['numpy==1.18.5'],
      )

