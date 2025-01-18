import requests
import time
import os
from json import loads
from xlsxwriter import Workbook
import logging
FORMAT = '%(asctime)s %(levelname)s: %(message)s'
# ERROR(40) / INFO(30) / WARNING(20) / DEBUG(10)
logging.basicConfig(level=logging.ERROR, filename='youbike.log', filemode='w', format=FORMAT)

workdir = os.path.dirname(__file__)
print('-- workdir = ' + workdir +'---')
os.chdir(workdir)
SOURCE = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
DATA_DIR = workdir + "/data/json/"
CONCERNED_PATH = workdir +"/data/concerned.txt"
EXCEL_DIR = workdir +"/data/excel/"

concerned = open(CONCERNED_PATH, "r", encoding="utf-8")
stations = {}
ordered_list = ['sna', 'sbi', 'bemp', 'tot', 'ar', 'act']
ordered_dict = {'sna': 'Name', 'sbi': 'Bike', 'bemp': 'Vacancy', 'tot': 'Total', 'ar': 'Location', 'act': 'Available'}

def read_stations():
    lines = concerned.readlines()
    for line in lines:
        a = line.split()
        stations.setdefault(a[0], a[1])

def edit_json(date:str, time:str):
    raw_data = open(DATA_DIR + date + '/' + time[:2] + '/' + time + '.json', "r", encoding="utf-8") 
    importance = []
    x  = loads(raw_data.read())
    for item in x:
        if item['sno'] in stations:
            item['sna'] = item['sna'][11:]
            importance.append(item)
    excel_path = EXCEL_DIR + date + '/' + time[:2]
    if not os.path.exists(excel_path):
        os.makedirs(excel_path)
    wb = Workbook(excel_path + '/' + time + '.xlsx')
    ws = wb.add_worksheet()
    
    for header in ordered_list:
        col=ordered_list.index(header) # we are keeping order.
        ws.write(0, col, ordered_dict[header]) # we have written first row which is the header of worksheet also.
    
    row = 1
    for stats in importance:
        col = 0
        for _key,_value in stats.items():
            try:
                col = ordered_list.index(_key)
                ws.write(row,col,_value)
                col += 1
            except:
                continue
        row += 1 #enter the next row
    wb.close()

def parse_file_name(filename:str):
    word = filename.split('-')
    if len(word[0]) == 1:
        word[0] = '0' + word[0]
    if len(word[1]) == 1:
        word[1] = '0' + word[1]
    new_name = word[0] + '-' + word[1]
    return new_name

def main():    
    startTime = time.localtime()
    startHour = startTime[3] #Hour
    read_stations()
    while True:
        date = time.localtime()
        if startHour != date[3]:
            break
        try:
            rq = requests.get(SOURCE)
            # yyyy-mm-dd
            date_str = str(date[0]) + "-" + str(date[1]) + "-" + str(date[2])
            # hh-mm
            filename = parse_file_name(str(date[3]) + "-" + str(date[4]))
            json_path = DATA_DIR + date_str + '/' + filename[:2] 
            if not os.path.exists(json_path):
                os.makedirs(json_path)
            f = open(json_path + "/" + filename + ".json" , "w", encoding="utf-8")
            f.write(rq.text)
            f.close()    
            edit_json(date_str, filename)
            print("Successfully download data: " + filename)
        except:
            logging.error("Catch an exception.", exc_info=True)
        if '59' == date[4]:
            break
        time.sleep(60)                

if __name__ == '__main__':
    main()
    