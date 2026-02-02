# Whisper GUI

Transcribe your audio locally with [Whisper](https://github.com/openai/whisper) multimodal speech-to-text model by OpenAI

## Installation 

### MacOS

Download DMG-image from [releases](https://github.com/loginchik/whisper-app/releases/latest) and launch it. You can use the application from image or copy it to `Applications` folder for a quick access. It's up to you.

When you first open dmg-image or application, you are most probable to get **untrusted developer warning**. It basically means that, as far as the project is non-commercial, I do not have neither funding, nor wish to register in Apple. To bypass the warning and use the application:
- open system settings
- navigate to privacy and security settings
- allow the application to run (enter password, if prompted)

To uninstall the application, move the .app file and `~/.cache/whisper` to trash. 

### Building from source 

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
2. Clone repository

```bash
git clone https://github.com/loginchik/whisper-app.git
cd whisper-app
```

3. Configure virtual environment 

```bash 
uv sync --all-groups
```

4. Build app

```bash 
make build_english 
```

## Usage

Internet connection is required only to download a model on its first usage, while all other processes run locally on your machine


### Launch application 

<img src="assets/images/main%20screen.png" height="400" alt="Main screen" />

You need to choose a model and add audio files to process

### Choose model

`tiny`, `base` or `small` are powerful enough to handle most tasks and can be run on almost any PC having at least 4GB of RAM. For more complicated cases you can try larger models, but remember about resource limitations of your machine. You can always check `About models` or [Whisper](https://github.com/openai/whisper/tree/v20250625?tab=readme-ov-file#available-models-and-languages) to study model's requirements. 


Previously used models, if you had not manually deleted them from cache directory, are almost ready to use. Models that need to be downloaded first are marked with red icon. 

<img src="assets/images/model selection.png" height="100" />

— here `tiny` and `base` are available locally; `small`, `medium` and `large` will be downloaded first. 

### Add audio files and configure task 

For each audio file, it is recommended to pass language for Whisper to start with relative context. Presets are predefined task settings (created by ChatGPT) that can help you handle popular tasks. If you are not sure which preset to choose, use `universal`.  

### Start transcription and wait it to complete

While task is running, most application features freeze. 

<img src="assets/images/task window.png" height="350" />

Transcribed files are exported in `Downloads` folder and can be located via double click.

## Contributing

This is a non-commercial project for personal usage, contributions are welcome. For major changes, please open an issue first to discuss what you would like to change. 

## Troubleshooting

If application crashes a few times in a row, consider it a bug. If you want the bug to be fixed, open an issue and make sure to include step-by-step description of your actions and log files from `~/.cache/whisper/logging` directory.

## License 

[GPL v3](LICENSE)
