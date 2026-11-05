#!/usr/bin/env python3
"""Apply public RenderStudio sources to an expanded TOX directory.

This script edits files only. It does not call TouchDesigner, inject test hooks,
or save a user's open project. Run toeexpand first and toecollapse afterwards.
"""
import argparse
import re
import shutil
import struct
from pathlib import Path

MODULES = ('catalog', 'chooser', 'determinism', 'encoding', 'engine', 'export_core', 'sources')
TD_SERIES = 'TD2025'


def write_text_dat(path, content):
    raw = path.read_bytes()
    assert raw[:3] == b'2\n*', path
    head = bytearray(raw[:0x1B])
    assert len(content) <= 0xFFFF, (path, len(content))
    head[0x19:0x1B] = struct.pack('>H', len(content))
    path.write_bytes(bytes(head) + content)


def edit_pattern(path, pattern, replacement, must=True):
    text = path.read_text(encoding='utf-8')
    updated, count = re.subn(pattern, replacement, text)
    if count == 0:
        assert not must, '%s: pattern not found: %s' % (path, pattern)
        return False
    assert count == 1, '%s: expected one match, got %d' % (path, count)
    path.write_text(updated, encoding='utf-8')
    return True


def source_version(source):
    text = (source / 'export_core.py').read_text(encoding='utf-8')
    matches = re.findall(r"(?m)^VERSION\s*=\s*['\"](\d+\.\d+\.\d+)['\"]\s*$", text)
    assert len(matches) == 1, 'expected one VERSION in source/export_core.py'
    return matches[0]


def remove_legacy(root, comp):
    for path in comp.glob('Legacy_2023_original*'):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    candidates = [root.parent / (root.name[:-4] + '.toc'),
                  root.parent.parent / (root.parent.name[:-4] + '.toc')]
    toc = next((path for path in candidates if path.is_file()), None)
    assert toc is not None, candidates
    lines = toc.read_text(encoding='utf-8').splitlines()
    kept = [line for line in lines if 'RenderStudio/Legacy_2023_original' not in line]
    removed = len(lines) - len(kept)
    if removed == 0:
        assert not list(comp.glob('Legacy_2023_original*')), comp
        print('LEGACY_ALREADY_ABSENT')
        return
    assert removed > 50, toc
    toc.write_text('\n'.join(kept) + '\n', encoding='utf-8')
    print('LEGACY_REMOVED', removed)


def apply(root, source):
    comp = root / 'RenderStudio'
    assert (comp / 'engine.text').is_file(), 'component directory not found under ' + str(root)
    version = source_version(source)
    display_version = '.'.join(version.split('.')[:2])
    help_text = (source / 'help.txt').read_text(encoding='utf-8')
    assert help_text.startswith('RenderStudio ' + display_version + ' ·'), 'update source/help.txt for ' + display_version

    for name in MODULES:
        write_text_dat(comp / (name + '.text'), (source / (name + '.py')).read_bytes())
    edit_pattern(comp / 'ui' / 'version.parm',
                 r'\d+\.\d+(?:\.\d+)?\s+·\s+NATIVE TD',
                 display_version + '  ·  NATIVE TD')
    for suffix in ('parm', 'cparm'):
        edit_pattern(root / ('RenderStudio.' + suffix),
                     r'"\d+\.\d+\.\d+ / ' + TD_SERIES + '"',
                     '"' + version + ' / ' + TD_SERIES + '"')
    for path in (root / 'RenderStudio.parm', comp / 'ui' / 'message.parm'):
        edit_pattern(path, r'"\d+\.\d+ 已就绪 ·', '"' + display_version + ' 已就绪 ·', must=False)
    write_text_dat(comp / 'help.text', help_text.encode('utf-8'))
    remove_legacy(root, comp)
    print('APPLY_OK version=%s root=%s' % (version, root))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('expanded_root', type=Path,
                        help='expanded directory containing RenderStudio/ and RenderStudio.parm')
    parser.add_argument('--source', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'source',
                        help='public source directory (default: repository source/)')
    args = parser.parse_args()
    apply(args.expanded_root, args.source)


if __name__ == '__main__':
    main()
