from transformers.pipelines import pipeline

pipe = pipeline("text2text-generation", model="reach-vb/parler-tts-expresso-v0.1")


result = pipe("Hello, world!")

print(result)
print(type(result))