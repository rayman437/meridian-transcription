# Meridian Assistant

Meridian Assistant is a versatile tool designed for transcribing audio files and summarizing texts. It can operate in both local and remote modes, and it offers a graphical user interface (GUI) for ease of use.

## Features

- **Transcription**: Convert audio files into text.
- **Summarization**: Summarize the content of text files.
- **Local and Remote Transcription**: Choose between local or remote transcription services.
- **Graphical User Interface**: Launch a GUI for easier interaction.

## Requirements

Before you start using Meridian Assistant, ensure you have Python installed on your system. Additionally, you need to install the required dependencies by running:

pip install -r requirements.txt


## Usage

To use Meridian Assistant, you can run it from the command line with various options:

- **Transcribe an Audio File**: Provide the path to the audio file you wish to transcribe.
python meridian_assistant.py --transcription_audio <path_to_audio_file>

- **Use Local Transcription Service**: Add `--local` to use the local transcription service.
python meridian_assistant.py --transcription_audio <path_to_audio_file> --local

- **Use Remote Transcription Service**: Add `--remote` to use the remote transcription service.
python meridian_assistant.py --transcription_audio <path_to_audio_file> --remote

- **Summarize Text**: Provide the path to the text file you wish to summarize.
python meridian_assistant.py --summarize_text <path_to_text_file>

- **Specify Output File**: Use `--output_file` to specify the path to the output file.
python meridian_assistant.py --transcription_audio <path_to_audio_file> --output_file <path_to_output_file>


If neither `--local` nor `--remote` is specified for transcription, the program will prompt you to choose the transcription service interactively.

## Contributing

Contributions to Meridian Assistant are welcome. Please ensure you follow the contributing guidelines.

## License

Meridian Assistant is released under the MIT License. See the LICENSE file for more details.
python meridian_assistant.py --gui

