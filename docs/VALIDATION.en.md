# Validation scope and publication status

[简体中文](VALIDATION.md) | [English](VALIDATION.en.md)

Prepared on 2026-10-25. This is an experimental source adaptation. Public availability does not mean a clean reconstruction has been validated.

## Lightweight checks completed

- Python sources pass AST syntax parsing.
- The runtime patch applies to the exact upstream commit in `upstream.json`. All 15 modified/new files match the SHA-256 values recorded during export.
- The organized tool sources produce shader chain `e09c9cc1f074`, matching the runtime header and the chain used by the existing local game build.
- The unvalidated live GPU profiling experiment is excluded from the published patch.
- On the two original assets already available in the maintainer's private workspace, the FPS-menu edit function produces the same SHA-256 results as the earlier runtime-tested version. The two chunks' BLAKE3 metadata hashes also match. This check did not copy the complete game container, and the test inputs are not included in the repository.
- Without `--build`, the builder returns a plan and does not download, extract, compile or launch the game.
- Publication manifest and text audit: see `release-files.json`; rerun `python scripts/audit_release.py` to check the reviewed file list.

## Existing runtime observations versus this build entry point

The earlier local application ran on an M1 Pro with macOS 26.5.1. Checks covered the initial playable area, Chinese text, audio, save/load and selection/persistence of the original game's 30/60 FPS settings. Keyboard mapping and virtual controller snapshots were also checked. That application was built and updated incrementally using the maintainer's existing workspace.

**Those observations are not a clean-build validation of the newly organized entry point in this repository.** Runtime preparation, build orchestration, applying the FPS patch from user-owned resources and packaging have only received the lightweight checks described above.

## Explicitly unverified

- End-to-end reconstruction from original NSPs and the builder's own keys in a fresh directory to a finished `.app`.
- Fresh upstream download, dependency installation, full compilation, packaging/signing and complete interruption recovery through this entry point.
- Independent reproduction or other Apple Silicon GPU/macOS combinations.
- Complete playthrough, sustained 60 FPS, every DLC feature or physical controller combinations.
- A complete fix for fire/transparent-particle flickering and first-use combat-effects stutter.

The user chose to defer a full reconstruction because of its disk-space requirements. Source packaging and documentation updates do not modify the existing installed application, saves or game resources, and do not rebuild shaders.
