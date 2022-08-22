import urllib
import urllib.request
import time
from datetime import datetime
import twaddleparser
from twaddleparser import theHillParser
from cleanup import cleanup

summaryWt = None
urlsRead = None
logFile = None
siteName = None
runTime = None
httpHeader = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

def twaddle(url, level):
    global logFile, urlsRead, summaryWt, siteName, runTime, httpHeader
    if siteName == None: # globals initialized first time called
        urlsRead = {url:1}
        siteName = url.split('/')[2]
        runTime = time.time()
        logFile = open('twaddle.log', 'w')
    else:
        if url in urlsRead:
            #duplicate URL Bail out
            logFile.write('Duplicate URL detected: %s\n' % url)
            return
        else:
            urlsRead[url] = 1
    httpRequest = urllib.request.Request(url, None, httpHeader)
    #httpRequest = urllib.request.Request(url)
    try:
        infile = urllib.request.urlopen(httpRequest)
        #infile = urllib.request.urlopen(url)
        #infile = open(url, 'r')
    except urllib.error.HTTPError as myexception:
        logFile.write('Exception in url request for %s\n'% url)
        logFile.write('reason: %s\n' % myexception.reason)
        logFile.write('headers: %s\n' % myexception.headers)
        return
    #print('%s level %d' % (url, level)) # give us feedback at the console
    parser = theHillParser(url, siteName, logFile, urlsRead)
    outfile = open('testout.txt', 'a')
    outfile.write('\n\n%s\n' % url)
    parser.feed(str(infile.read()))
    # We should now have our wt and url list populated
    newWt = parser.getWordTally()
#    if newWt.getPubTimeIso() == None:
#        if level > 0:
#            logFile.write('Pub time not available - item discarded\n\n')
#            return
#    else:
#        itemTime = datetime.fromisoformat(newWt.getPubTimeIso()).timestamp()
#        if runTime - itemTime > 172800: # 48 hours
#            logFile.write('Article too old - item discarded\n\n')
#            return
#
#    newUrls = parser.getUrlsPending()
#    logFile.write('Got %s words and %s urls\n\n'%(len(newWt.getTally()),
#                                                len(newUrls)))
    if summaryWt == None:
        summaryWt = newWt
    else:
        summaryWt = summaryWt.addTally(newWt)
#    if level < 2:  # limit depth of recursion
#        for newUrl in newUrls:
#            #make recursive call to twaddle
#            time.sleep(2.5) # slow down our requests to server
#            twaddle(newUrl, level+1)
#
def runTwaddle(url): # do not put a trailing / in the url
    global logFile, summaryWt, siteName
    twaddle(url, 0)
    summaryWt = cleanup(summaryWt)
    summaryWt.createDataFile('%s-wordtally.txt' % siteName)
    logFile.close()
