import pathlib
import hashlib
import shutil
import typing


colors = {
    "RED": "\033[0;31m",
    "GREEN": "\033[0;32m",
    "YELLOW": "\033[0;33m",
    "BLUE": "\033[0;34m",
    "NC": "\033[0m"
}


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
        log_str = ">>> [{}INFO{}]: Created replica {} folder.\n"
        log_file.write(log_str.format(
            "",
            "",
            path
        ))
        if not silent:
            print(log_str.format(
                colors.get("BLUE", ""),
                colors.get("NC", ""),
                path
            ), end="")
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


def sync_folders(
        src_path: str,
        dst_path: str,
        log_file: typing.TextIO,
        dst_folder_state: dict,
        silent: bool = False
    ) -> None:
    """
        Core function that handles synchronization between source and replica folders.
        It iterates over all files in source folder and looks into state structure.
        If the file doesn't exist in replica folder, function creates the file in replica
        folder with the same content. If the file exists in replica folder, but its content was
        modified (digest is different), function updates the file in replica folder. Finally,
        if file no longer exists in source folder but still exists in replica folder, function
        removes it from replica folder.
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
        log_str = ">>> [{}WARNING{}]: Source {} folder does not exist.\n"
        log_file.write(log_str.format(
            "",
            "",
            src_path
        ))
        print(log_str.format(
            colors.get("YELLOW", ""),
            colors.get("NC", ""),
            src_path
        ), end="")
    elif not any(src_folder.iterdir()):
        log_str = ">>> [{}INFO{}]: Source {} folder is empty.\n"
        log_file.write(log_str.format(
            "",
            "",
            src_path
        ))
        print(log_str.format(
            colors.get("BLUE", ""),
            colors.get("NC", ""),
            src_path
        ), end="")
    else:
        for src_file in src_folder.rglob("*"):
            filename = str(src_file)[len(str(src_folder)):]
            if filename in dst_folder_state:
                if src_file.is_file():
                    if get_file_hash(src_file) != dst_folder_state.get(filename, {}).get("hash", ""):
                        shutil.copy2(
                            str(src_file),
                            str(dst_folder) + filename,
                            follow_symlinks=True
                        )
                        f_updated += 1
                        log_str = ">>> [{}INFO{}]: Updated file {} in replica {} folder.\n"
                        log_file.write(log_str.format(
                            "",
                            "",
                            filename[1:],
                            dst_path
                        ))
                        if not silent:
                            print(log_str.format(
                                colors.get("BLUE", ""),
                                colors.get("NC", ""),
                                filename[1:],
                                dst_path
                            ), end="")
                dst_folder_state[filename]["checked"] = True
            else:
                if src_file.is_file():
                    shutil.copy2(
                        str(src_file),
                        str(dst_folder) + filename,
                        follow_symlinks=True
                    )
                    f_created += 1
                    log_str = ">>> [{}INFO{}]: Created new file {} in replica {} folder.\n"
                    log_file.write(log_str.format(
                        "",
                        "",
                        filename[1:],
                        dst_path
                    ))
                    if not silent:
                        print(log_str.format(
                            colors.get("BLUE", ""),
                            colors.get("NC", ""),
                            filename[1:],
                            dst_path
                        ), end="")
                elif src_file.is_dir():
                    pathlib.Path(str(dst_folder) + filename).mkdir(parents=True, exist_ok=True)
                    d_created += 1
                    log_str = ">>> [{}INFO{}]: Created new subdirectory {} in replica {} folder.\n"
                    log_file.write(log_str.format(
                        "",
                        "",
                        filename[1:],
                        dst_path
                    ))
                    if not silent:
                        print(log_str.format(
                            colors.get("BLUE", ""),
                            colors.get("NC", ""),
                            filename[1:],
                            dst_path
                        ), end="")
    for dst_file in dst_folder_state:
        if filename is None:
            filename = dst_file
        if not dst_folder_state.get(dst_file, {}).get("checked", True):
            if dst_folder_state.get(dst_file, {}).get("type", "") == "file":
                pathlib.Path(str(dst_folder) + dst_file).unlink(missing_ok=True)
                f_removed += 1
                log_str = ">>> [{}INFO{}]: Removed file {} from replica {} folder.\n"
                log_file.write(log_str.format(
                    "",
                    "",
                    filename[1:],
                    dst_path
                ))
                if not silent:
                    print(log_str.format(
                        colors.get("BLUE", ""),
                        colors.get("NC", ""),
                        filename[1:],
                        dst_path
                    ), end="")
            elif dst_folder_state[dst_file]["type"] == "dir":
                shutil.rmtree(str(dst_folder) + dst_file, ignore_errors=True)
                d_removed += 1
                log_str = ">>> [{}INFO{}]: Removed subdirectory {} from replica {} folder.\n"
                log_file.write(log_str.format(
                    "",
                    "",
                    filename[1:],
                    dst_path
                ))
                if not silent:
                    print(log_str.format(
                        colors.get("BLUE", ""),
                        colors.get("NC", ""),
                        filename[1:],
                        dst_path
                    ), end="")
    return f_updated, f_created, f_removed, d_created, d_removed
