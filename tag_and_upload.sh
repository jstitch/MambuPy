#!/bin/bash

mambupy_version=`python -c "import MambuPy; print(MambuPy.__version__)"`
git tag v$mambupy_version
git push gitlab v$mambupy_version
git push github v$mambupy_version
git push bitbucket v$mambupy_version

python setup.py bdist_wheel bdist_egg sdist
twine upload dist/MambuPy-$mambupy_version*
