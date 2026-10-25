# Third-party notices

This repository is a source overlay for [seedds/nxnative](https://github.com/seedds/nxnative), pinned to commit `86d9ba123967cfe520e556e882dcd4e0ef7ba272` in `upstream.json`.

The runtime patch contains modifications and context from nxnative. Its MIT license and original copyright notice are retained in `LICENSE-nxnative`. FPS asset reader and unkeyed BLAKE3 helper were written for this port; `LICENSE` covers the local scripts and adaptations, subject to the upstream notices for derived code.

The runtime checkout fetched by `prepare_runtime.py` includes its own dependency sources, notices and licenses. Retain them when redistributing source or tools. They include Ryujinx's shader translator projects (MIT), libvpx (BSD, with a patent grant), stb_vorbis (MIT/public domain), Vulkan-Headers (MIT/Apache-2.0), NVIDIA FLIP (BSD), and the runtime's documented deko3d and MacNativeGames adaptations. Consult that pinned checkout's `dm/third_party/README.md` and each component's license for the exact scope. .NET/LibHac, Python packages, SPIRV-Cross, Xcode and Apple's Metal tools have their own licenses and are obtained separately by the builder.

No Nintendo or Square Enix game program, recompiled game module, graphics, audio, text, font, compiled or translated shader, game icon, DLC payload, firmware or decryption key is supplied here. The profile tables contain identifiers, bindings, format facts and patch addresses; they do not contain executable shader bodies. The PSO manifest describes pipeline states only. Build tools regenerate game-derived files locally from the builder's own inputs.

The game title and controller names identify compatibility. This project is independent and is not affiliated with or endorsed by the game or platform rights holders. The MIT license applies to the supplied adaptation code, not to the game or third-party proprietary inputs. An application built by the scripts contains the builder's game content; it is not a source-only distributable.
