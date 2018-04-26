import numpy as np
from scipy.stats.stats import pearsonr
from scipy.stats.stats import linregress
from collections import defaultdict as dd
from scipy import stats


class Player:
    """
    The player class of syndicate 12 - The Last Jedi
    Group members include: Ernest, Iris, Junyi, Simon, Yan
    This players tries to achieve the victory condition as well as defeat others.
    Enemy counter strategies are grouped so that we have more generalized strategies which work for more than one case.
    E.g. counter_enemy_max tries to defeat others no matter what strategies the opponent has.

    Attributes:
        v_condition (str): The victory condition of the player
        v_col (str): The victory column of the player
        is_first_to_move (bool): if the player has the odd number of rows or even
                                enemy_col_cond (dict): Possible opponent's victory condition and columns.
                                E.g. enemy_col_cond['Max'] = ['Ernest', 'Simon']
                                it means Ernest and Simon columns may have victory conditions of Max
        turn_num (int): the number of turns at the moment
        played_data (dict): Keep track of what this player has played
        enemy_first_turn_1023 (bool): If the opponent put 1023.0 in the first turn
        enemy_first_turn_neg_1023 (bool): If the opponent put -1023.0 in the first turn

    TODO:
        * add documentation for each strategy later
    """
    v_condition = None
    v_col = None
    data = dict()
    is_first_to_move = True
    enemy_col_cond = dict()
    turn_num = 0
    played_data = dd(list)
    enemy_first_turn_1023 = False
    enemy_first_turn_neg_1023 = False

    def take_turn(self, data, victory):
        """Must return a dictionary with the same keys as data, and with single float values
        in the range [-1023, 1023].
        data is a dictionary with column names as keys and a list of floats
        as the column values of the game so far.
        victory the condition you should try and achieve and is a tuple (a,b) where
        a is victory condition (string)
        b is a column name (string - one of data.keys()).
        """
        self.data = data
        (self.v_condition, self.v_col) = victory

        self.turn_num = (len(self.data[list(self.data.keys())[0]])-1)//2+1

        self.is_first_to_move = self.check_is_first()
        if not self.enemy_col_cond:
            self.check_enemy_col()

        if self.v_condition == 'Max':
            return self.max_strategy()
        if self.v_condition == 'Min':
            return self.min_strategy()
        if self.v_condition == 'ZeroM':
            return self.zero_m_strategy()
        if self.v_condition == 'Linear':
            return self.linear_strategy()
        if self.v_condition == 'Quadratic':
            return self.quadratic_strategy()
        if self.v_condition == 'SumPos':
            return self.sum_pos_strategy()
        if self.v_condition == 'SumNeg':
            return self.sum_neg_strategy()

        return {k: 1.0 for k in data}

    def check_is_first(self):
        for col in self.data.keys():
            if self.data[col][::2] != self.played_data[col]:
                return False
        return True

    def max_strategy(self):
        ret_d = dict()

        if self.turn_num == 1:
            ret_d[self.v_col] = -1023.0
        elif self.turn_num == 2:
            if 1023.0 in self.data[self.v_col]:
                ret_d[self.v_col] = -1023.0
                self.enemy_first_turn_1023 = True
            else:
                ret_d[self.v_col] = np.random.uniform(-500, 500)
        elif 3 <= self.turn_num <= 9:
            if self.enemy_first_turn_1023:
                ret_d[self.v_col] = -1023.0
            else:
                ret_d[self.v_col] = np.random.uniform(-500, 500)
        elif self.turn_num == 10 and not self.enemy_first_turn_1023:
            ret_d[self.v_col] = 1023.0
        else:
            ret_d[self.v_col] = np.random.uniform(-500, 500)

        self.counter_enemy_max(ret_d)

        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def min_strategy(self):
        ret_d = dict()

        if self.turn_num == 1:
            ret_d[self.v_col] = 1023.0
        elif self.turn_num == 2:
            if -1023.0 in self.data[self.v_col]:
                ret_d[self.v_col] = 1023.0
                self.enemy_first_turn_neg_1023 = True
            else:
                ret_d[self.v_col] = np.random.uniform(-500, 500)
        elif 3 <= self.turn_num <= 9:
            if self.enemy_first_turn_neg_1023:
                ret_d[self.v_col] = 1023.0
            else:
                ret_d[self.v_col] = np.random.uniform(-500, 500)
        elif self.turn_num == 10 and not self.enemy_first_turn_neg_1023:
            ret_d[self.v_col] = -1023.0
        else:
            ret_d[self.v_col] = np.random.uniform(-500, 500)

        self.counter_enemy_min(ret_d)

        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def zero_m_strategy(self):
        # choose two other disguise col if not set
        ret_d = dict()
        current_sum = np.sum(self.data[self.v_col])
        if -0.000001 * len(self.data[self.v_col]) <= current_sum <= 0.000001 * len(self.data[self.v_col]):
            ret_d[self.v_col] = 0.0000001
        elif current_sum < 0:
            ret_d[self.v_col] = 1023.0  # or random(0,1023)?
        else:
            ret_d[self.v_col] = -1023.0
        if self.turn_num == 10:
            # take a guess
            if self.is_first_to_move:
                e_col = self.data[self.v_col][1::2]
            else:
                e_col = self.data[self.v_col][::2]
            mode = stats.mode(e_col)[0][0]

            ret_d[self.v_col] = min(max(-current_sum-mode, -1023.0), 1023.0)
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def linear_strategy(self):
        ret_d = dict()
        if self.turn_num <= 1:
            ret_d[self.v_col] = 1.0
        # elif self.turn_num == 10:
        #     ret_d[self.v_col] = 1023.0
        else:
            slope, intercept, r_value, p_value, std_err = \
                linregress(range((self.turn_num-1)*2+1), self.data[self.v_col])
            ret_d[self.v_col] = max(-1023.0, min(intercept + slope * ((self.turn_num-1)*2+1), 1023.0))

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def quadratic_strategy(self):
        ret_d = dict()
        if self.turn_num <= 1:
            ret_d[self.v_col] = 1.0
        # elif self.turn_num == 10:
        #     ret_d[self.v_col] = 1023.0
        else:
            x = np.array(range((self.turn_num-1)*2+1))
            slope, intercept, r_value, p_value, std_err = \
                linregress(list(x*x), self.data[self.v_col])
            y = np.sqrt(intercept + slope * ((self.turn_num-1)*2+1))
            ret_d[self.v_col] = max(-1023.0, min(y, 1023.0))

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def sum_pos_strategy(self):
        ret_d = dict()
        if np.sum(self.data[self.v_col]) > 0:
            ret_d[self.v_col] = 1023.0
        else:
            ret_d[self.v_col] = 1023.0 - self.turn_num

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def sum_neg_strategy(self):
        ret_d = dict()
        if np.sum(self.data[self.v_col]) < 0:
            ret_d[self.v_col] = -1023.0
        else:
            ret_d[self.v_col] = -1023.0 + self.turn_num
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def check_enemy_col(self):
        if self.turn_num <= 3:
            return
        for col in self.data:
            if col != self.v_col:
                arr = np.array(self.data[col])
                (r, p) = pearsonr(arr, range(len(arr)))
                if p <= 0.05 and r >= 0.9:
                    self.enemy_col_cond[col] = 'Linear'
                    continue
                arr_2 = arr * arr
                (r, p) = pearsonr(arr_2, range(len(arr)))
                if p <= 0.05 and r >= 0.9:
                    self.enemy_col_cond[col] = 'Quadratic'
                    continue
                if np.mean(arr) < 0.000001:
                    self.enemy_col_cond[col] = 'ZeroM'
                    continue

        for col in self.data:
            if col != self.v_col:
                if self.is_first_to_move:
                    arr = np.array(self.data[col][1::2])
                else:
                    arr = np.array(self.data[col][::2])
                if (arr > 0).all():
                    self.enemy_col_cond[col] = 'SumPos'
                if (arr < 0).all():
                    self.enemy_col_cond[col] = 'SumNeg'

    def counter_enemy_max(self, ret_d):
        for k in self.data.keys():
            if k not in ret_d:
                current_sum = np.sum(self.data[k])
                if current_sum == 0:
                    ret_d[k] = -1023.0
                else:
                    ret_d[k] = np.random.uniform(-100.0, 100.0)
                if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumNeg':
                    ret_d[k] = 1022.0
                if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumPos':
                    ret_d[k] = -1023.0

        return ret_d

    def counter_enemy_min(self, ret_d):
        for k in self.data.keys():
            if k not in ret_d:
                current_sum = np.sum(self.data[k])
                if current_sum == 0:
                    ret_d[k] = 1023.0
                else:
                    ret_d[k] = np.random.uniform(-100.0, 100.0)
                if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumNeg':
                    ret_d[k] = 1023.0
                if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumPos':
                    ret_d[k] = -1022.0

        return ret_d

    def counter_enemy_mix(self, ret_d):
        count = 0
        for k in self.data.keys():
            if k not in ret_d:
                current_sum = np.sum(self.data[k])
                if count % 2:
                    if self.turn_num == 1 or current_sum == 0:
                        ret_d[k] = -1023.0
                    else:
                        ret_d[k] = np.random.uniform(-100.0, 100.0)
                    if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumNeg':
                        ret_d[k] = 1023.0
                    if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumPos':
                        ret_d[k] = -1023.0
                else:
                    if self.turn_num == 1 or current_sum == 0:
                        ret_d[k] = 1023.0
                    else:
                        ret_d[k] = np.random.uniform(-100.0, 100.0)
                    if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumNeg':
                        ret_d[k] = 1023.0
                    if k in self.enemy_col_cond and self.enemy_col_cond[k] == 'SumPos':
                        ret_d[k] = -1023.0

                count += 1

        return ret_d

    def __repr__(self):
        """
        Print the representation of the player
        :return:
        """
        return str(self.data) + '\n' + self.v_col + ' ' + self.v_condition
