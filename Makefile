# Create translations files or update existing
update_translations:
	@pylupdate6 src -ts src/locales/ru/app_ru.ts;
	@pylupdate6 src -ts src/locales/en/app_en.ts;

# Create compiled translations files to use at application runtime
compile_translations:
	@lrelease src/locales/ru/app_ru.ts
	@lrelease src/locales/en/app_en.ts


