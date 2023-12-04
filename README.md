# mp4toflashcard

This script converts an MP4 file into a set of flashcards in CSV format. It extracts audio from the MP4 file, transcribes it using the Whisper model, and then uses OpenAI's GPT-4 to generate flashcards from the transcribed text.

#### Example

Using this video: https://www.youtube.com/watch?v=Tn6-PIqc4UM (React in 100 Seconds by Fireship) generates this output:

| Question                                                    | Answer                                            |
| :---------------------------------------------------------- | :------------------------------------------------ |
| What is React?                                              | A JavaScript library for building user interfaces |
| Who developed React?                                        | Facebook                                          |
| When was React released?                                    | 2013                                              |
| What are React components?                                  | Logical, reusable parts of the UI                 |
| What syntax does React use to combine JavaScript with HTML? | JSX                                               |
| How do you pass data into a React component?                | Using a props argument                            |

#### **Prerequisites**

- Python 3
- FFMPEG
- OPENAI API Key

#### **Installation**

1. **Install required Python packages:** Run `pip install -r requirements.txt` in the script's directory.

#### **Setting up Environment Variables**

- Ensure `OPENAI_API_KEY` is set in your environment variables. This key is required for using OpenAI's GPT-4 model.

#### **Usage**

1. **Command Line Arguments:**

   - `-i` or `--input`: Path to mp4 / path to txt file / url to txt file
   - `-o` or `--output`: Directory path for the output CSV file containing flashcards.
   - `-d` or `--duration`: Duration of the MP4 file to process (in seconds). Default is 60 seconds.
   - `-st` or `--starttime`: Start time for processing the MP4 file (in seconds). Default is 0.
   - `-l` or `--language`: Language for transcription. Default is English (`en`).

2. **Running the Script:**
   - Use the command line to navigate to the script's directory.
   - Execute the script with the required arguments. For example:
     ```bash
     python ./main.py -i path/to/video.mp4 -o path/to/output.csv
     ```
