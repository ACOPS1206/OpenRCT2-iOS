# OpenRCT2 iOS port: first integration slice

This is a source overlay for the upstream `develop` branch, inspected on 2026-09-26. It is **not** a completed iOS build. The patch introduces iOS platform and UI adapters and isolates macOS-only code. The game engine, renderer, audio and touch handling remain upstream.

## Apply

1. Check out `https://github.com/OpenRCT2/OpenRCT2` at `develop` on a Mac.
2. Run `python3 apply.py /path/to/OpenRCT2` from this directory.
3. Supply iOS-built dependencies (SDL2, ICU, libzip, zlib, zstd, libpng and, when enabled, audio/font libraries) through a CMake toolchain/prefix. Configure the `openrct2` target for an iOS device with Xcode. `-DDISABLE_OPENGL=ON -DDISABLE_HTTP=ON -DDISABLE_NETWORK=ON -DDISABLE_TTF=ON -DDISABLE_FLAC=ON -DDISABLE_VORBIS=ON -DENABLE_SCRIPTING=OFF -DMACOS_USE_DEPENDENCIES=OFF` reduces the initial dependency set.
4. Build and fix any upstream/platform issues reported by Xcode. The package has been syntax checked but cannot be cross compiled in this Linux workspace.

The `.app` needs OpenRCT2's freely distributable generated `data` contents at the bundle resource root. OpenRCT2 also requires the user's own original RCT2 files. The iOS adapter searches `Documents/RCT2` for those files; do not bundle them with a public binary. The app plist enables Files access to its Documents directory.

## Next integration gates

- Resolve all third party libraries for `arm64-apple-ios`, including SDL2's iOS main entry and iOS app bundle resource packaging.
- Verify first launch and original RCT2 data discovery on an iPhone, then validate touch coordinates, rotation, safe areas, audio and saving.
- Add a native Files picker/import flow; the initial adapter intentionally reports no in-game picker and exposes the Documents folder through Files.
- Add a macOS GitHub Actions build once the local device build succeeds, then sign with the developer's own team.

OpenRCT2 is GPL-3.0 licensed. Preserve its copyright notices and provide corresponding source when distributing a build. This overlay contains only newly written integration code.
