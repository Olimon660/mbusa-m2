import json
import socket

print('Server started.')

NUM_OF_TURNS = 10
# VICTORIES_CONDITIONS = ['Max', 'Min', 'Linear', 'Quadratic', 'ZeroM', 'SumNeg', 'SumPos']
# VICTORIES_CONDITIONS = ['Max', 'Min']
# VICTORIES_CONDITIONS = ['ZeroM']
VICTORIES_CONDITIONS1 = ['Min']
VICTORIES_CONDITIONS2 = ['Min']
# VICTORIES_CONDITIONS2 = ['SumNeg', 'SumPos']
# VICTORIES_CONDITIONS1 = ['Linear']
# VICTORIES_CONDITIONS2 = ['Min']
result_table = {}

p1_name = 'assign_stupid2_bkp.py'
p2_name = 'player_new_two.py'


def send_to_server(js):
    """Open socket and send the json string js to server with EOM appended, and wait
    for \n terminated reply.
    js - json object to send to server
    """
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('128.250.106.25', 5002))
    clientsocket.send("""{}EOM""".format(js).encode('utf-8'))
    data = ''
    while data == '' or data[-1] != "\n":
        data += clientsocket.recv(1024).decode('utf-8')
    # print(data)
    parsed = json.loads(data[8:])
    result_table[(parsed[1][1], parsed[2][1])] = parsed[-2]
    print(json.dumps(parsed, indent=4, sort_keys=True))

    clientsocket.close()


p1 = open(p1_name, 'r').read()
p2 = open(p2_name, 'r').read()

print('Tested Player goes first')
for vt1 in VICTORIES_CONDITIONS1:
    for vt2 in VICTORIES_CONDITIONS2:
        send_to_server(json.dumps({"cmd": "TEST", "syn": 12, "name": "The Last Jedi", "data": p1,
                                   "data2": p2, "vt1": vt1, "vt2": vt2}))
print(str(result_table))
result_table = {}

print('Tested Player goes second')
for vt1 in VICTORIES_CONDITIONS1:
    for vt2 in VICTORIES_CONDITIONS2:

        send_to_server(json.dumps({"cmd": "TEST", "syn": 12, "name": "The Last Jedi", "data": p2,
                                   "data2": p1, "vt1": vt2, "vt2": vt1}))
print(str(result_table))

print('Simulation finished')
