.PHONY: redis up down test run

# Run the Python rate limiter test (Redis must be running)
test:
	python3 test_limiter.py

# Start Redis and run the test
run: 
	docker compose up -d
	@sleep 2
	$(MAKE) test
	docker compose down
