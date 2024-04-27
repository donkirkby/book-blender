from _typeshed import Incomplete

langs: Incomplete

def get_grade_suffix(grade: int) -> str: ...

class textstatistics:
    text_encoding: str
    def __init__(self) -> None: ...
    def set_rounding(self, rounding: bool, points: int | None = None) -> None: ...
    def set_rm_apostrophe(self, rm_apostrophe: bool) -> None: ...
    pyphen: Incomplete
    def set_lang(self, lang: str) -> None: ...
    def char_count(self, text: str, ignore_spaces: bool = True) -> int: ...
    def letter_count(self, text: str, ignore_spaces: bool = True) -> int: ...
    def remove_punctuation(self, text: str) -> str: ...
    def lexicon_count(self, text: str, removepunct: bool = True) -> int: ...
    def miniword_count(self, text: str, max_size: int = 3) -> int: ...
    def syllable_count(self, text: str, lang: str | None = None) -> int: ...
    def sentence_count(self, text: str) -> int: ...
    def avg_sentence_length(self, text: str) -> float: ...
    def avg_syllables_per_word(self, text: str, interval: int | None = None) -> float: ...
    def avg_character_per_word(self, text: str) -> float: ...
    def avg_letter_per_word(self, text: str) -> float: ...
    def avg_sentence_per_word(self, text: str) -> float: ...
    def words_per_sentence(self, text: str) -> float: ...
    def count_complex_arabic_words(self, text: str) -> int: ...
    def count_arabic_syllables(self, text: str) -> int: ...
    def count_faseeh(self, text: str) -> int: ...
    def count_arabic_long_words(self, text: str) -> int: ...
    def flesch_reading_ease(self, text: str) -> float: ...
    def flesch_kincaid_grade(self, text: str) -> float: ...
    def polysyllabcount(self, text: str) -> int: ...
    def smog_index(self, text: str) -> float: ...
    def coleman_liau_index(self, text: str) -> float: ...
    def automated_readability_index(self, text: str) -> float: ...
    def linsear_write_formula(self, text: str) -> float: ...
    def difficult_words(self, text: str, syllable_threshold: int = 2) -> int: ...
    def difficult_words_list(self, text: str, syllable_threshold: int = 2) -> list[str]: ...
    def is_difficult_word(self, word: str, syllable_threshold: int = 2) -> bool: ...
    def is_easy_word(self, word: str, syllable_threshold: int = 2) -> bool: ...
    def dale_chall_readability_score(self, text: str) -> float: ...
    def gunning_fog(self, text: str) -> float: ...
    def lix(self, text: str) -> float: ...
    def rix(self, text: str) -> float: ...
    def spache_readability(self, text: str, float_output: bool = True) -> float | int: ...
    def dale_chall_readability_score_v2(self, text: str) -> float: ...
    def text_standard(self, text: str, float_output: bool | None = None) -> float | str: ...
    def reading_time(self, text: str, ms_per_char: float = 14.69) -> float: ...
    def fernandez_huerta(self, text: str) -> float: ...
    def szigriszt_pazos(self, text: str) -> float: ...
    def gutierrez_polini(self, text: str) -> float: ...
    def crawford(self, text: str) -> float: ...
    def osman(self, text: str) -> float: ...
    def gulpease_index(self, text: str) -> float: ...
    def long_word_count(self, text: str) -> int: ...
    def monosyllabcount(self, text: str) -> int: ...
    def wiener_sachtextformel(self, text: str, variant: int) -> float: ...
    def mcalpine_eflaw(self, text: str) -> float: ...

textstat: Incomplete
