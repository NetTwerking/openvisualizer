# Copyright (c) 2010-2013, Regents of the University of California. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License
import logging
log = logging.getLogger('ParserData')
log.setLevel(logging.ERROR)
log.addHandler(logging.NullHandler())
import struct
import csv
import pandas as pd
from pydispatch import dispatcher

from ParserException import ParserException
import Parser
import time

class ParserData(Parser.Parser):
    
    HEADER_LENGTH  = 2
    MSPERSLOT      = 20 #ms per slot.
    
    IPHC_SAM       = 4
    IPHC_DAM       = 0
    DONG = 'dongyeop'
    CLICKER_MASK1    = 'icke'
    SUM = 0.0
    COUNT = 0
    aggregation = {0xe7:0, 0xf5:0, 0xe8:0, 0xe1:0, 0xa8:0, 0x36:0, 0xe6:0, 0x00:0, 0xd0:0, 0x9a:0, 0x28:0,0xfc:0,0x24:0,0xdf:0,0x9d:0,0xab:0,0xee:0,0x4:0,0x15:0,0x3b:0}
    PDRs = {0xe7:0, 0xf5:0, 0xe8:0, 0xe1:0, 0xa8:0, 0x36:0, 0xe6:0, 0x00:0, 0xd0:0, 0x9a:0, 0x28:0,0xfc:0,0x24:0,0xdf:0,0x9d:0,0xab:0,0xee:0,0x4:0,0x15:0,0x3b:0}
    def __init__(self):
        # log
        log.info("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',                     # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]
        f1 = open('C:/DelayTest/result.csv', 'w')
        wr1 = csv.writer(f1)
        wr1.writerow(["MAC", "COUNT", "Current Delay(ms)", "Avg Delay(ms)", "Answer", "ASN", "Aggregation"])
        f2 = open('C:/DelayTest/PDR.csv', 'w')
        wr2 = csv.writer(f2)
        MAC_header = ""
        for key in self.PDRs:
            MAC_header += "%x," %(key)
        MAC_header += "PDR rate\n"
        f2.write(MAC_header)
        f1.close()
        f2.close()

    #======================== public ==========================================
    def getInfo(self, MAC, COUNT, CURRENT_DELAY, AVG_DELAY, ANSWER):
        return MAC, COUNT, CURRENT_DELAY, AVG_DELAY, ANSWER
    def parseInput(self,input):
        # log
        if log.isEnabledFor(logging.DEBUG):
            log.debug("received data {0}".format(input))
        
        # ensure input not short longer than header
        self._checkLength(input)
   
        headerBytes = input[:2]
        #asn comes in the next 5bytes.  
        
        asnbytes=input[2:7]
        (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes]))
        
        #source and destination of the message
        dest = input[7:15]
        
        #source is elided!!! so it is not there.. check that.
        source = input[15:23]
        
        if log.isEnabledFor(logging.DEBUG):
            a="".join(hex(c) for c in dest)
            log.debug("destination address of the packet is {0} ".format(a))
        
        if log.isEnabledFor(logging.DEBUG):
            a="".join(hex(c) for c in source)
            log.debug("source address (just previous hop) of the packet is {0} ".format(a))
        
        # remove asn src and dest and mote id at the beginning.
        # this is a hack for latency measurements... TODO, move latency to an app listening on the corresponding port.
        # inject end_asn into the packet as well
        input = input[23:]
        
        if log.isEnabledFor(logging.DEBUG):
            log.debug("packet without source,dest and asn {0}".format(input))
        
        # when the packet goes to internet it comes with the asn at the beginning as timestamp.
         
        # cross layer trick here. capture UDP packet from udpLatency and get ASN to compute latency.
        if len(input) >37:
            if self.CLICKER_MASK1 == ''.join(chr(i) for i in input[-4:]):
                #answer   = ''.join(chr(i) for i in input[-7:])
                answer = chr(input[-6])
                MAC = hex(input[-5])
                print('mac: ' + MAC)
                PDR = input[-7]
                if self.PDRs[input[-5]] != PDR:
                    self.PDRs[input[-5]] = PDR
                    self.COUNT += 1
                aux      = input[len(input)-14:len(input)-9]  # last 5 bytes of the packet are the ASN in the UDP latency packet
                diff     = self._asndiference(aux,asnbytes)   # calculate difference 
                timeinus = diff*self.MSPERSLOT                # compute time in ms
                SN       = input[len(input)-9:len(input)-7]   # SN sent by mote
                l3_source= "{0:x}{1:x}".format(input[len(input)-16], input[len(input)-15]) # mote id
                f1 = open('C:/DelayTest/result.csv', 'a')
                f2 = open('C:/DelayTest/PDR.csv', 'a')
                wr2 = csv.writer(f2)
                self.SUM += diff
                nth = ''.join(hex(i) for i in input[len(input)-14:len(input)-9])
                

                self.aggregation[input[-5]] += 1
                wr1 = csv.writer(f1)
                wr1.writerow([MAC, self.COUNT, diff * 10, self.SUM/self.COUNT * 10, answer, self.Calc_Asn(aux), self.aggregation[input[-5]]])
                PDRSum=0
                empty_str = ""
                for key in self.PDRs:
                    empty_str += "%d," %(self.PDRs[key])
                    PDRSum += self.PDRs[key]
                PDRrate = float(self.COUNT)/float(PDRSum)
                empty_str += '%f\n' %(PDRrate)
                f2.write(empty_str)
                f1.close()
                f2.close()
                f3 = open('C:/DelayTest/time.txt', 'r')
                now = time.localtime()
                now_time = now.tm_sec + (now.tm_min*60)
                txt_time = f3.readline()
                if len(txt_time) > 0 :
                    limit_time = int(txt_time)
                else :
                    limit_time = 0
                AnswerDir = 'C:\\DelayTest\\' + str(MAC) + '.csv' 
                
                if now_time < limit_time:
                    f4 = open(AnswerDir,'w')
                    wr = csv.writer(f4)
                    wr.writerow([MAC, answer, self.Calc_Asn(aux)])
                    f4.close()
                f3.close()
                pass
                # in case we want to send the computed time to internet..
                # computed=struct.pack('<H', timeinus)#to be appended to the pkt
                # for x in computed:
                    #input.append(x)
            else:
                # no udplatency
                # print input
                pass     
        else:
            pass      
        
        eventType='data'
        # notify a tuple including source as one hop away nodes elide SRC address as can be inferred from MAC layer header
        return eventType, (source, input)
        
 #======================== private =========================================
 
    def _asndiference(self,init,end):
      
       asninit = struct.unpack('<HHB',''.join([chr(c) for c in init]))
       asnend  = struct.unpack('<HHB',''.join([chr(c) for c in end]))
       if asnend[2] != asninit[2]: #'byte4'
          return 0xFFFFFFFF
       else:
           pass
        
       diff = 0
       if asnend[1] == asninit[1]:#'bytes2and3'
          return asnend[0]-asninit[0]#'bytes0and1'
       else:
          if asnend[1]-asninit[1]==1:##'bytes2and3'              diff  = asnend[0]#'bytes0and1'
              diff += 0xffff-asninit[0]#'bytes0and1'
              diff += 1
          else:   
              diff = 0xFFFFFFFF
       
       return diff

    def Calc_Asn(self, asn):
        result = 0
        for i in range(0,5):
            result += asn[i] * (256**i)
        return result