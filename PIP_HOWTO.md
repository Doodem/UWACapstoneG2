1. Create a fresh pip virtual environment with

	python3 -m venv venv

2. Activate environment with

	. ./venv/bin/activate

3. Install required packages

	pip install -r pip_requirements.txt

4. build the local tendersWA package and install it.

	cd src
	python3 setup.py bdist_wheel
	pip install dist/TendersWA-0.1.0-py3-none-any.whl

5. notebooks and scripts should now run. Notebooks are built with jupyter lab. Try

	jupyter lab

in the root directory to start an instance.
