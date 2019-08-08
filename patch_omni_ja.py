#!/usr/bin/env python3

__author__ = "Alexander Fratzer"
__email__ = "alexander.fratzer@gmail.com"

import os
import argparse
import fnmatch
import shutil
import tempfile
from subprocess import call
import re

rel_browser_xhtml = "chrome/browser/content/browser/browser.xhtml"
rel_browser_xul = "chrome/browser/content/browser/browser.xul"

class OmniPatcher:
    """
    Removes the key_close policy of firefox
    """
    def __init__(self, lib_path, omni_ja="omni.ja"):
        self.__omni_ja = omni_ja
        browser_path = os.path.join(lib_path, "browser")
        if os.path.isdir(lib_path):
            self.__browser_path = browser_path
        else:
            raise FileNotFoundError(lib_path)

    def __find_omni_ja(self):
        for root, dirs, files in os.walk(self.__browser_path):
            for base in files:
                if fnmatch.fnmatch(base, self.__omni_ja):
                    return os.path.join(root, base)

    def __backup_omni_ja(self, omni_ja):
        browser_dir = os.path.dirname(omni_ja)
        file = os.path.basename(omni_ja)
        shutil.copy2(omni_ja, os.path.join(browser_dir, file + ".bak"))

    def __init_sandbox(self, omni_ja):
        tmpdir = tempfile.mkdtemp()
        call(["unzip", omni_ja, "-d", tmpdir], stdout=open(os.devnull, "w"), stderr=open(os.devnull, "w"))
        return tmpdir

    def __perform_patch(self, tmpdir):
        wdir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(tmpdir)

        pattern1 = re.compile(r"(<key id=\"key_close.*)(reserved=\"true\")")

        for file in [rel_browser_xul]:
            with open(file, "r") as f:
                content = f.read()

            repl = pattern1.sub(r"\1", content)

            with open(file, "w") as f:
                f.write(repl)

        os.chdir(wdir)

    def __rezip_omni_ja(self, tmpdir):
        wdir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(tmpdir)

        call(["zip", "-qr9XD", "omni.ja"] + os.listdir(os.getcwd()))

        os.chdir(wdir)
        return os.path.join(tmpdir, "omni.ja")

    def patch(self):
        omni = self.__find_omni_ja()
        self.__backup_omni_ja(omni)
        tmpdir = self.__init_sandbox(omni)

        self.__perform_patch(tmpdir)
        new_omni = self.__rezip_omni_ja(tmpdir)

        shutil.move(new_omni, omni)
        shutil.rmtree(tmpdir)


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path_to_firefox_libs", help="Path to the firefox lib-dir default is: /usr/lib/firefox")
    args = parser.parse_args()

    patcher = OmniPatcher(args.path_to_firefox_libs)
    patcher.patch()
