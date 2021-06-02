import os
import json

SEEDSIZE = 16

# Custom exceptions
class MnemonicError(FileNotFoundError):
    pass


class KeyPair:
    def __init__(self, words: list, version: int = 3, language: str = "english"):
        self.words = words
        current = os.path.dirname(os.path.abspath(__file__))
        mnemonic_path = os.path.join(current, "languages", f"{language}.json")
        try:
            # Attempt reading the file
            with open(mnemonic_path, "r") as mnemonic_file:
                mnemonic_data = mnemonic_file.read()

            # Read the json file
            self.wordset = json.loads(mnemonic_data)

            # Verify if all required keys are in the language file
            if not all(key in self.wordset for key in ("prefix-length", "words")):
                raise MnemonicError("Invalid language file")

            self._verify_memonic()

        # Handle general parsing exceptions
        except FileNotFoundError as e:
            raise MnemonicError("Language not found") from e
        except json.decoder.JSONDecodeError as e:
            raise MnemonicError("Language file could not be decoded") from e

    def _decode_memonic(self):
        # TODO: check if this works for other languages
        # Prefix length isn't even doing anything

        word_count = len(self.words)
        prefix_length = self.wordset["prefix-length"]
        wordset = self.wordset["words"]
        wordset_length = len(wordset)
        checksum = ""
        output =""

        # Not a pure function
        if prefix_length > 0:
            self.checksum = self.words.pop()

        for i in range(0, word_count, 3):
            word1 = wordset.index(self.words[i])
            word2 = wordset.index(self.words[i + 1])
            word3 = wordset.index(self.words[i + 2])

            x = (
                word1
                + word_count * ((word_count - word1 + word2) % word_count)
                + word_count
                * word_count
                * word_count
                * ((word_count - word2 + word3) % word_count)
            )

            # This error will occour when you use abbey 13 times in your mnemonic
            if x % word_count != word1:
                raise MnemonicError("Something went wrong when decoding your private key, please try again")
            
            # TODO swap endian 4byte

    def _swap_endian_4byte(self, string):
        if len(string) != 8:
            raise MnemonicError(f"Invalid input length {len(string)}")

        return string[6:2] + string[4:2] + string[2:4] + string [0:2]

    def _verify_memonic(self):
        # TODO finish
        # TODO: check if this works for other languages
        word_count = len(self.words)
        prefix_length = self.wordset["prefix-length"]
        if word_count < 12:
            raise MnemonicError("Mnemonic seed is too short")
        elif (prefix_length == 0 and word_count % 3 != 0 or prefix_length > 0) and (
            prefix_length > 0 and word_count % 3 == 2
        ):
            raise MnemonicError("Mnemonic seed is too short")
        elif prefix_length > 0 and word_count % 3 == 0:
            raise MnemonicError("Last word in Menmonic seed is missing")

        # Check if all the words of the seed are in the wordset
        for i in range(word_count):
            if not self.words[i] in self.wordset["words"]:
                raise MnemonicError(f"Invalid word `{self.words[i]}` in mnemonic")

    @classmethod
    def from_words(cls, words, **kwargs):
        return KeyPair(words)

    @classmethod
    def from_file(path: str = "mnemonic.json", **kwargs):
        pass

    @classmethod
    def from_env(prefix: str = "", **kwargs):
        pass

    @classmethod
    def new_keys(language: str = "english"):
        pass
