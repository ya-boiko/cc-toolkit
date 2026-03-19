PLUGINS = tododo jira-tasks hubstaff git-commands

.PHONY: help install uninstall update install-% uninstall-% update-%

help:
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install all plugins"
	@echo "  uninstall        Remove all plugins"
	@echo "  update           Update all plugins (git pull + submodules)"
	@echo "  install-<name>   Install a specific plugin (e.g. make install-hubstaff)"
	@echo "  uninstall-<name> Remove a specific plugin"
	@echo "  update-<name>    Update a specific plugin"
	@echo ""
	@echo "Plugins: $(PLUGINS)"

install:
	@for p in $(PLUGINS); do echo "==> $$p" && $$p/install.sh; done

uninstall:
	@for p in $(PLUGINS); do echo "==> $$p" && $$p/uninstall.sh; done

update:
	@git submodule update --remote
	@for p in $(PLUGINS); do echo "==> $$p" && $$p/update.sh; done

install-%:
	@$*/install.sh

uninstall-%:
	@$*/uninstall.sh

update-%:
	@$*/update.sh
