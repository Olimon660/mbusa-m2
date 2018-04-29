from send_utility import *
import json

p1_name = 'player_new_one.py'
p5_name = 'player_new.py'
pe_name = 'player_new_e.py'

p1 = open(p1_name, 'r').read()
p5 = open(p5_name, 'r').read()
pe = open(pe_name, 'r').read()
pi = open('player_n10m.py').read()


send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Evil Again?", "data": pe}))

send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "10000 Bugs", "data": p5}))

send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Sleep No More 5cc3544+pi", "data": p1}))

send_to_server(json.dumps({"cmd": "ADD", "syn": 12, "name": "Sleep No More pi", "data": pi}))



send_to_server(json.dumps({"cmd": "DEL", "syn": 12, "name": "10000 Bugs", "data": p5}))

send_to_server(json.dumps({"cmd": "DEL", "syn": 12, "name": "Sleep No More pi", "data": p1}))

send_to_server(json.dumps({"cmd": "DEL", "syn": 12, "name": "Evil Again?", "data": p5}))

send_to_server(json.dumps({"cmd": "DEL", "syn": 6, "name": "000", "data": p1}))
