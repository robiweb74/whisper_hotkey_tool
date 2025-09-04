# 🎙️ Whisper Hotkey Tool

A Windows system tray application that provides real-time speech-to-text transcription using OpenAI's Whisper model. Simply hold a hotkey combination to record audio and automatically insert the transcribed text wherever your cursor is positioned.

## ✨ Features

- **🔥 Real-time transcription** using OpenAI Whisper
- **⌨️ Global hotkey** (Ctrl+Shift by default) for hands-free operation
- **🖱️ System tray integration** with right-click menu
- **🧠 Multiple model support** (tiny, small, medium, large-v3)
- **🎚️ Toggle listening on/off** without closing the app
- **📝 Direct text insertion** at cursor position
- **🔊 Audio feedback** with beep sounds
- **💻 Lightweight and efficient**

## 🚀 Quick Start

### Option 1: Run with Python (Recommended for development)

#### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- Microphone access

#### Installation Steps

1. **Clone or download** this repository
   ```bash
   git clone <repository-url>
   cd whisper-hotkey-tool
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv whisper_env
   whisper_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install sounddevice numpy keyboard faster-whisper pillow pystray
   ```

4. **Add a microphone icon** (optional)
   - Place a `mic_icon.png` file (16x16 or 32x32 pixels) in the project folder
   - Or let the app create a default icon automatically

5. **Run the application**
   ```bash
   python whisper_hotkey_tray.py
   ```

#### First-time setup
- The app will download the Whisper model on first run (may take a few minutes)
- Look for the microphone icon in your system tray
- Test the hotkey: Hold **Ctrl+Shift**, speak, then release to insert text

### Option 2: Standalone EXE (No Python required)

#### Download Pre-built EXE
1. Go to the [Releases](releases) page
2. Download `WhisperHotkey.exe`
3. Run the executable directly

#### Build Your Own EXE

If you want to build the EXE yourself:

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Prepare icon files**
   - Ensure you have `mic_icon.png` in the project folder
   - Optionally create `mic_icon.ico` for the EXE icon:
     ```python
     from PIL import Image
     img = Image.open('mic_icon.png')
     img.save('mic_icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48)])
     ```

3. **Build with simple command**
   ```bash
   pyinstaller --onefile --noconsole --icon=mic_icon.ico --add-data "mic_icon.png;." --hidden-import=faster_whisper --hidden-import=torch --hidden-import=sounddevice --hidden-import=pystray._win32 --hidden-import=keyboard._winkeyboard --name=WhisperHotkey whisper_hotkey_tray.py
   ```

4. **Advanced build (using spec file)**
   
   Create `whisper_hotkey.spec`:
   ```python
   # -*- mode: python ; coding: utf-8 -*-
   from PyInstaller.utils.hooks import collect_data_files
   
   faster_whisper_datas = collect_data_files('faster_whisper')
   torch_datas = collect_data_files('torch')
   
   a = Analysis(
       ['whisper_hotkey_tray.py'],
       pathex=[],
       binaries=[],
       datas=[
           ('mic_icon.png', '.'),
           *faster_whisper_datas,
           *torch_datas,
       ],
       hiddenimports=[
           'faster_whisper',
           'faster_whisper.transcribe',
           'faster_whisper.feature_extractor', 
           'faster_whisper.tokenizer',
           'faster_whisper.audio',
           'torch',
           'torch._C',
           'sounddevice',
           'numpy',
           'PIL',
           'PIL._tkinter_finder',
           'pystray._win32',
           'keyboard._winkeyboard',
           'tempfile',
           'wave',
           'winsound',
           'threading',
           'ctypes.wintypes',
       ],
       hookspath=[],
       runtime_hooks=[],
       excludes=[],
       win_no_prefer_redirects=False,
       win_private_assemblies=False,
       cipher=None,
       noarchive=False,
   )
   
   pyz = PYZ(a.pure, a.zipped_data, cipher=None)
   
   exe = EXE(
       pyz,
       a.scripts,
       a.binaries,
       a.zipfiles,
       a.datas,
       [],
       name='WhisperHotkey',
       debug=False,
       bootloader_ignore_signals=False,
       strip=False,
       upx=True,
       upx_exclude=[],
       runtime_tmpdir=None,
       console=False,
       disable_windowed_traceback=False,
       argv_emulation=False,
       target_arch=None,
       codesign_identity=None,
       entitlements_file=None,
       icon='mic_icon.ico',
   )
   ```
   
   Then build:
   ```bash
   pyinstaller whisper_hotkey.spec
   ```

5. **Find your EXE**
   - The built executable will be in the `dist/` folder
   - File size will be ~200-500MB (includes all dependencies)
   - Copy `WhisperHotkey.exe` anywhere and run it

