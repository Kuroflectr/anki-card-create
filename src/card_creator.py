import json
import os
from pathlib import Path
from typing import List, Optional, Any, Dict, Union

import requests
from googletrans import Translator
from langdetect import detect
from pydantic import BaseModel, model_validator


DIR_PATH = Path(os.path.dirname(os.path.abspath(__file__))).parent
API_URL = "http://127.0.0.1:8765"
DECK_NAME = "korean"
MODEL_NAME = "Basic (裏表反転カード付き)+sentense"


class AnkiNoteModel(BaseModel):
    deckName: str = DECK_NAME
    modelName: str = MODEL_NAME
    front: str
    back: str
    sentence: Optional[str] = None
    translated_sentence: Optional[str] = None
    audio: Optional[str] = None
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


class AnkiNoteResponse(AnkiNoteModel):
    status_code: int
    result: Union[None, int]
    error: Union[None, str]

    class Config:
        from_attributes = True


class AnkiNotes(BaseModel):
    anki_notes: List[AnkiNoteModel]

    @classmethod
    def from_input_word(
        cls,
        input_str: str,
        deck_name: str = DECK_NAME,
        model_name: str = MODEL_NAME,
    ):
        translator = Translator()

        translation = translator.translate(input_str, src="ko", dest="ja")
        translated_word = translation.text
        anki_note = AnkiNoteModel(
            deckName=deck_name,
            modelName=model_name,
            front=input_str,
            back=translated_word,
        )
        anki_notes_list = [anki_note]
        return cls(anki_notes=anki_notes_list)

    @classmethod
    def from_txt(
        cls,
        data_fname: str = DIR_PATH / "data" / "example.txt",
        deck_name: str = DECK_NAME,
        model_name: str = MODEL_NAME,
    ):
        """Create a list of notemodel which will be used in creating Anki-notes.
        The translated phrase will be automatically generated from the korean word
        listed on the front side.

        Args:
            data_fname (str, optional): _description_. Defaults to DIR_PATH/"data"/"example.txt".

        Returns:
            _type_: _description_
        """

        with open(data_fname, "r") as f:
            voc_list = f.read().split("\n")

        translator = Translator()

        anki_notes_list = []
        for word in voc_list:
            translation = translator.translate(word, src="ko", dest="ja")
            translated_word = translation.text
            anki_note = AnkiNoteModel(
                deckName=deck_name,
                modelName=model_name,
                front=word,
                back=translated_word,
            )
            anki_notes_list.append(anki_note)

        return cls(anki_notes=anki_notes_list)


class CardCreator:
    def __init__(self, anki_notes: List[AnkiNoteModel]):
        self._anki_notes = anki_notes

    @property
    def anki_notes(self):
        return self._anki_notes

    # TODO: Add audio to the anki cards
    def add_audio(self):
        pass

    @staticmethod
    def create_response(
        anki_note: AnkiNoteResponse,
        connector_response: requests.Response,
    ):
        response_json = connector_response.json()
        response_json["status_code"] = connector_response.status_code

        anki_note_dict = anki_note.model_dump()
        anki_note_dict.update(
            {
                "status_code": response_json["status_code"],
                "result": response_json["result"],
                "error": response_json["error"],
            }
        )

        return AnkiNoteResponse(**anki_note_dict)

    def send_notes(self) -> List[AnkiNoteResponse]:
        response_json_list = []
        for anki_note in self._anki_notes:
            # Create the anki payload based on the created anki-note
            note = {
                "deckName": anki_note.deckName,
                "modelName": anki_note.modelName,
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

            response_json_list.append(self.create_response(anki_note, response))

        return response_json_list

        # # Check if the deck exists and the note was added successfully
        # if response.status_code == 200:
        #     result = response.json()
        #     word_being_sent = f"{anki_note.front}, {anki_note.back}"
        #     if result["error"] is not None:
        #         # Check if the error message indicates that the deck does not exist
        #         if "deck not found" in result["error"]:
        #             print(word_being_sent + ":Error: Deck does not exist")
        #         else:
        #             print(word_being_sent + ": Error: {result['error']}")
        #     else:
        #         print(word_being_sent + ": Note added successfully")
        # else:
        #     print(word_being_sent + ": Error adding note to deck")


if __name__ == "__main__":
    # anki_notes = AnkiNotes.from_txt(
    #     data_fname="example.txt",
    # ).anki_notes
    # card_creator = CardCreator(anki_notes)
    # response_list = card_creator.send_notes()
    # for result in response_list:
    #     if result.error is not None:
    pass
