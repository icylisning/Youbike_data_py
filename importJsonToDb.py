#region
""" -------------------------------------
說明 : 將 youbike 的 json 資料會入 MariaDB 10 資料庫中
資料表結構為
CREATE TABLE `historyData` (
  `catchTime` datetime NOT NULL,
  `sno` varchar(10) NOT NULL,
  `sna` varchar(50) NOT NULL,
  `tot` int(11) NOT NULL,
  `sbi` int(11) NOT NULL,
  `sarea` varchar(50) NOT NULL,
  `mday` datetime NOT NULL,
  `lat` decimal(10,6) NOT NULL,
  `lng` decimal(10,6) NOT NULL,
  `ar` varchar(50) NOT NULL,
  `sareaen` varchar(50) NOT NULL,
  `snaen` varchar(100) NOT NULL,
  `aren` varchar(100) NOT NULL,
  `bemp` int(11) NOT NULL,
  `act` int(11) NOT NULL,
  `srcUpdateTime` datetime NOT NULL,
  `updateTime` datetime NOT NULL,
  `infoTime` datetime NOT NULL,
  `infoDate` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
--------------------------------------------------------"""
#endregion
#  本機環境呼叫命令:
#  c:\Users\TW\scoop\apps\winpython\current\python-3.8.9.amd64\python.exe importJsonToDb.py
#  匯入 json 檔案過程 會根據資料表中的 catchTime 來判斷是否需要匯入(json 中的資料值(catchTime) 必須大於資料表中的 catchTime 最大值)
#  
import mariadb
import sys
import logging
import os
from os import path,walk
import json 

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.ERROR, filename='importJsonToDb.log', filemode='w', format=FORMAT)
workdir = os.path.dirname(__file__)
print('-- workdir = ' + workdir +'---')
DIRSep = os.sep
MaxDbCatchTime = ''
DATA_DIR = path.join(workdir, 'data' , 'json')
DbConfig = {
    "user":"schooluser",
    "password":"hw@2021Shuan",
    "host":"192.168.1.13",
    "port":3307,
    "database":"youbikeDb"
}

def getNtuSites():
    global DbConfig
    dicSites = {}
    try:
        conn = mariadb.connect(
            user= DbConfig["user"],
            password= DbConfig["password"],
            host= DbConfig["host"],
            port= DbConfig["port"],
            database=DbConfig["database"]
        )
        # Get Cursor
        cur = conn.cursor()        
        cur.execute("Select sno From ntuSiteData")
        for (sno,) in cur:
            if sno:
                dicSites[sno] = 1
        cur.close()	
        # Close Connection
        conn.close()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    return dicSites

def insertDataToDb (srcList):
    # Connect to MariaDB Platform     
    global MaxDbCatchTime
    global DbConfig
    global NtuSites
    try:
        conn = mariadb.connect(
            user= DbConfig["user"],
            password= DbConfig["password"],
            host= DbConfig["host"],
            port= DbConfig["port"],
            database=DbConfig["database"]
        )
        # Get Cursor
        cur = conn.cursor()        
        #Adding Data
        # Disable Auto-Commit
        if not (MaxDbCatchTime):
            cur.execute("SELECT Max(catchTime) as maxCatchTime FROM historyData")
            for (maxCatchTime,) in cur:
                if not maxCatchTime is None:
                    dt=maxCatchTime.strftime('%Y-%m-%d %H:%M:%S')
                    MaxDbCatchTime = dt
                break         
            cur.close()	
            cur = conn.cursor()
        conn.autocommit = False
        for rowJson in srcList:
            # cur.execute(
            #     "INSERT INTO `historyData` (`catchTime`, `sno`, `sna`, `tot`, `sbi`, `sarea`, `mday`, `lat`, `lng`, `ar`, `sareaen`, `snaen`, `aren`, `bemp`, `act`, `srcUpdateTime`, `updateTime`, `infoTime`, `infoDate`) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", 
            #     (rowJson["catchTime"], rowJson["sno"], rowJson["sna"], rowJson["tot"], rowJson["sbi"], rowJson["sarea"], rowJson["mday"], rowJson["lat"], rowJson["lng"], rowJson["ar"], rowJson["sareaen"], rowJson["snaen"], rowJson["aren"], rowJson["bemp"], rowJson["act"], rowJson["srcUpdateTime"], rowJson["updateTime"], rowJson["infoTime"], rowJson["infoDate"]))
            if( rowJson["catchTime"] > MaxDbCatchTime) and (rowJson["sno"] in NtuSites):
                cur.execute(
                    "INSERT INTO `historyData` (`catchTime`, `sno`,  `tot`, `sbi`,  `mday`, `bemp`, `act`, `srcUpdateTime`, `updateTime`, `infoTime`, `infoDate`) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                    (rowJson["catchTime"], rowJson["sno"],  rowJson["tot"], rowJson["sbi"], rowJson["mday"], rowJson["bemp"], rowJson["act"], rowJson["srcUpdateTime"], rowJson["updateTime"], rowJson["infoTime"], rowJson["infoDate"]))
        conn.commit()
        # Close Connection
        conn.close()	
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

def getFileList(dataDir):    
    #os.listdir 取得檔案列表
    #os.walk 遞迴搜尋檔案
    allFiles = [] #[f for f in os.listdir(dataDir) if isfile(join(dataDir, f))]
    # 遞迴列出所有檔案的絕對路徑
    for root, dirs, files in walk(dataDir):
        for f in files:
            if f.endswith(".json"):
                fullpath = path.join(root, f) # f= 20-36.json
                sub = fullpath[len(dataDir)+1:len(fullpath)-5] # 2021-12-18\\20\\20-36
                subList = sub.split(DIRSep)
                if(len(subList) == 3):
                    datetimeStr = subList[0] + ' ' + subList[2].replace('-', ':') + ':00'
                    allFiles.append((fullpath , datetimeStr))
        
    return allFiles

# srcList = []
# rowJson = {
#             "sno": "500119090", 
#             "sna": "YouBike2.0_臺大新體育館東南側",
#             "tot": 40,
#             "sbi": 25,
#             "sarea": "臺大專區",
#             "mday": "2021-12-19 10:04:11",
#             "lat": 25.02112,
#             "lng": 121.53591,
#             "ar": "臺大體育館東側",
#             "sareaen": "NTU Dist",
#             "snaen": "YouBike2.0_NTU Sports Center(Southeast)",
#             "aren": "NTU Sports Center(East)",
#             "bemp": 15,
#             "act": "1",
#             "srcUpdateTime": "2021-12-19 10:14:14",
#             "updateTime": "2021-12-19 10:14:50",
#             "infoTime": "2021-12-19 10:04:11",
#             "infoDate": "2021-12-19"
#         }
# rowJson["catchTime"] = "2021-12-19 10:14:51"
# srcList.append(rowJson)
# rowJson02 = dict(rowJson)
# rowJson02["catchTime"] = "2021-12-19 10:14:52"
# srcList.append(rowJson02)
#insertDataToDb (srcList)
NtuSites = getNtuSites()
for (fullpath , datetimeStr) in getFileList(DATA_DIR):
    srcList =[]
    with open(fullpath, encoding='utf-8') as f:
        srcList = json.load(f)
        for row in srcList:
            row["catchTime"] = datetimeStr

    insertDataToDb (srcList)


		
