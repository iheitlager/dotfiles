## Forge: GitLab

- CLI: `glab`. Merge requests: issues are `#N`, MRs are `!N`. Say "MR", not "PR".
- CI: `.gitlab-ci.yml`; check a pipeline with `glab ci status` / `glab ci view`.
- Create: `glab mr create --fill --remove-source-branch`. Merge when green: `glab mr merge` (auto-merge is on by default).
- `Closes #N` in the MR description closes the issue on merge into the default branch.
