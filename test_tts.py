# =====================================================
# TTS Benchmark Script for Google Colab
# =====================================================
# This script lets you test ANY of the listed TTS packages in one go.
# - You choose the package + enter text
# - It auto-installs the package (and any system deps like espeak)
# - Measures total time to generate the audio file
# - Saves the speech file and auto-downloads it to your PC
# - Works on free Colab (CPU or GPU runtime)

import time
import subprocess
import os
'''from google.colab import files'''
import requests  # for piper model download

print("🚀 TTS Benchmark Script Loaded!")
print("Available packages:")
print("   1. pyttsx3")
print("   2. gTTS")
print("   3. mycroft-mimic3-tts")
print("   4. RealtimeTTS")
print("   5. piper-tts")
print("   6. styletts2")
print("   7. TTS (Coqui)")

package_choice = input("\nEnter package name or number (e.g. 'gTTS' or '2'): ").strip().lower()
text = input("\nEnter the text/paragraph you want to convert to speech:\n").strip()

if not text:
    text = "Hello, this is a test of the TTS system in Google Colab."

# Map user input to proper package name for pip
pkg_map = {
    "1": "pyttsx3", "pyttsx3": "pyttsx3",
    "2": "gtts", "gtts": "gtts", "gTTS": "gtts",
    "3": "mycroft-mimic3-tts", "mimic3": "mycroft-mimic3-tts",
    "4": "realtimetts", "realtimetts": "realtimetts",
    "5": "piper-tts", "piper": "piper-tts",
    "6": "styletts2", "styletts2": "styletts2",
    "7": "tts", "coqui": "tts", "coqui-tts": "tts"
}

pkg_name = pkg_map.get(package_choice, package_choice)
if pkg_name not in ["pyttsx3", "gtts", "mycroft-mimic3-tts", "realtimetts", "piper-tts", "styletts2", "tts"]:
    print(f"❌ Unknown package: {pkg_name}")
    raise SystemExit

print(f"\n🔄 Testing: {pkg_name}")
start_time = time.perf_counter()

# ====================== AUTO-INSTALL + SYSTEM DEPS ======================
try:
    __import__(pkg_name.replace("-", "_").split(".")[0])  # rough import check
except:
    print(f"   Installing {pkg_name} ...")
    subprocess.check_call(["pip", "install", "--quiet", pkg_name])

# Special system deps for some packages
if pkg_name in ["pyttsx3", "mycroft-mimic3-tts"]:
    print("   Installing espeak-ng (required for offline engines)...")
    subprocess.check_call(["apt-get", "update", "-qq"])
    subprocess.check_call(["apt-get", "install", "-y", "-qq", "espeak-ng"])

print("   Package ready!")

# ====================== TTS GENERATION PER PACKAGE ======================
filename = "speech_output.wav"   # default, some use mp3
if pkg_name == "gtts":
    filename = "speech_output.mp3"
    from gtts import gTTS
    tts = gTTS(text=text, lang="en", slow=False)
    tts.save(filename)

elif pkg_name == "pyttsx3":
    import pyttsx3
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.save_to_file(text, filename)
    engine.runAndWait()

elif pkg_name == "mycroft-mimic3-tts":
    filename = "speech_output.wav"
    # Mimic3 CLI (installed with the package)
    try:
        subprocess.check_call(["mimic3", text, "--output-file", filename])
    except:
        # Fallback: output to stdout and wrap as WAV (works on most installs)
        with open(filename, "wb") as f:
            subprocess.run(["mimic3", text], stdout=f)

elif pkg_name == "realtimetts":
    filename = None  # RealtimeTTS is streaming-first
    from RealtimeTTS import TextToAudioStream, SystemEngine
    engine = SystemEngine()           # uses pyttsx3/espeak under the hood
    stream = TextToAudioStream(engine)
    print("   Streaming & playing audio (RealtimeTTS style)...")
    stream.feed(text)
    stream.play()
    print("   NOTE: RealtimeTTS does not save a file by default (it's for real-time streaming).")
    print("         Audio played above. No file downloaded for this package.")

elif pkg_name == "piper-tts":
    filename = "speech_output.wav"
    model_dir = "/content/piper_models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "en_US-lessac-medium.onnx")
    
    if not os.path.exists(model_path):
        print("   Downloading Piper voice model (first time only ~150 MB)...")
        url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
        r = requests.get(url, stream=True, timeout=60)
        with open(model_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    from piper.voice import PiperVoice
    import wave
    voice = PiperVoice.load(model_path)
    with wave.open(filename, "w") as wav_file:
        voice.synthesize(text, wav_file)

elif pkg_name == "styletts2":
    filename = "speech_output.wav"
    from styletts2 import tts
    tts_engine = tts.StyleTTS2()          # auto-downloads checkpoints on first run
    tts_engine.inference(text, output_wav_file=filename)

elif pkg_name == "tts":
    filename = "speech_output.wav"
    from TTS.api import TTS
    # Fast English model (change if you want multilingual/XTTS)
    model_name = "tts_models/en/ljspeech/tacotron2-DDC"
    # Use GPU if Colab runtime has it enabled
    use_gpu = "cuda" in str(subprocess.check_output(["nvidia-smi"])) if os.path.exists("/usr/bin/nvidia-smi") else False
    tts_model = TTS(model_name=model_name, progress_bar=False, gpu=use_gpu)
    tts_model.tts_to_file(text=text, file_path=filename)

# ====================== TIMING & DOWNLOAD ======================
elapsed = time.perf_counter() - start_time

if filename and os.path.exists(filename):
    print(f"\n✅ Done! Speech file: {filename}")
    print(f"⏱️  Processing time: {elapsed:.3f} seconds")
    files.download(filename)
else:
    print(f"\n✅ Done (streaming mode)!")
    print(f"⏱️  Processing time: {elapsed:.3f} seconds")

print("\n🎉 Test complete! Run the cell again to test another package.")