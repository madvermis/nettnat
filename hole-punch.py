# -*- coding: utf-8 -*-
import sys
import socket
from select import select
import json, time, random
from punchobject import PunchObject

class Endpoint(object):
  track_dict = {}
  session_name = []
  SERVER_PORT = 60000
  SERVER_IP = '192.43.193.103'
  def __init__(self, session_name):
    self.session_name=session_name
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setblocking(0)
    self.s.settimeout(5)
    self.rand = random.SystemRandom()
    prt = self.rand.randint(20000,20005)
    self.s.bind(('0.0.0.0', prt))
    print "bound to port ", prt
    
  def send_request(self, server_ip, server_port, offset):
    self.SERVER_PORT = server_port
    self.SERVER_IP = server_ip
    self.s.sendto("%s,%d" % (self.session_name, offset) , (server_ip, server_port))
    data,addr=self.s.recvfrom(1024)
    self.dat = PunchObject(data)
    if self.dat.JSON:
      self.track_dict = json.loads(data[1:])
    
  def connect_endpoint(self, remote_name):
    """connect to another endpoint"""
    acc = 0.5 #TODO: implement sleep "growth"
    print self.track_dict
    connected = False
    synned = False
    remote_offset = None
    my_pub_offset = None
    syn_time=0
    ack_time=0
    self.dat = PunchObject("")
    for count in xrange(550):
      print "versuch %s" % count,
      r,w,x = select([self.s], [self.s], [], 0)
      if w:
	if count%4==0:
	  if my_pub_offset!=None:
	    self.send_request(self.SERVER_IP, self.SERVER_PORT, my_pub_offset)
	  else:
	    self.send_request(self.SERVER_IP, self.SERVER_PORT, 0)
	  r_addr = self.track_dict[remote_name]
	  r_offset = r_addr[2]
	  r_addr = r_addr[0], r_addr[1]
	  print "addr update"

	if connected:
	  print "send msg"
	  self.s.sendto(self.dat.compose('MSG', "%s offsetted msg: %s has public offset: %s" % (count, self.session_name, my_pub_offset)), (r_addr[0], r_addr[1]+remote_offset))
	  print r_addr[1]+remote_offset

        mx = (5 + r_offset + count*2)%65536
        mn =     (r_offset)%65536-count-5

        if mn>mx:
	  mn = mx+1
        if remote_offset==None:# and not connected:
	  print "probing offset in range: ", mn+r_addr[1], mx+r_addr[1]
	  for i in range(mn,mx):
	    #if count<20#if my_pub_offset == None or remote_offset==None:
	    if i!=my_pub_offset:
	      if not self.dat.SYN and not self.dat.ACK or my_pub_offset != None:
		msg = self.dat.compose('SYN', "%s %s,%s"%(count, self.session_name, i) )#SYN mit offset
		self.s.sendto(msg, (r_addr[0], r_addr[1]+i))
		syn_time = time.time()
	
	if self.dat.SYN:
	  for i in range(mn,mx):
	    if i!=my_pub_offset:
		msg = self.dat.compose('ACK',"%s %s,%s" % (count, self.session_name, my_pub_offset) )
		self.s.sendto(msg, (r_addr[0], r_addr[1]+i))
      if r:
        data,addr=self.s.recvfrom(1024)
        print "data: ", data
        self.dat = PunchObject(data)
	if self.dat.MSG:
	  num_nomsg = 0
	  print str(self.dat)
	elif self.dat.SYN:
	  print "recvd SYN ", str(self.dat)
	  if my_pub_offset == None and not self.session_name in data[1:]:
	    my_pub_offset = int(data[1:].split(",")[-1])
	    synned = True
	elif self.dat.ACK:
	  str_ro = data[1:].split(",")[-1]
	  if str_ro != "None":
	    remote_offset = int(str_ro)
	  ack_time = time.time()-syn_time
	  print "recvd ACK ", str(self.dat), ack_time
	  if synned:
	    connected = True
	    print "Connected."
	elif self.dat.JSON:
	  self.track_dict = json.loads(data[1:])
	else:
	  num_nomsg += 1
      time.sleep(acc)
    
if __name__ == "__main__":
  SERVER_IP = '192.43.193.103'
  SERVER_PORT = 60000
  name = sys.argv[1]
  connect_name = sys.argv[2]
  pt = Endpoint(name)
  pt.connect_endpoint(connect_name)
