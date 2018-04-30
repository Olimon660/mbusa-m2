from collections import defaultdict as df


class Player:
    epsilon = 0.00001 #decimal limitation
    ub = 1023.0 #upper bound
    lb = -1023.0 #lower bound
    result = {}
    count = -1

    def take_turn(self, data, victory):

        self.data = data
        self.victory_con = victory[0]
        self.victory_col = victory[1]
        self.data_keys = sorted(list(data.keys()))
        self.data_values = list(data.values())
        # self.count = int(len(self.list_all_numbers_before())/5)
        self.data_items = list(data.items())
        self.count += 2
        category = {
            'Max':self.maximum(),'Min':self.minimum(),\
            'Linear':self.linear(),'Quadratic':self.quadratic(),\
            'ZeroM':self.zeromean(),'SumNeg':self.sumneg(),\
            'SumPos':self.sumpos()
        }
        output = category[self.victory_con]

        lst2 = self.defence()
        lst2[self.victory_col] = 1023.0

        return {k: 1.0 for k in data}


    def defence(self):
        '''Defence Strategy'''
        self.result = dict()
        if self.count == 1:
            lst3 = {k: self.ub for k in self.data_keys}
            return lst3
            # play 1023.0 for each column at first round

        elif 2 <= self.count <= 18:
            for key in self.data_keys:
                if 0 <= sum(self.data[key]) <= self.ub:
                    # if the sum of that choose column is in between(0,1023.0)
                    # I guess he is playing SumNeg or Min
                    # then keep playing 1023.0 before the last round.
                    #this will also break ther Linear/Quaradict
                    self.result[key] = self.ub
                elif sum(self.data[key]) > self.ub + 1022.99999:
                    # if the sum of that choose column is greater than 1023.0+1022.99999
                    # guess he is playingMax.I already lost if the rival is playing SumPos.
                    # Then play  each round before the last round.
                    #this will also break ther Linear/Quaradict
                    self.result[key] = self.ub - ((self.count + 1)/2)*self.epsilon
                else:
                    self.result[key] = self.ub

            return {k: self.ub for k in self.data_keys}

        else:  # at last round
            for key in self.data_keys:
                if sum(self.data[key]) == 0.0:  # I guess he is playing ZeroM
                    self.result[key] == self.ub

                elif 0 < sum(self.data[key]) <= self.ub:
                    # since I played 1023.0 for all previous round, if the sum of choosen column is
                    # in between (0,1023.0), I guess he is playing Min
                    # find the min of existing data, add 0.00001
                    # the worst case at last round is that he will
                    # also play the same number with me, then tie.
                    uniqmin = self.find_unique_minimum() + self.epsilon
                    self.result[key] = uniqmin

                elif sum(self.data[key]) > self.ub + 1022.99999:
                    # if sum is positive, i already lost if other play SumPos
                    # since i played 0.00001 for all previous round. If the sum is greater then
                    # 1023.0+1022.99999, I guess he is playingMax
                    # at last round, I ll play a unique max of existing data.
                    uniqmax = self.find_unique_maximum() - self.epsilon
                    self.result[key] = uniqmax
                else:
                    self.result[key] = self.ub

            return {k: self.ub for k in self.data_keys}


    def list_all_numbers_before(self):
        '''list all existing numbers in a new list'''
        list1=[v for v in self.data_values]
        
        
        list_so_far=[num for element in list1 for num in element]
        
        return list_so_far

    def find_unique_maximum(self):
        '''find the unique maximum number of existing data'''
        list_all=self.list_all_numbers_before()
        
        my_dd=df(int)

        #create a dictionary that records the frequency of each number so far
        for char in sorted(list_all):
            my_dd[char]+=1

        list2=[tup for tup in my_dd.items() if tup[1]==1]#find the numbers that only appears once

        if len(list2)==0:
            #all the numbers so far are not unique, thus we find the minimum of those numbers
            #and after subtracting 0.00001 from it we will get the next unique maximum'''
            return 1022.99990
        else:
            uniquemax_so_far=max([a[0] for a in list2]) #find out the unique maximum number in the matrix
        
        return round(uniquemax_so_far,5)


    def find_unique_minimum(self):
        '''find the unique minimum number of existing data'''
        list_all=self.list_all_numbers_before()
        my_dd=df(int)

        #create a dictionary that records the frequency of each number so far
        for char in sorted(list_all):
            my_dd[char]+=1

        list2=[tup for tup in my_dd.items() if tup[1]==1]#find the numbers that only appears once

        if len(list2)==0:
        #all the numbers so far are not unique, thus we find the minimum of those numbers
        #and after subtracting 0.00001 from it we will get the next unique maximum'''
            return -1022.99990
        else:
            uniquemin_so_far=min([a[0] for a in list2]) #find out the unique maximum number in the matrix
        
        return uniquemin_so_far


    def maximum(self):
        '''our strategy for max and min is similar, we confuse our opponent by putting all kinds of numbers that
        satisfy other victory conditions in the non-victory columns
        so that it's hard for him to guess what's our column name and what our victory conditon is'''

        if 0 <= self.count < 7:
            return self.ub-(self.count//2)*self.epsilon

            
        elif self.count == 7:
        #confuse the other player, if his strategy to defeat my maximum is to find the unique maximum every turn and
        # repeat that number at the next turn to make it not unique anymore, it won't work here,since he will
        # miss 1022.99997

            return self.ub-((self.count+1)/2)*self.epsilon

        elif 8 <= self.count <= 18:
        #return{self.victory_col:self.ub-((self.count+1)/2)*self.epsilon

            return self.ub-((self.count+1)/2)*self.epsilon
        
        else: 
        #defend maximum strategy

            looking_num = [num for num in self.list_all_numbers_before() if num==1022.99997]
            
            if len(looking_num) == 0:
            #the list is empty which means no one put out 1022.99997 yet

                return 1022.99997

            elif len(looking_num) == 1:
            #our reserved number was already placed, and since it is the unique maximum number in the matrix so far,
            # we need to make it not unique anymore but also try to find a way to win

                return self.ub-11*self.epsilon

            else:
            #my reserved number is no longer maximum and unique,
            #thus we gamble and use the 'smallest' largest number in our colomn which is 1022.99991,
            # subtracting 0.00001*n in order to gain  a unique maximum number'''

                return 1022.99991-3*self.epsilon 

    def minimum(self):
        '''same strategy as mentioned above in the maximum method'''
        if 0 <= self.count < 7:
        #return{self.column_name[0]:self.ub-(self.count//2)*self.epsilon

            return self.lb+(self.count//2)*self.epsilon
        elif self.count == 7:
        #confuse the other player, if his strategy to defeat my minimum is to find the unique minimum every turn
        #  and repeat that number at the next turn to make it not unique anymore
        #it won't work here,since he miss -1022.99997

            return self.lb+((self.count+1)/2)*self.epsilon
        elif 8 <= self.count <= 18:
        #return{self.column_name[0]:self.ub-(self.count//2)*self.epsilon

            return self.lb+((self.count+1)/2)*self.epsilon
        else:  
        #defend minimum strategy
        #for the last turn, in case of the other player's victory condition is also minimum, we need
        # to check if the number we reserved,which is -1022.99997 has not appeared yet
            looking_num = [num for num in self.list_all_numbers_before() if num==-1022.99997]
   
            if len(looking_num) == 0:
            #the list is empty which means no one put out -1022.99997 yet

                return -1022.99997
            elif len(looking_num) == 1:
            #our reserved number was already placed, and since it is the unique minimum number in the matrix so far,
            #  we need to make it not unique anymore, but also try to find a way to win

                return self.lb+11*self.epsilon
            else:
            #my reserved number is no longer maximum and unique,
            #thus we gamble and use the 'smallest' largest number in our colomn which is -1022.99991,
            # subtracting 0.00001*n in order to gain  a unique minimum number

                return -1022.99991+3*self.epsilon

    def sumneg(self):
        '''always play -1023.0.If the rival play 1023, then tie'''
        return self.lb
    
    def sumpos(self):
        '''always play 1023.0. If the rival play -1023.0, then tie'''
        return self.ub


    def linear(self):
        '''Linear is hard to win, we will play 100,200,300,...1000 respectively.'''
        return round(100.0*((self.count)//2), 5)

    def quadratic(self):
        '''We will play -10,-sqrt(200),-sqrt(300),...-sqrt(1000) respectively.
                After squaring them, they will become 100,200,...1000
                Using negtive number might mislead the rival, he might think I
                am playing the SumPos.But still Quafratic is hard to win.'''
        return -round(100.0*((self.count+1)/2)**0.5,5)

    def zeromean(self):
        '''
        Always play -1023.0 at turn 1.From turn 2,if sum of the existing
        data in the victory column is 0, I guess the rival is playing
        +1023.0 at this colume,I will keep playing -1023.0.
        Otherwise, I'am guessing the rival is playing Max, I will play the
        unique maximum at the last turn. In the case, I lost if the rival keep playing
        negtive number in this column.
        '''

        if 1<=self.count<= 18:
            return self.lb
        else:
            if sum(self.data[self.victory_col]) == 0.0:
                return self.lb
            else:
                return self.find_unique_maximum()
