.PHONY: hard-wipe
hard-wipe:
	docker system prune -a

.PHONY: test
test:
	docker-compose -f docker-compose.yaml run --rm test

# TAG=x.y.z make release
.PHONY: release
release:
	poetry version $(TAG) && \
	poetry build && \
	git tag $(TAG) && \
	poetry publish
