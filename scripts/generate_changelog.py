#
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Alexei Eskenazi. All rights reserved
#
# AI-Snap utility
#
# Author: amesk <alexei.eskenazi@gmail.com>
#

import subprocess
from git import Repo

def get_git_logs():
    repo = Repo(".")
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime, reverse=True)
    changelog = []

    commits_set = set()
    commit_index_stored = 0
    
    for i, tag in enumerate(tags):
        if tag.name.startswith("versions/"):
            version = tag.name.split("/")[1]

            if i < len(tags) - 1:
                # Берём коммиты между текущим тегом и следующим (более старым)
                start_commit = tags[i + 1].commit
                end_commit = tag.commit
                commits = list(repo.iter_commits(rev=f"{start_commit}..{end_commit}"))
            else:
                # Для последнего тега (самого старого) не обрабатываем коммиты
                commits = []

            changelog.append(f"Version {version}:\n")

            something_added = False

            for commit in commits:
                if commit.message not in commits_set:
                    commits_set.add(commit.message)
                    changelog.append(f"  - {commit.message.strip()}\n")
                    something_added = True
                    commit_index_stored = i
                    
            if abs(i - commit_index_stored) > 3:
                commits_set = set()

            if something_added:
                changelog.append("\n")
            else:
                changelog.pop()
                
            

    return "".join(changelog)

def write_changelog(changelog):
    with open("dist/Changelog.txt", "w") as f:
        f.write(changelog)

if __name__ == "__main__":
    changelog = get_git_logs()
    write_changelog(changelog)