import re
from functools import cache
from gen import DB as db

processRules = 0

@cache
def malWordList(wordList):

    idList = wordList[0][1]
    mList = [db.getFieldValue("word", "wordlist", "wordid=" + id) for id in idList.split(',')]
    return tuple(mList)

@cache
def patternCheck(pattern):

    wordsExist = tuple(db.getFieldData("select pattern,wordid from words where pattern='%s'" % (pattern)))
    if len(wordsExist) == 0:
        return False, ()
    else:
        return True, tuple(malWordList(wordsExist))

@cache
def getWordKeys(word):

    query = "select pattern,value1,value2,value3,id from symbols where pattern = '%s'" % (word)
    return db.getFieldData(query)


def tokenizeWord(word):
    tokenList = []
    maxTokenSize = 8
    while len(word) > 0:

        trialWord = word[:min(len(word), maxTokenSize)]

        while len(trialWord) > 0:
            wordKeys = getWordKeys(trialWord)

            if len(wordKeys) == 0:
                trialWord = trialWord[:len(trialWord) - 1]
            else:
                break
        else:
            tokenList.append(word[0])
            word = word[1:]
            trialWord = ''

        word = word[len(trialWord):]
        tokenList.append(wordKeys)

    return tokenList


def mConvertion(mWord):
    wordsList = []
    trialWord = mWord
    itr = 1

    while itr < len(trialWord):

        leftWise = patternCheck(trialWord[:len(trialWord)-itr])
        if leftWise[0] == True:
            wordsList.append(leftWise[1])
            trialWord, itr = trialWord[len(trialWord)-itr:], 0
            continue

        # print('r--------',trialWord[itr:])
        # rightWise = patternCheck(trialWord[itr:])
        # if rightWise[0] == True:
        #     wordsList.insert(0,rightWise[1])
        #     trialWord, itr = trialWord[:itr], 0
        #     print('right----', trialWord)
        #     continue

        itr = itr + 1

    if len(trialWord) == 0:
        return wordsList
    else:
        remList = tokenizeWord(trialWord)
        return wordsList + remList

def flatten(tokenList, onlyOne=False):
    stack = []
    virama = '്'

    for tok in tokenList:
        if str(type(tok)) == "<class 'tuple'>":
            if len(stack) == 0:
                stack = list(tok)
            else:
                ns = []

                for el in range(0, len(stack)):
                    li = len(stack[el]) - 1
                    if stack[el][li] == virama:
                        stack.append(stack[el][:li])

                for elmt in tok:
                    for elms in stack:
                        ns.append(elms + elmt)
                stack = ns
        else:
            if len(stack) == 0:
                for elm in tok:
                    stack.append(elm[1])
                    if elm[2] != '':
                        stack.append(elm[2])
                    if elm[3] != '':
                        stack.append(elm[3])
            else:
                ns = []

                for el in range(0, len(stack)):
                    li = len(stack[el]) - 1
                    if stack[el][li] == virama:
                        stack[el] = stack[el][:li]

                for i, elmt in enumerate(tok):
                    if onlyOne and i > 0:
                        break
                    for j, elms in enumerate(stack):
                        if onlyOne and j > 0:
                            break
                        ns.append(elms + elmt[1])
                        if elmt[2] != '' and elmt[2] != None:
                            ns.append(elms + elmt[2])
                        if elmt[3] != '' and elmt[3] != None:
                            ns.append(elms + elmt[3])
                stack = ns
    return list(stack)


def createdMalWord(engWord):

    engWord = engWord.lower()
    malWord = flatten(mConvertion(engWord), True)[0]

    if processRules & 2 == 2:

        engWordID = db.getId("words")
        malWordCnt = db.getFieldValueI("COUNT(word)", "wordlist", "word= '%s'" % (malWord))

        if malWordCnt == 0:
            malWordID = db.getId("wordlist", "wordid")
            db.implement("insert into wordlist (wordid,word,engword_id) values(%d,'%s',%d)" % (malWordID, malWord, engWordID))
        elif malWordCnt == 1:
            malWordID = db.getFieldValueI("wordid", "wordlist", "word= '%s'" % (malWord))
        else:
            print('More than one entry in wordlist for word-' + malWord)
            raise Exception('More than one entry in wordlist for word-' + malWord)

        db.implement("INSERT INTO words (id,pattern,wordid) values(%d,'%s','%s')" % (engWordID, engWord, malWordID))

    return malWord


def getMalFromDB(engWord):

    idList = db.getFieldValue("wordid", "words", "pattern= '%s'" % (engWord.lower()))

    query = "SELECT wl.word, wl.wordid " \
            "FROM words AS w LEFT JOIN wordlist AS wl ON wl.wordid IN (%s) " \
            "WHERE w.pattern = '%s' ORDER BY wl.frequency DESC, w.wordid DESC" % (idList, engWord.lower())
    rl = db.getFieldData(query)

    exist, mWord, id = (True, rl[0][0], rl[0][1]) if len(rl) > 0 else (False, "", "")

    return exist, mWord, id


def getMalWord(engWord):

    isExist, malWord, malId = getMalFromDB(engWord)

    if isExist:
        if processRules & 1 == 1:
            query = "UPDATE wordList SET frequency = frequency + 1 WHERE wordId = '%s'" % (malId)
            db.implement(query)

        return malWord
    else:
        return createdMalWord(engWord)


def convertToMal(textToConvert, processIns):

    global processRules
    processRules = processIns

    nonchars = '\.\,\!\?\;\“\”\"' + "\'"
    MEDict = {}
    convertedMalText = ''

    if textToConvert != '':
        engWordList = re.findall(r"[\w']+|[" + nonchars + "]", textToConvert)

        for i in range(len(engWordList)):

            if engWordList[i] in nonchars:
                convertedMalText += engWordList[i]
            elif engWordList[i].isnumeric():
                convertedMalText += '  ' + engWordList[i]
            else:
                mal_word = getMalWord(engWordList[i])
                MEDict[mal_word] = engWordList[i]
                convertedMalText += '  ' + mal_word if i != 0 else mal_word

    return convertedMalText, MEDict


def more_mal_options(engWord: str) -> list:

    optNum = 100
    primList = flatten(mConvertion(engWord))

    return primList + flatten(tokenizeWord(engWord))[:optNum-len(primList)]


if __name__ == "__main__":
    getMalWord("nwsfnosdnfo")
    pass

