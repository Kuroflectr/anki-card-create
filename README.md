# Create Korean Anki cards with audios


1. Set up the package using: 
```
git clone https://github.com/Kuroflectr/anki-card-create.git
cd ./anki-card-create
poetry install
```

2. Create a single anki card using: 
```
cd ./src
python ankicard.py -w 안녕하세요
```

3. Or, create multiple anki cards using: 
```
cd ./src
python ankicard.py -f <file-with-korean-vocabularies-listed>
```