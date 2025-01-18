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

def saveImage(sqliteConn , sno1 ,snaName1, sno2, snaName2):
    try:        
        sqliteCursor = sqliteConn.cursor()
        # MariaDB SQL
        #SELECT hd.*,ns.sna FROM historyData hd Inner Join ntuSiteData ns On hd.sno=ns.sno WHERE ns.sno='500119048' 
        #SELECT mday ,sbi, catchTime FROM historyData WHERE sno='500119048' and mday > '2021-12-20 00:00:00' and mday < '2021-12-21 00:00:00' and DATE_FORMAT(catchTime,"%i:%S") = '05:00' Order by catchTime
        sqlCmd= f"""
        SELECT catchTime ,sbi ,sno FROM historyData WHERE (sno='{sno1}' Or sno='{sno2}') 
        and catchTime >= '2021-12-20 00:00:00' and catchTime < '2021-12-21 00:00:00' 
        and (substr(catchTime,16,1)='0' or substr(catchTime,16,1)='5') Order by sno,catchTime
        """
        sqliteCursor.execute(sqlCmd)
        allRow = sqliteCursor.fetchall()
        sqliteCursor.close()
        xList = []
        xList1 =[]
        xList2=[]
        xList3=[]
        xList4=[]
        yList = []
        yList1 =[]
        yList2=[]
        yList3=[]
        yList4=[]

        for r in allRow:            
            timeInt = convertHHmmTiInt(r[0][11:])
            dayDate = r[0][8:10]
            sno = r[2]
            if (sno == '500119048'):
                xList.append(timeInt)
                yList.append(r[1])
            elif (sno == '500119077'):
                xList1.append(timeInt)
                yList1.append(r[1])
            # elif "2021-12-21" in r[0]:
            #     xList1.append(timeInt)
            #     yList1.append(r[1])
            # elif "2021-12-22" in r[0]:
            #     xList2.append(timeInt)
            #     yList2.append(r[1])
            # elif "2021-12-23" in r[0]:
            #     xList3.append(timeInt)
            #     yList3.append(r[1])
            # elif "2021-12-24" in r[0]:
            #     xList4.append(timeInt)
            #     yList4.append(r[1])

        snaName1 = snaName1.replace("YouBike2.0_","")       
        snaName2 = snaName2.replace("YouBike2.0_","")         
        plt.figure(figsize=(16,8))
        plt.title(snaName1 + ' V.S.' + snaName2)
        
        line, = plt.plot(xList, yList)
        line1, =plt.plot(xList1, yList1)
        # line2, =plt.plot(xList2, yList2)
        # line3, =plt.plot(xList3, yList3)
        # line4, =plt.plot(xList4, yList4) 

        #處理 Label 呈現
        lineObjList = [line, line1] #line1, line2, line3, line4,]
        labelList =  [snaName1,snaName2]
        plt.legend(lineObjList, labelList ,loc='upper left')
        labX = ['00:30:00','03:30:00','06:30:00','09:30:00'
        ,'12:30:00','15:30:00','18:30:00','21:30:00' ,'24:30:00']
        labInt = [convertHHmmTiInt(x) for x in labX]
        plt.xticks(labInt,labX)
        # plt.show()
        # print(f"OK")
        plt.savefig(f"Comp{dayDate}-{snaName1}_{snaName2}.png")

    except Exception as e:
        print(f"-- exception --{e}")
        logging.error("Catch an exception.", exc_info=True)
        sys.exit(1)

#print(convertHHmmTiInt('12:30:00'))

sno1 = "500119048"
snaName1 = "YouBike2.0_臺大大一女舍北側"
sno2= "500119077"
snaName2 = 'YouBike2.0_臺大博雅館西側'
print(f'--{snaName2}--')
saveImage(sqliteConn, sno1, snaName1, sno2, snaName2)

#region
""" -------------------------------------
問題: 如何自動儲存不同天的圖片?

--------------------------------------------------------"""
#endregion
# 