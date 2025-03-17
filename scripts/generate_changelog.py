#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Evolution Marine Digital. All rights reserved
#
# Time reports retrieval utility
#
# Author: amesk <alexei.eskenazi@evomarine.ru>
#

import subprocess
import sys
from git import Repo
from datetime import datetime, timezone
from typing import List, Set

# Date from which Semantic Commit Messages filtering is applied (offset-aware in UTC)
SEMANTIC_COMMIT_DATE: datetime = datetime(2025, 3, 15, tzinfo=timezone.utc)

def is_semantic_commit(message: str) -> bool:
    """
    Checks if the commit message follows the Semantic Commit Messages convention.

    Args:
        message (str): The commit message to be checked.

    Returns:
        bool: True if the message follows the convention, False otherwise.
    """
    # Example: "feat(api): add new endpoint"
    parts: List[str] = message.split(":")
    if len(parts) < 2:
        return False
    
    type_scope: str = parts[0].strip()
    type_scope_parts: List[str] = type_scope.split("(")
    
    if len(type_scope_parts) == 1:
        # No scope, only type
        commit_type: str = type_scope_parts[0]
    else:
        # Scope is present
        commit_type: str = type_scope_parts[0]
    
    # List of valid commit types
    valid_types: List[str] = ["feat", "fix", "docs", "style", "refactor", "test", "chore"]
    
    return commit_type in valid_types

def get_git_logs() -> str:
    """
    Retrieves git logs and generates a changelog based on commit messages and tags.

    Returns:
        str: A formatted changelog as a string.
    """
    repo: Repo = Repo(".")
    tags: List = sorted(repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
    changelog: List[str] = []

    commits_set: Set[str] = set()
    commit_index_stored: int = 0
    
    for i, tag in enumerate(tags):
        if tag.name.startswith("versions/"):
            version: str = tag.name.split("/")[1]

            if i < len(tags) - 1:
                # Get commits between the current tag and the next (older) tag
                start_commit = tags[i + 1].commit
                end_commit = tag.commit
                commits = list(repo.iter_commits(rev=f"{start_commit}..{end_commit}"))
            else:
                # For the last (oldest) tag, do not process commits
                commits = []

            changelog.append(f"Version {version}:\n")

            something_added: bool = False

            for commit in commits:
                commit_date: datetime = commit.committed_datetime
                message: str = commit.message.strip()

                if commit_date >= SEMANTIC_COMMIT_DATE:
                    # Filter commits by Semantic Commit Messages
                    if not is_semantic_commit(message):
                        continue

                if message not in commits_set:
                    commits_set.add(message)
                    changelog.append(f"  - {message}\n")
                    something_added = True
                    commit_index_stored = i
                    
            if abs(i - commit_index_stored) > 3:
                commits_set = set()

            if something_added:
                changelog.append("\n")
            else:
                changelog.pop()
                
    return "".join(changelog)

def write_changelog(file: str, changelog: str) -> None:
    """
    Writes the generated changelog to a file.

    Args:
        file (str): The path to the file where the changelog will be written.
        changelog (str): The changelog content to be written to the file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(changelog)

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "Changelog.txt"
    changelog: str = get_git_logs()
    write_changelog(filename,changelog)
