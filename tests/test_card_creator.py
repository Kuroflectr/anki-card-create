from src.card_creator import AnkiNotes, CardCreator, AnkiNoteModel
import pytest
from typing import Dict


@pytest.fixture
def test_features() -> Dict[str, str]:
    return {
        "test_data": "test_data.txt",
        "deck_name": "test",
        "model_name": "Basic (裏表反転カード付き)+sentense",
    }


def test_anki_note_model():
    """test 1: Create a note by manually input the text"""
    note = AnkiNoteModel(
        deckName="korean",
        modelName="Basic (裏表反転カード付き)+sentense",
        front="안녕하세요",
        back="こんにちは",
    )

    assert note.deckName == "korean"
    assert note.modelName == "Basic (裏表反転カード付き)+sentense"
    assert note.front == "안녕하세요"
    assert note.back == "こんにちは"
    assert note.frontLang == "ko"


def test_create_anki_notes_from_txt(test_features):
    anki_notes = AnkiNotes.from_txt(
        data_fname=test_features["test_data"],
    ).anki_notes
    assert len(anki_notes) == 2
    assert anki_notes[0].front == "죄송합니다"
    assert anki_notes[1].front == "이거 얼마예요"
    assert anki_notes[0].back == "ごめん"
    assert anki_notes[1].back == "いくらですか"


def test_create_anki_notes_from_input():
    anki_notes = AnkiNotes.from_input_word(
        input_str="죄송합니다",
    ).anki_notes
    assert len(anki_notes) == 1
    assert anki_notes[0].front == "죄송합니다"
    assert anki_notes[0].back == "ごめん"


def test_send_anki_note(test_features):
    # Send the created notes to the specified deck
    anki_notes = AnkiNotes.from_txt(
        data_fname=test_features["test_data"],
        deck_name=test_features["deck_name"],
        model_name=test_features["model_name"],
    ).anki_notes
    card_creator = CardCreator(anki_notes)

    response_list = card_creator.send_notes()
    assert len(response_list) == 2
    assert response_list[0].status_code == 200
    assert response_list[1].status_code == 200


# def test_send_duplicated_anki_note(voc_txt):
#     deck_name = "test"
#     model_name = "Basic (裏表反転カード付き)+sentense"
