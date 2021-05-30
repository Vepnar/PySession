import os
import json

SEEDSIZE = 16


# Custom exceptions
class MnemonicError(FileNotFoundError):
    pass


class KeyPair:
    def __init__(self, words: list, version: int, language: str = "english"):
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

        # Handle general parsing exceptions
        except FileNotFoundError as e:
            raise MnemonicError("Language not found") from e
        except json.decoder.JSONDecodeError as e:
            raise MnemonicError("Language file could not be decoded") from e

    @classmethod
    def from_words(words, **kwargs):
        pass

    @classmethod
    def from_file(path: str = "mnemonic.json", **kwargs):
        pass

    @classmethod
    def from_env(prefix: str = "", **kwargs):
        pass

    @classmethod
    def new_keys(language: str = "english"):
        pass
