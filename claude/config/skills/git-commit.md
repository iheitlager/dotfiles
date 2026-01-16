# Git Commit as Claude

When committing code, use Claude as the author so contributions are properly attributed.

## Commit Command

```bash
git commit --author="Claude <noreply@anthropic.com>" -m "$(cat <<'EOF'
Commit message here.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

## For Existing Commits

To amend the last commit to change the author:

```bash
git commit --amend --author="Claude <noreply@anthropic.com>" --no-edit
```

If already pushed, force push is required:

```bash
git push --force-with-lease
```

## Notes

- The `--author` flag sets who wrote the code
- The committer (from git config) is preserved separately
- Use `--force-with-lease` instead of `--force` for safer force pushes
