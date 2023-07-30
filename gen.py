import sqlite3
import inspect


class DB:

    conn = sqlite3.connect("mal.db")
    cursor = conn.cursor()

    def __init__(self):
        pass

    @staticmethod
    def implement(query: str):
        print('executingDB*************', query)

        DB.cursor.execute(query)
        DB.conn.commit()

    @staticmethod
    def getFieldData(query: str):
        print('dataB*************', query, '-> ', end=" ")

        DB.cursor.execute(query)
        return DB.cursor.fetchall()

    @staticmethod
    def getFieldValue(field="", table="", cndn=""):

        qry = "SELECT " + field + " FROM " + table
        qry = qry + " WHERE " + cndn if cndn != "" else qry

        try:
            value = str(DB.getFieldData(qry)[0][0])
        except IndexError:
            value = ''
        print(value)

        return value

    @staticmethod
    def getFieldValueI(field="", table="", cndn=""):

        return int(DB.getFieldValue(field, table, cndn))

    @staticmethod
    def getId(tbl, id="id"):

        qry = f"WITH RECURSIVE  cnt(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM cnt LIMIT (SELECT ifnull(max({id}),0) from {tbl}))\
                    SELECT ifnull(min(x),(SELECT ifnull(max({id}),0) from {tbl})+1) as nextid\
                    FROM cnt\
                    WHERE x NOT IN (select {id} from {tbl}) order by x"

        return int(DB.getFieldData(qry)[0][0])


def LOG(*datas):
    callerframerecord = inspect.stack()[1]
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    fileName = info.filename.split('\\')[-1]

    print(fileName + ' >> ' + info.function + ' >> ' + str(info.lineno) + ' :-- ', end="")
    for data in datas[:-1]:
        print(data, end=" ")
    else:
        print(datas[-1])

    
if __name__ == "__main__" :
    pass
