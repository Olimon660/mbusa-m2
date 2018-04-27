import numpy as np
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
                                E.g. enemy_col_cond['Max'] = 'Simon'
                                it means Simon column may have victory conditions of Max
        turn_num (int): the number of turns at the moment
        played_data (dict): Keep track of what this player has played

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

    unique_max_col_count = dd(int)
    unique_min_col_count = dd(int)

    EPSILON = 0.00001
    BOUNDARY = 1023.0

    def take_turn(self, data, victory):
        """Must return a dictionary with the same keys as data, and with single float values
        in the range [-1023, 1023].
        data is a dictionary with column names as keys and a list of floats
        as the column values of the game so far.
        victory the condition you should try and achieve and is a tuple (a,b) where
        a is victory condition (string)
        b is a column name (string - one of data.keys()).
        """
        # update the data/v_col/v_condition attributes of the player class
        self.data = data
        (self.v_condition, self.v_col) = victory

        # update the turn number
        self.turn_num = (len(self.data[list(self.data.keys())[0]])-1)//2+1

        # check if the player's row is entered before or after the opponent
        # even if two rows are inserted together at each turn, there is an order
        if self.turn_num < 3:
            self.is_first_to_move = self.check_is_first()

        # check if there is any clue for opponent's victory condition and column
        self.check_enemy_col()

        # based on the victory condition, choose one of the strategies
        if self.v_condition == 'Max':
            return self.max_strategy()
        if self.v_condition == 'Min':
            return self.min_strategy()
        if self.v_condition == 'ZeroM':
            return self.zero_m_strategy()
        if self.v_condition == 'Linear':
            # return self.linear_strategy()
            return self.linear2()
        if self.v_condition == 'Quadratic':
            # return self.quadratic_strategy()
            return self.quad2()
        if self.v_condition == 'SumPos':
            return self.sum_pos_strategy()
        if self.v_condition == 'SumNeg':
            return self.sum_neg_strategy()

        # should not reach here. for unknown victory conditions we return 1.0 for all
        return {k: 1.0 for k in data}

    def check_is_first(self):
        for col in self.data.keys():
            if self.data[col][1::2] != self.played_data[col]:
                return False
        return True

    def max_strategy(self):
        """
        Need to take both max and min in the column
        :return:
        """
        ret_d = dict()
        ret_d[self.v_col] = round(1023.0 - (self.turn_num-1) * self.EPSILON, 5)

        if self.turn_num == 10:
            ret_d[self.v_col] = self.next_after(self.get_next_unique_max(), -1)

            # assign the next max to two other columns
            next_max = self.get_next_unique_max()
            count = 0
            for k in self.played_data:
                if k != self.v_col and self.played_data[k][-1] > 0:
                    ret_d[k] = next_max
                    count += 1
                if count > 1:
                    break

        # if self.turn_num == 10 and 'Max' in self.enemy_col_cond:
        #     ret_d[self.v_col] = self.next_after(self.get_current_unique_max(), -1)

        self.counter_enemy_mix(ret_d)

        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def min_strategy(self):
        """
        Need to take both max and min in the column
        :return:
        """
        ret_d = dict()
        ret_d[self.v_col] = round(1023.0 - (self.turn_num-1) * self.EPSILON, 5)

        if self.turn_num == 10:
            ret_d[self.v_col] = self.next_after(self.get_next_unique_min(), 1)

            # assign the next min to two other columns
            next_min = self.get_next_unique_min()
            count = 0
            for k in self.played_data:
                if k != self.v_col and self.played_data[k][-1] > 0:
                    ret_d[k] = next_min
                    count += 1
                if count > 1:
                    break

        # if self.turn_num == 10 and 'Min' in self.enemy_col_cond:
        #     ret_d[self.v_col] = self.next_after(self.get_current_unique_min(), -1)

        self.counter_enemy_mix(ret_d)

        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def zero_m_strategy(self):
        # choose two other disguise col if not set
        ret_d = dict()
        current_sum = np.sum(self.data[self.v_col])
        if current_sum <= abs(0.000001 * len(self.data[self.v_col])):
            ret_d[self.v_col] = 0.0000001
        elif current_sum < 0:
            ret_d[self.v_col] = current_sum + self.EPSILON  # or random(0,1023)?
        else:
            ret_d[self.v_col] = -current_sum - self.EPSILON
        if self.turn_num == 10:
            # take a guess

            if self.is_first_to_move:
                e_col = self.data[self.v_col][2::2]
            else:
                e_col = self.data[self.v_col][1::2]

            guess = stats.mode(e_col)[0][0]

            if 'Max' in self.enemy_col_cond and self.enemy_col_cond['Max'] == self.v_col:
                guess = self.get_next_unique_max()
            if 'Min' in self.enemy_col_cond and self.enemy_col_cond['Min'] == self.v_col:
                guess = self.get_next_unique_min()

            ret_d[self.v_col] = min(max(-current_sum-guess, -self.BOUNDARY), self.BOUNDARY)
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def linear_strategy(self):
        ret_d = dict()
        if self.turn_num <= 1:
            ret_d[self.v_col] = 0.0
        # elif self.turn_num == 10:
        #     ret_d[self.v_col] = self.BOUNDARY
        else:
            slope, intercept, r_value, p_value, std_err = \
                linregress(range((self.turn_num-1)*2+1), self.data[self.v_col])
            ret_d[self.v_col] = max(-self.BOUNDARY, min(intercept + slope * ((self.turn_num-1)*2+1), self.BOUNDARY))

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def linear2(self):
        ret_d = dict()
        # ret_d[self.v_col] = 1023.0
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def quad2(self):
        ret_d = dict()
        # ret_d[self.v_col] = 1023.0
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def quadratic_strategy(self):
        ret_d = dict()
        if self.turn_num <= 1:
            ret_d[self.v_col] = 0.0
        # elif self.turn_num == 10:
        #     ret_d[self.v_col] = self.BOUNDARY
        else:
            x = np.array(range((self.turn_num-1)*2+1))
            slope, intercept, r_value, p_value, std_err = \
                linregress(list(x*x), self.data[self.v_col])
            y = np.sqrt(intercept + slope * ((self.turn_num-1)*2+1))
            ret_d[self.v_col] = max(-self.BOUNDARY, min(y, self.BOUNDARY))

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def sum_pos_strategy(self):
        ret_d = dict()
        if np.sum(self.data[self.v_col]) > 0:
            ret_d[self.v_col] = self.BOUNDARY
        elif self.turn_num <= 3:
            ret_d[self.v_col] = self.BOUNDARY - (self.turn_num - 1) * self.EPSILON
        else:
            ret_d[self.v_col] = self.BOUNDARY
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def sum_neg_strategy(self):
        ret_d = dict()
        if np.sum(self.data[self.v_col]) < 0:
            ret_d[self.v_col] = -self.BOUNDARY
        elif self.turn_num <= 3:
            ret_d[self.v_col] = -self.BOUNDARY + (self.turn_num - 1) * self.EPSILON
        ret_d[self.v_col] = -self.BOUNDARY
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def check_enemy_col(self):
        """
        :return:
        """
        if self.turn_num <= 3:
            return

        if self.turn_num == 9:
            sorted_max = sorted(self.unique_max_col_count.items(), key=lambda x: x[1], reverse=True)
            sorted_min = sorted(self.unique_min_col_count.items(), key=lambda x: x[1], reverse=True)
            if sorted_max and sorted_max[0][1] >= 4:
                self.enemy_col_cond['Max'] = sorted_max[0][0]
            if sorted_min and sorted_min[0][1] >= 4:
                self.enemy_col_cond['Min'] = sorted_min[0][0]

        if self.turn_num == 4:
            for col in self.data:
                if self.is_first_to_move:
                    target = np.array(self.data[col][-1])
                else:
                    target = np.array(self.data[col][-2])
                arr = np.array(self.data[col][:6])    # first 5 numbers
                slope, intercept, r_value, p_value, std_err = \
                    linregress(range(len(arr)), arr)

                pred = max(-self.BOUNDARY, min(intercept + slope * ((self.turn_num-2)*2+1), self.BOUNDARY))
                if abs(pred - target) < 100:
                    self.enemy_col_cond['Linear'] = col

                arr_2 = arr * arr
                slope, intercept, r_value, p_value, std_err = \
                    linregress(range(len(arr_2)), arr_2)
                pred = max(-self.BOUNDARY, min(intercept + slope * ((self.turn_num - 2) * 2 + 1), self.BOUNDARY))
                if abs(pred - target) < 100:
                    self.enemy_col_cond['Quadratic'] = col
                    continue

                if np.mean(arr) < 0.000001:
                    self.enemy_col_cond['ZeroM'] = col
                    continue

        if self.turn_num == 3:
            for col in self.data:
                if col != self.v_col:
                    if self.is_first_to_move:
                        arr = np.array(self.data[col][2::2])
                    else:
                        arr = np.array(self.data[col][1::2])
                    if (arr == 1023.0).all():
                        self.enemy_col_cond['SumPos'] = col
                    if (arr == -1023.0).all():
                        self.enemy_col_cond['SumNeg'] = col

    def counter_enemy_mix(self, ret_d):
        count = 0

        current_max = self.get_current_unique_max()
        current_min = self.get_current_unique_min()

        if self.turn_num == 10:
            if 'Max' in self.enemy_col_cond:
                if current_max > 0:
                    ret_d[self.enemy_col_cond['Max']] = current_max
                else:
                    ret_d[self.enemy_col_cond['Max']] = self.next_after(self.get_next_unique_max(), -1)
                next_max = self.get_next_unique_max()
                for k in self.data:
                    if k not in ret_d:
                        ret_d[k] = next_max
                        next_max = self.get_next_unique_max()

            if 'Min' in self.enemy_col_cond:
                if current_min < 0:
                    ret_d[self.enemy_col_cond['Min']] = current_min
                else:
                    ret_d[self.enemy_col_cond['Min']] = self.next_after(self.get_next_unique_min(), 1)
                next_min = self.get_next_unique_min()
                for k in self.data:
                    if k not in ret_d:
                        ret_d[k] = next_min
                        next_min = self.get_next_unique_min()

        for k in self.data.keys():
            if k not in ret_d:
                current_sum = np.sum(self.data[k])

                if self.turn_num == 1 or current_sum == 0:
                    if count % 2:
                        ret_d[k] = -self.BOUNDARY
                    else:
                        ret_d[k] = self.BOUNDARY
                else:
                    # if current unique max/min in this col, make it not unique
                    if self.turn_num != 10 and current_max > 0 and current_max in self.data[k]:
                        ret_d[k] = current_max
                        # increment the col count
                        self.unique_max_col_count[k] += 1
                    elif self.turn_num != 10 and current_min < 0 and current_min in self.data[k]:
                        ret_d[k] = current_min
                        # increment the col count
                        self.unique_min_col_count[k] += 1
                    else:
                        if count % 2:
                            ret_d[k] = -self.BOUNDARY
                        else:
                            ret_d[k] = self.BOUNDARY
                        if self.turn_num > 2:
                            if 'SumPos' in self.enemy_col_cond and self.enemy_col_cond['SumPos'] == k:
                                ret_d[k] = -self.BOUNDARY
                            elif 'SumNeg' in self.enemy_col_cond and self.enemy_col_cond['SumNeg'] == k:
                                ret_d[k] = self.BOUNDARY
                            else:
                                ret_d[k] = np.random.uniform(-1000.0, 1000.0)

                    # following two lines may need tweak

                    # if 'SumNeg' in self.enemy_col_cond and self.enemy_col_cond['SumNeg'] == k:
                    #     ret_d[k] = self.BOUNDARY
                    # if 'SumPos' in self.enemy_col_cond and self.enemy_col_cond['SumPos'] == k:
                    #     ret_d[k] = -self.BOUNDARY

                count += 1

        for k in ret_d:
            ret_d[k] = round(float(ret_d[k]), 5)

        return ret_d

    def get_current_unique_max(self):
        nums_count = dd(int)
        for col in self.data.keys():
            for number in self.data[col]:
                nums_count[number] += 1

        current_max = -self.BOUNDARY
        for num in sorted(nums_count.keys(), reverse=True):
            if nums_count[num] == 1:
                current_max = num
                break

        return current_max

    def get_current_unique_min(self):
        nums_count = dd(int)
        for col in self.data.keys():
            for number in self.data[col]:
                nums_count[number] += 1

        current_min = self.BOUNDARY
        for num in sorted(nums_count.keys()):
            if nums_count[num] == 1:
                current_min = num
                break

        return current_min

    def get_next_unique_max(self):
        m = self.BOUNDARY
        while m >= -self.BOUNDARY:
            for col in self.data:
                if m in self.data[col]:
                    m = self.next_after(m, -1)
                    break
            else:
                return m
        return m

    def get_next_unique_min(self):
        m = -self.BOUNDARY
        while m <= self.BOUNDARY:
            for col in self.data:
                if m in self.data[col]:
                    m = self.next_after(m, 1)
                    break
            else:
                return m
        return m

    def next_after(self, num, direction):
        return round(num + direction * self.EPSILON, 5)

    def __repr__(self):
        """
        Print the representation of the player
        :return:
        """
        return str(self.data) + '\n' + self.v_col + ' ' + self.v_condition
