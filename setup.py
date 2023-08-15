from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='corankco',
      version='7.2.0',
      description='Kemeny-Young method for rank aggregation of incomplete rankings with ties',
      long_description_content_type='text/markdown',
      long_description=readme(),
      url='https://github.com/pierreandrieu/corankco',
      author='Pierre Andrieu',
      author_email='pierre.andrieu@lilo.org',
      license='GPLv2',
      packages=find_packages(include=['corankco', 'corankco.*']),
      python_requires='>=3.8',
      zip_safe=False,
      install_requires=['numpy>=1.24',
                        'python-igraph',
                        'pulp>=2.7',
                        'numba>=0.57.1'
                        'setuptools>=68.0.0',
                        ]
      )
