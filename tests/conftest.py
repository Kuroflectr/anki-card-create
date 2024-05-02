import pytest
from pathlib import Path
from typing import Dict


@pytest.fixture(scope="session")
def global_data() -> Dict[str, str]:
    return {
        "dir_path": Path(__file__).resolve().parent,
        "test_word": "안녕하세요",
        "test_word_in_txt": ["죄송합니다", "이거 얼마예요"],
        "test_file_name": "test_data.txt",
        "deck_name": "test",
        "model_name": "Basic (裏表反転カード付き)+sentense",
        "audio_name": "naver_hello_korean_test.mp3",
    }
