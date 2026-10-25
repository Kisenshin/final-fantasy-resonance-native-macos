# HK 1.0.1: exact build gate, original instruction asserted by patch_nso.py.
# Static evidence: constructor BL at 0x137f0 -> 0xae770; x0 points to main+0x77c6210.
# Constructor assigns the 32-slot UE5_6 vtable main+0x67df800.
# See work/runtime-research/hk-allocator-evidence.json in the caller workspace.
CUTS = {
    'b7f965b9d7227db8e29f04e84ea7331b': [
        (0x137f0, 'e06b0294', '1f2003d5', 'HK nninitStartup: verified FMallocBinned3 constructor BL -> nop; host UE5_6 allocator installed'),
    ],
}
