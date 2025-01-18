#region
""" -------------------------------------
說明 : 將存放在 Mariadb 10 中的資料轉入本機端的 Sqlite 資料庫中

--------------------------------------------------------"""
#endregion
# 
import logging
import os
from os import path
import mariadb
import sys
import decimal
import sqlite3

D=decimal.Decimal
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.ERROR, filename='syncMariadbToSqlite.log', filemode='w', format=FORMAT)
workdir = os.path.dirname(__file__)

# Python decimal 的 必須轉換才能新增到 Sqlite
def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return D(s)

# Register the adapter
sqlite3.register_adapter(D, adapt_decimal)
# Register the converter
sqlite3.register_converter("decimal", convert_decimal)

Db_File = path.join(workdir, 'youbikeData.db')
# sqliteConn = sqlite3.connect(Db_File)
# cursor = sqliteConn.cursor()
# print('資料庫連線成功!')
# sqliteConn.close()

DbConfig = {
    "user":"schooluser",
    "password":"hw@2021Shuan",
    "host":"192.168.1.13",
    "port":3307,
    "database":"youbikeDb"
}

def syncTableData(tbName ,filterColumn=''):
    global DbConfig
    
    try:
        mariadbConn = mariadb.connect(
            user= DbConfig["user"],
            password= DbConfig["password"],
            host= DbConfig["host"],
            port= DbConfig["port"],
            database=DbConfig["database"]
        )
        sqliteConn = sqlite3.connect(Db_File)        
        if filterColumn:
            sqliteCursor = sqliteConn.cursor()
            sqliteCursor.execute(f"Select Max({filterColumn}) From {tbName}")
            onRow = sqliteCursor.fetchone()
            if onRow and onRow[0]:
                filterVal = onRow[0]
                filterColumn = " Where " + filterColumn + " > '" + filterVal + "' "
            else:
                filterColumn = ""
            sqliteCursor.close()
            
        
        # Get Cursor
        mariadbCur = mariadbConn.cursor()        
        mariadbCur.execute(f"DESCRIBE {tbName}")
        fieldsList = mariadbCur.fetchall()        
        colsList = []
        paramList = []
        for fieldInfo in fieldsList:
            colsList.append(fieldInfo[0])
            paramList.append('?')
        
        mariadbCur.execute(f"Select * From {tbName}{filterColumn}")
        # 取出全部資料
        batchRows = 10
        sumRows = 0
        getRowsCount = 0
        sqliteCursor = sqliteConn.cursor()
        while getRowsCount == sumRows:            
            #allRows = mariadbCur.fetchall()
            allRows = mariadbCur.fetchmany(batchRows)
            getRowsCount = mariadbCur.rowcount
            sqliteCursor.executemany(f"INSERT INTO {tbName} ( " + ",".join(colsList) + " ) VALUES (" + ",".join(paramList) + ")", allRows)
            sqliteConn.commit()
            sumRows += batchRows
            
        sqliteCursor.close()
        mariadbCur.close()        
        # Close Connection
        mariadbConn.close()
        sqliteConn.close()
    except mariadb.Error as e:
        print(f"Error : {e}")
        sys.exit(1)
    
syncTableData('historyData' , 'catchTime') # siteData historyData  ntuSiteData catchTime

