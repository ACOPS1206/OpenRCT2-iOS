#!/usr/bin/env python3
"""Apply the first iOS adaptation to a clean upstream OpenRCT2 checkout."""

from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one upstream anchor, found {count}")
    return source.replace(old, new, 1)


def plan(upstream: Path) -> dict[Path, str]:
    changes = {}

    path = upstream / "CMakeLists.txt"
    source = path.read_text()
    source = replace_once(source,
        "if (APPLE)\n    execute_process(COMMAND /usr/bin/uname -m",
        "if (APPLE AND NOT IOS)\n    execute_process(COMMAND /usr/bin/uname -m", "macOS architecture")
    source = replace_once(source,
        'if (APPLE)\n    set(CMAKE_SYSTEM_PROCESSOR "${CMAKE_OSX_ARCHITECTURES}"',
        'if (APPLE AND NOT IOS)\n    set(CMAKE_SYSTEM_PROCESSOR "${CMAKE_OSX_ARCHITECTURES}"', "macOS processor")
    source = replace_once(source,
        '    "APPLE" OFF)\n', '    "APPLE;NOT IOS" OFF)\n', "macOS dependencies")
    changes[path] = source

    path = upstream / "cmake/platform.cmake"
    source = path.read_text()
    source = replace_once(source,
        'if (APPLE)\n    target_link_libraries(${target} "-framework Cocoa -framework CoreServices")',
        'if (IOS)\n    target_link_libraries(${target} "-framework Foundation" "-framework UIKit" "-framework CoreText")\nelseif (APPLE)\n    target_link_libraries(${target} "-framework Cocoa -framework CoreServices")', "Apple frameworks")
    changes[path] = source

    path = upstream / "src/openrct2-ui/CMakeLists.txt"
    source = path.read_text()
    source = replace_once(source,
        'elseif (MSVC)\n    find_package(SDL2 REQUIRED)\nelse ()\n    PKG_CHECK_MODULES(SDL2 REQUIRED IMPORTED_TARGET sdl2)',
        'elseif (MSVC)\n    find_package(SDL2 REQUIRED)\nelseif (IOS)\n    find_package(SDL2 CONFIG REQUIRED)\nelse ()\n    PKG_CHECK_MODULES(SDL2 REQUIRED IMPORTED_TARGET sdl2)', "SDL2 dependency")
    source = replace_once(source,
        'add_executable(openrct2 ${OPENRCT2_UI_SOURCES} ${OPENRCT2_UI_MM_SOURCES})',
        'if (IOS)\n    add_executable(openrct2 MACOSX_BUNDLE ${OPENRCT2_UI_SOURCES} ${OPENRCT2_UI_MM_SOURCES})\n    set_target_properties(openrct2 PROPERTIES MACOSX_BUNDLE_INFO_PLIST "${ROOT_DIR}/ios/Info.plist")\nelse ()\n    add_executable(openrct2 ${OPENRCT2_UI_SOURCES} ${OPENRCT2_UI_MM_SOURCES})\nendif ()', "iOS app bundle")
    source = replace_once(source,
        'elseif (NOT MSVC AND NOT WIN32)\n    target_link_libraries(openrct2 "libopenrct2"\n                                    PkgConfig::SDL2)',
        'elseif (IOS)\n    target_link_libraries(openrct2 "libopenrct2" SDL2::SDL2 SDL2::SDL2main)\nelseif (NOT MSVC AND NOT WIN32)\n    target_link_libraries(openrct2 "libopenrct2"\n                                    PkgConfig::SDL2)', "iOS SDL2 link")
    changes[path] = source

    path = upstream / "src/openrct2/CMakeLists.txt"
    source = path.read_text()
    source = replace_once(source,
        'if (UNIX AND NOT HAIKU AND NOT ${CMAKE_SYSTEM_NAME} MATCHES "BSD")',
        'if (UNIX AND NOT IOS AND NOT HAIKU AND NOT ${CMAKE_SYSTEM_NAME} MATCHES "BSD")', "libdl")
    changes[path] = source

    for relative in ("src/openrct2/platform/Platform.macOS.mm", "src/openrct2-ui/UiContext.macOS.mm"):
        path = upstream / relative
        source = path.read_text()
        source = replace_once(source, '#if defined(__APPLE__) && defined(__MACH__)',
            '#include <TargetConditionals.h>\n#if defined(__APPLE__) && defined(__MACH__) && !TARGET_OS_IPHONE', relative)
        changes[path] = source

    for origin, destination in (
        ("ios/Info.plist", "ios/Info.plist"),
        ("ios/UiContext.iOS.mm", "src/openrct2-ui/UiContext.iOS.mm"),
        ("ios/Platform.iOS.mm", "src/openrct2/platform/Platform.iOS.mm"),
    ):
        target = upstream / destination
        if target.exists():
            raise ValueError(f"already exists: {target}")
        changes[target] = (ROOT / origin).read_text()
    return changes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--check", action="store_true", help="validate anchors without writing")
    args = parser.parse_args()
    checkout = args.checkout.resolve()
    changes = plan(checkout)
    if not args.check:
        for path, content in changes.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    print(f"{'Validated' if args.check else 'Applied'} {len(changes)} source files in {checkout}")


if __name__ == "__main__":
    main()
