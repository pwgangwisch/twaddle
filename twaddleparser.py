from html.parser import HTMLParser
from wordtally import wordTally
import time

class theHillParser(HTMLParser): # Parser tuned to thehill.com
    def __init__(self, url, siteName, logFile, urlsRead):
        HTMLParser.__init__(self)
        self.siteName = siteName # derived from first url
        self.logFile = logFile
        self.urlsRead = urlsRead # global list of urls which have been read
        self.inParagraph = False # parsing data between <p> and </p> 
        self.urlsPending = []    # urls found in the current url
        self.wt = wordTally(url) # wordTally for the current url

    def acceptUrlCandidate(self, url):
        # the parser has encountered a link and we are checking whether
        # we should include it in our list to be visited.
        if (url in self.urlsRead) or (url in self.urlsPending):
            return False
        urlSplit = url.split('/')
        if (len(urlSplit) < 4) or (urlSplit[2] != self.siteName):
            return False
        if urlSplit[3] in ('author', 'video', 'opinion',
                           'hilltv', 'resources', 'events',
                           'sponsored-content'): # reject topics
            return False
        return True

    def handle_starttag(self, tag, attrs):
        # parser has encountered a start tag.  We are interested in 3 types:
        # paragraph - finding article text
        # href - possible link to visit
        # article:published_time - used to check for stale articles
        if tag == 'meta':
            if attrs[0][0] == 'property': 
                if attrs[0][1] == 'article:published_time':
                    if attrs[1][0] == 'content':
                        pubTime = attrs[1][1]
                        # Note: times are assumed local
                        # May want to revisit that since the pubTime
                        # string includes offset from GMT, now ignored
                        self.logFile.write('Published time: %s\n' % pubTime)
                        pubTimeStruct = time.strptime(pubTime[:-6],
                                "%Y-%m-%dT%H:%M:%S")
                        self.wt.setPubTime(time.mktime(pubTimeStruct))
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
        # Here we only care about paragraph ends so we can stop reading 
        # text for an article
        if tag == 'p':
            self.inParagraph = False

    def handle_data(self, data):
        # method to process data while the parser is in a paragraph.
        # We are collecting words and adding them to our wordTally
        punctuation = ['.', ',', ':', '_', '“', '”', '’s', '?', '©', '|',
                '\\n', '\\t', '[', ']', '\\x94', '\\x98', '\\x99', '\\x9c',
                '\\x9d', '\\xa0', '\\xa9', '\\xc2', '\\xe2']
        footers = ['THE HILL 1625 K STREET, NW SUITE 900 WASHINGTON DC',
                '1998 - 2022 Nexstar Inc. | All Rights Reserved.',
                'The Hill has removed its comment section, as there']
        if self.inParagraph:
            for footer in footers:
                if footer in data:
                    return # Don't want to analyze the footers
            self.logFile.write('%s\n' % data)
            wordlist = data.split()
            for word in wordlist: # clean up our words
                for mark in punctuation:
                    word = word.replace(str(mark), '')
                word = word.replace('\\x80', '\'') # use ' for apostrophes
                if (len(word) > 1) and (word[-2:] == "'s"):
                    word = word[:-2] # remove 's endings
                if (len(word) > 0) and (word[0] == '\''):
                    word = word[1:] # remove leading single quotes
                if (len(word) > 0) and (word[-1] == '\''):
                    word = word[:-1] # remove trailing single quotes
                if len(word) > 0:
                    word = word.upper()
                    self.wt.addWord(word)

    def getWordTally(self):
        # send parser's word tally to the main app for inclusion
        return self.wt

    def getUrlsPending(self):
        # send parser's list of urls to the main app for recursive calls
        return self.urlsPending

