import os
import zlib
import json
import math

SEEDSIZE = 16

# Custom exceptions
class MnemonicError(FileNotFoundError):
    pass


def swap_endian_bytes(hex_string):
    if len(hex_string) != 8:
        raise MnemonicError("Invalid input length")
    return hex_string[6:8] + hex_string[4:6] + hex_string[2:4] + hex_string[0:2]


class KeyPair:
    def __init__(self, version: int = 3, language: str = "english"):
        current = os.path.dirname(os.path.abspath(__file__))
        mnemonic_path = os.path.join(current, "languages", f"{language}.json")
        try:
            # Attempt reading the file
            with open(mnemonic_path, "r") as mnemonic_file:
                # Read the json file
                self.language_set = json.load(mnemonic_file)

        # Handle general parsing exceptions
        except FileNotFoundError as e:
            raise MnemonicError("Language not found") from e
        except json.decoder.JSONDecodeError as e:
            raise MnemonicError("Language file could not be decoded") from e

        # Verify if all required keys are in the language file
        if not all(key in self.language_set for key in ("prefix-length", "words")):
            raise MnemonicError("Invalid language file")

        self.prefix_length = self.language_set["prefix-length"]
        self.wordset = self.language_set["words"]
        self.version = version
        self.language = language

    def load_words(self, words):
        self.words = words
        # Self explainatory
        self._verify_memonic()
        self._extract_checksum()
        self._decode_memonic()

    def get_mnemonic(self):
        return " ".join(self.words)

    def _extract_checksum(self):

        # There is only a checksum word when the prefix is longer than 0
        if self.prefix_length > 0:
            self.checksum = self.words.pop()

    def _get_checksum_index(self, wordlist):
        trimmed = ""
        for word in wordlist:
            trimmed += word[: self.prefix_length]

        checksum = zlib.crc32(bytes(trimmed, "ascii"))

        return checksum % len(wordlist)

    def _decode_memonic(self):
        # TODO: check if this works for other languages
        # Prefix length isn't even doing anything

        word_count = len(self.words)
        wordset_length = len(self.wordset)
        output = ""

        for i in range(0, word_count, 3):
            word1 = self.wordset.index(self.words[i])
            word2 = self.wordset.index(self.words[i + 1])
            word3 = self.wordset.index(self.words[i + 2])

            segment = (
                word1
                + wordset_length * ((wordset_length - word1 + word2) % wordset_length)
                + wordset_length
                * wordset_length
                * ((wordset_length - word2 + word3) % wordset_length)
            )
            # This error will occour when you use abbey 13 times in your mnemonic
            if segment % wordset_length != word1:
                raise MnemonicError(
                    "Something went wrong when decoding your private key, please try again"
                )

            # Convert number to hex with a constant length
            segment_hex = ("0" * 8 + hex(segment)[2:])[-8:]

            # Swap endian 4 bytes
            # Append swapped bytes to the output
            output += swap_endian_bytes(segment_hex)

        if self.prefix_length > 0:
            index = self._get_checksum_index(self.words)
            expected_word = self.words[index]
            if expected_word != self.checksum:
                raise MnemonicError(
                    "Your private key could not be verified, please verify the checksum word"
                )

        self._seed32 = output
        return output

    def _encode_memonic(self):
        output = []
        wordset_length = len(self.wordset)
        seed = self._seed32
        seed_length = len(self._seed32)  # probably 32

        for i in range(0, seed_length, 8):
            seed = seed[:i] + swap_endian_bytes(seed[i : i + 8]) + seed[i + 8 :]

        for i in range(0, seed_length, 8):
            section = int(seed[i : i + 8], 16)
            word1 = section % wordset_length
            word2 = (math.floor(section / wordset_length) + word1) % wordset_length
            word3 = (
                math.floor(math.floor(section / wordset_length) / wordset_length)
                + word2
            ) % wordset_length

            output += [self.wordset[word1], self.wordset[word2], self.wordset[word3]]

        if self.prefix_length > 0:
            output.append(output[self._get_checksum_index(output)])

        self.words = output

    def _verify_memonic(self):
        word_count = len(self.words)
        if word_count < 12:
            raise MnemonicError("Mnemonic seed is too short")
        elif (self.prefix_length == 0 and word_count % self.prefix_length != 0) or (
            self.prefix_length > 0 and word_count % self.prefix_length > 1
        ):
            print(word_count % self.prefix_length, word_count)
            raise MnemonicError("Mnemonic seed is too short")
        elif self.prefix_length > 0 and word_count % self.prefix_length == 0:
            raise MnemonicError("Last word in Menmonic seed is missing")

        # Check if all the words of the seed are in the wordset
        for i in range(word_count):
            if not self.words[i] in self.wordset:
                raise MnemonicError(f"Invalid word `{self.words[i]}` in mnemonic")

    @classmethod
    def from_words(cls, words, **kwargs):
        pair = KeyPair(**kwargs)
        pair.load_words(words.split(" "))
        return pair

    @classmethod
    def from_file(cls, path: str = "mnemonic.json", **kwargs):
        pass

    @classmethod
    def from_env(cls, prefix: str = "", **kwargs):
        pass

    @classmethod
    def new_keys(cls, **kwargs):
        pair = KeyPair(**kwargs)
        pair._seed32 = os.urandom(SEEDSIZE).hex()
        pair._encode_memonic()
        return pair
