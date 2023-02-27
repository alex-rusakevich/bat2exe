#!/usr/bin/env python3
import sys
import re
from pathlib import Path
from subprocess import call
import os.path
import os
import argparse

file_beginning = """#include<stdlib.h>
#include<stdio.h>

#define ARRAY_LENGTH %ARRAY_LENGTH%

char *bat_lines[ARRAY_LENGTH] = {
"""

file_end = """};

int main(){
    for(int i = 0; i<ARRAY_LENGTH; i++) {
//@echo_off        printf("%s\\n", bat_lines[i]);
        system(bat_lines[i]);
    }
    return 0;
}
"""


def chompnl(str_in: str) -> str:
    return re.sub(r"\n", "", str_in)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input_file",
        metavar="BAT_FILE_PATH",
        type=str,
        nargs=1,
        help=".bat file to compile",
    )
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        metavar="EXE_FILE_PATH",
        help="resulting .exe file path",
    )
    parser.add_argument(
        "-C",
        "--no-c-remove",
        action="store_true",
        help="don't delete .c file with .exe code after exit",
    )
    parser.add_argument(
        "-E",
        "--no-echo",
        action="store_true",
        help="don't print all the commands while running",
    )
    args = parser.parse_args()

    file_in_path = args.input_file[0]
    file_out_path = ""
    if not args.out:
        file_out_path = os.path.splitext(file_in_path)[0] + ".exe"
    else:
        file_out_path = args.out
        if not file_out_path.endswith(".exe"):
            file_out_path += ".exe"

    global file_beginning, file_end

    file_in = open(file_in_path, "r", encoding="utf8")
    c_file_path = os.path.join(
        os.path.dirname(file_out_path), "__" + Path(file_out_path).stem + ".c"
    )
    c_file = open(c_file_path, "w", encoding="utf8")

    commands_as_c_str = ""
    bat_file_size = sum(1 for _ in file_in)
    file_in.seek(0)

    for bat_command in file_in:
        if bat_command.strip() != "":
            bat_command = bat_command.replace("\\", "\\\\").replace('"', '\\"')
            commands_as_c_str += f'    "{chompnl(bat_command)}",\n'
        else:
            bat_file_size -= 1

    file_beginning = file_beginning.replace("%ARRAY_LENGTH%", str(bat_file_size))
    c_file.write(file_beginning)
    c_file.write(commands_as_c_str)

    if not args.no_echo:
        file_end = file_end.replace("//@echo_off", "")

    c_file.write(file_end)

    file_in.close()
    c_file.close()

    call(["gcc", c_file_path, "-o", file_out_path])
    call(["strip", file_out_path])

    if not args.no_c_remove:
        os.remove(c_file_path)


if __name__ == "__main__":
    main()
