import re
from setuptools import setup


requirements = []
with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

version = ""
with open('gitbot/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError("version does not appear to be set.")

readme = ""
with open("README.md", "r") as f:
    readme = f.read()

extras_require = {
    "proxy-support": ["aiohttp_remotes"]
}

packages = [
    "sapid",
    "sapid.types"
]

setup(
    name="gitty",
    version=version,
    author="justanotherbyte",
    description="A robust asynchronous framework for building scalable GitHub Applications.",
    long_description=readme,
    packages=packages,
    license="MIT",
    extras_require=extras_require,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=requirements,
     classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed',
      ]
)