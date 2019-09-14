from enum import Enum


class Field(Enum):
    all_commits, all_revisions, all_files, change_actions, check, commit_footers, \
    current_actions, current_commit, current_files, \
    current_revision, detailed_accounts, detailed_labels, \
    download_commands, labels, messages, \
    no_limits,push_certificates, reviewed, reviewer_updates, \
    skip_mergeable, skip_diffstat, submittable, \
    tracking_ids, web_links = range(24)

    def __str__(self):
        return f"{self.name}"
