1. Create a fresh pip virtual environment with

	python3 -m venv venv

2. Activate environment with

	. ./venv/bin/activate

3. Install required packages

	pip install -r pip_requirements.txt

4. Wheel needs to be installed. For whatever reason it wont include in the requirements.

	pip install wheel

5. build the local tendersWA package and install it.

	cd src
	python3 setup.py bdist_wheel
	pip install dist/TendersWA-0.1.0-py3-none-any.whl

Its likely some package will fail to install due to differing OS and environments. For instance many nvidia packages are linux distro specific and fail on mac os. Consult

https://stackoverflow.com/questions/22250483/stop-pip-from-failing-on-single-package-when-installing-with-requirements-txt

for workarounds. It also okay to remove failing packages.

6. notebooks and scripts should now run. Notebooks are built with jupyter lab. Try

	jupyter lab

in the root directory to start an instance.
