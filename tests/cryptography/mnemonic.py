"""Unit test for /pysession/cryptography/mnemonic.py"""
import base64
import os

import pytest

from pysession.cryptography.mnemonic import KeyPair, MnemonicError, swap_endian_bytes


@pytest.fixture
def words() -> str:
    """Hardcoded set of words used for the tests"""
    return "spout suffice lynx factual lexicon gigantic dodge roared lawsuit bluntly cycling meant lexicon"


@pytest.fixture
def invalid_checksum() -> str:
    return "spout suffice lynx factual lexicon gigantic dodge roared lawsuit bluntly cycling meant spout"


@pytest.fixture
def public_key_v2() -> bytes:
    return base64.b64decode("BVU1hwmy38i/bdF9tBKkIFnyVeIf2S2bQDCr2D9QrmFY")


@pytest.fixture
def public_key_v3() -> bytes:
    return base64.b64decode("BZOSuZXwU360W8v7an5w1J7LrvIlbKxA1y89KROcuLhs")


def test_swap_endian_bytes():
    """Test byte swapping"""
    assert swap_endian_bytes("12345678") == "78563412"


def test_seed32_from_words(words):
    pair = KeyPair.from_words(words)
    assert pair._seed32 == "dbfadcb2190181d98c13f8c07ed7765a"


def test_pubkey_from_seed_v2(words, public_key_v2):
    """Verify if the words generate the same public key.
    Private key can't be checked like this since there are collisions.
    See: https://gist.github.com/Vepnar/696b21ef6d52430305cec360225b89ea
    """
    pair = KeyPair.from_words(words, version=2)

    # Verify public key
    assert pair._pub == public_key_v2


def test_pubkey_from_seed_v3(words, public_key_v3):
    """Verify if the words generate the same public key.
    Private key can't be checked like this since there are collisions.
    See: https://gist.github.com/Vepnar/696b21ef6d52430305cec360225b89ea
    """
    pair = KeyPair.from_words(words, version=3)

    # Verify public key
    assert pair._pub == public_key_v3


def test_invalid_seed_version(words):
    """Test if KeyPair raises an error when the version is invalid"""
    try:
        KeyPair.from_words(words, version=-1)
        assert False
    except MnemonicError as ex:
        assert ex.args[0] == "Unknown seed version"


def test_too_short_seed():
    """Test if the seed is valid with too little words"""
    try:
        seed = " ".join(["abbey"] * 11)
        KeyPair.from_words(seed)
        assert False
    except MnemonicError as ex:
        assert ex.args[0] == "Mnemonic seed is too short"


def test_no_seed_checksum():
    """Test if the seed is valid without checksum"""
    try:
        seed = " ".join(["abbey"] * 12)
        KeyPair.from_words(seed)
        assert False
    except MnemonicError as ex:
        assert ex.args[0] == "Last word in Menmonic seed is missing"


def test_invalid_word():
    """Test if the seed is valid with invalid words"""
    try:
        seed = " ".join(["banana"] * 13)
        KeyPair.from_words(seed)
        assert False
    except MnemonicError as ex:
        assert ex.args[0] == "Invalid word `banana` in mnemonic"


def test_invalid_checksum(invalid_checksum):
    """Test if the seed is valid with an invalid checksum"""
    try:
        KeyPair.from_words(invalid_checksum)
        assert False
    except MnemonicError as ex:
        assert (
            ex.args[0]
            == "Your private key could not be verified, please verify the checksum word"
        )


def test_langauge_exist(words):
    """Test what would happen in the user select an invalid language"""
    try:
        KeyPair.from_words(words, language="MoewMoew")
        assert False
    except MnemonicError as ex:
        assert ex.args[0] == "Language not found"


def test_from_enviroment_v3(words, public_key_v3):
    """Test creating KeyPair from enviroment variable with & without prefix"""

    # Test creating pair without prefix
    envs = {"WORDS": words, "VERSION": 3, "LANGUAGE": "english"}
    setattr(os, "environ", envs)
    pair = KeyPair.from_env()
    assert pair._pub == public_key_v3

    # Test with prefix
    envs = {"TEST_WORDS": words, "TEST_VERSION": 3, "TEST_LANGUAGE": "english"}
    setattr(os, "environ", envs)
    pair = KeyPair.from_env(prefix="TEST_")
    assert pair._pub == public_key_v3


def test_from_enviroment_v2(words, public_key_v2):
    """Test creating KeyPair from enviroment variable with & without prefix"""

    # Test creating pair without prefix
    envs = {"WORDS": words, "VERSION": 2, "LANGUAGE": "english"}
    setattr(os, "environ", envs)
    pair = KeyPair.from_env()
    assert pair._pub == public_key_v2

    # Test with prefix
    envs = {"TEST_WORDS": words, "TEST_VERSION": 2, "TEST_LANGUAGE": "english"}
    setattr(os, "environ", envs)
    pair = KeyPair.from_env(prefix="TEST_")
    assert pair._pub == public_key_v2
