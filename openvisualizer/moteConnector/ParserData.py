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
    CLICKER_MASK1    = 'licke'
    SUM = 0.0
    COUNT = 0
    aggregation = {0x3b:0, 0xdf:0, 0x05:0, 0xfb:0, 0x15:0}
    PDRs = {0x15:0, 0xdf:0, 0x05:0, 0xfb:0, 0x15:0}
    def __init__(self):
        # log
        log.info("create instance")
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',                     # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]
    

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
            if self.CLICKER_MASK1 == ''.join(chr(i) for i in input[-5:]):
                #answer   = ''.join(chr(i) for i in input[-7:])
                answer = chr(input[-6])
                PDR = ord(answer[0])
                self.PDRs[source[7]] = PDR
                aux      = input[len(input)-14:len(input)-9]  # last 5 bytes of the packet are the ASN in the UDP latency packet
                diff     = self._asndiference(aux,asnbytes)   # calculate difference 
                timeinus = diff*self.MSPERSLOT                # compute time in ms
                SN       = input[len(input)-9:len(input)-7]   # SN sent by mote
                l3_source= "{0:x}{1:x}".format(input[len(input)-16], input[len(input)-15]) # mote id
                f = open('C:/DelayTest/result.txt', 'a')
                f2 = open('C:/DelayTest/aggregations.txt', 'a')
                f3 = open('C:/DelayTest/PDR.txt', 'a')
                self.COUNT += 1
                self.SUM += diff
                nth = ''.join(hex(i) for i in input[len(input)-14:len(input)-9])
                MAC = hex(source[7])
                
                f.write("MAC : %x , COUNT : %i , Current Delay : %i , Avg Delay : %.2f, Answer : %s Nth : %s\n" %(source[7], self.COUNT, diff, self.SUM/self.COUNT, answer, aux))
                self.aggregation[source[7]] += 1
                for key in self.aggregation:
                    f2.write("%x : %i " %(key, self.aggregation[key]))
                PDRSum=0
                for key in self.PDRs:
                    f3.write("%x pdr : %d, " %(key, self.PDRs[key]))
                    PDRSum += self.PDRs[key]
                PDRrate = float(PDRSum)/float(self.COUNT)
                f3.write("\n PDR rate: %f\n" %(PDRrate))
                f2.write("\n")
                f.close()
                f2.close()
                f3.close()
                f5 = open('C:/DelayTest/time.txt', 'r')
                now = time.localtime()
                now_time = now.tm_sec + (now.tm_min*60)
                limit_time = int(f5.readline())
                AnswerDir = 'C:\\DelayTest\\' + str(MAC) + '.csv' 

                if now_time < limit_time:
                    f4 = open(AnswerDir,'w')
                    wr = csv.writer(f4)
                    wr.writerow([MAC, answer, self.Calc_Asn(aux)])
                    f4.close()
                f5.close()
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