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
logging.basicConfig(level=logging.ERROR, filename='analysis.log', filemode='w', format=FORMAT)
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

def convertHHmmTiInt(hhMm):
    hh = hhMm[0:2]
    mm = hhMm[3:5]
    return int(hh)*60 + int(mm)

def saveImage(sqliteConn , sno ,statName):
    try:        
        sqliteCursor = sqliteConn.cursor()
        # MariaDB SQL
        #SELECT hd.*,ns.sna FROM historyData hd Inner Join ntuSiteData ns On hd.sno=ns.sno WHERE ns.sno='500119048' 
        #SELECT mday ,sbi, catchTime FROM historyData WHERE sno='500119048' and mday > '2021-12-20 00:00:00' and mday < '2021-12-21 00:00:00' and DATE_FORMAT(catchTime,"%i:%S") = '05:00' Order by catchTime

        sqliteCursor.execute(f"SELECT catchTime ,sbi FROM historyData WHERE sno='{sno}' and catchTime >= '2021-12-20 00:00:00' and catchTime <= '2021-12-27 00:30:00' and (substr(catchTime,16,1)='0' or substr(catchTime,16,1)='5') Order by catchTime") #
        allRow = sqliteCursor.fetchall()
        sqliteCursor.close()
        xList = []
        xList1 =[]
        xList2=[]
        xList3=[]
        xList4=[]
        xList5=[]
        xList6=[]
        yList = []
        yList1 =[]
        yList2=[]
        yList3=[]
        yList4=[]
        yList5=[]
        yList6=[]
        totList =[]
        for r in allRow:  #先定義所有List皆為空陣列          
            timeInt = convertHHmmTiInt(r[0][11:])
            if "2021-12-20" in r[0]:
                xList.append(timeInt)
                yList.append(r[1])
            elif "2021-12-21" in r[0]:
                xList1.append(timeInt)
                yList1.append(r[1])
            elif "2021-12-22" in r[0]:
                xList2.append(timeInt)
                yList2.append(r[1])
            elif "2021-12-23" in r[0]:
                xList3.append(timeInt)
                yList3.append(r[1])
            elif "2021-12-24" in r[0]:
                xList4.append(timeInt)
                yList4.append(r[1])
            elif "2021-12-25" in r[0]:
                xList5.append(timeInt)
                yList5.append(r[1])
            elif "2021-12-26" in r[0]:
                xList6.append(timeInt)
                yList6.append(r[1])

        

        for i in range(len(yList)):
            newItem = (yList[i]+yList1[i]+yList2[i]+yList3[i]+yList4[i])//5
            totList.append(newItem)

        statName = statName.replace("YouBike2.0_","")            
        plt.figure(figsize=(16,8))
        plt.title(statName)
        
        line, = plt.plot(xList, totList)
        # line1, =plt.plot(xList1, yList1)
        # line2, =plt.plot(xList2, yList2)
        # line3, =plt.plot(xList3, yList3)
        # line4, =plt.plot(xList4, yList4)
        line5, =plt.plot(xList5, yList5)
        # line6, =plt.plot(xList6, yList6)  

        #處理 Label 呈現
        lineObjList = [line , line5] #line1, line2, line3, line4, line6
        labelList =  ['Weekdays' ,'2021-12-25'] #, '2021-12-21' , '2021-12-22' , '2021-12-23' , '2021-12-24' , '2021-12-25' , '2021-12-26']
        plt.legend(lineObjList, labelList ,loc='upper left')
        labX = ['00:30:00','03:30:00','06:30:00','09:30:00','12:30:00','15:30:00','18:30:00','21:30:00' ,'24:30:00']
        labInt = [convertHHmmTiInt(x) for x in labX]
        plt.xticks(labInt,labX)
        # plt.show()
        # print(f"OK")
        plt.savefig(f"Lines{statName}.png")

    except Exception as e:
        print(f"-- exception --{e}")
        logging.error("Catch an exception.", exc_info=True)
        sys.exit(1)

#print(convertHHmmTiInt('12:30:00'))

for r in allSiteRows:
    sno = r[0]
    sna = r[1]
    print(f'--{sna}--')
    if '臺大校史館南側' in sna :
        continue
    saveImage(sqliteConn, sno, sna)
    # if allSiteRows.index(r) == 0:
    #     break
