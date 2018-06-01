#################################
#                               #
#       Presence Checker        #
#   Progetto Gestione di Rete   #
#          AA 2017/18           #
#                               #
#      Francesco Vatteroni      #
#                               #
#################################

import sys
import os
import pcapy
import time
import datetime
import signal
import thread
from impacket.ImpactDecoder import RadioTapDecoder, Dot11ControlDecoder, DataDecoder

interface = 'wlan0mon'
monitor_enable  = 'airmon-ng start wlan0;'
monitor_disable = 'airmon-ng stop wlan0mon;'

max_bytes = 1024 # da rivedere si puo accorciare
promiscuous = True
read_timeout = 100
ignore = ["0x0:0x0:0x0:0x0:0x0:0x0"] #mac da ignorare (ex. accesspoint della rete)
ha={}

delay = 5 # delay per export
lastexport = datetime.datetime.now()

#scrittura su file
def exporter(haexport):
    name = "wfm "+ str(datetime.datetime.now()) +".log"
    with open(name, "a") as myfile:
        for h in haexport:
            myfile.write(h + "\n")
            for n in haexport.get(h):
                t = n[0]
                i = n[1]
                myfile.write("      " + str(t) + " |> " + str(i) + "\n")

# callback per ricevere pacchetti
def recv_pkts(hdr, data):
    global lastexport
    global ha

    #decodifica del pacchetto
    radio = RadioTapDecoder().decode(data)
    datadown = radio.get_body_as_string()
    ethe = Dot11ControlDecoder().decode(datadown)
    datadowndown = ethe.get_body_as_string()
    decodedDataDownDown = DataDecoder().decode(datadowndown)
    ethMacS = [None] * 6
    for i in range(0,6):
        #salto i primi 8 byte per ottenere il mac trasmittente
        ethMacS[i] = hex(decodedDataDownDown.get_byte(8+i)) 
    macS = ':'.join(map(str, ethMacS))
    s = type(radio.get_dBm_ant_signal())
    
    time = datetime.datetime.now()

    #aggiunta al dizionario
    if (s is int) & (macS not in ignore):
        signal = hex(radio.get_dBm_ant_signal())
        t = (time,signal)
        if (ha.has_key(macS)):
            ha.get(macS).append(t)
        else:
            l = [t]
            ha[macS] = l

    #esporta su file (thread in parallelo)
    if ((time - lastexport).seconds > delay) & len(ha.keys()) :
        haexport = ha
        ha = {}
        lastexport = time
        thread.start_new_thread(exporter, (haexport, ) )

def mysniff(interface):
    pcapy.findalldevs()
    pc = pcapy.open_live(interface, max_bytes, promiscuous, read_timeout)
    pc.setfilter('')    
    packet_limit = -1 # -1 per infiniti
    pc.loop(packet_limit, recv_pkts) # cattura pacchetti

def main():
    thread.start_new_thread(exporter,())
    os.system(monitor_enable)
    try: mysniff(interface)
    except KeyboardInterrupt: sys.exit()
    finally:
        os.system(monitor_disable)

main()