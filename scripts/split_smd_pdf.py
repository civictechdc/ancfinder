#!/usr/bin/python

# hacky script to split up the SMD PDF into individual pages, labeled by ANC
# requires pdftk and pdftotext, expects the SMD PDF as an argument, and creates output in the current directory

import subprocess, re, os, sys, shutil

# make output directories
for directory in ('pages', 'labeled'):
    if not os.path.exists(directory):
        os.mkdir(directory)

# split the file
print "Splitting the main file..."
subprocess.Popen(["pdftk", sys.argv[1], "burst", "output", "pages/pg_%03d.pdf"]).communicate()

print "Detecting names..."
for filename in os.listdir('pages'):
    if re.match("pg_\d+.pdf", filename):
        filepath = os.path.join('pages', filename)
        lines = subprocess.Popen(["pdftotext", filepath, "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0].split("\n")
        smd_lines = [line for line in lines if re.match(r"^SMD \d[A-Z]\d{2}$", line.strip())]
        
        if not len(smd_lines) == 1:
            # there are a couple of weird ones that have differently structured output
            smd_lines = [line for line in lines if re.match(r"^\( \d[A-Z]\d{2}$", line.strip())]

        # if it's still busted, give up
        if not len(smd_lines) == 1:
            raise Exception("didn't find a matching line")

        smd = smd_lines[0].split(" ")[-1]

        print filename, "->", "%s.pdf" % smd
        shutil.copy(filepath, os.path.join("labeled", "%s.pdf" % smd))