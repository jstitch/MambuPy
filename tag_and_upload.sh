#!/bin/bash

echo "getting version"
mambupy_version=`python -c "import MambuPy; print(MambuPy.__version__)"`

echo "tagging"
git tag v$mambupy_version

echo "pushing tags"
git push gitlab v$mambupy_version
git push github v$mambupy_version
git push bitbucket v$mambupy_version

echo "building wheel, egg and sdist"
python setup.py bdist_wheel bdist_egg sdist

echo "uploading to pypi"
twine upload dist/MambuPy-$mambupy_version*
