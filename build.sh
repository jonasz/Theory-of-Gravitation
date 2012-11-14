#! /bin/bash

pushd ./Box2D-2.0.2b2
python setup.py build || exit 1
popd
