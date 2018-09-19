#!/bin/env python2

#################################
#                               #
#       Presence Checker        #
#   Progetto Gestione di Rete   #
#          AA 2017/18           #
#                               #
#      Francesco Vatteroni      #
#                               #
#################################

import os
import sys
import time
import pcapy
import signal
import thread
import datetime
import xml.etree.ElementTree as ET
from impacket.ImpactDecoder import RadioTapDecoder, Dot11ControlDecoder, DataDecoder

ha={}
delay = 5 # delay per export
ignore = [] # mac da ignorare (ex. accesspoint della rete)
max_bytes = 256
read_timeout = 100
promiscuous = True
pacchetticatturati = 0
lastexport = datetime.datetime.now()

interface = ''
moninterface = ''
monitor_disable = 'airmon-ng stop '
monitor_enable  = 'airmon-ng start '
canale = 0 #canali da 1-13 (giro i numeri da 0-12)
directory = os.path.expanduser("~")

#rotazione dei canali
def channelLoop(s):
    while(1):
        global canale
        canale = ((canale + 1) % 13)
        change_channel = 'iw dev wlan0mon set channel ' + str(canale+1)
        os.system(change_channel)
        time.sleep(s)

#stampa di "interfaccia"
def interfaceLoop():
    while(1):
        PC = str(pacchetticatturati)
        LE = str(lastexport)
        sys.stdout.write("\rPacchetti Catturati: "+PC+" - Ultimo Export: "+LE)
        sys.stdout.flush()
        time.sleep(0.5)

#formattazione MAC
def addressDecode(x):
    s = ""
    aux = [None] * 6
    for i in range(0,6):
        #salto i primi 8 byte per ottenere il mac trasmittente
        aux[i] = hex(x.get_byte(8+i))[2:]
    s = ':'.join(aux)
    return s

#scrittura su file
def exporter(haexport):
    name = directory + "/prschk "+ str(lastexport) +".log.xml"

    root = ET.Element("root")
    for h in haexport:
        doc = ET.SubElement(root, h)
        idx = 0
        for n in haexport.get(h):
            t = n[0]
            i = n[1]
            tup = ET.SubElement(doc, str(idx))
            ET.SubElement(tup, "time").text = str(t)
            ET.SubElement(tup, "intensify").text = str(i)
            idx = idx + 1

    tree = ET.ElementTree(root)
    tree.write(name)

# callback per ricevere pacchetti
def recv_pkts(hdr, data):
    global lastexport
    global ha
    global pacchetticatturati

    try:
        #decodifica del pacchetto
        radio = RadioTapDecoder().decode(data)
        datadown = radio.get_body_as_string()
        ethe = Dot11ControlDecoder().decode(datadown)
        datadowndown = ethe.get_body_as_string()
        decodedDataDownDown = DataDecoder().decode(datadowndown)

        macS = (addressDecode(decodedDataDownDown))
        s = type(radio.get_dBm_ant_signal())

        time = datetime.datetime.now()

        #aggiunta al dizionario
        #controllo se il segnale ha un valore consistente, in caso contrario scarto
        if (s is int):
            signal = str(-(256 - radio.get_dBm_ant_signal()))+ " dB"
            t = (time,signal)
            if (ha.has_key(macS)):
                ha.get(macS).append(t)
            else:
                l = [t]
                ha[macS] = l
            pacchetticatturati = pacchetticatturati + 1

        #esporta su file (thread in parallelo)
        if ((time - lastexport).seconds > delay) & len(ha.keys()) :
            haexport = ha
            ha = {}
            lastexport = time
            thread.start_new_thread(exporter, (haexport, ) )
    
    except KeyboardInterrupt: raise
    except: pass #per evitare che crashi qual'ora ci siano errori nel pacchetto

def mysniff(interface):
    global ignore

    pcapy.findalldevs()
    pc = pcapy.open_live(interface, max_bytes, promiscuous, read_timeout)
    #ignoro i tipi che non hanno mac sorgente
    filt = 'not(subtype ack or subtype cts)'
    #aggiungo i mac da ignorare
    for e in ignore:
        filt = filt + ' and wlan addr2 not ' + e
    pc.setfilter(filt)
    packet_limit = -1 # -1 per infiniti
    pc.loop(packet_limit, recv_pkts) # cattura pacchetti

def main():

    global ignore
    global directory
    global interface
    global moninterface
    global monitor_enable
    global monitor_disable

    interfaces = os.listdir('/sys/class/net/')
    
    if (len(sys.argv) == 2) and (sys.argv[1] in interfaces) or ((len(sys.argv) == 3) and (sys.argv[1] in interfaces) and (os.path.isfile(sys.argv[2]))):
        interface = sys.argv[1]

        #cartella per export
        directory = directory + "/PresenceCheckerLOG/" + interface
        if not os.path.exists(directory):
            os.makedirs(directory)

        moninterface = interface + 'mon'
        monitor_enable = monitor_enable + interface + ';'
        monitor_disable = monitor_disable + moninterface + ';'

        if len(sys.argv) == 3:
            tree = ET.parse(sys.argv[2])
            root = tree.getroot() 

            for child in root:
                ignore.append(child.text)

        os.system(monitor_enable)

        try:
            #avvio la rotazione dei canali
            thread.start_new_thread(channelLoop, (1,))
            thread.start_new_thread(interfaceLoop, ())
            mysniff(moninterface)
        except KeyboardInterrupt: sys.exit()
        finally:
            os.system(monitor_disable)
    else:
        print '[!] Insert a valid interface or a valid ignore file'
        print '[!] example: python ' + sys.argv[0] + ' wlan0'
        print '[!] example: python ' + sys.argv[0] + ' wlan0 ./ignore.xml'

main()