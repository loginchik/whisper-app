# Create translations files or update existing
update_translations:
	@pylupdate6 src -ts src/locales/ru/app_ru.ts;
	@pylupdate6 src -ts src/locales/en/app_en.ts;

# Create compiled translations files to use at application runtime
compile_translations:
	@lrelease src/locales/ru/app_ru.ts
	@lrelease src/locales/en/app_en.ts

# Creates/updates virtual environment and sets up locales
setup_dev:
	uv sync --all-groups;
	$(MAKE) update_translations
	$(MAKE) compile_translations
	cp "src/locales/en/app_en.qm" "src/locales/app.qm"
