import sounddevice as sd
import numpy as np
import keyboard
import tempfile
import wave
import winsound
from faster_whisper import WhisperModel
import os
import sys
from PIL import Image
import pystray
import threading

# -------------------------------
# Resource path handling for PyInstaller
# -------------------------------
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -------------------------------
# Config
# -------------------------------
MODEL_LIST = ["tiny", "small", "medium", "large-v3"]
model_index = 1  # default small
DEVICE = "cpu"
HOTKEY_MOD = "ctrl"
HOTKEY_KEY = "shift"
LANGUAGE = "en"
is_listening_enabled = True
# -------------------------------

print("🚀 Initializing Whisper model...")
model = WhisperModel(MODEL_LIST[model_index], device=DEVICE, compute_type="int8")
print("✅ Model loaded successfully")

samplerate = 16000
channels = 1
recording = []
is_recording = False
running = True
tray_icon = None

# -------------------------------
# Audio handling
# -------------------------------
def start_recording(event):
    global recording, is_recording
    if not is_recording and is_listening_enabled:
        recording = []
        is_recording = True
        try:
            winsound.Beep(1000, 150)
        except:
            pass  # Ignore beep errors in some environments
        print("🎤 Listening...")

def stop_recording(event):
    global is_recording
    if is_recording:
        is_recording = False
        try:
            winsound.Beep(600, 200)
        except:
            pass  # Ignore beep errors in some environments
        print("🛑 Processing...")

        # Create temp file for audio
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                with wave.open(tmp.name, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(2)
                    wf.setframerate(samplerate)
                    wf.writeframes(b''.join(recording))
                audio_path = tmp.name

            size_kb = os.path.getsize(audio_path) / 1024
            print(f"📁 Recorded file size: {size_kb:.1f} KB")

            if size_kb < 2:
                print("⚠️ No audio captured.")
                os.unlink(audio_path)  # Clean up temp file
                return

            # Transcribe audio
            segments, _ = model.transcribe(audio_path, language=LANGUAGE, beam_size=5)
            text = " ".join([seg.text for seg in segments]).strip()
            text = text.lstrip("Ee ").strip()

            # Clean up temp file
            try:
                os.unlink(audio_path)
            except:
                pass

            if text:
                keyboard.write(text)
                print("✅ Inserted:", text)
            else:
                print("⚠️ Got no transcription.")
                
        except Exception as e:
            print(f"❌ Error during transcription: {e}")

def callback(indata, frames, time, status):
    global recording
    if is_recording:
        int16_audio = (indata * 32767).astype(np.int16)
        recording.append(int16_audio.tobytes())

# -------------------------------
# Tray menu functions
# -------------------------------
def on_quit(icon, item):
    global running
    running = False
    print("🛑 Shutting down...")
    icon.stop()
    sys.exit()

def toggle_listening(icon, item):
    global is_listening_enabled
    is_listening_enabled = not is_listening_enabled
    status = "ON" if is_listening_enabled else "OFF"
    print(f"👂 Listening: {status}")
    
    # Update the menu with new status
    update_menu()

def switch_model(icon, item):
    global model_index, model
    old_model = MODEL_LIST[model_index]
    model_index = (model_index + 1) % len(MODEL_LIST)
    new_model = MODEL_LIST[model_index]
    
    print(f"🔄 Switching model from {old_model} to {new_model}...")
    try:
        model = WhisperModel(new_model, device=DEVICE, compute_type="int8")
        print(f"✅ Switched to model: {new_model}")
    except Exception as e:
        print(f"❌ Failed to load model {new_model}: {e}")
        # Revert to previous model
        model_index = MODEL_LIST.index(old_model)
        return
    
    # Update the menu with new model
    update_menu()

def create_menu():
    """Create the tray menu with current status"""
    listening_status = "ON" if is_listening_enabled else "OFF"
    current_model = MODEL_LIST[model_index]
    
    return pystray.Menu(
        pystray.MenuItem(f"🎤 Listening: {listening_status}", toggle_listening),
        pystray.MenuItem(f"🧠 Model: {current_model}", switch_model),
        pystray.MenuItem("", None),  # Separator
        pystray.MenuItem(f"⌨️ Hotkey: {HOTKEY_MOD.title()}+{HOTKEY_KEY.title()}", None, enabled=False),
        pystray.MenuItem("", None),  # Separator
        pystray.MenuItem("❌ Quit", on_quit)
    )

def update_menu():
    """Update the tray menu to reflect current status"""
    global tray_icon
    if tray_icon:
        tray_icon.menu = create_menu()
        tray_icon.update_menu()

def create_default_icon():
    """Create a default microphone icon if the image file doesn't exist"""
    try:
        icon_path = get_resource_path("mic_icon.png")
        return Image.open(icon_path)
    except FileNotFoundError:
        print("⚠️ mic_icon.png not found, creating default icon")
        # Create a simple 16x16 microphone-like icon
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        pixels = img.load()
        
        # Simple microphone shape in blue
        for y in range(16):
            for x in range(16):
                if (6 <= x <= 9 and 2 <= y <= 8) or \
                   (7 <= x <= 8 and 9 <= y <= 11) or \
                   (5 <= x <= 10 and 12 <= y <= 12) or \
                   (7 <= x <= 8 and 13 <= y <= 15):
                    pixels[x, y] = (100, 149, 237, 255)  # Cornflower blue
        
        return img
    except Exception as e:
        print(f"❌ Error loading icon: {e}")
        # Create minimal fallback icon
        img = Image.new('RGBA', (16, 16), (100, 149, 237, 255))
        return img

def tray_thread():
    global tray_icon
    try:
        icon_image = create_default_icon()
        
        tray_icon = pystray.Icon(
            "WhisperHotkey", 
            icon_image, 
            "Whisper Speech-to-Text\nHold Ctrl+Shift to record", 
            menu=create_menu()
        )
        
        print("🔧 Starting system tray...")
        tray_icon.run()
        
    except Exception as e:
        print(f"❌ Error starting tray: {e}")

# -------------------------------
# Main
# -------------------------------
def main():
    print("=" * 60)
    print("🎙️  WHISPER HOTKEY TOOL")
    print("=" * 60)
    print(f"📝 Initial model: {MODEL_LIST[model_index]}")
    print(f"🎯 Hotkey: Hold {HOTKEY_MOD.upper()}+{HOTKEY_KEY.upper()} to record")
    print(f"👂 Listening: {'ON' if is_listening_enabled else 'OFF'}")
    print(f"💻 Device: {DEVICE}")
    print(f"🌐 Language: {LANGUAGE}")
    print("=" * 60)
    
    # Start tray in separate thread
    tray_thread_obj = threading.Thread(target=tray_thread, daemon=True)
    tray_thread_obj.start()

    try:
        print("🎵 Initializing audio stream...")
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            print(f"✅ Ready! Hold {HOTKEY_MOD.upper()}+{HOTKEY_KEY.upper()} to talk, release to insert text...")
            print("💡 Use the system tray icon to change settings")
            
            # Set up keyboard hooks
            keyboard.on_press_key(HOTKEY_KEY, lambda e: start_recording(e) if keyboard.is_pressed(HOTKEY_MOD) else None)
            keyboard.on_release_key(HOTKEY_KEY, lambda e: stop_recording(e) if not keyboard.is_pressed(HOTKEY_KEY) else None)

            # Main loop
            while running:
                try:
                    sd.sleep(100)
                except KeyboardInterrupt:
                    break
                    
    except KeyboardInterrupt:
        print("\n🛑 Received interrupt signal...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")
    finally:
        print("🧹 Cleaning up...")
        if tray_icon:
            tray_icon.stop()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()