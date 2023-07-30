
import sqlite3

schemefile = sqlite3.connect("mal.db")
cursor = schemefile.cursor()


def setupScheme():
    cursor.execute('''
    create table if not exists symbols(
      id integer not null primary key autoincrement,
      pattern varchar(32),
      value1  varchar(32),
      value2  varchar(32),
      value3 varchar(32),
      type integer,
      matchType integer,
      frequency integer default 0
    )
  ''')

    cursor.execute('''
    create table if not exists words(
      id integer not null primary key autoincrement,
      pattern varchar(120),
      wordid varchar(100)
    )
  ''')
    cursor.execute('''
    create table if not exists wordlist(
      wordid integer not null primary key autoincrement,
      word varchar(120),
      frequency integer default 0,
      engword_id integer default 0
    )
  ''')

    # INDEXES TO SPEED UP QUERY
    cursor.execute('create index pattern_SYMBOLS on symbols (pattern asc)')
    cursor.execute('create index pattern_WORDS on words (pattern asc)')
    cursor.execute('create index wordid_WORDLIST on wordlist (wordId asc)')
    cursor.execute('create index value1_SYMBOLS on symbols (value1 asc)')

    schemefile.commit()
    return True


def saveKeyValue(key, values, Tokentype, matchType):
    if str(type(values)) == "<class 'list'>":
        if len(values) > 2:
            value1 = values[0]
            value2 = values[1]
            value3 = values[2]
        elif len(values) > 1:
            value1 = values[0]
            value2 = values[1]
            value3 = ''
    else:
        value1 = values
        value2 = ''
        value3 = ''

    sql = '''insert into symbols 
      (pattern,value1,value2,value3,type,matchType) 
      values('%s','%s','%s','%s',%d,%d)''' % (key, value1, value2, value3, Tokentype, matchType)
    return cursor.execute(sql)  # ,[])


def generateCV():
    tokensv = []
    tokensc = []
    sqlv = "select pattern,value2 from symbols where type = 1"
    sqlc = "select pattern,value1,value2 from symbols where type=2"
    res = cursor.execute(sqlv)
    for i in res:
        tokensv.append(i)
    res = cursor.execute(sqlc)
    for i in res:
        tokensc.append(i)
    for consonant in tokensc:
        consonant_has_inherent_a_sound = (
                    consonant[0][len(consonant[0]) - 1] == 'a' and consonant[0][len(consonant[0]) - 2] != 'a')
        if consonant_has_inherent_a_sound:
            pattern = consonant[0][:len(consonant[0]) - 1]
            value = consonant[1] + '്'
            saveKeyValue(pattern, value, 3, 1)
        for v in tokensv:
            if v[1] != '':
                if consonant_has_inherent_a_sound:
                    pattern = consonant[0][:len(consonant[0]) - 1] + v[0]
                else:
                    pattern = consonant[0] + v[0]
                values = consonant[1] + v[1]
                saveKeyValue(pattern, values, 3, 1)


def extractKeysAndValues(keys, values, Tokentype, matchType=1):
    if str(type(keys)) == "<class 'tuple'>":
        for key in keys:
            if str(type(key)) == "<class 'tuple'>":
                extractKeysAndValues(key, values, Tokentype, 2)
            else:
                saveKeyValue(key, values, Tokentype, matchType)
    else:
        saveKeyValue(keys, values, Tokentype, matchType)


def vowel(hash):
    for hashKey in hash:
        extractKeysAndValues(hashKey, hash[hashKey], 1, 1)
        schemefile.commit()


def consonants(hash):
    for hashKey in hash:
        extractKeysAndValues(hashKey, hash[hashKey], 2, 1)
        schemefile.commit()


