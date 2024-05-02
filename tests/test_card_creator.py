from pathlib import Path
from typing import Dict
import os

import pytest

from src.card_creator import AnkiNotes, CardCreator


@pytest.fixture(scope="module")
def create_test_data() -> None:
    input_word = ["죄송합니다", "이거 얼마예요"]
    file_path = "test_data.txt"
    with open(file_path, "w") as f:
        for i, word in enumerate(input_word):
            if i > 0:
                f.write("\n")
            f.write(word)
    yield
    os.remove(file_path)  # Cleanup after the module tests are done


@pytest.fixture(scope="function")
def test_features(create_test_data) -> Dict[str, str]:
    return {
        "test_data": Path(__file__).resolve().parent.parent / "tests" / "test_data.txt",
        "deck_name": "test",
        "model_name": "Basic (裏表反転カード付き)+sentense",
    }


def test_create_anki_notes_from_txt(test_features):
    """TESTCASE1: Create anki notes from a given txt file."""
    anki_notes = AnkiNotes.from_txt(
        data_fname=test_features["test_data"],
    ).anki_notes
    assert len(anki_notes) == 2
    assert anki_notes[0].front == "죄송합니다"
    assert anki_notes[1].front == "이거 얼마예요"
    assert anki_notes[0].back == "ごめん"
    assert anki_notes[1].back == "いくらですか"


def test_create_anki_notes_from_input():
    """TESTCASE2: Create anki notes from the input"""
    anki_notes = AnkiNotes.from_input_word(
        input_str="죄송합니다",
    ).anki_notes
    assert len(anki_notes) == 1
    assert anki_notes[0].front == "죄송합니다"
    assert anki_notes[0].back == "ごめん"


def test_send_anki_note_not_audio(test_features):
    """TESTCASE3: Send the created notes to the specified deck"""
    anki_notes = AnkiNotes.from_txt(
        data_fname=test_features["test_data"],
        deck_name=test_features["deck_name"],
        model_name=test_features["model_name"],
    ).anki_notes
    card_creator = CardCreator(anki_notes)

    response_list = card_creator.send_notes(audio=False)
    assert len(response_list) == 2
    assert response_list[0].status_code == 200
    assert response_list[1].status_code == 200


# def test_send_duplicated_anki_note(voc_txt):
#     deck_name = "test"
#     model_name = "Basic (裏表反転カード付き)+sentense"
