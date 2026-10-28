import logging


def log(text, level=logging.INFO):
    print(f"{logging.getLevelName(level)} => {text}")
