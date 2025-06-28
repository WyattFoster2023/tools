import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

# Load the model (uses GPU if available)
model = ChatterboxTTS.from_pretrained(device="cuda")  # or "cpu"

text = """Managing time effectively is an important skill for WGU students, but it can be challenging. Life's ups and downs can sometimes throw off our plans, and emotions can get in the way of managing our time well. These feelings can make it harder to stay focused and motivated.
Emotional blockers are like mental roadblocks that slow us down, stop us from getting things done, and make it hard to focus and stay motivated."""
wav = model.generate(text, audio_prompt_path="audio/sample_tina_huang.wav")

# Optional: clone/voice conversion with an audio prompt
# wav = model.generate(text, audio_prompt_path="speaker_sample.wav")

ta.save("chatterbox_out.wav", wav, model.sr)
print("Saved to chatterbox_out.wav")
