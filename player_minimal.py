import numpy as np

class Player:
    v_condition = ''
    data = {}

    is_first_to_move = True

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
        self.v_condition = victory
        return {k: np.random.uniform(-1023.0, 1023.0) for k in data}

    def __repr__(self):
        """
        Print the representation of the player
        :return:
        """
        return str(self.data) + '\n' + str(self.v_condition)
