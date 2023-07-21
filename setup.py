from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='corankco',
      version='7.0.1',
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
      install_requires=['numpy~=1.24.4',
                        'python-igraph',
                        'pulp~=2.7',
                        'bioconsertinc>=1.0.2',
                        'setuptools~=68.0.0',
                        ]
      )
