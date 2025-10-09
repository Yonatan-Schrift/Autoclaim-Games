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

from core.utils import env_to_bool
from sites.epic_games import EpicGames
from sites.prime_gaming import PrimeGaming
# from sites.gog import gog

def main():
    load_dotenv(override=True, dotenv_path="./user.env")
    args = sys.argv[1:]

    if len(args) == 0:
        print_help()
        return 0

    status = run(args)

    return status


def run(args):
    status = 0
    headless = env_to_bool("HEADLESS", False)
    for arg in args:
        match arg:
            case '-h' | '--help':
                print_help()
                return 0
            case '-eg' | '--epic-games':
                status |= EpicGames.run(os.getenv("EG_EMAIL"), os.getenv("EG_PASSWORD"), headless)
            case '-pg' | '--prime-games':
                print("Prime Gaming is experimental and may not work as expected.")
                status |= PrimeGaming.run(os.getenv("PG_EMAIL"), os.getenv("PG_PASSWORD"), headless)
            case '-g' | '--gog':
                # status |= gog(os.getenv("GOG_EMAIL"), os.getenv("GOG_PASSWORD"), headless)
                print("GOG support is not yet implemented.")
            case '-a' | '--all':
                status |= EpicGames.run(os.getenv("EG_EMAIL"), os.getenv("EG_PASSWORD"), headless)
                status |= PrimeGaming.run(os.getenv("PG_EMAIL"), os.getenv("PG_PASSWORD"), headless)
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
            -pg, --prime-games Claim free games from Prime Gaming (Working but not tested thoroughly)
            -g, --gog    Claim free games from GOG (not yet implemented)
            -a, --all      Claim free games from all supported stores
    """))


if __name__ == '__main__':
    main()
