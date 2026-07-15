# Duplicate Killer 🔍

**Find and remove duplicate files. Free up disk space. Safely.**

Duplicate Killer is a modern, fast, and safe desktop application for finding and removing duplicate files on your computer. Built with Python and CustomTkinter. Supports **Windows** and **Linux**.

## Features

- **Fast 2-phase scanning** — groups files by size, then compares content via MD5 hash
- **Safe deletion** — files go to Recycle Bin, not permanently erased
- **Dark & Light theme** — your choice
- **English / Русский** — built-in bilingual support
- **Export results** — TXT and CSV reports
- **Folder & extension exclusions** — skip what you don't need
- **Non-blocking UI** — stays responsive during scan

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Build executables

### Windows
```bash
pip install nuitka
nuitka --onefile --windows-console-mode=disable --enable-plugin=tk-inter main.py
```

### Linux
```bash
pip install nuitka
nuitka --onefile --enable-plugin=tk-inter main.py
```

## Requirements

- Python 3.8+
- customtkinter
- send2trash (optional, for Recycle Bin support)

## License

Proprietary. All rights reserved.
