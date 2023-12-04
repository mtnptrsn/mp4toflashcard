import argparse
import shlex
import os
import ffmpeg
import whisper
import openai
from halo import Halo
import requests

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT_DIR, "prompt.txt"), "r") as file:
    PROMPT = file.read()

MP3_TMP_PATH = "/tmp/transcript.mp3"
TXT_TMP_PATH = "/tmp/transcript.txt"


def is_url(s):
    return s.startswith("http://") or s.startswith("https://")


def download_file(url, content_type):
    response = requests.get(url)
    response_content_type = response.headers.get("Content-Type")

    if response_content_type is None:
        raise ValueError("The response does not contain a Content-Type header.")

    if response_content_type.split(";")[0].strip() != content_type:
        raise ValueError(
            f"Expected Content-Type '{content_type}', but got '{response_content_type}' instead."
        )

    return response.content


def strip_quotes(arg_value):
    if arg_value:
        return shlex.split(arg_value)[0]
    return arg_value


def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert MP4/txt to Flashcards")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        type=strip_quotes,
        help="Input MP4/txt file path/url to txt file",
    )
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        type=strip_quotes,
        help="Output directory for flashcards CSV file",
    )
    parser.add_argument(
        "-d",
        "--duration",
        required=False,
        type=strip_quotes,
        help="Duration",
        default=60,
    )
    parser.add_argument(
        "-st",
        "--starttime",
        required=False,
        type=strip_quotes,
        help="Start time",
        default=0,
    )
    parser.add_argument(
        "-l",
        "--language",
        required=False,
        type=strip_quotes,
        help="Language",
        default="en",
    )
    return parser.parse_args()


def mp3_to_text(mp3_file, language="en"):
    model = whisper.load_model("base")
    result = model.transcribe(mp3_file, language=language)
    return result["text"]


def mp4_to_mp3(mp4_file, mp3_file, start_time, duration):
    ffmpeg.input(mp4_file, ss=start_time, t=duration).output(
        mp3_file, format="mp3"
    ).run(overwrite_output=True, capture_stdout=True, capture_stderr=True)


@Halo(text="Generating flashcards with ChatGPT...", spinner="dots")
def text_to_flashcards(text):
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # or the specific model you want to use
        messages=[{"role": "user", "content": f"{PROMPT}\n\n{text}"}],
    )

    try:
        flashcards_csv = response["choices"][0]["message"]["content"]
        return flashcards_csv
    except Exception as e:
        print("Error in generating flashcards:", e)
        return ""


if not os.getenv("OPENAI_API_KEY"):
    raise Exception("OPENAI_API_KEY environment variable is not set")


@Halo(text="Getting transcript...", spinner="dots")
def get_transcript(input, starttime, duration, language):
    if input.endswith(".mp4"):
        mp4_to_mp3(input, MP3_TMP_PATH, starttime, duration)
        return mp3_to_text(MP3_TMP_PATH, language)

    if input.endswith(".txt"):
        with open(input, "r") as file:
            return file.read()

    if is_url(input):
        return download_file(input, "text/plain")

    raise Exception("Unsupported file format. Please provide an MP4 or TXT file.")


args = parse_arguments()

transcript = get_transcript(
    input=args.input,
    starttime=args.starttime,
    duration=args.duration,
    language=args.language,
)

flashcards_csv = text_to_flashcards(transcript)

with open(args.output, "w") as file:
    file.write(flashcards_csv)

print(f"Flashcards CSV file generated at {args.output}")
