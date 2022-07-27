from html.parser import HTMLParser
from wordtally import wordTally
import twaddle

class theHillParser(HTMLParser): # Parser tuned to thehill.com
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.inParagraph = False
        self.urlsPending = []
        self.wt = wordTally(url)

    def acceptUrlCandidate(self, url):
        if (url in twaddle.urlsRead) or (url in self.urlsPending):
            return False
        urlSplit = url.split('/')
        if (len(urlSplit) < 4) or (urlSplit[2] != twaddle.siteName):
            return False
        if urlSplit[3] in ('author', 'video', 'opinion',
                           'hilltv'): # reject topics
            return False
        return True

    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            if attrs[0][0] == 'property': 
                if attrs[0][1] == 'article:published_time':
                    if attrs[1][0] == 'content':
                        pubTime = attrs[1][1]
                        twaddle.logFile.write('Published time: %s\n' % pubTime)
                        self.wt.setPubTime(pubTime)
        elif tag == 'p':
            self.inParagraph = True
        elif tag == 'a':
            if 'href' in attrs[0]:
                urlCandidate = attrs[0][1]
                if urlCandidate[-1] == '/':
                    urlCandidate = urlCandidate[:-1]
                if self.acceptUrlCandidate(urlCandidate):
                    self.urlsPending += [urlCandidate]

    def handle_endtag(self, tag):
        if tag == 'p':
            self.inParagraph = False

    def handle_data(self, data):
        punctuation = ['.', ',', '“', '”', '’s', '?', '©', '|']
        if self.inParagraph:
            wordlist = data.split()
            for word in wordlist:
                for mark in punctuation:
                    if mark in word:
                        word = word.replace(mark, '')
                if len(word) > 0:
                    self.wt.addWord(word)

    def getWordTally(self):
        return self.wt

    def getUrlsPending(self):
        # check for multiple entries
        returnValue = []
        for item in self.urlsPending:
            if not item in returnValue:
                returnValue += [item]
            else: # we found a duplicate
                twaddle.logFile.write('Duplicate url detected: %s\n' % item)
        return returnValue

