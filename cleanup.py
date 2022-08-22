# This module contains a list of common words that don't contribute to the
# articles' context but have high frequency, so we want to exclude them.
# Making this a separate module makes it easy to add to the list as necessary.
# The procedure deletes them from the input wordTally.

throwaways = ['A', 'ABOUT', 'ALL', 'ALSO', 'AM', 'AN', 'AND', 'ANY', 'ARE',
        'AS', 'AT', 'BE', 'BECAUSE', 'BEEN', 'BUT', 'BY', 'CAN', 'DID', 'DO',
        'DON\'T', 'DURING', 'EACH', 'ET', 'FOR', 'FROM', 'GET', 'HAD',
        'HAS', 'HAVE', 'HE', 'HER', 'HERE', 'HIM', 'HIS', 'HOW', 'I',
        'I\'M', 'IF', 'IN', 'INTO', 'IS', 'IT', 'ITS', 'MANY', 'ME',
        'MORE', 'MOST', 'MY', 'NEW', 'NO', 'NOT', 'OF', 'ON', 'ONLY',
        'OR', 'OTHER', 'OUR', 'OUT', 'PM', 'SAID', 'SAY', 'SEE', 'SHE',
        'SO', 'SOME', 'SUCH', 'THAN', 'THAT', 'THE', 'THEIR', 'THEM',
        'THERE', 'THEY', 'THING', 'THINGS', 'THIS', 'THOSE', 'TO', 'TWO',
        'US', 'VERY', 'WAS', 'WE', 'WERE', 'WE\'RE', 'WHAT', 'WHEN',
        'WHERE', 'WHICH', 'WHILE', 'WHO', 'WHOSE', 'WITH', 'WOULD', 'YOU',
        'YOUR']

def cleanup(wt):
    global throwaways
    tally = wt.tally
    # delete entries for throwaways
    for ta in throwaways:
        if ta in tally:
            del tally[ta]
    # delete single character or empty entries
    deletions = [] # make a list of deletions since we can't delete from
                   # dictionary within iteration
    for key in tally.keys():
        if len(key) < 2:
            deletions += [key]
        elif '@' in key: # remove email address fragments, mostly
            deletions += [key]
        else: # remove annoying date strings MO/DY/YR
            test = key.split('/')
            if len(test) == 3:
                deletions +=[key]
    for item in deletions:
        del tally[item]
    return wt


