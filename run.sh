#! /bin/bash
export PYTHONPATH=$PYTHONPATH:"`pwd`/`find .  -name _Box2D.so | xargs dirname`"
export PYTHONPATH=$PYTHONPATH:"`pwd`/Box2D-2.0.2b2/"

python game.py
