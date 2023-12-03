import argparse
import ffmpeg
import whisper
import openai
import os
from halo import Halo


def parse_arguments():
    parser = argparse.ArgumentParser(description='Convert MP4 to Flashcards')
    parser.add_argument('-i', '--input', required=True,
                        help='Input MP4 file path')
    parser.add_argument('-o', '--output', required=True,
                        help='Output directory for flashcards CSV file')
    parser.add_argument('-d', '--duration', required=False,
                        help='Duration', default=60)
    parser.add_argument('-st', '--starttime', required=False,
                        help='Start time', default=0)
    parser.add_argument('-l', '--language', required=False,
                        help='Language', default="en")
    return parser.parse_args()


def mp3_to_text(mp3_file, language="en"):
    model = whisper.load_model("base")
    result = model.transcribe(mp3_file, language=language)
    return result["text"]


def mp4_to_mp3(mp4_file, mp3_file, start_time, duration):
    ffmpeg.input(mp4_file, ss=start_time, t=duration).output(
        mp3_file, format='mp3').run(overwrite_output=True, capture_stdout=True, capture_stderr=True)


def text_to_flashcards(text):
    prompt = "I want you to act as a anki flashcard creator. You are creating flashcards for students that are taking a course in a specific subject. You will be given a transcript of a lecture. I want you to create flashcards that are relevant to the course. I want you to respond with only CSV content without codeblock or any other text. Do not include a header row.\n\nHere is the transcript:\n\n" + text

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # or the specific model you want to use
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    try:
        flashcards_csv = response['choices'][0]['message']['content']
        return flashcards_csv
    except Exception as e:
        print("Error in generating flashcards:", e)
        return ""


if not os.getenv("OPENAI_API_KEY"):
    raise Exception("OPENAI_API_KEY environment variable is not set")

args = parse_arguments()

MP3_TMP_PATH = "/tmp/speech.mp3"

with Halo(text='Converting mp4 to mp3', spinner='dots'):
    mp4_to_mp3(args.input, MP3_TMP_PATH, args.starttime, args.duration)

with Halo(text='Converting mp3 to text', spinner='dots'):
    speech_text = mp3_to_text(MP3_TMP_PATH, args.language)

with Halo(text='Generating flashcards', spinner='dots'):
    flashcards_csv = text_to_flashcards(speech_text)

with open(args.output, 'w') as file:
    file.write(flashcards_csv)

print(f"Flashcards CSV file generated at {args.output}")
