import os
import re
from time import *
from base64 import b64encode as doggy


Test_String = "This is a blank string"
obvious_ip_address = "192.168.0.1"
obvious_port_number = 4444

split_value_1, split_value_2 = ("Hello","World")
split_value_3, split_value_4 = 7

function_return_value = Test_String.replace("blank","fucking")
string_with_function = "{aa} {bb} with things".format(aa="aaa",bb="bbb")

split_value_4 = 22


print(obvious_ip_address)
print(string_with_function)


def tuesday(apples):
    apples = 1234
    return apples

class Orange:
    def __init__(self):
        self.apples = 1234
        pass
    def test_call(self,punk):
        return self.apples


tuesday(split_value_2)
tuesday(split_value_3)
gg = Orange()
gg.test_call(12345)


split_value_2 = 55567

"""apples
and
Oranges
Also pears"""