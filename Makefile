.PHONY: install-dev run check format clean run-all-skip-seq run-all-all-par open-user run-cli

# Install dependencies
install:
	poetry install

# Install development dependencies
install-dev:
	poetry install --with dev

# Run the application
run:
	poetry run python kizzy/main.py

# Save cookies
save:
	poetry run python kizzy/save_cookies.py

# Check code style
check:
	poetry run ruff check kizzy/

# Format code
format:
	poetry run ruff format kizzy/

# Clean up
clean:
	rm -rf .ruff_cache

# Non-interactive convenience targets

# Run on all users, skip pools already bet on, sequential execution
run-all-skip-seq:
	poetry run python kizzy/main.py -a 2 -b 1 -e 1

# Run on all users, skip pools already bet on, parallel execution
run-all-skip-par:
	poetry run python kizzy/main.py -a 2 -b 1 -e 2

# Open a specific user with cookies only; usage: make open-user INDEX=2
open-user:
	@if [ -z "$(INDEX)" ]; then echo "Please provide INDEX, e.g. make open-user INDEX=2"; exit 1; fi
	poetry run python kizzy/main.py -a 1 -u $(INDEX)

# Pass arguments directly to the Python entrypoint; usage: make run-cli ARGS='-a 2 -b 1 -e 2'
run-cli:
	poetry run python kizzy/main.py $(ARGS)