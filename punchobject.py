# -*- coding: utf-8 -*-
class PunchObject(object):
  fields = 1
  def __init__(self, content):
    self._content = content
    self._types = {"\x01": 'SYN', "\x02": 'ACK', '\x03': 'MSG', "\x04": 'JSON'}
    self._types_inv = {}
    self.build()
  def __str__(self):
    s=""
    for (k,v) in self.__dict__.items():
      if not '_' in k and v:
	s+="%s: %s" % (k, self._content[self.fields:])
    return s
  
  def build(self):
    for k in self._types.keys():
      self.__dict__[self._types[k]] = False
    for c in self._content[0:self.fields]:
      if c in self._types:
	self.__dict__[self._types[c]] = True

  def compose(self, flag, data):
    #if len(self._types_inv)==0:
    self._types_inv = dict( (v,k) for k, v in self._types.iteritems())
    return str("%s%s" % (self._types_inv[flag], data))
  