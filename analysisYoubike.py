#region
""" -------------------------------------
說明 : 將存放在 Mariadb 10 中的資料轉入本機端的 Sqlite 資料庫中

--------------------------------------------------------"""
#endregion
# 
import logging
import os
from os import path
import sys
import decimal
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mticker
plt.rcParams['font.sans-serif'] = ['microsoft jhenghei'] 

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
sqliteConn = sqlite3.connect(Db_File)
sqliteCursorSite = sqliteConn.cursor()
sqliteCursorSite.execute("SELECT sno,sna FROM ntuSiteData")
allSiteRows = sqliteCursorSite.fetchall()
sqliteCursorSite.close()

def saveImage(sqliteConn , sno ,statName):
    try:        
        sqliteCursor = sqliteConn.cursor()
        # MariaDB SQL
        #SELECT hd.*,ns.sna FROM historyData hd Inner Join ntuSiteData ns On hd.sno=ns.sno WHERE ns.sno='500119048' 
        #SELECT mday ,sbi, catchTime FROM historyData WHERE sno='500119048' and mday > '2021-12-20 00:00:00' and mday < '2021-12-21 00:00:00' and DATE_FORMAT(catchTime,"%i:%S") = '05:00' Order by catchTime

        sqliteCursor.execute(f"SELECT catchTime ,sbi FROM historyData WHERE sno='{sno}' and catchTime >= '2021-12-20 00:00:00' and catchTime <= '2021-12-27 00:30:00' and substr(catchTime,15,5)='30:00' Order by catchTime") #
        allRow = sqliteCursor.fetchall()
        sqliteCursor.close()
        xList = []
        yList = []
        for r in allRow:    
            xList.append(r[0])
            yList.append(r[1])

        statName = statName.replace("YouBike2.0_","")            
        plt.figure(figsize=(16,8))
        plt.title(statName)
        #fig, ax = plt.subplots(1,1)
        plt.plot(xList, yList)  
        
        # width = 0.35
        # x1 = np.arange(len(x)) 

        # fig, ax = plt.subplots()
        # rects1 = ax.bar(x1 - width/2, y1, width, label='商家A')
        # rects2 = ax.bar(x1 + width/2, y2, width, label='商家B')

        # ax.set_title('Matplotlib—柱狀圖')
        # ax.set_xticks(x1)
        # ax.set_xticklabels(x)
        # ax.legend()
        
        #tick_spacing = 24 # x軸密集度
        #ax.xaxis.set_major_locator(mticker.MultipleLocator(tick_spacing))
        labX = ['2021-12-20 00:30:00','2021-12-21 00:30:00','2021-12-22 00:30:00','2021-12-23 00:30:00'
        ,'2021-12-24 00:30:00','2021-12-25 00:30:00','2021-12-26 00:30:00','2021-12-27 00:30:00']
        plt.xticks(labX,labX)
        plt.savefig(f"Plot{statName}.png")

    except Exception as e:
        print(f"-- exception --{e}")
        logging.error("Catch an exception.", exc_info=True)
        sys.exit(1)
    
for r in allSiteRows:
    sno = r[0]
    sna = r[1]
    print(f'--{sna}--')
    if '臺大校史館南側' in sna :
        continue
    saveImage(sqliteConn, sno, sna)
    # if allSiteRows.index(r) == 2:
    #     break
