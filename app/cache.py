import json
import os
import shutil
import datetime


class CachedValue:
    def __init__(self, filename: str, folder: str = "data"):
        self.filename = filename
        self._filepath = f"{folder}/{filename}.json"
        self._internal = {}

        if os.path.exists(self._filepath):
            self._update_from_disk()
        else:
            # Create file if it doesn't exist
            os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
            # Write initial value to the file to create it
            self._store_to_disk()

    def _store_to_disk(self):
        with open(self._filepath, "w") as f:
            f.write(json.dumps(self._internal, indent=2))

    def _update_from_disk(self):
        try:
            with open(self._filepath, "r") as df:
                self._internal = json.load(df)
        except Exception as _:
            # Error loading existing file, overwriting with initial value...
            # But store a backup first
            now_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d-%H-%M-%S")
            backup_path = f"backups/{now_str}/{self._filepath}"
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(self._filepath, backup_path)
            self._store_to_disk()

    def read(self):
        return self._internal

    def save(self, action) -> None:
        self._internal = action(self._internal)
        self._store_to_disk()


## To deal with diffs
# When updating server, timestamp it
# Then when a device reconnects to the server
# and has modifications with a more recent timestamp
# and the server hasn't had modifications since
# the device was disconnected
# then we can update the server with the cache directly

# if the server has received modifications since the
# device was last connected, and it has no changes
# update the device

# if both server and device have had modifications.
# allow user to perform the diff
