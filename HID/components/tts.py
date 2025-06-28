from dataclasses import dataclass, field
from typing import Optional, List
import torchaudio as ta
from chatterbox.tts import ChatterboxTTS
import os
import sounddevice as sd
import numpy as np

@dataclass
class TTSConfig:
    device: str = 'cuda'
    default_voice_sample: Optional[str] = None  # Path to default sample
    output_path: str = 'chatterbox_out.wav'
    sample_dir: str = 'audio/'  # Directory with voice samples

class Voices:
    """Dynamically exposes voice samples as attributes (e.g., TINA, MALE1)."""
    def __init__(self, sample_dir: str):
        self._samples = {}
        if os.path.isdir(sample_dir):
            for f in os.listdir(sample_dir):
                if f.endswith('.wav'):
                    name = os.path.splitext(f)[0].upper().replace(' ', '_')
                    setattr(self, name, f)
                    self._samples[name] = f

    def list(self) -> List[str]:
        return list(self._samples.values())

    def __iter__(self):
        return iter(self._samples.values())

class TTS:
    def __init__(self, config: TTSConfig = TTSConfig()):
        self.config = config
        self.model = ChatterboxTTS.from_pretrained(device=config.device)
        self.voices = Voices(config.sample_dir)

    def list_voice_samples(self):
        return self.voices.list()

    def synthesize(self, text: str, voice: Optional[str] = None, output_path: Optional[str] = None, play: bool = True, save: bool = False):
        """Generate speech from text using a selected voice sample (by name or file). Optionally play and/or save the audio."""
        sample = voice or self.config.default_voice_sample
        if sample and not os.path.isabs(sample):
            sample = os.path.join(self.config.sample_dir, sample)
        wav = self.model.generate(text, audio_prompt_path=sample)
        sr = self.model.sr
        if play:
            # Convert torch tensor to numpy if needed
            arr = wav.cpu().numpy() if hasattr(wav, 'cpu') else np.array(wav)
            sd.play(arr, sr)
            sd.wait()
        out_path = output_path or self.config.output_path
        if save:
            ta.save(out_path, wav, sr)
            return out_path
        return None

if __name__ == '__main__':
    tts = TTS()
    print('Available voice samples:', tts.list_voice_samples())
    # Example: use tts.voices.TINA if 'TINA.wav' exists
    tina_voice = getattr(tts.voices, 'TINA', None)
    if tina_voice:
        out = tts.synthesize("This is TINA's voice!", voice=tina_voice, play=True, save=True)
        if out:
            print(f'Saved synthesized audio to {out}')
    else:
        print('No TINA voice found.') 