PYTHON=python3
PID=app.pid

run:
	$(PYTHON) app.py

start:
	$(PYTHON) app.py > /dev/null 2>&1 & echo $$! > $(PID)

magic:
	black simple_slack_bot tests && isort . && flake8 simple_slack_bot --show-source && mypy simple_slack_bot && bandit simple_slack_bot && safety check && dodgy

test: magic
	pytest

package:
	python3 setup.py sdist bdist_wheel

upload-test-pypi:
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*

upload-pypi:
	python3 -m twine upload dist/*

example:
	python3 example_component.py

kill:
	kill $$(cat $(PID))
