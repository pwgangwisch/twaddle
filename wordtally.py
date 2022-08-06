import copy
import time

class wordTally():
    def __init__(self, url, tally=None):
        # Object designed to hold the word count results for a single url
        # or for the composite results of a site
        # Data members:
        #   url     => the url as a string
        #   pubTime => time of creation in seconds since epoch
        #   tally   => dictionary with words as keys and counts as values
        self.url = url
        self.pubTime = time.time()
        if tally == None:
            self.tally = {}
        else:
            self.tally = tally

    def addTally(self, other):
        # other is another wordTally object to be combined with this object
        # to produce a new combined wordTally
        # self's url and the greater of the pubTimes are used for the 
        # combined wordTally
        newWT = wordTally(self.url, copy.deepcopy(self.tally))
        # TBD - check whether deepcopy is really necessary here.
        # I don't really think so.
        otherTally = other.getTally()
        for word in otherTally:
            newWT.addWord(word, otherTally[word])
        if self.getPubTime() < other.getPubTime():
            newWT.setPubTime(other.getPubTime())
        return newWT

    def addWord(self, word, number=1):
        # method to add one or multiple numbers of a word to a wordTally
        if len(word) == 0:
            return
        if word in self.tally:
            self.tally[word] += number
        else:
            self.tally[word] = number

    def getPubTime(self):
        # get the PubTime as seconds since epoch
        return self.pubTime

    def getTally(self):
        # returns the dictionary of word, number pairs
        return self.tally

    def getTallyListAlpha(self):
        # tally as aphabetically sorted list of duples
        # duples are (word, number)
        tallyList = list(self.tally.items())
        tallyList.sort()
        return tallyList

    def getTallyListNum(self):
        # tally as numerically descending sorted list of duples
        # duples are (number, word)
        tallyList = list(self.tally.items())
        tallyListNumber = []
        for item in tallyList:
            tallyListNumber.append((item[1], item[0]))
        tallyListNumber.sort()
        # make sort descending
        tallyListNumber.reverse()
        return tallyListNumber

    def getUrl(self):
        # returns the url member of the wordTally
        return self.url

    def setPubTime(self, time):
        # method to change the pubTime if necessary
        self.pubTime = time

    def createDataFile(self, filename, mode='num', header=True):
        # method to create a csv data file
        # mode parameter is the sort mode, alphabetic or numeric
        # header parameter selects whether the url and time data is included
        # returns number of lines in new data file
        if mode == 'alpha':
            tallyList = self.getTallyListAlpha()
        elif mode == 'num':
            tallyList = self.getTallyListNum()
        else:
            print('Error: invalid mode.  Should be alpha or num')
            return 0
        file = open(filename, 'w')
        dataLength = len(tallyList)
        headerLength = 1
        if header:
            file.write('%s\n' % self.url)
            file.write('%s\n' % time.ctime(self.pubTime))
            headerLength += 2
        file.write('WORD, NUMBER\n')
        if dataLength > 0:
            for item in tallyList: # item is (word, number) - for alpha
                if mode == 'num':  #      or (number, word) - for num
                    file.write('%s, %s\n' % (item[1], item[0]))
                else:
                    file.write('%s, %s\n' % (item[0], item[1]))
                # data in file is always word, number
        file.close()
        return dataLength + headerLength

