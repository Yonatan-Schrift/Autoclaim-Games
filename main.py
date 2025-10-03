"""
@file:   main.py
@module: main
@brief:  A program that automatically claims free video games from select web-stores.
@author: Yonatan-Schrift
"""
import os
import sys
import textwrap

from dotenv import load_dotenv
from sites.epic_games import epic_games
from sites.prime_gaming import prime_gaming


def main():
    load_dotenv(override=True, dotenv_path="./user.env")
    args = sys.argv[1:]
    status = 0

    if len(args) == 0:
        print_help()
        return 0

    status = run(args)

    return status


def run(args):
    status = 0
    headless = os.getenv("HEADLESS", "False").lower() in ("1", "true", "yes", "on")
    for arg in args:
        match arg:
            case '-h' | '--help':
                print_help()
                return 0
            case '-eg' | '--epic-games':
                status |= epic_games(os.getenv("EG_EMAIL"), os.getenv("EG_PASSWORD"), headless)
            case '-pg' | '--prime-games':
                # status |= prime_gaming(os.getenv("PG_EMAIL"), os.getenv("PG_PASSWORD"), headless)
                print("Prime Gaming support is not yet implemented.")
            case '-gog' | '--gog':
                print("GOG support is not yet implemented.")
            case '-a' | '--all':
                status |= epic_games(os.getenv("EG_EMAIL"), os.getenv("EG_PASSWORD"), headless)
                #status |= prime_gaming(os.getenv("PG_EMAIL"), os.getenv("PG_PASSWORD"), headless)
                print("Prime Gaming support is not yet implemented.")
            case _:
                print(f"Unknown argument: {arg}")
                return 1
    return status


def print_help():
    print(textwrap.dedent("""
        Usage: python main.py [options]
        Options:
            -h, --help     Show this help message and exit
            -eg, --epic-games  Claim free games from Epic Games Store
            -pg, --prime-games Claim free games from Prime Gaming (not yet implemented)
            -gog, --gog    Claim free games from GOG (not yet implemented)
            -a, --all      Claim free games from all supported stores
    """))


if __name__ == '__main__':
    main()
