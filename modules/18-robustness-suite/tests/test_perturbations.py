"""Tests de cada perturbación individual."""

import random

import pytest

from perturbations import (
    PERTURBATION_SPECS,
    PERTURBERS,
    PerturbationCategory,
    apply,
    emojify,
    inject_typos,
    lang_switch_token,
    paraphrase,
    passive_voice,
    remove_diacritics,
    truncate,
    uppercase,
    verbose,
    zero_width,
)


class TestSpecs:
    def test_all_canonical_perturbations_present(self):
        expected = {
            "inject_typos", "remove_diacritics", "morph_number_swap", "passive_voice",
            "paraphrase", "lang_switch_token", "truncate", "verbose", "uppercase",
            "emojify", "zero_width",
        }
        assert set(PERTURBATION_SPECS.keys()) == expected

    def test_8_categories_covered(self):
        cats = {s.category for s in PERTURBATION_SPECS.values()}
        assert len(cats) == 8

    def test_all_categories_enum(self):
        assert len(list(PerturbationCategory)) == 8


class TestLexicalPerturbations:
    def test_inject_typos_changes_string_with_high_rate(self, rng):
        out = inject_typos("the quick brown fox", rng, rate=1.0)
        # Con rate=1.0 todo intercambio adyacente sucede
        assert out != "the quick brown fox"

    def test_inject_typos_preserves_length(self, rng):
        original = "hello world example"
        out = inject_typos(original, rng, rate=0.3)
        assert len(out) == len(original)

    def test_remove_diacritics(self):
        assert remove_diacritics("camión rápido", random.Random()) == "camion rapido"

    def test_remove_diacritics_preserves_ascii(self):
        assert remove_diacritics("hello world", random.Random()) == "hello world"


class TestSyntacticPerturbations:
    def test_passive_voice_adds_prefix(self):
        out = passive_voice("el gato come pescado", random.Random())
        assert out.startswith("se conoce que ")

    def test_passive_voice_idempotent(self):
        once = passive_voice("hola", random.Random())
        twice = passive_voice(once, random.Random())
        assert once == twice


class TestSemanticPerturbations:
    def test_paraphrase_substitutes_synonyms(self):
        out = paraphrase("el gato come comida", random.Random())
        assert "felino" in out
        assert "alimento" in out

    def test_paraphrase_preserves_words_without_synonym(self):
        out = paraphrase("hola mundo", random.Random())
        assert out == "hola mundo"


class TestLengthPerturbations:
    def test_truncate_shortens(self):
        out = truncate("una query bastante larga aquí", random.Random())
        assert len(out) < len("una query bastante larga aquí")

    def test_truncate_minimum_length(self):
        out = truncate("hola", random.Random())
        assert len(out) >= 8 or len(out) == len("hola")

    def test_verbose_adds_filler(self):
        out = verbose("query", random.Random())
        assert "consulta" in out


class TestCaseFormatPerturbations:
    def test_uppercase_converts(self):
        assert uppercase("hello world", random.Random()) == "HELLO WORLD"

    def test_emojify_appends_emoji(self):
        out = emojify("hola", random.Random())
        assert "👍" in out


class TestIdiomaticPerturbations:
    def test_lang_switch_adds_english(self):
        out = lang_switch_token("dame el saldo", random.Random())
        assert "please" in out.lower()

    def test_lang_switch_idempotent(self):
        once = lang_switch_token("please give me data", random.Random())
        assert once == "please give me data"


class TestAdversarialSubtle:
    def test_zero_width_inserts_zero_width_space(self):
        out = zero_width("abc", random.Random())
        # 'a' + zwsp + 'b' + zwsp + 'c' = 5 caracteres
        assert "​" in out
        assert len(out) > len("abc")


class TestApplyDispatcher:
    def test_apply_with_valid_name(self):
        out = apply("uppercase", "hola")
        assert out == "HOLA"

    def test_apply_unknown_perturbation_raises(self):
        with pytest.raises(KeyError, match="desconocida"):
            apply("imaginaria", "query")

    def test_apply_deterministic_with_seed(self):
        a = apply("inject_typos", "hello world", random.Random(7))
        b = apply("inject_typos", "hello world", random.Random(7))
        assert a == b

    def test_all_perturbations_callable_from_dispatcher(self):
        rng = random.Random(42)
        for name in PERTURBERS:
            out = apply(name, "una query de ejemplo", rng)
            assert isinstance(out, str)
