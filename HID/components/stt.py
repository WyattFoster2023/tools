from dataclasses import dataclass
from typing import Optional, List
import sounddevice as sd
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel, BatchedInferencePipeline
import os

@dataclass
class STTConfig:
    model_name: str = 'base'
    device: str = 'cuda'
    sample_rate: int = 16000
    channels: int = 1
    temp_dir: str = 'HID/transcribe/tmp'
    default_record_filename: str = 'recording.wav'

class STT:
    def __init__(self, config: STTConfig = STTConfig()):
        self.config = config
        self.model = WhisperModel(config.model_name, device=config.device)
        self.pipeline = BatchedInferencePipeline(model=self.model)
        os.makedirs(self.config.temp_dir, exist_ok=True)

    def record_audio(self, duration: Optional[float] = None, filename: Optional[str] = None) -> str:
        """Record audio from the microphone. If duration is None, records until interrupted. Returns the file path."""
        filename = filename or self.config.default_record_filename
        file_path = os.path.join(self.config.temp_dir, filename)
        print(f"Recording audio{' for ' + str(duration) + ' seconds' if duration else ''}...")
        frames = []
        with sd.InputStream(samplerate=self.config.sample_rate, channels=self.config.channels) as stream:
            if duration:
                total_frames = int(self.config.sample_rate * duration)
                while len(frames) * 1024 < total_frames:
                    data, _ = stream.read(1024)
                    frames.append(data)
            else:
                try:
                    while True:
                        data, _ = stream.read(1024)
                        frames.append(data)
                except KeyboardInterrupt:
                    print("Recording stopped by user.")
        if frames:
            audio = np.concatenate(frames, axis=0)
            sf.write(file_path, audio, self.config.sample_rate)
            print(f"Audio saved to {file_path}")
        else:
            print("No audio recorded.")
        return file_path

    def transcribe(self, file_path: str) -> str:
        """Transcribe the given audio file and return the text."""
        segments, info = self.pipeline.transcribe(file_path)
        text = " ".join([segment.text for segment in segments]).strip()
        print(f"Transcription: {text}")
        return text

    def record_and_transcribe(self, duration: Optional[float] = None, filename: Optional[str] = None) -> str:
        """Record audio and return the transcription."""
        file_path = self.record_audio(duration=duration, filename=filename)
        return self.transcribe(file_path)

if __name__ == '__main__':
    stt = STT()
    print("Speak into the microphone. Press Ctrl+C to stop recording.")
    text = stt.record_and_transcribe()
    print(f"You said: {text}") 