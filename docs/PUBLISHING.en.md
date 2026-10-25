# Publication checklist

[简体中文](PUBLISHING.md) | [English](PUBLISHING.en.md)

1. Use only this source directory as the Git repository. Do not include its parent workspace, a private build directory or a generated application.
2. Run `python scripts/audit_release.py`. After manually reviewing source changes, run `python scripts/audit_release.py --seal` to update the manifest and inspect its diff. Sealing alone does not establish copyright clearance or credential safety.
3. Choose a repository name and public/private visibility for your own GitHub account. Publish to your own repository; the upstream URL in `upstream.json` is not your publication destination.
4. Initialize Git, review status and staged diffs, then commit and push. `.gitignore` is an aid, not a substitute for checking already tracked or staged files.
5. Describe the project as experimental: the existing M1 Pro local build runs, while the newly organized build entry point has not been validated end to end. Do not describe local runtime observations as independent hardware verification or a verified one-command build.
6. Publish the source directory, not an `.app`, NSP, key, extracted game file, shader binary or game resource. Users generate those privately on their own computers.

The public repository contains source only; no application or resource package containing the game is published.
