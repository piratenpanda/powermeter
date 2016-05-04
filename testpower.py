#!/usr/bin/env python
# -*- coding: utf-8 -*-

import visa, time
from pyvisa.highlevel import ascii 

rm = visa.ResourceManager('@py')
##list_of_insts = rm.list_resources()

my_test_inst = rm.open_resource('ASRL/dev/ttyACM0::INSTR', values_format=ascii)
print(my_test_inst.query("*IDN?"))

my_test_inst.write("ABORt")
my_test_inst.write("INITiate")
while(True):
    print(my_test_inst.read_raw())
    time.sleep(0.1)
