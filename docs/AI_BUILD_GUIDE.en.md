# Building with an AI assistant

[简体中文](AI_BUILD_GUIDE.md) | [English](AI_BUILD_GUIDE.en.md)

**FINAL FANTASY RESONANCE Native macOS** is an experimental source adaptation based on nxnative. It supplies an existing porting approach and build entry point; an assistant does not need to invent a new porting engine.

## What the link provides

An assistant can read the supported version, upstream dependencies, build scripts and known issues, then help inspect the environment, execute commands and troubleshoot failures. A successful build still requires your own game inputs, keys and an execution environment with access to your Apple Silicon Mac's terminal and files. A chat assistant without local execution access can only provide instructions for you to run.

**The existing local port running successfully does not mean the newly organized entry point has been validated from a clean environment.** Keep those claims separate. A build plan or passing static checks is not a completed port.

## Information to provide

| Information | Example or requirement |
| --- | --- |
| Repository | `https://github.com/Kisenshin/final-fantasy-resonance-native-macos` |
| Mac environment | Apple Silicon model, memory and macOS version |
| Base game path | Your own Hong Kong base NSP; title ID `0100B8A026F14000` |
| Update path | Your own Hong Kong 1.0.1 update NSP; title ID `0100B8A026F14800` |
| Key-file path | The local path to `prod.keys` dumped from your own console; do not send its contents |
| Private work directory | Outside the source repository; budget around 100–120 GiB of free space |
| Optional DLC | Your own DLC path and index; the tested starter-pack mount uses index `2` |

Preparing the pinned upstream source requires network access. Dependency installation and .NET package restoration may also need the network. Game module and shader builds run locally. Other game regions and versions are not covered; build ID checks reject mismatched inputs.

## Copyable prompt

Replace the placeholders with actual local paths before giving this to an assistant with local execution access. Do not paste key values.

```text
Please help me build a personal-use macOS application for the Hong Kong
1.0.1 version of FINAL FANTASY RESONANCE on my Apple Silicon Mac using:
https://github.com/Kisenshin/final-fantasy-resonance-native-macos

My environment:
- Mac model / memory: [fill in]
- macOS version: [fill in]
- My own Hong Kong base NSP: [local path]
- My own Hong Kong 1.0.1 update NSP: [local path]
- prod.keys dumped from my console: [local path only]
- Private build directory: [local path outside the source repository]
- Optional owned DLC: [omit if absent; otherwise provide index and path]

Read README.en.md, docs/AI_BUILD_GUIDE.en.md and docs/VALIDATION.en.md first.
This is an experimental source adaptation based on nxnative. The newly
organized entry point has not been clean-build verified end to end;
do not promise one-command success.

Check the system, dependencies and free space. Prepare the pinned nxnative
commit and apply the patch. Inspect build_mac.py's default plan, then run
with --build when the requirements are met.
Keep logs. Investigate version or checksum mismatches instead of bypassing
checks. Keep game inputs, keys, generated game modules, shaders and the
finished app in private directories.
After packaging, verify the signature and --inspect output, then test startup.
Distinguish successful packaging from reaching a playable scene.
Use docs/CONTROLS_AND_FPS.en.md for controller and frame-rate instructions.
```

## Suggested workflow

1. Check dependencies and validation status. A full build can use substantial space; reusing an existing shader cache is not evidence of a clean reconstruction.
2. Clone this adaptation repository. Use `scripts/prepare_runtime.py --destination ...` to prepare the pinned nxnative checkout outside it. Do not substitute the latest upstream commit or another region's profile.
3. In the correct Python environment, inspect `python scripts/build_mac.py`, then supply the real inputs and `--build` as described in the README.
4. Logs stay in the private work directory. Input checks, rewriting, shader compilation, the FPS-menu patch and packaging can each fail; assess actual exit codes and output.
5. Verify the signature, startup and game image. Seeing the title, loading Continue, reaching gameplay and loading a save are separate checks and should be reported separately.
6. For project bug reports, provide the environment, build ID, error and redacted logs. Do not upload keys, game modules, resources or a complete generated app.

See the [English README](../README.en.md) for commands, dependencies and input requirements. Using an assistant does not expand the supported game versions or automatically fix the known particle problems and occasional stutter.
