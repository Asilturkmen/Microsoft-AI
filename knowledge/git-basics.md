# Git Basics

Git is a distributed version-control system. A repository stores snapshots of project files as commits. Each commit records its parent, author information, message, and a reference to the saved tree.

## Branches and merging

A branch is a movable name pointing to a commit. Creating a feature branch allows work to progress without immediately changing the main branch. A merge combines histories; when incompatible edits touch the same area, Git asks the developer to resolve a merge conflict.

## Working safely

`git status` shows working-tree and staging-area changes. `git add` stages selected content, and `git commit` records the staged snapshot. Small focused commits with descriptive messages make review and recovery easier.
