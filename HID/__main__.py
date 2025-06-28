from .components.tts import TTS
from .components.stt import STT
from .keybinder import KeyBinder


def main():
    tts = TTS()
    stt = STT()
    binder = KeyBinder()

    def speak_test():
        text = "This is a test of the TTS system."
        samples = tts.list_voice_samples()
        sample = samples[0] if samples else None
        tts.synthesize(text, voice=sample, play=True, save=False)
        print('Spoke (not saved)')

    def speak_and_save():
        text = "This is a saved TTS test."
        samples = tts.list_voice_samples()
        sample = samples[0] if samples else None
        out = tts.synthesize(text, voice=sample, play=True, save=True)
        print(f'Spoke and saved to {out}')

    def stt_test():
        print("Speak into the microphone. Press Ctrl+C to stop recording.")
        text = stt.record_and_transcribe()
        print(f"You said: {text}")

    binder.register('f8', speak_test)
    binder.register('ctrl+f8', speak_and_save)
    binder.register('f1', stt_test)
    binder.run()

if __name__ == '__main__':
    main() 