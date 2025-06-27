import sounddevice as sd
import soundfile as sf
import numpy as np
import keyboard
import pyperclip
from faster_whisper import WhisperModel, BatchedInferencePipeline
import time

PTT_KEY = 'f23'
RECORD_KEY = 'ctrl+f23'
RECORD_FILENAME = 'tmp/recording.wav'
SAMPLE_RATE = 16000
CHANNELS = 1


model = WhisperModel("base", device="cuda")
model = BatchedInferencePipeline(model=model)


def wait_for_key_and_record(key, filename):
    print(f"Hold {key.upper()} to record. Release to stop and transcribe.")
    keyboard.wait(key)
    print("Recording...")
    frames = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS) as stream:
        while keyboard.is_pressed(key):
            data, _ = stream.read(1024)
            frames.append(data)
    print("Recording stopped.")
    if frames:
        audio = np.concatenate(frames, axis=0)
        sf.write(filename, audio, SAMPLE_RATE)
    else:
        print("No audio recorded.")


def toggle_record_and_save(key, filename):
    print(f"Press {key.upper()} to start recording. Press again to stop and transcribe.")
    recording = False
    frames = []
    while True:
        keyboard.wait(key)
        # Debounce: wait for key release
        while keyboard.is_pressed(key):
            sd.sleep(50)
        if not recording:
            print("Recording...")
            frames = []
            recording = True
            with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS) as stream:
                while recording:
                    if keyboard.is_pressed(key):
                        # Debounce: wait for key release
                        while keyboard.is_pressed(key):
                            sd.sleep(50)
                        print("Recording stopped.")
                        recording = False
                        break
                    data, _ = stream.read(1024)
                    frames.append(data)
            break  # Exit after one record-toggle cycle
    if frames:
        audio = np.concatenate(frames, axis=0)
        sf.write(filename, audio, SAMPLE_RATE)
    else:
        print("No audio recorded.")


def transcribe_and_copy(filename):
    segments, info = model.transcribe(filename)
    text = " ".join([segment.text for segment in segments]).strip() + " "
    print(text)
    pyperclip.copy(text)
    print("Transcription copied to clipboard!\n")
    keyboard.press_and_release("ctrl+v")


def handle_ptt():
    wait_for_key_and_record(PTT_KEY, RECORD_FILENAME)
    transcribe_and_copy(RECORD_FILENAME)


def handle_record():
    toggle_record_and_save(RECORD_KEY, RECORD_FILENAME)
    transcribe_and_copy(RECORD_FILENAME)


def main():
    print(f"Press and hold {PTT_KEY.upper()} for Push-To-Talk, or CTRL+{PTT_KEY.upper()} to toggle Record mode.")
    last_ptt = False
    last_record = False
    while True:
        ptt_now = keyboard.is_pressed(PTT_KEY) and not keyboard.is_pressed('ctrl')
        record_now = keyboard.is_pressed(PTT_KEY) and keyboard.is_pressed('ctrl')
        # PTT: F23 pressed (without Ctrl)
        if ptt_now and not last_ptt:
            handle_ptt()
        # RECORD: Ctrl+F23 pressed
        if record_now and not last_record:
            handle_record()
        last_ptt = ptt_now
        last_record = record_now
        time.sleep(0.05)


if __name__ == "__main__":
    main()