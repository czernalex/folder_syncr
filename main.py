import argparse
import pathlib
import time
import datetime

from src.utils import (
    colors,
    sync_folders,
    get_dst_folder_state
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
    args = get_parsed_args()
    with open(args.log_file, mode="w", encoding="utf-8") as log_file:
        if args.src_folder == args.dst_folder:
            log_str = ">>> [{}ERROR{}]: Source folder and replica folder must be different.{}"
            log_file.write(log_str.format(
                "","","\n"
            ))
            exit(log_str.format(
                colors.get("RED", ""),
                colors.get("NC", ""),
                ""
            ))
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
            log_str = ">>> [{}SUCCESS{}]: Synchronization from {} folder to {} completed. Took {} ms.\n"
            log_str += ">>> [{}SYNC STATS{}]:\n"
            log_str += "    - Files updated: {}.\n"
            log_str += "    - Files created: {}.\n"
            log_str += "    - Files deleted: {}.\n"
            log_str += "    - Directories created: {}.\n"
            log_str += "    - Directories deleted: {}.\n"
            log_str += ">>> [{}INFO{}]: Next synchronization in aprox. {} seconds.\n\n\n"
            log_file.write(log_str.format(
                "",
                "",
                args.src_folder,
                args.dst_folder,
                int((sync_end - sync_start).total_seconds() * 1000),
                "",
                "",
                f_u,
                f_c,
                f_r,
                d_c,
                d_r,
                "",
                "",
                args.sync_interval
            ))
            if not args.silent:
                print(log_str.format(
                    colors.get("GREEN", ""),
                    colors.get("NC", ""),
                    args.src_folder,
                    args.dst_folder,
                    int((sync_end - sync_start).total_seconds() * 1000),
                    colors.get("BLUE", ""),
                    colors.get("NC", ""),
                    f_u,
                    f_c,
                    f_r,
                    d_c,
                    d_r,
                    colors.get("BLUE", ""),
                    colors.get("NC", ""),
                    args.sync_interval
                ), end="")
            time.sleep(args.sync_interval)
