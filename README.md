# Meridian Assistant

Meridian Assistant is a versatile tool designed for transcribing audio files and summarizing texts for Dungeons & Dragons sessions. It can operate in both local and remote modes (if given a valid OpenAI API key), and it offers a graphical user interface (GUI) for ease of use.

## Features

- **Transcription**: Convert audio files into text.
- **Summarization**: Summarize the content of text files.
- **Local and Remote Transcription**: Support local NVIDIA GPU-based computation or via OpenAI
- **Graphical User Interface**: Launch a GUI for easier interaction.

## Usage

To launch the GUI (default usage mode), just launch the following script

./meridian_assistant.py 

For windows users, start the following batch file to invoke the program:

.\meridian_assistant.bat

## Installation

Before you start using Meridian Assistant, ensure you have Python installed on your system. The usage of a venv using Python version 3.10 is reccomended to avoid causing issues with your systems default python installation and to allow for the needed packages to function properly. You can install the required dependencies by running:

pip install -r requirements.txt

It's also required to have ollama and whisperx installed - please consult those project's instructions for details

Ollama: [GitHub](https://github.com/ollama/ollama)
Whisperx: [PyPi](https://pypi.org/project/whisperx/) 

You'll also likely need a HuggingFace account and an API key to access whisper modeldata, which will be automatically loaded on first use. Please read more here: [HuggingFace](https://huggingface.co/)

Development has been done with expectation that you have an NVIDIA GPU and the latest CUDA drivers installed. The tasks in this project are technically possible to be done on regular CPUs but the speed will be awful. That said, it's also possible to use OpenAI APIs and for debugging is an acceptable way to work without incurring too much cost. If you've gotten through all of this, congratulations! You're ready to start playing with Meridian Assistant :)

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


If neither `--local` nor `--remote` is specified for transcription, the program will assume local transcription is desired to save API costs. By default the GUI will open, and the commandline is mostly deprecated and may not work properly as of time of this latest README update.

## Contributing

Contributions to Meridian Assistant are welcome. Please ensure you follow the contributing guidelines.

## License

Meridian Assistant is released under the MIT License. See the LICENSE file for more details.


