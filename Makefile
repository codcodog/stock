.PHONY: check
check:
	@yapf -d -r . || true

.PHONY: fix
fix:
	@yapf -i -r .

.PHONY: dep
dep:
	@source venv/bin/activate && pip freeze > requirements.txt
