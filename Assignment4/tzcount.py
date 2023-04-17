#!/usr/bin/python3
import sys
input = []
for line in sys.stdin:
    if line.startswith("Date: "):
	    input.append(line.rstrip())

tzs = {}
for line in input:
    line = line[-5:]
    if line in tzs:
        tzs[line] += 1
    else:
        tzs[line] = 1

tzs = dict(sorted(tzs.items()))

ntzs = {}
ptzs = {}

for key, value in tzs.items():
    if key[0] == '-':
        ntzs[key] = value
    else:
        ptzs[key] = value

ntzs = dict(sorted(ntzs.items(), reverse=True))
        
for key, value in ntzs.items():
    print (key, value)

for key, value in ptzs.items():
    print (key, value)
