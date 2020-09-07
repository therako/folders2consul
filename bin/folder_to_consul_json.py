#!/usr/bin/env python3
"""Can read and emit consul kv export JSON files as well
as mapping them into a directory structure on disk.

The intended use case is to make it easy to store configs in unique
keys in a Git repository but also bulk load into Consul.

Nice to haves:
    - Diff between two configs
    - Highlight removed keys and force a removal
"""
import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Union

import attr


class Value:
    value: str
    flags: int

    def __init__(self, value: str, flags: int = 0):
        self.value = str(value).rstrip()
        self.flags = flags


def _strip_file_extension(f: str) -> str:
    return f.split(".", maxsplit=1)[0]


class Config:
    keys: Dict[str, Value]

    def __init__(self, keys: Dict[str, Value] = dict()):
        self.keys = keys

    def __setitem__(self, key: str, value: Value) -> None:
        self.keys[key] = value

    def __getitem__(self, key: str) -> Value:
        return self.keys[key]

    @classmethod
    def from_folders(cls, path: Union[str, Path]) -> "Config":
        """Maps each file in a folder structure to the config"""
        config = cls()
        for x in os.walk(path, False):
            directory, _, files = x
            if not files:
                continue
            basename = directory.replace(str(path), "").lstrip("/")
            for f in files:
                f = _strip_file_extension(f)
                with open(f"{directory}/{f}") as fh:
                    config[f"{basename}/{f}"] = Value(fh.read())

        return config

    def to_folders(self, path: Union[str, Path]) -> None:
        """Writes the values into a folder structure at `path`"""
        if isinstance(path, str):
            path = Path(path)

        for k, v in self.keys.items():
            f = path / k
            f.parent.mkdir(0o755, parents=True, exist_ok=True)
            f.write_text(v.value)

    @classmethod
    def from_file(cls, file: Union[Path, str]) -> "Config":
        """Reads a consul kv export json file"""
        config = cls()
        with open(file) as f:
            for k in json.load(f):
                config[k["key"]] = Value(base64.b64decode(str(k["value"]).rstrip()).decode("utf-8"), k["flags"])

        return config

    def to_file(self, file: Union[Path, str]) -> None:
        """Exports the current config to the consul kv export json format"""
        values = []
        for k in sorted(self.keys.keys()):
            v = self.keys[k]
            values.append(
                dict(key=k, flags=v.flags, value=base64.b64encode(v.value.encode("utf-8")).decode("ascii"))
            )

        with open(file, "w+") as f:
            f.write(leading_spaces_to_tabs(json.dumps(values, indent=4), indent=4))


def leading_spaces_to_tabs(content: str, indent: int):
    """Converts `indent` leading spaces on each line of `content` into tabs

    Examples:
        >>> leading_spaces_to_tabs("hello\n    there", 2)
        "hello\n\t\tthere"
    """
    return re.sub(r"\n( +)", lambda m: "\n" + "".join(["\t"] * int(len(m.group(1)) / indent)), content)


class Cli:
    @classmethod
    def main(cls):
        parser = argparse.ArgumentParser(
            description="Map configs from consul export JSON files and config directory structure on disk"
        )
        parser.add_argument("command", help="Subcommand to run", choices=["to-folders", "from-folders"])
        args = parser.parse_args(sys.argv[1:2])
        cli = cls()
        getattr(cli, args.command.replace("-", "_"))()

    def to_folders(self) -> None:
        parser = argparse.ArgumentParser(
            description=(
                "Reads values from a consul kv export JSON file and " "writes them out as a folder structure"
            )
        )
        parser.add_argument("file", help="The export JSON file to read values from")
        parser.add_argument("path", help="The path to export the values into")
        args = parser.parse_args(sys.argv[2:])
        Config.from_file(args.file).to_folders(args.path)

    def from_folders(self) -> None:
        parser = argparse.ArgumentParser(
            description="Reads a folder structure and emits a consul kv export JSON file"
        )
        parser.add_argument("path", help="The path to read values from")
        parser.add_argument("file", help="The file to create")
        args = parser.parse_args(sys.argv[2:])
        Config.from_folders(args.path).to_file(args.file)


if __name__ == "__main__":
    Cli.main()
