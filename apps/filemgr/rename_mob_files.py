#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

lst = os.listdir(".")
# print lst

pattern = re.compile(r'Mobistar-D�tails-(\d{11})-(\d{4})(\d{2})(\d{2}).pdf')

n = 0
for file in lst:
    match = pattern.search(file)
    if match:
        print file
        g = match.groups()
        newname = 'mobistar-%s-%s-%s-facture-%s.pdf' % (g[1], g[2], g[3], g[0])
        print ' =>', newname
        os.rename(file, newname)
        n += 1

print n, 'files processed'
print "[enter to quit]"
raw_input()
