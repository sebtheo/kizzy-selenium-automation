.PHONY: install-dev run check format clean

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