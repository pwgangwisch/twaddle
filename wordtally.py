import copy

class wordTally():
    def __init__(self, url, tally=None):
        # data members
        # url => the url as a string
        # tally => dictionary with words as keys and counts as values
        self.url = url
        self.pubTime = None
        if tally == None:
            self.tally = {}
        else:
            self.tally = tally

    def addTally(self, other):
        # other is another wordTally object to be combined with this object
        # to produce a new combined wordTally
        # the left hand url is used for the new wordTally
        newWT = wordTally(self.url, copy.deepcopy(self.tally))
        otherTally = other.getTally()
        for word in otherTally:
            newWT.addWord(word, otherTally[word])
        return newWT

    def addWord(self, word, number=1):
        if len(word) == 0:
            return
        if word in self.tally:
            self.tally[word] += number
        else:
            self.tally[word] = number

    def getPubTimeIso(self):
        return self.pubTime

    def getTally(self):
        # returns the dictionary of word, number pairs
        return self.tally

    def getTallyListAlpha(self): # tally sorted aphabetically
        tallyList = list(self.tally.items())
        tallyList.sort()
        return tallyList

    def getTallyListNum(self): # tally list sorted numerically descending
        tallyList = list(self.tally.items())
        tallyListNumber = []
        for item in tallyList:
            tallyListNumber.append((item[1], item[0]))
        tallyListNumber.sort()
        # make sort descending
        tallyListNumber.reverse()
        return tallyListNumber

    def getUrl(self):
        return self.url

    def setPubTime(self, time):
        self.pubTime = time

    def createDataFile(self, filename, mode='num'):
        if mode == 'alpha':
            tallyList = self.getTallyListAlpha()
        elif mode == 'num':
            tallyList = self.getTallyListNum()
        else:
            print('Error: invalid mode.  Should be alpha or num')
            return 0
        file = open(filename, 'w')
        file.write('%s\n' % self.url)
        file.write('%s\n' % self.pubTime)
        length = len(tallyList)
        if length > 0:
            for item in tallyList:
                file.write('%s, %s\n' % (item[1], item[0]))
        file.close()
        return length + 2 # returns number of lines in new data file

