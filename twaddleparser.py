from html.parser import HTMLParser
from wordtally import wordTally
import time

class twaddleParser(HTMLParser): # base class twaddle parser
    def __init__(self, url, siteName, logFile):
        HTMLParser.__init__(self)
        self.siteName = siteName # derived from first url
        self.logFile = logFile
        self.inScript = False # parsing data within scripts
        self.urlsPending = []    # urls found in the current url
        self.wt = wordTally(url) # wordTally for the current url

    def acceptUrlCandidate(self, url):
        # the parser has encountered a link and we are checking whether
        # we should include it in our list to be visited.
        if url in self.urlsPending:
            return False
        return True

    def handle_starttag(self, tag, attrs):
        # parser has encountered a start tag.
        if tag == 'a':
            if 'href' in attrs[0]:
                urlCandidate = attrs[0][1]
                if urlCandidate[-1] == '/': # remove trailing slash
                    urlCandidate = urlCandidate[:-1]
                if self.acceptUrlCandidate(urlCandidate):
                    self.urlsPending += [urlCandidate]
        elif tag == 'script':
            'data-n-head' in attrs[0]:
                logFile.write('<script tag: data: %s\n' % str(attrs))

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if self.inScript:

    def getWordTally(self):
        # send parser's word tally to the main app for inclusion
        return self.wt

    def getUrlsPending(self):
        # send parser's list of urls to the main app for recursive calls
        return self.urlsPending

