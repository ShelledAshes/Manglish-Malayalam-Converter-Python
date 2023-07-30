import re
from gen import DB as db, LOG


def incrementFrequency(dictMalEng, malWordList):

    for mWord, eWord in dictMalEng.items():
        print(mWord, eWord)

        mal_cnt = db.getFieldValueI("COUNT(word)", "wordlist", f"word='{mWord}'")
        if mal_cnt > 1:
            mal_idlist = db.getFieldValue("GROUP_CONCAT(wordid)", "wordlist", f"word='{mWord}'")
            eng_idlist = db.getFieldValue("wordid", "words", f"pattern='{eWord.lower()}'")
            for id in mal_idlist.split(','):
                if id in eng_idlist:
                    mal_id = id
                    break
        else:
            mal_id = db.getFieldValueI("wordid", "wordlist", f"word='{mWord}'")

        cnt = malWordList.count(mWord)
        db.implement(f"UPDATE wordList SET frequency = frequency + {cnt} WHERE wordid = {mal_id}")


def decrement_replace(m_word, rm_word, e_word):

    if db.getFieldValueI("COUNT(pattern)", "words", "pattern = '%s'" % e_word.lower()) > 0:
        eword_id = db.getFieldValueI("id", "words", "pattern = '%s'" % e_word.lower())
    else:
        eword_id = db.getId("words")

    freq = db.getFieldValueI("frequency", "wordlist", f"word= '{m_word}' and engword_id={eword_id}")
    
    if freq > 0:
        rmword_id = db.getId("wordlist", "wordid")
        db.implement("insert into wordlist (wordid,word,engword_id) values(%d,'%s',%d)" % (rmword_id, rm_word, eword_id))

        malword_idlist = db.getFieldValue("wordid", "words", "id= %d" % eword_id)
        new_idlist = malword_idlist + "," + str(rmword_id)
        db.implement("UPDATE words SET wordid = '%s' WHERE id= %d" % (new_idlist, eword_id))
    else:
        db.implement("UPDATE wordList SET word = '%s' WHERE word= '%s'" % (rm_word, m_word))


def getReplacedMalText(text, word, rWord, engWord, exChars):

    LOG(text)

    ex = exChars
    new_text = ''

    word_list = [word for word in re.split(ex, text) if word]
    LOG(word_list)
    for i in range(len(word_list)):
        if word_list[i] == word:
            word_list[i] = rWord

        if word_list[i] not in ex:
            new_text += '  ' + word_list[i] if i != 0 else word_list[i]
        else:
            new_text += word_list[i]

    LOG(new_text)
    return new_text


def getEngWordFromDB(malWord) -> str:

    query = f"select w.pattern from wordlist as wl LEFT join words as w on w.wordId=wl.wordId  \
            where wl.word == '{malWord}' order by w.id DESC LIMIT 1"
    engWord = db.implement(query)[0][0]
    return engWord


def checkSavedWords(engWord):

    malWord_idList = db.getFieldValue("wordid", "words", f"pattern = '{engWord}'")
    qry = f"SELECT word from wordlist where wordid in ({malWord_idList})"
    return db.getFieldData(qry)


def deleteDataInDb(engId, malId):

    idList = db.getFieldValue("wordid", "words", f"id={engId}")
    LOG(idList)

    db.implement(f"delete from wordlist where wordid={malId}")

    if ',' + malId in idList:
        idList = idList.replace(',' + malId, '')
        db.implement(f"update words set wordid= '{idList}' where id={engId}")

    elif malId + ',' in idList:
        idList = idList.replace(malId+',', '')
        db.implement(f"update words set wordid= '{idList}' where id={engId}")

    elif malId == idList:
        db.implement(f"delete from words where id={engId}")


def editEngDataInDb(engId, malId, editedEngWord):

    existingEngWord = db.getFieldValue("pattern", "words", f"id={engId}")

    if editedEngWord == existingEngWord:
        return
    else:
        idList = db.getFieldValue("wordid", "words", f"id={engId}")

        if idList == malId:
            db.implement(f"update words set pattern='{editedEngWord}' where id={engId}")
        elif ',' in idList:
            if ',' + malId in idList:
                idList = idList.replace(',' + malId, '')
            elif malId + ',' in idList:
                idList = idList.replace(malId + ',', '')

            db.implement(f"update words set pattern= '{idList}' where id={engId}")
            newEngId = db.getId("words")
            db.implement(f"insert into words (id,pattern,wordid) values({newEngId},'{editedEngWord}',{malId})")
            db.implement(f"update wordlist set engword_id={newEngId} where wordid={malId}")


def insertDataInDb(engWord, malWord):

    eWordId = db.getId("words")
    mWordId = db.getId("wordlist", "wordid")

    db.implement(f"insert into words (id,pattern,wordid) values({eWordId},'{engWord}',{mWordId})")
    db.implement(f"insert into wordlist (wordid,word,engword_id) values({mWordId},'{malWord}',{eWordId})")


def alterDataInDb(eWordEditList, mWordEditList, wordDelList, insertedWordList):

    try:
        if len(eWordEditList) > 0:
            for eData in eWordEditList:
                eid, mid, word = eData[0], eData[1], eData[2]
                editEngDataInDb(id, word)

        if len(mWordEditList) > 0:
            for mData in mWordEditList:
                id, word, freq = mData[0], mData[1], mData[2]
                db.implement(f"update wordlist set word='{word}',frequency={freq} where wordid={id}")

        if len(insertedWordList) > 0:
            for data in insertedWordList:
                eWord, mWord = data[0], data[1]
                insertDataInDb(eWord, mWord)

        if len(wordDelList) > 0:
            for ids in wordDelList:
                eWordId, mWordId = ids[0], ids[1]
                deleteDataInDb(eWordId, mWordId)
    except Exception as e:
        raise Exception(e)
    finally:
        return [], [], [], []


if __name__ == "__main__":
    pass