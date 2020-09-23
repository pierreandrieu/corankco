from setuptools import setup, find_packages
from distutils.extension import Extension


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='corankco',
      version='0.0.5',
      description='Kemeny-Young method for rank aggregation of incomplete rankings with ties',
      long_description=readme(),
      url='https://github.com/pierreandrieu/corankco',
      author='Pierre Andrieu',
      author_email='pierre.andrieu@lilo.org',
      license='MIT',
      packages=find_packages(include=['corankco', 'corankco.*']),
      ext_modules=[Extension("bioconsertcimpl", ["bioconsertcimpl.c"])],
      python_requires='>=3',
      zip_safe=False,
      install_requires=['numpy',
                        'python-igraph',
                        'pulp==2.3',
                        'bioconsertinc==0.0.2',
                        ]
      )
