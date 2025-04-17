from pocketbase import PocketBase
import os

client = PocketBase("https://db.babel-revolution.fr")
PB_EMAIL = os.getenv("POCKETBASE_EMAIL")
PB_PASSWORD = os.getenv("POCKETBASE_PASSWORD")

def main():
    pass


if __name__ == "__main__":
    main()
    