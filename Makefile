SHELL := /bin/sh
BOOTSTRAP_PYTHON ?= python3
PYTHON ?= .venv/bin/python
OUTPUT ?= /tmp/order-fulfillment-central-domain

.PHONY: install test verify example clean-example
install:
	@$(BOOTSTRAP_PYTHON) -c 'import sys; required=(3,11); sys.exit(0 if sys.version_info >= required else "需要 Python 3.11+，当前为 %s.%s；请通过 BOOTSTRAP_PYTHON 指定新版本" % sys.version_info[:2])'
	@$(BOOTSTRAP_PYTHON) -m venv .venv
	@.venv/bin/python -m pip install -r requirements.txt
	@.venv/bin/python -m pip install -e .

test:
	@test -x "$(PYTHON)" || { echo '缺少 .venv，请先运行 make install' >&2; exit 1; }
	@$(PYTHON) -m unittest discover -s tests -v

verify: test
	@$(PYTHON) -m central_repo_scaffold validate --config examples/domain.yaml
	@$(PYTHON) scripts/verify-scaffold.py
	@echo '脚手架校验通过'

example:
	@test -x "$(PYTHON)" || { echo '缺少 .venv，请先运行 make install' >&2; exit 1; }
	@$(PYTHON) -m central_repo_scaffold create --config examples/domain.yaml --output "$(OUTPUT)"

clean-example:
	@test -n "$(OUTPUT)" && test "$(OUTPUT)" != "/"
	@rm -rf "$(OUTPUT)"
