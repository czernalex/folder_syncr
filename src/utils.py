import os
import pathlib
import hashlib
import shutil
import typing
import copy

from .config import (
    SOURCE_FOLDER_NOT_EXISTS,
    SOURCE_FOLDER_EMPTY,
    SOURCE_FOLDER_CREATED,
    REPLICA_FOLDER_CREATED,
    FILE_CREATED,
    FILE_UPDATED,
    FILE_REMOVED,
    SUBDIR_CREATED,
    SUBDIR_REMOVED
)


def get_file_hash(path: pathlib.Path) -> str:
    """
        Returns the string digest of provided file. It contains hexadecimal characters only.
        Input file is read by chunks in case it would not fit in memory because of its size.
            Parameters:
                path (pathlib.Path): Input file.
            Returns:
                hash_function.hexdigest() (str): Hexadecimal string containing file digest.
    """
    hash_function = hashlib.sha1()
    with open(path, "rb") as file:
        chunk = 0
        while chunk != b"":
            chunk = file.read(1024)
            hash_function.update(chunk)
    return hash_function.hexdigest()


def log(log_str: str, log_file: typing.TextIO, formatters: dict, silent: bool = False) -> None:
    """
        This function handles logging completed operations in provided Log file and to standard output.
        Parameters:
            log_str (str): Completed operation to log.
            log_file (typing.TextIO): Log file.
            formatters (dict): Parameters to insert in prepared log_str.
            silent (bool): Whether to provide verbose log in standard output.
    """
    log_file_formatters = copy.deepcopy(formatters)
    if "C" in log_file_formatters:
        log_file_formatters["C"] = ""
    if "C1" in log_file_formatters:
        log_file_formatters["C1"] = ""
    if "C2" in log_file_formatters:
        log_file_formatters["C2"] = ""
    if "NC" in log_file_formatters:
        log_file_formatters["NC"] = ""
    if "NC1" in log_file_formatters:
        log_file_formatters["NC1"] = ""
    if "NC2" in log_file_formatters:
        log_file_formatters["NC2"] = ""
    log_file.write(log_str.format(
        **log_file_formatters
    ))
    if not silent:
        print(log_str.format(
            **formatters
        ), end="")


def get_dst_folder_state(path: str, log_file: typing.TextIO, silent: bool = False) -> dict:
    """
        This function is called before every synchronization. It iterates over files in replica folder
        and creates simple dictionary with file informations necessary for successfull synchronization.
            Parameters:
                path (str): Path to the replica folder.
                log_file (typing.TextIO): File to log operations in.
                silent (bool): Whether to provide verbose output.
            Returns:
                state (dict): Object containing necessary information abou replica folder files.
    """
    dst_folder = pathlib.Path(path)
    state = dict()
    if not dst_folder.is_dir():
        dst_folder.mkdir(parents=True, exist_ok=True)
        log(
            REPLICA_FOLDER_CREATED,
            log_file,
            {
                "C": os.getenv("BLUE", "").encode("utf-8").decode("unicode_escape"),
                "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
                "dir": path
            },
            silent
        )
        return state
    for file in dst_folder.rglob("*"):
        filename = str(file)[len(str(dst_folder)):]
        if file.is_file():
            state[filename] = {
                "type": "file",
                "checked": False,
                "hash": get_file_hash(file)
            }
        elif file.is_dir():
            state[filename] = {
                "type": "dir",
                "checked": False
            }
    return state


def create_update_file(
    src_file: str,
    dst_file: str,
    log_file: typing.TextIO,
    silent: bool = False,
    create: bool = True
    ) -> None:
    """
        Creates or updates file in replica folder.
        Parameters:
                dst_file (str): Path to the file to create or update.
                log_file (typing.TextIO): Log file.
                silent (bool): Whether to provide verbose output.
    """
    shutil.copy2(
        src_file,
        dst_file,
        follow_symlinks=True
    )
    log(
        FILE_CREATED if create else FILE_UPDATED,
        log_file,
        {
            "C": os.getenv("BLUE", "").encode("utf-8").decode("unicode_escape"),
            "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
            "file": dst_file.split("/")[-1],
            "dir": "/".join(dst_file.split("/")[:-1])
        },
        silent
    )


def create_dir(dst_path: str, log_file: typing.TextIO, silent: bool = False) -> None:
    """
        Creates sub directory in replica folder.
        Parameters:
                dst_path (str): Path to the dir to create.
                log_file (typing.TextIO): Log file.
                silent (bool): Whether to provide verbose output.
    """
    pathlib.Path(dst_path).mkdir(parents=True, exist_ok=True)
    log(
        SUBDIR_CREATED,
        log_file,
        {
            "C": os.getenv("BLUE", "").encode("utf-8").decode("unicode_escape"),
            "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
            "file": dst_path.split("/")[-1],
            "dir": "/".join(dst_path.split("/")[:-1])
        },
        silent
    )


