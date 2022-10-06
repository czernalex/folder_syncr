import argparse
import os
import time
import datetime

from dotenv import load_dotenv

from src.utils import (
    log,
    sync_folders,
    get_dst_folder_state
)
from src.config import (
    SOURCE_REPLICA_FOLDERS_ERR,
    SYNC_COMPLETED
)


def get_parsed_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simple CLI tool to periodically synchronize src folder into dst folder",
        epilog="<> by Alexandr Czerny, https://czernalex.github.io"
    )
    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        default=False,
        help="Don't provide verbose output"
    )
    parser.add_argument(
        "src_folder",
        help="Path to the source folder"
    )
    parser.add_argument(
        "dst_folder",
        help="Path to the replica folder, must be different from src_folder"
    )
    parser.add_argument(
        "log_file",
        help="Path to the log file"
    )
    parser.add_argument(
        "sync_interval",
        type=int,
        help="Time interval between each folders synchronizations in seconds"
    )
    return parser.parse_args()


if __name__ == "__main__":
    load_dotenv()
    args = get_parsed_args()
    with open(args.log_file, mode="w", encoding="utf-8") as log_file:
        if args.src_folder == args.dst_folder:
            log(
                SOURCE_REPLICA_FOLDERS_ERR,
                log_file,
                {
                    "C": os.getenv("RED", "").encode("utf-8").decode("unicode-escape"),
                    "NC": os.getenv("NC", "").encode("utf-8").decode("unicode-escape"),
                },
                args.silent
            )
            exit()
        while True:
            sync_start = datetime.datetime.now()
            f_u, f_c, f_r, d_c, d_r = sync_folders(
                args.src_folder,
                args.dst_folder,
                log_file,
                get_dst_folder_state(args.dst_folder, log_file, args.silent),
                args.silent
            )
            sync_end = datetime.datetime.now()
            log(
                SYNC_COMPLETED,
                log_file,
                {
                    "C1": os.getenv("GREEN", "").encode("utf-8").decode("unicode-escape"),
                    "NC1": os.getenv("NC", "").encode("utf-8").decode("unicode-escape"),
                    "C2": os.getenv("BLUE", "").encode("utf-8").decode("unicode-escape"),
                    "NC2": os.getenv("NC", "").encode("utf-8").decode("unicode-escape"),
                    "src": args.src_folder,
                    "dst": args.dst_folder,
                    "f_u": f_u,
                    "f_c": f_c,
                    "f_r": f_r,
                    "d_c": d_c,
                    "d_r": d_r,
                    "delta": int((sync_end - sync_start).total_seconds() * 1000),
                    "interval": args.sync_interval
                },
                args.silent
            )
            time.sleep(args.sync_interval)
