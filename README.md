# Create Korean Anki cards with audios

Add anki cards with audios (korean vocabulary) simply with only one command: `kanki`.

## Package setup

Set up the package using: 
```
git clone https://github.com/Kuroflectr/anki-card-create.git
cd ./anki-card-create
poetry install
```

## Usage

1. Ensure that Anki has been running in the background. 

2. Ensure that anki-connect has been installed. 

3. Create a single anki card using: 
```
kanki -w 안녕하세요
```

4. Or, create multiple anki cards using: 
```
kanki -f <file-with-korean-vocabularies-listed>
```