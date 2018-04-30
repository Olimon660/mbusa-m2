from send_utility import *
import json

p1 = open('player_new_one.py', 'r').read()
p2 = open('player_new_two.py', 'r').read()
p3 = open('player_n10m.py', 'r').read()

pi = open('player_n10m.py').read()
pm = open('assign_stupid2_bkp.py').read()

send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Sleep No More The Beauty 1", "data": p1}))

send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Sleep No More The Beauty 2", "data": p2}))

send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Sleep No More The Beauty 3", "data": p3}))

send_to_server(json.dumps({"cmd": "ADD", "syn": 1, "name": "Here Comes the Old B", "data": pm}))


# send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Sleep No More pi", "data": pi}))



send_to_server(json.dumps({"cmd": "DEL", "syn": 12, "name": "10000 Bugs", "data": p1}))

send_to_server(json.dumps({"cmd": "DEL", "syn": 12, "name": "Sleep No More 5cc3544", "data": p1}))

send_to_server(json.dumps({"cmd": "DEL", "syn": 12, "name": "Evil Again?", "data": p1}))

send_to_server(json.dumps({"cmd": "DEL", "syn": 6, "name": "000", "data": p1}))
