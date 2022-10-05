# Folder Syncr
The task was to create simple CLI tool that periodically synchronizes two folders, `source` and `replica`. The tool should maintain a full, identical copy of source folder at replica folder.

## Prerequisites
- [python 3](https://www.python.org/downloads/)

## Installation
Open your terminal and run following commands in given order.
```
$ git clone git@github.com:czernalex/folder_syncr.git
$ cd folder_syncr
$ python3 -m venv venv
$ source venv/bin/activate
```

## Usage
After successfully cloning repository and creating virtual env:
```
(venv) $ python main.py path_to_source_folder path_to_replica_folder path_to_log_file sync_interval_in_seconds
```