#!/bin/bash

source ~/.virtualenvs/mambupy/bin/activate

mambupy_version=`python -c "import MambuPy; print(MambuPy.__version__)"`
git tag v$mambupy_version
git push origin v$mambupy_version
git push watson v$mambupy_version
git push github v$mambupy_version
git push bitbucket v$mambupy_version

python setup.py bdist_wheel bdist_egg sdist
twine upload dist/MambuPy-$mambupy_version*

deactivate
