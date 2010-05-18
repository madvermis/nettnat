# -*- coding: utf-8 -*-
import socket, json
from punchobject import PunchObject

class Tracker(object):
  track_dict = {'this': ['localhost', 60000, 0]}
  
  def __init__(self):
    self.p = PunchObject("")
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.bind(('0.0.0.0', self.track_dict['this'][1]))

  def listen(self):
    while 1:
      (data,addr)= self.s.recvfrom(1024)
      data = data.split(',')
      session_name = data[0]
      offset = data[1]
      self.track_dict[session_name] = [addr[0], int(addr[1]), int(offset)]
      msg = self.p.compose('JSON', json.dumps(self.track_dict))
      self.s.sendto( msg, addr)
      print self.track_dict


t = Tracker()
t.listen()