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
import json
import argparse
import requests
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
from datetime import datetime,  timedelta

value = {}

def printUsage(n):
    print '[!] ' + n + ' [Folder Path] [MAC]'

def srcVendor(m):
    MAC_URL = 'http://macvendors.co/api/%s'
    r = requests.get(MAC_URL % m)
    obj = r.json()['result']['company']
    return obj

def printGrap(d,m):
    x = []
    y = []
    last_d = None
    i = 0
    s = 0
    if d.has_key(m):
        d[m].sort(key=lambda tup: tup[0])
        for e in d[m]:
            current_d = datetime.strptime(e[0][:-7],'%Y-%m-%d %H:%M:%S')
            if (last_d is not None) and (last_d - current_d) == timedelta(0):
                i = i+1
                s = s+int(e[1][:-3])
            else :
                if (last_d is not None):
                    x.append(last_d)
                    y.append(s/i)
                last_d = current_d
                i = 1
                s = int(e[1][:-3])
        plt.xticks(rotation = 30)
        plt.yticks(rotation = 30)
        
        vendor = srcVendor(m)
        plt.title(vendor + "\n" + m)

        plt.plot(x, y)
        plt.show()
    else:
        print "[!] MAC not found"

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
    parser = argparse.ArgumentParser(description="https://github.com/The90Frank/PresenceChecker/")
    parser.add_argument("-d", "--directory", help="Path to import XML file", type=str, required=True)
    parser.add_argument("-m", "--macaddress", help="MAC address to analyze, e.g. 00:11:22:33:44:55", type=str, required=True)
    argms = parser.parse_args()

    parseAll(argms.directory)

    if len(value) != 0:
        printGrap(value, argms.macaddress)
    else:
        print "[!] No Files"


main()