import json
import os
from pathlib import Path
from typing import List, Optional

import requests
from googletrans import Translator
from langdetect import detect
from pydantic import BaseModel, model_validator

DIR_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
API_URL = "http://127.0.0.1:8765"
DECK_NAME = "Korean"
MODEL_NAME = "Basic (裏表反転カード付き)"


class AnkiNoteModel(BaseModel):
    deckName: str
    modelName: str
    front: str
    back: str
    sentence: Optional[str] = None
    translated_sentence: Optional[str] = None
    frontLang: str = "ko"  # Default expected language for the 'front' field
    # backLang: str = [
    #     "ja",
    #     "ko",
    #     "zh-tw",
    #     "zh-cn",
    # ]  # Default expected language for the 'back' field

    @model_validator(mode="after")
    def check_languages(self):
        front_lang = self.frontLang
        # back_lang = self.backLang

        # Detect languages of `front` and `back` fields
        detected_front_lang = detect(self.front)
        # detected_back_lang = detect(self.back)

        # Validate detected languages against expected languages
        if front_lang != detected_front_lang:
            raise ValueError(
                f"Expected language for 'front' field is '{front_lang}', but detected '{detected_front_lang}'."
            )

        # if detected_back_lang not in back_lang:
        #     raise ValueError(
        #         f"Expected language for 'back' field is '{back_lang}', but detected '{detected_back_lang}'."
        #     )

        return self


class AnkiNotes(BaseModel):
    anki_notes: List[AnkiNoteModel]

    @classmethod
    def from_txt(cls, data_fname: str = DIR_PATH / "data" / "example.txt"):
        with open(data_fname, "r") as f:
            voc_list = f.read().split("\n")

        translator = Translator()

        anki_notes_list = []
        for word in voc_list:
            translation = translator.translate(word, src="ko", dest="ja")
            translated_word = translation.text
            anki_note = AnkiNoteModel(
                deckName=DECK_NAME,
                modelName=MODEL_NAME,
                front=word,
                back=translated_word,
            )
            anki_notes_list.append(anki_note)

        return cls(anki_notes=anki_notes_list)


# TODO: sentenceも入力できるように
class CardCreator:
    def __init__(self, anki_notes: List[AnkiNoteModel]):
        self._anki_notes = anki_notes

    @property
    def anki_notes(self):
        return self._anki_notes

    def add_audio(self):
        pass

    def send_notes(self) -> None:
        for anki_note in self._anki_notes:
            note = {
                "deckName": "korean",
                "modelName": "Basic (裏表反転カード付き)",
                "fields": {
                    "表面": anki_note.front,
                    "裏面": anki_note.back,
                },
            }
            # Send the request to AnkiConnect to add the note to the deck
            response = requests.post(
                API_URL,
                json.dumps(
                    {
                        "action": "addNote",
                        "version": 6,
                        "params": {
                            "note": note,
                        },
                    }
                ),
            )

            # Check if the deck exists and the note was added successfully
            if response.status_code == 200:
                result = response.json()
                word_being_sent = f"{anki_note.front}, {anki_note.back}"
                if result["error"] is not None:
                    # Check if the error message indicates that the deck does not exist
                    if "deck not found" in result["error"]:
                        print(word_being_sent + ":Error: Deck does not exist")
                    else:
                        print(word_being_sent + ": Error: {result['error']}")
                else:
                    print(word_being_sent + ": Note added successfully")
            else:
                print(word_being_sent + ": Error adding note to deck")


if __name__ == "__main__":
    # test 1
    # note = AnkiNoteModel(
    #     deckName="Korean",
    #     modelName="Basic (裏表反転カード付き)",
    #     front="안녕하세요",
    #     back="こんにちは",
    # )

    # test 2
    # Create anki notes according to example.txt
    anki_notes = AnkiNotes.from_txt().anki_notes
    print(anki_notes)

    # test 3
    # Send the created notes to Anki
    card_creator = CardCreator(anki_notes)
    card_creator.send_notes()
