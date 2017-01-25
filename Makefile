PYTHON=python3
PID=app.pid

run:
	$(PYTHON) app.py
start:
	$(PYTHON) app.py > /dev/null 2>&1 & echo $$! > $(PID)
kill:
	kill $$(cat $(PID))
test:
	$(PYTHON) simple_slack_bot/test_simple_slack_bot.py
