import json
from pathlib import Path
from typing import List, Union

import requests
from googletrans import Translator
from pydantic import BaseModel

from src import API_URL, DECK_NAME, DIR_PATH, MODEL_NAME
from src.models import AnkiNoteModel, AnkiNoteResponse
from src.utils import create_audio, create_message


class AnkiNotes(BaseModel):
    """Create Anki notes based on the method user has specified."""

    # A List for the created Anki notes.
    anki_notes: List[AnkiNoteModel]

    @classmethod
    def from_input_word(
        cls,
        input_str: str,
        translated_word: str = None,
        deck_name: str = DECK_NAME,
        model_name: str = MODEL_NAME,
    ):
        # Translate the word if its not specified.
        if translated_word is None:
            translator = Translator()
            translation = translator.translate(input_str, src="ko", dest="ja")
            translated_word = translation.text

        # Create the anki model
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

    @staticmethod
    def send_media(audio_path: Union[Path, str]) -> None:
        audio_filename = audio_path.name.__str__()
        audio_file_path = audio_path.parent.__str__()
        # Store the audio file in Anki's media folder
        response = requests.post(
            API_URL,
            json={
                "action": "storeMediaFile",
                "version": 6,
                "params": {
                    "filename": audio_filename,
                    "path": audio_file_path,
                },
            },
        )

        return response.status_code

    def send_notes(self, audio: bool = True) -> List[AnkiNoteResponse]:
        # TODO: not adding audio when its specified.
        response_json_list = []
        for anki_note in self._anki_notes:
            # Create the mp3 file
            audio_path = create_audio(anki_note.front)

            # Send the mp3 to Anki's media folder
            media_response_code = self.send_media(audio_path)
            if media_response_code != 200:
                print("Adding audio received failure")

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

            # Translate the API response to a readable message
            card_create_response = self.create_response(anki_note, response)
            response_json_list.append(card_create_response)
            print(create_message(card_create_response))

        return response_json_list
