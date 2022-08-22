from html.parser import HTMLParser
from wordtally import wordTally
import time

class foxParser(HTMLParser): # Fox News twaddle parser
    def __init__(self, url, siteName, logFile):
        HTMLParser.__init__(self)
        self.siteName = siteName # derived from first url
        self.logFile = logFile
        self.inScript = False    # parsing data within scripts
        self.urlsPending = []    # urls found in the current url
        self.wt = wordTally(url) # wordTally for the current url

    def acceptUrlCandidate(self, url):
        # the parser has encountered a link and we are checking whether
        # we should include it in our list to be visited.
        rejectTopics = ['shows', 'fox-nation', 'terms-of-use',
                 'privacy-policy', 'donotsell', 'closed-captioning',
                 'contact', 'about', 'alerts', 'newsletters',
                 'accessibility-statement', 'person', 'live-news',
                 'entertainment', 'sports', 'lifestyle', 'auto',
                 'food-drink']
        if url in self.urlsPending:
            return False
        urlSplit = url.split('/')
        if (len(urlSplit) < 4) or (urlSplit[2] != self.siteName):
            return False
        if urlSplit[3] in rejectTopics: # reject topics
            return False
        return True

    def handle_starttag(self, tag, attrs):
        # parser has encountered a start tag.
        if (tag == 'a') and (len(attrs) > 0):
            if 'href' in attrs[0]:
                urlCandidate = attrs[0][1]
                if (len(urlCandidate) == 0) or (urlCandidate[:8]
                        != 'https://'):
                    return
                elif urlCandidate[-1] == '/':
                    urlCandidate = urlCandidate[:-1]
                if self.acceptUrlCandidate(urlCandidate):
                    self.urlsPending += [urlCandidate]
                    self.logFile.write('URL found: %s\n' % urlCandidate)
        elif tag == 'script':
            if (len(attrs) > 0) and ('data-n-head' in attrs[0]):
                self.logFile.write('<script tag: data: %s\n' % str(attrs))
                self.inScript = True

    def handle_endtag(self, tag):
        if tag == 'script':
            if self.inScript:
                self.logFile.write('End of script\n')
            self.inScript = False

    def handle_data(self, data):
        pubDate = ''
        punctuation = ['.', ',', ':', ';', '_', '"', '\'s', '\\\\', '?', '©',
                '|', '\\n', '\\t', '[', ']', '\\x80', '\\x93', '\\x94',
                '\\x98', '\\x99', '\\x9c', '\\x9d', '\\xa0', '\\xa9',
                '\\xc2', '\\xe2', '&amp', '\\']
        junkPhrases = ['CLICK HERE TO GET THE FOX NEWS APP',
                'FOX NEWS EXCLUSIVE:',
                'HEAD TO THE FOX NEWS ELECTIONS CENTER FOR THE '\
                + 'LATEST PRIMARY RESULTS',
                'CLICK HERE FOR THE LATEST FOX NEWS REPORTING '\
                + 'FROM THE CAMPAIGN TRAIL', 'FOX NEWS']
        if self.inScript:
            if ('headline' in data) and ('articleBody' in data):
                # we found article text
                data = data.replace('&nbsp;', ' ')
                dataLines = data.split('\\n')
                headlineMarker = '"headline":'
                bodyMarker = '"articleBody":'
                dateMarker = '"datePublished":'
                articleWords = []
                for line in dataLines:
                    self.logFile.write('%s\n' % str(line))
                    if headlineMarker in line:
                        line = line.replace(headlineMarker, '')
                        headWords = line.split()
                        articleWords += headWords
                    elif bodyMarker in line:
                        line = line.replace(bodyMarker, '')
                        for phrase in junkPhrases:
                            if phrase in line:
                                line = line.replace(phrase, ' ')
                        bodyWords = line.split()
                        articleWords += bodyWords
                    elif dateMarker in line:
                        line = line.replace(dateMarker, '')
                        dateWords = line.split()
                        self.logFile.write('dateWords: %s\n' % str(dateWords))
                        pubDate = dateWords[0].replace('"', '')[:25]
                        # date string should have 25 chars, no extra
                        # Note: times are assumed local
                        # May want to revisit that since the pubTime
                        # string includes offset from GMT, now ignored
                        self.logFile.write('Published time: %s\n' % pubDate)
                        pubTimeStruct = time.strptime(pubDate[:-6],
                                "%Y-%m-%dT%H:%M:%S")
                        self.wt.setPubTime(time.mktime(pubTimeStruct))
                        self.logFile.write('pubDate: %s\n' % pubDate)
                for word in articleWords:
                    for mark in punctuation:
                        word = word.replace(str(mark), '')
                    if (len(word) > 0) and (word[0] == '\''):
                        word = word[1:] # remove leading single quotes
                    if (len(word) > 0) and (word[-1] == '\''):
                        word = word[:-1] # remove trailing single quotes
                    if len(word) > 0:
                        word = word.upper()
                        self.wt.addWord(word)
                        self.logFile.write('%s\n' % word)


    def getWordTally(self):
        # send parser's word tally to the main app for inclusion
        return self.wt

    def getUrlsPending(self):
        # send parser's list of urls to the main app for recursive calls
        return self.urlsPending