def remove_file(dst_file: str, log_file: typing.TextIO, silent: bool = False) -> None:
    """
        Removes file from replica folder, if it no longer exists in source folder.
            Parameters:
                dst_file (str): Path to the file to remove.
                log_file (typing.TextIO): Log file.
                silent (bool): Whether to provide verbose output.
    """
    pathlib.Path(dst_file).unlink(missing_ok=True)
    log(
        FILE_REMOVED,
        log_file,
        {
            "C": os.getenv("BLUE", "").encode("utf-8").decode("unicode_escape"),
            "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
            "file": dst_file.split("/")[-1],
            "dir": "/".join(dst_file.split("/")[:-1])
        },
        silent
    )


def remove_dir(dst_path: str, log_file: typing.TextIO, silent: bool = False) -> None:
    """
        Removes sub directory from replica folder, if it no longer exists in source folder.
            Parameters:
                dst_path (str): Path to the dir to remove.
                log_file (typing.TextIO): Log file.
                silent (bool): Whether to provide verbose output.
    """
    shutil.rmtree(dst_path, ignore_errors=True)
    log(
        SUBDIR_REMOVED,
        log_file,
        {
            "C": os.getenv("BLUE", "").encode("utf-8").decode("unicode_escape"),
            "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
            "file": dst_path.split("/")[-1],
            "dir": "/".join(dst_path.split("/")[:-1])
        },
        silent
    )


def sync_folders(
        src_path: str,
        dst_path: str,
        log_file: typing.TextIO,
        dst_folder_state: dict,
        silent: bool = False
    ) -> None:
    """
        Core function that handles synchronization between source and replica folders.
            Parameters:
                src_path (str): Path to the source folder.
                dst_path (str): Path to the replica folder.
                log_file (typing.TextIO): File to log operations in.
                dst_folder_state (dict): State of the replica folder.
                silent (bool): Whether to provide verbose output.
            Returns:
                (tuple): Stats numbers.
    """
    src_folder = pathlib.Path(src_path)
    dst_folder = pathlib.Path(dst_path)
    f_updated = 0
    f_created = 0
    f_removed = 0
    d_created = 0
    d_removed = 0
    filename = ""
    if not src_folder.is_dir():
        log (
            SOURCE_FOLDER_NOT_EXISTS,
            log_file,
            {
                "C": os.getenv("YELLOW", "").encode("utf-8").decode("unicode_escape"),
                "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
                "dir": src_path
            },
            silent
        )
        src_folder.mkdir(parents=True, exist_ok=True)
        log (
            SOURCE_FOLDER_CREATED,
            log_file,
            {
                "C": os.getenv("BLUE", "").encode("utf-8").decode("unicode_escape"),
                "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
                "dir": src_path
            },
            silent
        )
    elif not any(src_folder.iterdir()):
        log(
            SOURCE_FOLDER_EMPTY,
            log_file,
            {
                "C": os.getenv("YELLOW", "").encode("utf-8").decode("unicode_escape"),
                "NC": os.getenv("NC", "").encode("utf-8").decode("unicode_escape"),
                "dir": src_path
            },
            silent
        )
    else:
        for src_file in src_folder.rglob("*"):
            filename = str(src_file)[len(str(src_folder)):]
            if filename in dst_folder_state:
                if src_file.is_file():
                    if get_file_hash(src_file) != dst_folder_state.get(filename, {}).get("hash", ""):
                        create_update_file(
                            str(src_file),
                            str(dst_folder) + filename,
                            log_file,
                            silent,
                            False
                        )
                        f_updated += 1
                dst_folder_state[filename]["checked"] = True
            else:
                if src_file.is_file():
                    parent_dir = pathlib.Path("/".join((str(dst_folder) + filename).split("/")[:-1]))
                    if not parent_dir.is_dir():
                        create_dir(
                            str(parent_dir),
                            log_file,
                            silent
                        )
                    create_update_file(
                        str(src_file),
                        str(dst_folder) + filename,
                        log_file,
                        silent
                    )
                    f_created += 1
                elif src_file.is_dir():
                    create_dir(
                        str(dst_folder) + filename,
                        log_file,
                        silent
                    )
                    d_created += 1
    for dst_file in dst_folder_state:
        if not dst_folder_state.get(dst_file, {}).get("checked", True):
            if filename is None:
                filename = dst_file
            if dst_folder_state.get(dst_file, {}).get("type", "") == "file":
                remove_file(
                    str(dst_folder) + dst_file,
                    log_file,
                    silent
                )
                f_removed += 1
            elif dst_folder_state[dst_file]["type"] == "dir":
                shutil.rmtree(str(dst_folder) + dst_file, ignore_errors=True)
                remove_dir(
                    str(dst_folder) + dst_file,
                    log_file,
                    silent
                )
                d_removed += 1
    return f_updated, f_created, f_removed, d_created, d_removed
