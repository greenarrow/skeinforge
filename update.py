#!/usr/bin/env python

import urllib
import re
import time
import subprocess


URL_BASE = "http://fabmetheus.crsndoo.com"
URL_INDEX = "/index.php?all=true"
URL_FILES = "/files"

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

TEST = True

RE_VERSION = re.compile(
    r'<a href="/files/([^"]+?).zip">(\d+-\d+-\d+ \d+:\d+:\d+)'
)


def shell(cmd):
    """Run a command through a shell"""
    if TEST:
        print "$ %s" % cmd
        return

    p = subprocess.Popen(cmd, shell=True)
    assert p.wait() == 0


if __name__ == "__main__":
    # fetch all the skeinforge versions from download page
    versions = map(
        lambda (tag, timestamp): (
            tag, time.strptime(timestamp, TIMESTAMP_FORMAT)
        ),
        RE_VERSION.findall(
            urllib.urlopen("%s%s" % (URL_BASE, URL_INDEX)).read()
        )
    )

    # read all the current git tags
    p = subprocess.Popen("git tag", shell=True, stdout=subprocess.PIPE)
    assert p.wait() == 0
    tags = filter(len, p.communicate()[0].split("\n"))

    # work out all the versions that are available but not in our repo
    new = sorted(
        filter(
            lambda (tag, timestamp): tag not in tags,
            versions
        ),
        key=lambda (tag, timestamp): timestamp
    )

    print "%d new versions" % len(new)

    for tag, timestamp in new:
        shell("git reset --hard")

        # download version
        url = "%s%s/%s.zip" % (URL_BASE, URL_FILES, tag)
        shell("wget %s" % url)

        # extract zip file
        shell("unzip -o %s.zip" % tag)
        shell("rm %s.zip" % tag)

        # commit all files
        shell("git add .")
        shell("git commit -a -m \"Release %s\n\nFilename %s.zip\nDate     %s\nURL      %s\"" % (
            tag, tag, time.strftime(TIMESTAMP_FORMAT, timestamp), url
        ))

        # tag
        shell("git tag %s" % tag)

    # push master
    shell("git push origin master")

    # push new tags
    for tag, timestamp in new:
        shell("git push origin tag %s" % tag)


# put in README + script before adding any versions