## 📖 Usage

### Basic Operation
1. **Start the application** - Look for the microphone icon in your system tray
2. **Record audio** - Hold **Ctrl+Shift** and speak clearly
3. **Release hotkey** - The app will process your speech and insert the text
4. **System tray menu** - Right-click the tray icon for options

### Tray Menu Options
- **🎤 Listening: ON/OFF** - Toggle voice recording on/off
- **🧠 Model: [current]** - Cycle through Whisper models (tiny → small → medium → large-v3)
- **⌨️ Hotkey: Ctrl+Shift** - Shows current hotkey combination
- **❌ Quit** - Exit the application

### Whisper Models
| Model | Size | Speed | Accuracy | Use Case |
|-------|------|--------|----------|----------|
| tiny | ~39 MB | Fastest | Good | Quick notes, testing |
| small | ~244 MB | Fast | Better | General use |
| medium | ~769 MB | Moderate | Good | Balanced performance |
| large-v3 | ~1550 MB | Slower | Best | High accuracy needed |

## ⚙️ Configuration

Edit the configuration section in `whisper_hotkey_tray.py`:

```python
# Configuration options
MODEL_LIST = ["tiny", "small", "medium", "large-v3"]
model_index = 1  # default: small (0=tiny, 1=small, 2=medium, 3=large-v3)
DEVICE = "cpu"  # Use "cuda" for GPU acceleration (if available)
HOTKEY_MOD = "ctrl"  # Modifier key
HOTKEY_KEY = "shift"  # Main key
LANGUAGE = "en"  # Language code (en, es, fr, de, etc.)
is_listening_enabled = True  # Start with listening enabled
```

### Common Languages
- `"en"` - English
- `"es"` - Spanish  
- `"fr"` - French
- `"de"` - German
- `"it"` - Italian
- `"pt"` - Portuguese
- `"ru"` - Russian
- `"ja"` - Japanese
- `"zh"` - Chinese

## 🔧 Troubleshooting

### Common Issues

#### "No module named 'faster_whisper'"
```bash
pip install faster-whisper
```

#### "Could not find a microphone"
- Check microphone permissions in Windows Settings
- Ensure your microphone is set as the default recording device

#### "Package not found" when building EXE
- Install missing packages: `pip install <missing-package>`
- Add hidden imports to the PyInstaller command

#### EXE is very large (200+ MB)
- This is normal - includes PyTorch and Whisper models
- Use `upx=True` in spec file for compression
- Consider using smaller models for distribution

#### Tray icon doesn't appear
- Check if icon file exists: `mic_icon.png`
- Ensure `pystray._win32` is in hidden imports
- Try running as administrator

#### No audio beeps
- Check Windows sound settings
- Some systems may not support `winsound.Beep()`
- The app will still work without audio feedback

#### Transcription is slow/inaccurate
- Try different Whisper models via tray menu
- Ensure good microphone quality and quiet environment
- Consider GPU acceleration by changing `DEVICE = "cuda"`

### Performance Tips
- Use **tiny** or **small** models for faster processing
- Enable GPU acceleration if you have CUDA-compatible graphics
- Close other audio applications during use
- Use a good quality microphone in a quiet environment

## 📁 Project Structure

```
whisper-hotkey-tool/
├── whisper_hotkey_tray.py    # Main application script
├── requirements.txt          # Python dependencies
├── mic_icon.png             # Tray icon (16x16 or 32x32 px)
├── mic_icon.ico             # EXE icon (optional)
├── whisper_hotkey.spec      # PyInstaller spec file
├── README.md                # This file
├── dist/                    # Built executables (after PyInstaller)
│   └── WhisperHotkey.exe
└── build/                   # Build artifacts (temporary)
```

## 📋 Requirements

### Python Dependencies
```
sounddevice>=0.4.0
numpy>=1.21.0
keyboard>=1.13.0
faster-whisper>=0.9.0
Pillow>=9.0.0
pystray>=0.19.0
```

### System Requirements
- **OS**: Windows 10/11 (64-bit recommended)
- **RAM**: 2GB minimum, 4GB+ recommended for larger models
- **Storage**: 1-2GB free space for models
- **Audio**: Working microphone and speakers/headphones

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit changes: `git commit -am 'Add new feature'`
5. Push to branch: `git push origin feature-name`
6. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- [pystray](https://github.com/moses-palmer/pystray) - System tray functionality
- [keyboard](https://github.com/boppreh/keyboard) - Global hotkey support

## 💬 Support

- **Issues**: Report bugs and request features via [GitHub Issues](issues)
- **Discussions**: Join the conversation in [GitHub Discussions](discussions)
- **Documentation**: Check this README and inline code comments

---

**⭐ If you find this tool helpful, please give it a star!** ⭐