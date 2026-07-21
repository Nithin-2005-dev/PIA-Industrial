# Adapters Package (The Ears and Eyes)

This package contains the logic for **Adapters**. The system itself does not know what a "GitHub Pull Request" or a "Jira Ticket" is. It only understands its own internal format. Adapters serve as translators.

## `github/` (The GitHub Translator)
- **What it does**: This folder contains the scripts that listen to GitHub. When a developer pushes code, GitHub sends a messy, massive JSON file. The GitHub adapter catches this file, reads it, throws away the junk, and translates it into a perfect, clean "Event" that the rest of the system can understand.
- **Why we need it**: If we ever decide to switch from GitHub to GitLab, we only have to build a new `gitlab/` adapter. The rest of the AI brain doesn't have to change at all.