def createSchemeFile():
    setupScheme()

    vowel({"~": "്"})
    vowel({"a": "അ"})
    vowel({"a": ["ഃ", "അഃ"]})
    vowel({"ah": ["ഃ", "അഃ"]})
    vowel({(("a"), "aa", "A"): ["ആ", "ാ"]})
    vowel({"i": ["ഇ", "ി"]})
    vowel({("ee", "I", "ii", ("i")): ["ഈ", "ീ"]})
    vowel({"u": ["ഉ", "ു"]})
    vowel({(("u"), "uu", "oo", "U"): ["ഊ", "ൂ"]})
    vowel({(("ri", "ru"), "R"): ["ഋ", "ൃ", "ർ"]})
    vowel({"e": ["എ", "െ"]})
    vowel({("E", ("e")): ["ഏ", "േ"]})
    vowel({("ai", "ei"): ["ഐ", "ൈ"]})
    vowel({"o": ["ഒ", "ൊ"]})
    vowel({("O", ("o")): ["ഓ", "ോ"]})
    vowel({("ou", "au", "ow"): ["ഔ", "ൌ"]})
    vowel({("OU", "AU", "OW"): ["ഔ", "ൗ"]})

    consonants({("ka"): "ക"})
    consonants({("kha", ("gha")): "ഖ"})
    consonants({"ga": "ഗ"})
    consonants({("gha", ("kha")): "ഘ"})
    consonants({("NGa", ("nga")): "ങ്ങ"})
    consonants({"cha": "ച"})
    consonants({("CHa", ("cha", "jha")): "ഛ"})
    consonants({(("cha")): "ച്ഛ"})
    consonants({"ja": "ജ"})
    consonants({("jha", "JHa"): "ഝ"})
    consonants({(("nja"), "NJa"): "ഞ്ഞ"})
    consonants({("ta", ("tta")): "റ്റ"})
    consonants({(("da", "ta"), "Ta"): "ട"})
    consonants({(("da", "ta"), "TTa"): "ഠ"})
    consonants({("Da", ("da")): "ഡ"})
    consonants({(("da"), "DDa"): "ഢ"})
    consonants({("tha", ("ta")): "ത"})
    consonants({(("tha", "dha"), "thha"): "ഥ"})
    consonants({(("tha", "dha"), "tathha"): "ത്ഥ"})
    consonants({"da": "ദ"})
    consonants({(("dha"), "ddha"): "ദ്ധ"})
    consonants({"dha": "ധ"})
    consonants({"pa": "പ"})
    consonants({("pha", "fa", "Fa"): "ഫ"})
    consonants({"ba": "ബ"})
    consonants({"bha": "ഭ"})
    consonants({("va", "wa"): "വ"})
    consonants({("Sa", ("sha", "sa")): "ശ"})
    consonants({("sa", "za"): "സ"})
    consonants({"ha": "ഹ"})

    consonants({"nja": ["ഞ", "ഞ്ഞ"]})
    consonants({"nga": ["ങ", "ങ്ങ"]})

    consonants({("kra"): "ക്ര"})
    consonants({"gra": "ഗ്ര"})
    consonants({("ghra", ("khra")): "ഘ്ര"})
    consonants({("CHra", ("chra", "jhra")): "ഛ്ര"})
    consonants({"jra": "ജ്ര"})
    consonants({(("dra", "tra"), "Tra"): "ട്ര"})
    consonants({("Dra", ("dra")): "ഡ്ര"})
    consonants({"Dhra": "ഢ്ര"})
    consonants({("thra", ("tra")): "ത്ര"})
    consonants({"dra": "ദ്ര"})
    consonants({("ddhra", ("dhra")): "ദ്ധ്ര"})
    consonants({"dhra": "ധ്ര"})
    consonants({"pra": "പ്ര"})
    consonants({("phra", "fra", "Fra"): "ഫ്ര"})
    consonants({"bra": "ബ്ര"})
    consonants({"bhra": "ഭ്ര"})
    consonants({("vra", "wra"): "വ്ര"})
    consonants({("Sra", ("shra", "sra")): "ശ്ര"})
    consonants({"shra": "ഷ്ര"})
    consonants({("sra", "zra"): "സ്ര"})
    consonants({"hra": "ഹ്ര"})
    consonants({"nthra": "ന്ത്ര"})
    consonants({(("ndra", "ntra"), "nDra", "Ntra", "nTra"): "ണ്ട്ര"})
    consonants({"ndra": "ന്ദ്ര"})
    consonants({(("thra"), "THra", "tthra"): "ത്ത്ര"})
    consonants({"nnra": "ന്ന്ര"})
    consonants({("kkra", "Kra", "Cra"): "ക്ക്ര"})
    consonants({("mpra", "mbra"): "മ്പ്ര"})
    consonants({("skra", "schra"): "സ്ക്ര"})
    consonants({"ndhra": "ന്ധ്ര"})
    consonants({"nmra": "ന്മ്ര"})
    consonants({("NDra", ("ndra")): "ണ്ഡ്ര"})

    consonants({("cra"): "ക്ര"})

    consonants({"ya": "യ"})
    consonants({"sha": "ഷ"})
    consonants({"zha": "ഴ"})
    consonants({("xa", ("Xa")): "ക്സ"})
    consonants({"ksha": "ക്ഷ"})
    consonants({"nka": "ങ്ക"})
    consonants({("ncha", ("nja")): "ഞ്ച"})
    consonants({"ntha": "ന്ത"})
    consonants({"nta": "ന്റ"})
    consonants({(("nda"), "nDa", "Nta"): "ണ്ട"})
    consonants({"nda": "ന്ദ"})
    consonants({"tta": "ട്ട"})
    consonants({(("tha"), "THa", "ttha"): "ത്ത"})
    consonants({"lla": "ല്ല"})
    consonants({("LLa", ("lla")): "ള്ള"})
    consonants({"nna": "ന്ന"})
    consonants({("NNa", ("nna")): "ണ്ണ"})
    consonants({("bba", "Ba"): "ബ്ബ"})
    consonants({("kka", "Ka"): "ക്ക"})
    consonants({("gga", "Ga"): "ഗ്ഗ"})
    consonants({("jja", "Ja"): "ജ്ജ"})
    consonants({("mma", "Ma"): "മ്മ"})
    consonants({("ppa", "Pa"): "പ്പ"})
    consonants({("vva", "Va", "wwa", "Wa"): "വ്വ"})
    consonants({("yya", "Ya"): "യ്യ"})
    consonants({("mpa", "mba"): "മ്പ"})
    consonants({("ska", "scha"): "സ്ക"})
    consonants({(("cha"), "chcha", "ccha", "Cha"): "ച്ച"})
    consonants({"ndha": "ന്ധ"})
    consonants({"jnja": "ജ്ഞ"})
    consonants({"nma": "ന്മ"})
    consonants({("Nma", ("nma")): "ണ്മ"})
    consonants({("nJa", ("nja")): "ഞ്ജ"})
    consonants({("NDa", ("nda")): "ണ്ഡ"})

    consonants({("ra"): "ര"})
    consonants({(("ra"), "Ra"): "റ"})
    consonants({("na"): "ന"})
    consonants({(("na"), "Na"): "ണ"})
    consonants({("la"): "ല"})
    consonants({(("la"), "La"): "ള"})
    consonants({("ma"): "മ"})

    consonants({("rva", "rwa"): "ര്വ"})
    consonants({"rya": "ര്യ"})
    consonants({("Rva", "Rwa", ("rva")): "റ്വ്"})
    consonants({("Rya", ("rya")): "റ്യ്"})
    consonants({("nva", "nwa"): "ന്വ"})
    consonants({"nya": "ന്യ"})
    consonants({("Nva", "Nwa", ("nva", "nwa")): "ണ്വ"})
    consonants({("Nya", ("nya")): "ണ്യ"})
    consonants({("lva", "lwa"): "ല്വ"})
    consonants({"lya": "ല്യ"})
    consonants({("Lva", "Lwa", ("lva", "lwa")): "ള്വ"})
    consonants({("Lya", ("lya")): "ള്യ"})
    consonants({("mva", "mwa"): "മ്വ"})
    consonants({"mya": "മ്യ"})
    consonants({'c': "ക്"})

    generateCV()

    consonants({
        (("ru")): "ര്",
        (("r~", "ru")): "റ്",
        (("nu")): "ന്",
        (("n~", "nu")): "ണ്",
        (("lu")): "ല്",
        (("l~", "lu")): "ള്",
        (("mu")): "മ്",
        ("r~"): "ര്",
        ("R~"): "റ്",
        ("n~"): "ന്",
        ("N~"): "ണ്",
        ("l~"): "ല്",
        ("L~"): "ള്",
        ("m~"): "മ്",
        "m": ["ം", "ം", "മ"],
        "n": ["ൻ", "ന്‍", "ന"],
        ("N", ("n")): ["ൺ", "ണ്‍", "ണ"],
        "l": ["ൽ", "ല്‍", "ല"],
        ("L", ("l")): ["ൾ", "ള്‍", "ള"],
        ("r"): ["ർ", "ര്‍", "ര"]
    })

    consonants({('q','qu'): "ക്യു"})
    consonants({('q', 'qu'): "കോ"})


createSchemeFile()

