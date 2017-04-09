#! /usr/bin/env python
# -*- coding: latin-1; -*-

import os, os.path, glob

codes = {
 '�' : '&agrave;',
 '�' : '&egrave;',
 '�' : '&ugrave;',
 '�' : '&eacute;',
 '�' : '&euml;',
 '�' : '&acirc;',
 '�' : '&ecirc;',
 '�' : '&icirc;',
 '�' : '&ocirc;',
 '�' : '&ucirc;', 
 '�' : '&ccedil;' 
 }


def convert(filename):
    if os.path.isfile(filename):
        if os.path.splitext(filename)[1]!='.bak':
            # read file   
            file = open(filename,'rt')
            txt = file.read()
            file.close()
            # convert
            txt2 = txt
            for x, xhtml in codes.items():
                txt2 = txt2.replace(x, xhtml)
            if len(txt2)!=len(txt):
                print "%s converted" % filename
                bakfile = filename+'.bak'
                if os.path.isfile(bakfile):
                    os.remove(bakfile)
                # do backup
                os.rename(filename, bakfile)
                #write result
                file = open(filename,'wt')
                file.write(txt2)
                file.close()
            else:
                print "%s skipped" % filename
            


if __name__ == "__main__":
    import sys
    if len(sys.argv)==1:
        print "\nusage: %s [files]\n" % sys.argv[0]
        print "remplace les accents par les codes HTML correspondants\n"
        sys.exit()
    
    for files in sys.argv[1:]:
        for file in glob.glob(files):
            convert(file)
        