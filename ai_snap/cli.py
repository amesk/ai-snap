#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Alexei Eskenazi. All rights reserved
#
# AI-Snap utility
#
# Author: amesk <alexei.eskenazi@gmail.com>
#

import os
import sys

import click
import chardet
import pyperclip

from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern
from pathlib import Path

from typing import Optional, Any

# Try to retrieve application version from generate version.py file
try:
    from .version import VERSION
except:
    VERSION = "0.0.1"

def read_config_file(file_path:str) -> Optional[PathSpec]:
    """
    Read a configuration file (e.g., .gitignore) and return a PathSpec object.
    """
    spec = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            spec += f.read().splitlines()
    except FileNotFoundError:
            click.echo(click.style(f"Config file not found: {file_path}", fg="red"), err=True)
            sys.exit(1)
    spec += [ '!.ai-snap', '!ai-snap-instruct']
    return PathSpec.from_lines(GitWildMatchPattern, spec)


def get_language_from_extension(file_name:str) -> str:
    """
    Determine the language based on the file extension.
    """
    extension_to_language = {
        ".py": "python",
        ".js": "javascript",
        ".java": "java",
        ".cpp": "cpp",
        ".cxx": "cpp",
        ".cc": "cpp",
        ".c++": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
        ".h++": "cpp",
        ".h": "c",
        ".c": "c",
        ".html": "html",
        ".css": "css",
        ".json": "json",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".sh": "bash",
        ".txt": "text",
        ".xml": "xml",
        ".sql": "sql",
        ".php": "php",
    }
    _, ext = os.path.splitext(file_name)
    return extension_to_language.get(ext, "")


def detect_file_encoding(file_path:str) -> str:
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    return chardet.detect(raw_data)['encoding']


def read_file_with_autoencoding(file_path:str) -> str:
    try:
        with open(file_path, 'r', encoding=detect_file_encoding(file_path)) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def make_project_snapshot(root_path:str, config_spec:Optional[PathSpec], instructions:Optional[str],
                          footer:Optional[str]) -> str:
    """
    Save the project structure and contents of all files in the project to a text file,
    considering rules from the config file.
    """
    project_structure = []
    file_contents = []

    for root, dirs, files in os.walk(root_path):
        for file in files:
            rel_dir = os.path.relpath(root, root_path)
            rel_file = Path(os.path.join(rel_dir, file)).as_posix()

            if config_spec and not config_spec.match_file(Path(rel_file).as_posix()):
                continue

            project_structure.append(rel_file)

            try:
                content = read_file_with_autoencoding(os.path.join(root, file))
                language = get_language_from_extension(file)
                file_contents.append(f"{rel_file}:\n```{language}\n{content}\n```\n")
            except Exception as e:
                file_contents.append(f"{rel_file}:\n```text\nError reading file: {e}\n```\n")

    # Since we're going to make a snapshot for AI chat, we can't get large amount of data,
    # so we may create it im
    output = ""

    # Add instructions to the beginning of the file if provided as an argument
    if instructions:
        output = instructions + "\n\n"

    # Write out project structure and file contents
    output += "Project Structure:\n"
    output += "\n - ".join(project_structure) + "\n\n"
    output += "File Contents:\n"
    output += "\n".join(file_contents)

    if footer:
        output += "\n\n" + footer

    return output


CLI_HELP_EPILOG = """
\b
See more at https://github.com/ai-snap/ai-snap
"""

@click.group(name="ai-snap", invoke_without_command=True, epilog=CLI_HELP_EPILOG)
@click.version_option(VERSION, prog_name="ai-snap")
@click.option("--instruct", type=click.Path(exists=True),
              help="Path to the instruction file to include at the beginning")
@click.option("--instruct-footer", "instruct_footer", type=click.Path(exists=True),
              help="Path to the footer instruction file that follows the file contents")
@click.option("-c", "--config-file", type=click.Path(exists=True),
              help="Path to the config file (e.g., .gitignore-like file containing patterns)")
@click.option("-p", "--clipboard", is_flag=True,
              help="Copy the output to the clipboard")
@click.option("-o", "--output", type=click.Path(exists=False), default="-",
                help="Output file path (default: stdout)")

def cli(instruct:str, instruct_footer:str, config_file:str, output:str, clipboard:bool) -> None:
    """
    Save project structure and file contents, considering rules from the config file.
    """
    if clipboard and output != "-":
        click.echo(
            click.style(f"Error: --clipboard and --output are mutually exclusive", fg="red"), err=True)
        sys.exit(1)
    
    default_config_file = '.ai-snap'
    default_instruct_file = '.ai-snap-instructions'
    default_instruct_footer_file = '.ai-snap-instructions-footer'

    # Используем указанный config-file или default_ignore_file, если он существует
    if config_file:
        config_spec = read_config_file(config_file)
    elif os.path.exists(default_config_file):
        config_spec = read_config_file(default_config_file)
    else:
        config_spec = None

    instructions_text = None

    if not instruct and os.path.exists(default_instruct_file):
        instruct = default_instruct_file
        
    if instruct:
        instructions_text = read_file_with_autoencoding(instruct)

    footer_text = None

    if not instruct_footer and os.path.exists(default_instruct_footer_file):
        instruct_footer = default_instruct_footer_file
        
    if instruct_footer:
        footer_text = read_file_with_autoencoding(instruct_footer)

    text = make_project_snapshot(".", config_spec, instructions_text, footer_text)

    if clipboard:
        pyperclip.copy(text)
    else:
        if output == "-":
            click.echo(text)
        else:
            with open(output, "w", encoding="utf-8") as f:
                f.write(text)


if __name__ == "__main__" and not os.environ.get("_AI_SNAP_CLI_COMPLETE", "").endswith("source"):
   cli()
