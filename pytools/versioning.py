# -*- coding: latin-1 -*-

from __future__ import print_function
from builtins import object
import pytools.utils as pu
import os, os.path, subprocess, re


class Repo(object):
    def __init__(self):
        pass

    def update(self):
        pass

class GITRepo(Repo):
    def __init__(self, name, repo):
        self.name = name
        self.repo = repo

    def update(self):

        if not os.path.isdir(self.name):
            #print "skipping %s" % self.name  # should checkout instead
            #return
            cmd = 'git clone %s' % self.repo
            if not pu.isUnix():
                cmd = r'"C:\Program Files\Git\bin\sh.exe" --login -c "%s"' % cmd
            status = subprocess.call(cmd, shell=True)
            if status:
                raise Exception('"%s" FAILED with error %d' % (cmd, status))
            print('status =', status)

        else:
            pu.chDir(self.name)
            if pu.isUnix():
                cmd = 'git pull origin master'
            else:
                cmd = r'"C:\Program Files\Git\bin\sh.exe" --login -c "git pull origin master"'
            print(cmd)
            # os.system necessite des "" en plus autour de la cmd)
            #os.system('"%s"' % cmd)
            status = subprocess.call(cmd, shell=True)
            if status:
                raise Exception('"%s" FAILED with error %d' % (cmd, status))
            print('status=', status)
            pu.chDir('..')
        
        # set core.filemode=false in .git/config on windows!
        # (otherwise executable files are considered as diffs)
        if not pu.isUnix():
            pu.chDir(self.name)
            cmd = 'git config core.filemode false'
            cmd = r'"C:\Program Files\Git\bin\sh.exe" --login -c "%s"' % cmd
            print(cmd)
            status = subprocess.call(cmd, shell=True)
            if status:
                raise Exception('"%s" FAILED with error %d' % (cmd, status))
            pu.chDir('..')  

    def outdated(self):
        "checks whether the working copy is outdated"

        if not os.path.isdir(self.name):
            return True
        else:
            os.chdir(self.name)

        # git remote -v update (fetch everything)
        cmd = ['git', 'remote', '-v', 'update']
        if not pu.isUnix():
            cmd = [r'C:\Program Files\Git\bin\sh.exe', '--login', '-c', ' '.join(cmd) ]
        with open(os.devnull, 'w') as FNULL:
            status = subprocess.call(cmd, stdout=FNULL, stderr=subprocess.STDOUT)
        if status:
            raise Exception('"%s" FAILED with error %d' % (cmd, status))
       
        # git status -uno  (check "Your branch is up to date") 
        cmd = ['git', 'status', '-uno']
        if not pu.isUnix():
            cmd = [r'C:\Program Files\Git\bin\sh.exe', '--login', '-c', ' '.join(cmd) ]
        out = subprocess.check_output(cmd)
        out = out.decode()  # python 3 returns bytes
        m = re.search(r'Your branch is up to date', out)
        os.chdir('..')

        return (m==None)


class SVNRepo(Repo):
    def __init__(self, name, repo):
        self.name = name
        self.repo = repo

        # set SVN_SSH, sinon: "can't create tunnel"
        if not pu.isUnix():
            os.environ[
                'SVN_SSH'] = r'C:\\Program Files\\TortoiseSVN\\bin\\TortoisePlink.exe'  # '\\\\' ou 'r et \\' !!

    def update(self):

        if not os.path.isdir(self.name):
            cmd = 'svn co %s %s' % (self.repo, self.name)
        else:
            cmd = 'svn update %s' % self.name

        print(cmd)
        status = subprocess.call(cmd, shell=True)
        if status: raise Exception('"%s" FAILED with error %d' % (cmd, status))

    def outdated(self):
        "checks whether the working copy is outdated"

        if not os.path.isdir(self.name):
            return True

        # svn info 
        out = subprocess.check_output(['svn', 'info', self.name])
        out = out.decode(errors='ignore')  # python 3 returns bytes
        m = re.search(r'Last Changed Rev: (\d+)', out)
        if m and len(m.groups()) > 0:
            version = m.group(1)
        else:
            raise Exception('cannot read "svn info" output')

        # svn info -r HEAD
        out = subprocess.check_output(['svn', 'info', '-r', 'HEAD', self.name])
        out = out.decode(errors='ignore')  # python 3 returns bytes
        m = re.search(r'Last Changed Rev: (\d+)', out)
        if m and len(m.groups()) > 0:
            version_HEAD = m.group(1)
        else:
            raise Exception('cannot read "svn info -r HEAD" output')

        #print('version =', version)
        #print('version_HEAD =', version_HEAD)

        return version!=version_HEAD
