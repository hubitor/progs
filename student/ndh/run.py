#!/usr/bin/env python
# -*- coding: latin-1 -*-
# runs a test as if it was installed

if __name__=="__main__":    
    import sys, os
    # adds "." to the pythonpath
    thisdir = os.path.split(os.path.abspath(__file__))[0]
    thisdir = os.path.normcase(thisdir)
    sys.path.append(thisdir)

    # add binary dir to PYTHONPATH
    pyexe = os.path.basename(sys.executable)
    if pyexe.find('_d.exe')>=0:
        sys.path.append(os.path.join(thisdir, 'build', 'bin', 'Debug')) # win/debug
    elif pyexe.find('.exe')>=0:
        sys.path.append(os.path.join(thisdir, 'build', 'bin', 'Release')) # win/release
    else:
        sys.path.append(os.path.join(thisdir, 'build', 'bin')) # linux

    # parse args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verb", help="increase output verbosity", action="count", default=0)
    parser.add_argument('file', nargs='*', help='python files')
    args = parser.parse_args()

    # run all tests sequentially
    for testname in args.file:    
        testname = os.path.abspath(testname)
        testname = os.path.normcase(testname)  # F:/ => f:/ on Windows
        # create workspace
        common = os.path.commonprefix( (testname, thisdir+os.sep) )
        resdir = testname[len(common):].replace(os.sep,"_")
        resdir = os.path.splitext(resdir)[0]  
        wdir=os.path.join('workspace', resdir)
        print 'workspace=', wdir
        if not os.path.isdir(wdir):
            os.makedirs(wdir)
        os.chdir(wdir)

        __file__ = testname
        execfile(testname)
