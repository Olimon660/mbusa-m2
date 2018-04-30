import numpy as np
from scipy.stats.stats import linregress
from collections import defaultdict as dd
from scipy import stats


class Player:
    """This is the Sleep No More series.
    Several players have been added to and deleted from the server.

    The player class of syndicate 12 - Sleep No More
    Group members include: Ernest Yau, Iris Li, Junyi Gao, Simon Cai, Yan Liu
    This player tries to achieve the victory condition as well as defeat others.
    Enemy counter strategies are grouped so that we have more generalized strategies which work for more than one case.

    This class file fully complies with PEP8.
    Some duplicate codes are retained for better readability.
    Some repetitive inline comments are omitted in the later strategy functions.

    Attributes:
        data (dict): the data object taken from take_turn will be assigned to this class attribute
        enemy_col_cond (dict): Possible opponent's victory condition and columns.
                                E.g. enemy_col_cond['Max'] = 'Simon'
                                it means Simon column may have victory conditions of Max
        is_first_to_move (bool): if the player has the odd number of rows or even
        played_data (dict): Keep track of what this player has played
        turn_num (int): the number of turns at the moment

        unique_max_col_count (dd(int)): the number of times a column contains the unique max
        unique_min_col_count (dd(int)): the number of times a column contains the unique min

        v_condition (str): The victory condition of the player
        v_col (str): The victory column of the player

        EPSILON (float): constant - the minimum change in a floating number
        BOUNDARY (float): constant - the boundary of numbers for this game
    """

    data = dict()
    enemy_col_cond = dict()
    is_first_to_move = True
    played_data = dd(list)
    turn_num = 0

    unique_max_col_count = dd(int)
    unique_min_col_count = dd(int)

    v_condition = None
    v_col = None

    EPSILON = 0.00001
    BOUNDARY = 1023.0

    def take_turn(self, data, victory):
        """This function is called by the server each turn to give 5 numbers to append to the game matrix.

        :param data: given by the server. current state of the game matrix.
        :param victory: (victory_condition, victory_column) tuple given by the server
        :return: a dict whose keys are the 5 columns with values to be added by this player for the current turn
        """
        # update class attributes
        self.data = data
        (self.v_condition, self.v_col) = victory
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
            return self.linear_strategy_special()
        if self.v_condition == 'Quadratic':
            return self.quadratic_strategy_special()
        if self.v_condition == 'SumPos':
            return self.sum_pos_strategy()
        if self.v_condition == 'SumNeg':
            return self.sum_neg_strategy()

        # should not reach here. for unknown victory conditions we return 1.0 for all
        return {k: 1.0 for k in data}

    def check_is_first(self):
        """This function checks if this player is served as player1 or player2.
        It is used to check which values are from the opponent.

        :return: True if the player's value is entered before the opponent in the matrix, False otherwise.
        """
        for col in self.data:
            if self.data[col][1::2] != self.played_data[col]:
                return False
        return True

    def max_strategy(self):
        """This function is called when our victory condition is Max.
        It first enters the value to meet our own victory condition.
        Then it passes the ret_d to the counter_enemy_mix function to put in values to defeat others.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()

        # for the victory column, fill in the upper boundary deducting a small number in round 1-9
        ret_d[self.v_col] = round(self.BOUNDARY - (self.turn_num-1) * self.EPSILON, 5)

        if self.turn_num == 10:
            # in round 10, assign the float that is 2 unit smaller than the
            # current unique max to the winning column
            ret_d[self.v_col] = self.next_after(self.get_next_unique_max(), -1)

            # assign the next unique max to two other columns
            next_max = self.get_next_unique_max()
            count = 0
            for k in self.played_data:
                if k != self.v_col and self.played_data[k][-1] > 0:
                    ret_d[k] = next_max
                    count += 1
                if count >= 2:
                    break

        # fill in values for other columns to defeat the opponent
        self.counter_enemy_mix(ret_d)

        # record the values this player played in this round
        for k in ret_d:
            self.played_data[k].append(ret_d[k])

        return ret_d

    def min_strategy(self):
        """This function is called when our victory condition is Min.
        It first enters the value to meet our own victory condition.
        Then it passes the ret_d to the counter_enemy_mix function to put in values to defeat others.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        # for the victory column, fill in the lower boundary adding a small number in round 1-9
        ret_d[self.v_col] = round(-1023.0 + (self.turn_num-1) * self.EPSILON, 5)

        if self.turn_num == 10:
            # in round 10, assign the float that is 2 unit larger than the
            # current unique min to the winning column
            ret_d[self.v_col] = self.next_after(self.get_next_unique_min(), 1)

            # assign the next min to two other columns
            next_min = self.get_next_unique_min()
            count = 0
            for k in self.played_data:
                if k != self.v_col and self.played_data[k][-1] < 0:
                    ret_d[k] = next_min
                    count += 1
                if count >= 2:
                    break

        # fill in values for other columns to defeat the opponent
        self.counter_enemy_mix(ret_d)

        # record the values this player played in this round
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def zero_m_strategy(self):
        """This function is called when our victory condition is ZeroM.
        It first enters the value to meet our own victory condition.
        Then it passes the ret_d to the counter_enemy_mix function to put in values to defeat others.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        current_sum = sum(self.data[self.v_col])

        # winning col: make current average as good as possible in round 1-9
        if current_sum <= abs(0.000001 * len(self.data[self.v_col])):
            ret_d[self.v_col] = 0.0000001   # do not use 0
        elif current_sum < 0:
            # min/max for boundary checking
            ret_d[self.v_col] = min(max(current_sum + self.EPSILON, -self.BOUNDARY), self.BOUNDARY)
        else:
            ret_d[self.v_col] = min(max(-current_sum - self.EPSILON, -self.BOUNDARY), self.BOUNDARY)
        if self.turn_num == 10:
            # Extract opponent's data and predict what they might put in for the last round
            if self.is_first_to_move:
                e_col = self.data[self.v_col][2::2]
            else:
                e_col = self.data[self.v_col][1::2]

            # default guess is the mode
            guess = stats.mode(e_col)[0][0]

            # if Max/Min is detected in our own col, use the next unique value
            if 'Max' in self.enemy_col_cond and self.enemy_col_cond['Max'] == self.v_col:
                guess = self.get_next_unique_max()
            if 'Min' in self.enemy_col_cond and self.enemy_col_cond['Min'] == self.v_col:
                guess = self.get_next_unique_min()

            ret_d[self.v_col] = min(max(-current_sum-guess, -self.BOUNDARY), self.BOUNDARY)

        # fill in values for other columns to defeat the opponent
        self.counter_enemy_mix(ret_d)

        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def linear_strategy(self):
        """This is the UNUSED version of our player's linear strategy, to demonstrate that we have attempted to meet
        this victory condition in a more proper way than just giving up.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        if self.turn_num <= 1:
            # for the first turn we start with 0
            ret_d[self.v_col] = 0.0
        else:
            # use linear regression for the next value
            slope, intercept, r_value, p_value, std_err = \
                linregress(range((self.turn_num-1)*2+1), self.data[self.v_col])
            ret_d[self.v_col] = max(-self.BOUNDARY, min(intercept + slope * ((self.turn_num-1)*2+1), self.BOUNDARY))

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def linear_strategy_special(self):
        """This is the actual strategy we use for linear victory condition.
        Since it is almost impossible to win linear/quadratic, we PURELY focus on defending, in the case
        when the opponent is in the same column as us.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        # put 1023.0 to defend the column in the case two players have the same column
        ret_d[self.v_col] = 1023.0
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def quadratic_strategy(self):
        """This is the UNUSED version of our player's quadratic strategy, to demonstrate that we have attempted to meet
        this victory condition in a more proper way than just giving up.

        This logic is the same as linear_strategy.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        if self.turn_num <= 1:
            ret_d[self.v_col] = 0.0
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

    def quadratic_strategy_special(self):
        """This is the actual strategy we use for quadratic victory condition.
        Since it is almost impossible to win linear/quadratic, we PURELY focus on defending, in case
        when the opponent is in the same column as us.

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        ret_d[self.v_col] = 1023.0
        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def sum_pos_strategy(self):
        """ This function is called when our victory condition is SumPos

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        if sum(self.data[self.v_col]) > 0:
            # if the current sum is already positive, we only need to put in 1023.0 guarantee to win
            ret_d[self.v_col] = self.BOUNDARY
        elif self.turn_num <= 3:
            # for the first 3 turns, we slightly decrease the value to avoid detection
            ret_d[self.v_col] = self.BOUNDARY - (self.turn_num - 1) * self.EPSILON
        else:
            ret_d[self.v_col] = self.BOUNDARY

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def sum_neg_strategy(self):
        """This function is called when our victory condition is SumNeg

        :return: a dictionary with same keys as data, with single float values to be filled in the game matrix
        """
        ret_d = dict()
        if sum(self.data[self.v_col]) < 0:
            # if the current sum is already negative, we only need to put in -1023.0 to guarantee a win
            ret_d[self.v_col] = -self.BOUNDARY
        elif self.turn_num <= 3:
            # for the first 3 turns, we slightly increase the value to avoid detection
            ret_d[self.v_col] = -self.BOUNDARY + (self.turn_num - 1) * self.EPSILON
        else:
            ret_d[self.v_col] = -self.BOUNDARY

        self.counter_enemy_mix(ret_d)
        for k in ret_d:
            self.played_data[k].append(ret_d[k])
        return ret_d

    def check_enemy_col(self):
        """This function uses current data to predict opponent's winning
        conditions in other columns. Different winning conditions are checked
        at different rounds.

        :return: It only updates self.enemy_col_cond and has no return value
        """

        # at turn 3 we detect if there is SumPos or SumNeg by checking if they keep putting in 1023.0/-1023.0
        if self.turn_num == 3:
            for col in self.data:
                if col != self.v_col:
                    if self.is_first_to_move:
                        arr = np.array(self.data[col][2::2])
                    else:
                        arr = np.array(self.data[col][1::2])
                    if (arr == 1023.0).all():   # if all values the opponent put in is 1023.0
                        self.enemy_col_cond['SumPos'] = col
                    if (arr == -1023.0).all():
                        self.enemy_col_cond['SumNeg'] = col

        # at the second last round we detect if there is any Max/Min
        if self.turn_num == 9:
            # which columns have contained the unique max/min for the most number of times
            sorted_max = sorted(self.unique_max_col_count.items(), key=lambda x: x[1], reverse=True)
            sorted_min = sorted(self.unique_min_col_count.items(), key=lambda x: x[1], reverse=True)

            # if the column has contained the unique max/min for more than once, we detect it as Max/Min
            if sorted_max and sorted_max[0][1] >= 2:
                self.enemy_col_cond['Max'] = sorted_max[0][0]
            if sorted_min and sorted_min[0][1] >= 2:
                self.enemy_col_cond['Min'] = sorted_min[0][0]

    def counter_enemy_mix(self, ret_d):
        """This is the meat of the whole class.
        Defeat algorithms are generalized for minimal coding.
        wipe out means make unique number non-unique in the following context.

        Max:        Keep wiping out the current max. Special logic in the 10th turn.
                    If Max is detected, we not only wipe out the current max, but wipe out the next two unique numbers
                    However if we are also Max, we wipe out only one next unique, so we don't defeat ourselves.
        Min:        The negation of Max.
        Linear:     Automatically blocked by other countering logic.
        Quadratic:  Automatically blocked by other countering logic.
        ZeroM:      Automatically blocked by other countering logic. It is hard to predict value.
        SumPos:     If current_sum is 0, we keep putting the negative boundary value to attempt to defeat.
        SumNeg:     If current_sum is 0, we keep putting the positive boundary value to attempt to defeat.

        :param ret_d: the dictionary with 1 value filled in for the victory column already
        :return: the dictionary with 5 numbers ready to be used by the server
        """
        current_max = self.get_current_unique_max()
        current_min = self.get_current_unique_min()

        #  special defeat logic in the last turn
        if self.turn_num == 10:
            if 'Max' in self.enemy_col_cond:
                if current_max > 0:
                    ret_d[self.enemy_col_cond['Max']] = current_max
                else:
                    # if current_max < 0 it means there is no unique max at the moment
                    ret_d[self.enemy_col_cond['Max']] = self.next_after(self.get_next_unique_max(), -1)

                next_max = self.get_next_unique_max()
                if self.v_col == 'Max':
                    count = 0
                    for k in self.data:
                        if k not in ret_d:
                            #  if we are Max as well, only put one next Max, so we don't defeat ourselves
                            ret_d[k] = next_max
                            next_max = self.next_after(next_max, -1)
                            count += 1
                        if count >= 1:  # only put in 1 next unique value
                            break
                else:
                    for k in self.data:
                        if k not in ret_d:
                            ret_d[k] = next_max
                            next_max = self.next_after(next_max, -1)
            elif 'Min' in self.enemy_col_cond:
                # the following part is the negation of the Max clause
                # meant to keep separate for better readability
                if current_min < 0:
                    ret_d[self.enemy_col_cond['Min']] = current_min
                else:
                    ret_d[self.enemy_col_cond['Min']] = self.next_after(self.get_next_unique_min(), 1)
                next_min = self.get_next_unique_min()
                if self.v_col == 'Min':
                    count = 0
                    for k in self.data:
                        if k not in ret_d:
                            #  if we are Min as well, only put one next Min, so we don't defeat ourselves
                            ret_d[k] = next_min
                            next_min = self.next_after(next_min, 1)
                            count += 1
                        if count >= 1:
                            break
                else:
                    for k in self.data:
                        if k not in ret_d:
                            ret_d[k] = next_min
                            next_min = self.next_after(next_min, 1)

        count = 0
        for k in sorted(self.data.keys()):
            if k not in ret_d:  # only insert values if it is not already added from strategy functions
                current_sum = sum(self.data[k])

                if self.turn_num == 1 or current_sum == 0:
                    ret_d[k] = self.BOUNDARY   # purely focus on SumNeg

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
                        ret_d[k] = self.BOUNDARY

                count += 1

        for k in ret_d:
            # convert to float again...
            ret_d[k] = round(float(ret_d[k]), 5)

        return ret_d

    def get_current_unique_max(self):
        """Utility function
        :return: the unique maximum value in the current game matrix.
        """
        # find each number with its frequency
        nums_count = dd(int)
        for col in self.data:
            for number in self.data[col]:
                nums_count[number] += 1

        # sort the number descending and get the largest whose freq == 1
        current_max = -self.BOUNDARY
        for num in sorted(nums_count.keys(), reverse=True):
            if nums_count[num] == 1:
                current_max = num
                break

        return current_max

    def get_current_unique_min(self):
        """Utility function
        :return: the unique minimum value in the current game matrix.
        """
        # find each number with its frequency
        nums_count = dd(int)
        for col in self.data:
            for number in self.data[col]:
                nums_count[number] += 1

        # sort the number ascending and get the largest whose freq == 1
        current_min = self.BOUNDARY
        for num in sorted(nums_count.keys()):
            if nums_count[num] == 1:
                current_min = num
                break

        return current_min

    def get_next_unique_max(self):
        """Utility function
        From the boundary to check each number.
        If it is not yet added in the matrix, return the value

        :return: the maximum value possible that hasn't been put into the game matrix.
        """
        m = self.BOUNDARY
        while m > -self.BOUNDARY:
            for col in self.data:
                if m in self.data[col]:
                    m = self.next_after(m, -1)
                    break
            else:
                return m    # return m if it is not yet in the matrix

        # still return some value in the case there is no unique number at all within the range
        return m

    def get_next_unique_min(self):
        """Utility function
        From the boundary to check each number.
        If it is not yet added in the matrix, return the value

        :return: the minimum value possible that hasn't been put into the game matrix.
        """
        m = -self.BOUNDARY
        while m < self.BOUNDARY:
            for col in self.data:
                if m in self.data[col]:
                    m = self.next_after(m, 1)
                    break
            else:
                return m
        return m

    def next_after(self, num, direction):
        """Utility function
        Get the next floating number with the precision of self.EPSILON

        :param num: the base number to increment/decrement
        :param direction: +1/-1 as the direction to move
        :return: the next floating number towards direction dir
        """
        return round(num + direction * self.EPSILON, 5)

    def __repr__(self):
        """
        Print the representation of the player
        :return:
        """
        return str(self.data) + '\n' + str(self.v_col) + ' ' + str(self.v_condition)
