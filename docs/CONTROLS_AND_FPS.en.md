# Keyboard, controllers and in-game 30/60 FPS settings

[简体中文](CONTROLS_AND_FPS.md) | [English](CONTROLS_AND_FPS.en.md)

These instructions describe the local Hong Kong 1.0.1 adaptation. The new source build entry point has not been validated end to end from a clean environment; see [validation status](VALIDATION.en.md).

The current launcher defaults to Simplified Chinese. English menu names below explain the Chinese labels; switching this documentation to English does not change the game's language.

## Connecting a controller and reading hints

Connect the controller through macOS, return to the game and press a button or move a stick. The adaptation reads controllers through Apple GameController. A device must be recognized by that framework; compatibility with every third-party controller is not guaranteed.

- Using the keyboard selects keyboard mappings in the bottom hint bar.
- Using Xbox or Switch Pro selects the corresponding controller hints.
- F1 opens the full mapping guide; F2 shows/hides the hint bar. The top `Controls` menu is another way to open it. If your MacBook uses F1/F2 for brightness, hold Fn as well.
- **Automatic device switching affects the adaptation's bottom hint bar. The original game still shows Switch button icons; in-game icons have not been replaced throughout the game with keyboard or Xbox symbols.** Use the table below.

## Mapping table

Xbox uses matching letters: **A confirms, B goes back**. Switch Pro keeps its original layout. Their confirmation buttons occupy different physical positions.

| Switch prompt / function | Keyboard | Xbox | Switch Pro |
| --- | --- | --- | --- |
| A: confirm / dialogue | J or Space | A (bottom) | A (right) |
| B: back | K, Esc or Backspace | B (right) | B (bottom) |
| X | U | X (left) | X (top) |
| Y | I | Y (top) | Y (left) |
| Left stick: movement | W, A, S, D | Left stick | Left stick |
| Right stick | Option + arrow keys, or numeric keypad 4/6/8/2 | Right stick | Right stick |
| D-pad | Arrow keys ↑↓←→ | D-pad | D-pad |
| L / R | Q / E | LB / RB | L / R |
| ZL / ZR | Z / C | LT / RT | ZL / ZR |
| Press left / right stick | F / G | L3 / R3 | Press left / right stick |
| +: system menu | Enter | Menu | + |
| − | Tab | View | − |

X/Y, shoulders and other entries describe their Switch button equivalents, not a fixed combat action. Follow the game's current action prompt. Keypad 4/6 move the right stick left/right; 8/2 move it up/down. Arrow keys without Option act as the D-pad.

Input is released when the game loses focus. Sticks have a small dead zone to reduce drift. Physical connection, wireless stability and controller-model compatibility need more testing. Mappings passed Apple GameController virtual snapshot checks covering face buttons, both sticks, stick clicks, D-pad, shoulders, triggers and Menu/View. Motion, rumble and system Home/Capture buttons are outside this adaptation's scope.

## Switching 30/60 FPS in the original game menu

Path: **System Menu (系统菜单) → Options (选项) → Display Settings (画面设置) → Frame Rate (帧率)**. The title-screen `Option` opens the same settings.

1. In gameplay, open the system menu with keyboard **Enter**, Xbox **Menu** or Switch Pro **+**. On the title screen, select `Option` instead.
2. Enter Options and switch to Display Settings. The game's L/R tab controls map to keyboard **Q/E**, Xbox **LB/RB** and Switch Pro **L/R**.
3. Select Frame Rate using directional input. Open the dropdown with keyboard **J/Space** or controller **A**.
4. Select **30** or **60**, then confirm. The adaptation keeps only these two choices.
5. Apply using the game's **Y** prompt (`套用` / `应用`): keyboard **I**, Xbox **Y (top)** or Switch Pro **Y (left)**.
6. Select **Yes (是)** in the confirmation dialog and confirm with keyboard **J/Space** or controller **A**.

Once applied, the setting takes effect immediately and is saved by the game's own `OptionSaveData`. The earlier local workspace build was tested saving 30 and restoring it after restart, and saving 60 and restoring it after restart. Changing the dropdown alone does not establish that the setting was saved.

The top `Performance` menu indicates the selected target. Make changes in the original game settings. **Selecting 60 FPS sets a target; it does not mean every measured frame reaches 60 FPS.** Combat effects, initial resource creation and other work can still cause drops. The 60 FPS mode is experimental.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| The bottom bar still shows keyboard hints | Confirm the controller is connected in macOS, then actually press a button or move a stick. Connecting alone may not change the active hints. |
| The game still shows Switch icons | This is the current implementation scope. Use this table or F1; bottom hints do not replace every in-game icon. |
| Xbox and Switch Pro confirmation buttons are in different positions | Follow letters: A confirms and B goes back on both. Xbox A is at the bottom; Switch Pro A is on the right. |
| F1/F2 change brightness or trigger another system function | Try Fn+F1/F2, or use the top Controls menu. |
| The FPS selection does not persist | Select it again, Apply with Y and confirm Yes with A. On keyboard, use I, then J/Space. |
| The Frame Rate row is missing | Check the supported Hong Kong 1.0.1 version and whether the FPS-menu patch succeeded in the build log. Do not force assets from another version into the build. |
| 60 FPS is selected but drops still occur | This is a target. Compare with 30 FPS and report the scene and logs; it is not evidence of sustained 60 FPS or a complete effects fix. |

## Full screen, quitting and saves

- Full screen: **Control+Command+F**, the green window button, or `Window → Enter Full Screen`.
- Quit: **Command+Q**.
- Saves: `~/Library/Application Support/FFRNative/0100B8A026F14000/save`.

The repository supplies no saves, and the builder does not package existing saves. See the README for particle rendering issues and occasional stutter.
