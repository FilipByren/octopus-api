.PHONY: test
test:
	docker-compose -f docker-compose.yaml run --rm test

# TAG=0.1.1 make release
.PHONY: release
release:
	poetry version $(TAG) && \
	poetry build && \
	git tag $(TAG) && \
	poetry publish