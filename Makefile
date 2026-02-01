spec_file="build.spec"

locales_dir="src/locales"
build_qm_filepath="${locales_dir}/app.qm"
en_qm_filepath="${locales_dir}/en/app_en.qm"
ru_qm_filepath="${locales_dir}/ru/app_ru.qm"

all: setup_dev update_translations

# Create translations files or update existing
update_translations:
	@pylupdate6 src -ts ${locales_dir}/ru/app_ru.ts;
	@pylupdate6 src -ts ${locales_dir}/en/app_en.ts;

# Create compiled translations files to use at application runtime
compile_translations:
	@lrelease ${locales_dir}/ru/app_ru.ts
	@lrelease ${locales_dir}/en/app_en.ts

# Creates/updates virtual environment and sets up locales
setup_dev:
	uv sync --all-groups;
	$(MAKE) update_translations
	$(MAKE) compile_translations
	cp $en_qm_filepath $build_qm_filepath

# Build for Russian language
build_russian: compile_translations
	@cp $ru_qm_filepath $build_qm_filepath;
	@pyinstaller --noconfirm $spec_file;
	@echo "Done";

# Build for English language
build_english: compile_translations
	@cp "src/locales/en/app_en.qm" $build_qm_filepath;
	@pyinstaller --noconfirm $spec_file;
	@echo "Done";