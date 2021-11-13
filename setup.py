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
    