#!/bin/bash
# shellcheck source=/dev/null
/usr/bin/python3 -m venv --copies "$1"
source "$1"/bin/activate
#pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
python -m pip install --upgrade pip
python -m pip install -r "$2" --use-pep517
python -m pip install wheel
# temporary for custom aiVLE Gym and Grader
python -m pip install "$3"/aivle_grader --use-pep517
python -m pip install "$3"/aivle_gym --use-pep517
deactivate