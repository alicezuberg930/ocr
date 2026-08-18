### Install pytesseract

pytesseract is only a Python wrapper around the actual Tesseract OCR executable, and its documentation explicitly requires Tesseract to be installed and available as the tesseract command.

- Install the package

+ On arch linux

```sudo pacman -S tesseract```

+ On windows
```choco install tesseract -y```

- Install the language packs

+ On arch linux

```bash
sudo pacman -S \
  tesseract-data-eng \
  tesseract-data-vie \
  tesseract-data-fra \
  tesseract-data-deu \
  tesseract-data-spa \
  tesseract-data-jpn \
  tesseract-data-chi_sim
```

+ On windows
For your language packs:

eng      English
vie      Vietnamese
fra      French
deu      German
spa      Spanish
jpn      Japanese
chi_sim  Simplified Chinese

download these files from the official Tesseract tessdata repository - Link: https://github.com/tesseract-ocr/tessdata_best

*.traineddata

and put them in:

```C:\Program Files\Tesseract-OCR\tessdata\```

Afterward, your folder would look roughly like:

```text
C:\Program Files\Tesseract-OCR\
│
├── tesseract.exe
│
└── tessdata\
    ├── eng.traineddata
    ├── vie.traineddata
    ├── fra.traineddata
    ├── deu.traineddata
    ├── spa.traineddata
    ├── jpn.traineddata
    └── chi_sim.traineddata
```

- Check which languages you currently have with:
```tesseract --list-langs```

input
  ↓
grayscale
  ↓
denoise
  ↓
contrast enhancement
  ↓
threshold
  ↓
deskew
  ↓
Tesseract