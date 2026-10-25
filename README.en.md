# FINAL FANTASY RESONANCE Native macOS

[简体中文](README.md) | [English](README.en.md)

An experimental Apple Silicon macOS adaptation of FINAL FANTASY RESONANCE, based on [nxnative](https://github.com/seedds/nxnative). Supply your own game files and keys dumped from your own console to build a Mac application locally. This repository provides adaptation source, patches, identifier tables and scripts. It does not provide the game or a ready-to-play application.

> **Status: the existing local port has run on an M1 Pro with macOS 26.5.1. The newly organized build entry point has not been validated end to end from a clean environment, and no independent reproduction on another machine has been completed.** This is for testers willing to troubleshoot builds; one-command success and a complete playthrough are not guaranteed.

The language links switch the project documentation. The current launcher still defaults to Simplified Chinese; this update does not add an in-game language selector. Chinese menu labels are included in the English controls guide to help identify the settings.

## Supported scope

- Hong Kong base title ID: `0100B8A026F14000`; update ID: `0100B8A026F14800`.
- Game update: **1.0.1**; `main` build ID: `b7f965b9d7227db8e29f04e84ea7331b`. Other regions and versions are unverified, and the scripts reject mismatched modules.
- Simplified Chinese, audio, windowed/full-screen display, keyboard controls, Xbox and Switch Pro mappings, and device-specific hints.
- **30/60 FPS** selection inside the original game's settings. The 60 FPS mode is experimental.
- Optional owned DLC: mounting the starter pack labelled `見習騎士起步衝刺包`, index `2`, was tested. Claiming the actual rewards was not separately verified.
- The title, opening, initial playable area, basic movement and save loading were tested. Testing does not cover every chapter, battle or feature.

## Known limitations

Some fire/transparent particles still show black flickering or other rendering errors. Combat effects can stutter on first use; the prewarm manifest covers only recorded scenes. Results can vary with macOS, GPU and toolchain versions. Physical controllers need more testing; the mappings have passed virtual snapshot checks.

The published runtime sources come from a snapshot saved before the live GPU profiling experiment. **The unvalidated live GPU profiling changes are excluded.** Disabling a particle material is not shipped as a rendering fix.

## Building with an AI assistant

An AI assistant with access to your Mac's terminal and files can use this repository to follow the process and investigate errors. It still needs your game files, key-file path, Mac environment and sufficient disk space. Sending a link alone does not guarantee a successful port.

[AI build guide and copyable prompt](docs/AI_BUILD_GUIDE.en.md) · [Keyboard, Xbox, Switch Pro and 30/60 FPS instructions](docs/CONTROLS_AND_FPS.en.md)

## Your inputs and dependencies

1. Your own Hong Kong base NSP, 1.0.1 update NSP and `prod.keys` path; optionally your own DLC.
2. An Apple Silicon Mac, native arm64 Python 3.12 or newer, and **macOS 26 or newer**. Only the M1 Pro environment above has a local runtime record.
3. Xcode development tools and the Metal toolchain. Both `xcrun -sdk macosx --find metal` and the corresponding `metallib` lookup must succeed. The build also uses `clang`, `make`, `codesign`, `sips` and `iconutil`.
4. The .NET **10 SDK**, `spirv-cross`, `zstd`, Git and the Python packages below. The scripts do not download or search for decryption keys.
5. Budget approximately **100–120 GiB of free space** for a full reconstruction, preferably on an external APFS SSD. This estimate comes from existing build artifacts; the peak usage of this new entry point has not been measured.

Extraction and patching happen in a private build directory and do not modify the original NSPs. Keep that directory, your keys and the runtime checkout outside this source repository. The resulting `.app` contains your game content and is for your personal use; do not upload it as a GitHub Release for this project.

## Build steps — experimental, not clean-build verified

Create a Python environment and install the dependencies. Replace the example paths with your actual paths. Pass the path to a key file, never key values on the command line.

```sh
git clone https://github.com/Kisenshin/final-fantasy-resonance-native-macos.git
cd final-fantasy-resonance-native-macos
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Prepare the pinned runtime. This downloads a specific nxnative commit and applies the source patch. It does not read game files.

```sh
python scripts/prepare_runtime.py --destination ../ffr-runtime
```

Inspect the build plan first. The default mode does not decrypt, build, download or launch the game.

```sh
python scripts/build_mac.py
```

Add `--build` explicitly to execute the pipeline:

```sh
python scripts/build_mac.py \
  --runtime ../ffr-runtime \
  --base /path/to/owned-base.nsp \
  --update /path/to/owned-update-1.0.1.nsp \
  --keys /path/to/your-own/prod.keys \
  --work /Volumes/BuildSSD/FFR-private-build \
  --jobs 4 \
  --build
```

For your own index-2 DLC, add `--dlc '2=/path/to/owned-dlc.nsp'`. Its title ID is checked against the Hong Kong game and the selected index. Use `--compiler-bin /path/to/metal-tools` to select a local compiler directory if needed; the tools must still pass the `xcrun` checks.

The default output is `最终幻想共鸣.app` in the private build directory. The script packages and ad-hoc signs it locally; it does not install or launch the game, or change system security settings. Signature verification is not Apple notarization. An existing output is not overwritten; use a new `--output /path/to/new-name.app` to retain an earlier build.

## Interruptions and troubleshooting

- Logs are under `logs/` in the private work directory. The input record does not contain key values. Check usernames, paths and personal information before sharing logs.
- Upstream helpers can reuse completed extraction, module rewriting and compatible shader caches. **Complete interruption recovery has not been tested through this entry point.** For changed inputs/dependencies or incomplete extraction, prefer a fresh private work directory and retain the error logs.
- A source/profile mismatch means the runtime or profile no longer matches this release snapshot. Run `prepare_runtime.py` into a fresh directory. Do not bypass build ID or resource checks.
- Metal tools, .NET and graphics APIs come from your local environment. Install missing dependencies as indicated by the errors; disabling SIP or Gatekeeper is not a troubleshooting substitute.
- The FPS-menu patch reads two assets from your extracted IoStore and validates their hashes. No `.uasset` files or modified game containers are provided here.

## Controls and in-game 30/60 FPS

- **Xbox uses letter matching: A confirms, B goes back.** Switch Pro keeps its native layout. See the [detailed guide](docs/CONTROLS_AND_FPS.en.md) for the full table, connection steps and hints.
- The most recently used input device selects the bottom hint bar. **The original game still shows Switch button icons**; use the bottom hints and mapping table to find the corresponding controls. F1 opens the guide; F2 toggles the hint bar.
- FPS path: **System Menu → Options → Display Settings → Frame Rate → 30/60 → Y to Apply → Yes → A to confirm**. On keyboard, Apply is **I**, confirmation is **J/Space**. Applied settings persist across restarts. The title-screen `Option` opens the same settings. See the guide for the corresponding Chinese labels.
- 60 FPS is an experimental target, not a promise of sustained performance. The top `Performance` menu indicates the target; change it in the original game settings.
- Full screen: **Control+Command+F** or the green window button. Saves are under `~/Library/Application Support/FFRNative/0100B8A026F14000/save`. The build tools do not read or package existing saves.

## Repository contents and validation

- `patches/runtime.patch`: runtime source changes against the pinned upstream commit.
- `profile/0100B8A026F14000/`: Hong Kong configuration, build gates, shader identifiers/reflection facts and PSO state descriptions; no shader program bodies.
- `scripts/`: runtime preparation, experimental build orchestration, FPS asset patching and packaging.
- `launcher/`: launcher source and control hints.
- `upstream.json`, `release-files.json`: upstream revision, source hashes and reviewed publication manifest.
- [Validation status](docs/VALIDATION.en.md): lightweight checks and explicitly unverified items.

This repository organizes an existing local adaptation into a source entry point for reproduction attempts. **Source organization and passing static checks do not establish a successful clean build.** For bug reports, include your Mac model, macOS/Xcode/Python/.NET versions, game build ID and redacted logs. Do not upload keys, game modules or game resources.

## License

Local adaptation scripts use MIT. The runtime patch retains nxnative's MIT license and attribution in `LICENSE-nxnative`. See `THIRD_PARTY_NOTICES.md` and the runtime's original notices for dependencies. These licenses do not grant rights to copy or distribute the game itself.
