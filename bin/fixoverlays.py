#! /usr/bin/env python
# -*- coding: latin-1 -*-
#
# from: https://cito.github.io/blog/overlay-icon-battle/

from __future__ import with_statement
import os
import _winreg as reg

# names of all overlay icons that shall be boosted:

boost = """
    Tortoise1Normal
    Tortoise2Modified
    Tortoise3Conflict
    Tortoise4Locked
    Tortoise5ReadOnly
    Tortoise6Deleted
    Tortoise7Added
    Tortoise8Ignored
    Tortoise9Unversioned
    DropboxExt01
    DropboxExt02
    DropboxExt03
    DropboxExt04
    DropboxExt05
    DropboxExt06
"""

boost = set(boost.split())


def main():
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion'
            r'\Explorer\ShellIconOverlayIdentifiers') as base:

        names = set()
        renames = []
        i = 0
        while True:
            try:
                name = reg.EnumKey(base, i)
            except OSError:
                break
            core = name.strip()
            if core in names:
                print('Delete', repr(core))
                reg.DeleteKey(base, name)
            else:
                names.add(core)
                if core in boost:
                    core = ' ' + core
                if core != name:
                    renames.append((name, core))
            i += 1

        if renames:
            for old_name, new_name in renames:
                print('Rename', repr(old_name), 'to', repr(new_name))
                value = reg.QueryValue(base, old_name)
                reg.CreateKey(base, new_name)
                reg.SetValue(base, new_name, reg.REG_SZ, value)
                reg.DeleteKey(base, old_name)
            print('Restart Windows Explorer')
            if not os.system('taskkill /F /IM explorer.exe'):
                os.system('start explorer.exe')
        else:
            print('Nothing to rename')


if __name__ == '__main__':
    main()
