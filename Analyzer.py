#!/usr/bin/env python

#################################
#                               #
#        Prschk Analyzer        #
#                               #
#      Francesco Vatteroni      #
#                               #
#################################

import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

value = {}

def printUsage(n):
    print '[!] ' + n + ' [folder path] [mac]'

def printGrap(d,m):
    x = []
    y = []
    d[m].sort(key=lambda tup: tup[0])
    for e in d[m]:
        x.append(datetime.strptime(e[0],'%Y-%m-%d %H:%M:%S.%f'))
        y.append(int(e[1][:-3]))
        print datetime.strptime(e[0],'%Y-%m-%d %H:%M:%S.%f')
    plt.plot(x, y)
    plt.show()

def parseAll(path):
    global value
    os.chdir(path)
    for filename in os.listdir(path):
        if filename.endswith('.xml'):
            fullname = filename
            root = ET.parse(fullname).getroot()
            for child in root:
                k = child.attrib.get('value')
                for el in child:
                    time = el[0].text
                    intes = el[1].text
                    t = (time, intes)
                    if value.has_key(k):
                        value.get(k).append(t)
                    else:
                        l = [t]
                        value[k] = l
            

def main():
    if ((len(sys.argv) != 3) or not(os.path.isdir(sys.argv[1]))):
        printUsage(sys.argv[0])
        sys.exit()
    else:
        parseAll(sys.argv[1])
    printGrap(value, sys.argv[2])


main()