"""
@file:   main.py
@brief:  A program that automatically claims free video games from select web-stores.
@author: Yonatan-Schrift
"""
import os
from dotenv import load_dotenv
from sites.epic_games import epic_games







def main():
    load_dotenv(override=True, dotenv_path="./user.env")

    epic_games(os.getenv("EG_EMAIL"), os.getenv("EG_PASSWORD"))

    return 0


if __name__ == '__main__':
    main()
