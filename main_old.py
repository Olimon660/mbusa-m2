from assign_stupid2_bkp import Player as Player
from player_minimal import Player as Player_Min
from scipy.stats.stats import pearsonr
import numpy as np
import random

print('Server started.')

NUM_OF_TURNS = 10
VICTORIES_CONDITIONS = ['Max']
COLUMN_NAMES = ('A', 'B', 'C', 'D', 'E')


def check_win_state(data, victory):
    (player_col, v_condition) = victory
    if v_condition == 'Max':
        max_player = max(data[player_col])
        max_all = 0
        max_count = 1
        for v in data.values():
            col_max = max(v)
            if max_all < col_max:
                max_all = col_max
                max_count = 1
            elif max_all == col_max:
                max_count += 1
        return max_all == max_player and max_count == 1
    elif v_condition == 'Min':
        min_player = min(data[player_col])
        min_all = 0
        min_count = 1
        for v in data.values():
            col_min = min(v)
            if min_all > col_min:
                min_all = col_min
                min_count = 1
            elif min_all == col_min:
                min_count += 1
        return min_all == min_player and min_count == 1
    elif v_condition == 'Linear':
        (r, p) = pearsonr(data[player_col], range(NUM_OF_TURNS*2))
        return p <= 0.05 and r >= 0.9
    elif v_condition == 'Quadratic':
        a = np.array(data[player_col])
        a = list(a*a)
        (r, p) = pearsonr(a, range(NUM_OF_TURNS*2))
        return p <= 0.05 and r >= 0.9
    elif v_condition == 'ZeroM':
        return -0.000001 < np.mean(data[player_col]) < 0.000001
    elif v_condition == 'SumNeg':
        return np.sum(data[player_col]) < 0
    elif v_condition == 'SumPos':
        return np.sum(data[player_col]) > 0
    else:
        raise SystemError


column1 = random.choice(COLUMN_NAMES)
column2 = random.choice(list(set(COLUMN_NAMES)-set([column1])))

res = ''
for victory_condition1 in VICTORIES_CONDITIONS:
    for victory_condition2 in VICTORIES_CONDITIONS:
        game_state = {}
        for c in COLUMN_NAMES:
            game_state[c] = [0]

        p1 = Player()
        p2 = Player_Min()

        for i in range(NUM_OF_TURNS):
            turn_data1 = p1.take_turn(game_state, (victory_condition1, column1))

            turn_data2 = p2.take_turn(game_state, (victory_condition2, column2))

            for c in turn_data1:
                game_state[c].append(turn_data1[c])
            for c in turn_data2:
                game_state[c].append(turn_data2[c])

        print(p1)
        print(p2)

        # check win condition
        win1 = check_win_state(game_state, (column1, victory_condition1))
        win2 = check_win_state(game_state, (column2, victory_condition2))

        res += str(victory_condition1)+',' + str(victory_condition2) + '\t'
        if win1 and win2 or not win1 and not win2:
            print('The game is a draw')
            res += '0\n'
        elif win1:
            print('player 1 won')
            res += '1\n'
        else:
            print('player 2 won')
            res += '2\n'

print(res)
print('Simulation finished')
