import time
from castle_manager import CastleManager
from database import init_db


def main():
    init_db()
    start_time = time.time()
    manager = CastleManager(
        "https://www.bulgariancastles.com/category/severozapadna-b-ya/"
    )
    castles = manager.get_all_castles()

    print(f"\nTotal castles processed: {len(castles)}")

    print(f"\nExecution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()

#