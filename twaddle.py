import urllib
import urllib.request
import time
from datetime import datetime
import wordtally
from twaddleparser import theHillParser
from cleanup import cleanup

summaryWt = None
urlsRead = None
logFile = None
siteName = None
runTime = None
# fake the server that we are using my browser!
httpHeader = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'}

def twaddle(url, level):
    # This module connects to a web site and parses the code to find words
    # in articles and count them, and for each page, get any links. It then
    # is called recursively for each unvisited link where it again counts
    # words in articles, gets links and visits them recursively to a depth
    # of 2.  The initial URL is depth 0.
    recursionDepth = 2
    global logFile, urlsRead, summaryWt, siteName, runTime, httpHeader
    # parsers tuned to the site we are reading
    parsers = {'thehill.com': theHillParser} # more to come
    if siteName == None: # globals initialized first time called
        urlsRead = [url]
        siteName = url.split('/')[2]
        runTime = time.time()
        # give a unique identifier for log file, don't overwrite!
        fileName = 'twaddle:%s%s.log' % (siteName, str(runTime)[:-8])
        logFile = open(fileName, 'w')
    else:
        if url in urlsRead:
            #duplicate URL Bail out
            return
        else:
            urlsRead += [url]
    # choose our parser based on target site
    parser = parsers[siteName](url, siteName, logFile, urlsRead)
    httpRequest = urllib.request.Request(url, None, httpHeader)
    try:
        dataStream = urllib.request.urlopen(httpRequest)
    except urllib.error.HTTPError as myexception:
        logFile.write('Exception in url request for %s\n'% url)
        logFile.write('reason: %s\n' % myexception.reason)
        logFile.write('headers: %s\n' % myexception.headers)
        return
    print('%s%s level %d' % (' '*level, url[:150], level)) # console display
    logFile.write('\n\nParsing %s\n' % url)
    try:
        parser.feed(str(dataStream.read()))
    except:
        logFile.write('Error parsing %s\n' % url)
        return
    dataStream.close()
    # We should now have our wt and url list populated
    newWt = parser.getWordTally()
    if newWt.getPubTime() == None:
        if level > 0:
            logFile.write('Pub time not available - item discarded\n\n')
            return
    else:
        itemTime = newWt.getPubTime()
        if runTime - itemTime > 172800: # 48 hours
            logFile.write('Article too old - item discarded\n\n')
            return

    newUrls = parser.getUrlsPending()
    logFile.write('Got %s words and %s urls\n\n'%(len(newWt.getTally()),
                                                len(newUrls)))
    if summaryWt == None:
        summaryWt = newWt
    else:
        summaryWt = summaryWt.addTally(newWt)
    if level < recursionDepth:  # limit depth of recursion
        for newUrl in newUrls:
            #make recursive call to twaddle
            time.sleep(2.5) # slow down our requests to server
            twaddle(newUrl, level+1)
    if level == 0:
        logFile.close()

def runTwaddle(url): # do not put a trailing / in the url
    global logFile, summaryWt, siteName, runTime
    twaddle(url, 0)
    summaryWt = cleanup(summaryWt)
    summaryWt.createDataFile('words:%s%s.txt' % (siteName, str(runTime)[:-8]))
