Clean up merged git branches (both local and remote).

Steps:
1. Fetch and prune remote tracking branches: `git fetch --prune`
2. List merged local branches (excluding main/master): `git branch --merged | grep -vE '^\*|main|master'`
3. List merged remote branches: `git branch -r --merged origin/main | grep -v 'main\|master\|HEAD'`
4. Show the branches that would be deleted and ask for confirmation
5. Delete local merged branches: `git branch -d <branch>`
6. Delete remote merged branches: `git push origin --delete <branch>`

Be careful not to delete:
- The current branch
- main, master, or develop branches
- Any branch with uncommitted work

Show a summary of what was cleaned up.
