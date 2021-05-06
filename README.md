corankco
===============

This package implements methods for rank aggregation of incomplete rankings with ties 

Installation
------------

Install from PyPI:

``pip3 install --user corankco``


Example usage
-------------

# profile-readme

[![Build Status](https://travis-ci.org/Robert-96/profile-readme.svg?branch=master)](https://travis-ci.org/Robert-96/profile-readme)
[![Documentation Status](https://readthedocs.org/projects/profile-readme/badge/?version=latest)](https://profile-readme.readthedocs.io/en/latest/?badge=latest)

A CLI tool for generating a GitHub profile README using the [Jinja2](https://jinja.palletsprojects.com/) template engine.

It lets you use all features provide by [Jinja2](https://jinja.palletsprojects.com/) to help you customize your GitHub profile README and it provides data from the GitHub API to your template.

Read the documentation on https://profile-readme.rtfd.io/.

## Installation

Use the following command to install `profile-readme`:

```
$ python3 -m pip install profile-readme
```

### Living on the edge

If you want to work with the latest code before it’s released, install or update the code from the `master` branch:

```
$ python3 -m pip install -U git+https://github.com/Robert-96/profile-readme.git
```

## Quickstart

Use the `init` command to generate a new project with an example template:

```
$ profile-readme init
```

Use the `render` command to update your `README.md` file:

```
$ profile-readme render
```

## Advanced Usage

### Using Custom Build Scripts

The command line shortcut is convenient, but sometimes your project needs something different than the defaults. To change them, you can use a build script.

A minimal build script looks something like this:

```python
from profile_readme import get_github_context, ProfileGenerator


context = {}

# If you don't need the GitHub data you can remove the next line
context.update(**get_github_context('octocat'))


if __name__ == "__main__":
    ProfileGenerator.render(
        template_path="README-TEMPLATE.md",
        output_path="README.md",
        context=context
    )

```

Finally, just save the script as `build.py` (or something similar) and run it with your Python interpreter.

```
$ python build.py
```

> Note: Don't forgot to also update `.github/workflows/readme.yml`.
> Replace `python3 -m profile_readme render` with `python3 build.py`.

### Loading Data

The simplest way to supply data to the template is to pass `ProfileGenerator.render` a mapping from variable names to their values (a “context”) as the `context` keyword argument.

```python
from profile_readme import get_github_context, ProfileGenerator


context = {
    greeting='Hello, world!'
}

# If you don't need the GitHub data you can remove the next line
context.update(**get_github_context('octocat'))


if __name__ == "__main__":
    ProfileGenerator.render(
        template_path="README-TEMPLATE.md",
        output_path="README.md",
        context=context
    )

```

Anything added to this dictionary will be available in the template:

```md
# Title

{{ greeting }}
```

### Filters

Variables can be modified by [filters](https://jinja.palletsprojects.com/en/2.11.x/templates/#filters). All the standard Jinja2 filters are supported (you can found the full list [here](https://jinja.palletsprojects.com/en/2.11.x/templates/#builtin-filters)).  To add your own filters, simply pass filters as an argument to `ProfileGenerator`.

```python
from profile_readme import get_github_context, ProfileGenerator


context = get_github_context('octocat')
filters = {
    'hello': lambda x: 'Hello, {}!',
}


if __name__ == "__main__":
    ProfileGenerator.render(
        template_path="README-TEMPLATE.md",
        output_path="README.md",
        context=context,
        filters=filters
    )

```

Then you can use them in your template as you would expect:

```md
{{ 'World'|hello }}
```

## License

This project is licensed under the [MIT License](LICENSE).