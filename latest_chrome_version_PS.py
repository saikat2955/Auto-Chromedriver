import zipfile
import os
import requests
import wget
import traceback
import chromedriver_autoinstaller
from bs4 import BeautifulSoup as bs
import datetime
from typing import Dict,Tuple
import warnings
warnings.filterwarnings("ignore")

# ~~~~~~~~~~~~ EMERGENCY PROCESS KILL INFO ~~~~~~~~~~~~
print('PYTHON PID:', os.getpid(), flush=True)
kill_cmd = '''taskkill /F /PID ''' + str(os.getpid())
print('EMERGENCY KILL COMMAND:', kill_cmd, flush=True)

chrome_driver_dir_path ="""__{chrome_driver_dir_path}__"""
chrome_driver_dir_path = r"D:\Project\auto_chromedriver\output"
pivot_year = "2018-01-01"


def get_chrome_and_driver_map() -> Dict[int,str]:
    """ returns chrome_version : latest_chrome_driversion mapping """
    
    try:
        url = """https://chromedriver.storage.googleapis.com"""
        soup = bs(requests.get(url).text,'html.parser')
        contents = soup.findAll('contents')
        chrome_memory = {}
        temp_memory = []
        for content in contents:
            zip_name = content.find('key').text
            if zip_name.endswith("chromedriver_win32.zip"):
                zip_name = zip_name.split("/")[0]
                modification_date = datetime.datetime.strptime(content.find('lastmodified').text,"%Y-%m-%dT%H:%M:%S.%fZ")
                temp_memory.append((modification_date,zip_name))

        temp_memory.sort(key=lambda x : x[0],reverse=True)   
        temp_memory = [pair for pair in temp_memory if pair[0] > datetime.datetime.strptime(pivot_year,"%Y-%m-%d")]

        for pair in temp_memory:
            prefix = int(pair[-1].split('.')[0])
            if prefix not in chrome_memory:
                chrome_memory[prefix] = pair[-1]
        return chrome_memory,True
    except Exception as e:
        traceback.print_exc(e)
        return None,False
    

def get_chrome_and_chromedriver_version(chrome_memory: Dict[int,str]) -> Tuple[int,int,bool]:
    """ returns chrome version chrome driver version and success status """
    
    try:
        chrome_version,chromedriver_version = "",""
        chrome_version = chromedriver_autoinstaller.get_chrome_version()
        chromedriver_version = chrome_memory[int(chrome_version.split(".")[0])]
        return int(chrome_version.split(".")[0]),int(chromedriver_version.split(".")[0]),True
    except Exception as e:
        traceback.print_exc(e)
        return None,None,False
        
    
def get_chrome_driver(chrome_driver_dir_path: str,version: int= 0) -> bool:
    """ downloads chrome driver of specific version """
    
    try:
        download_path = os.path.join(chrome_driver_dir_path,'chromedriver.zip')
        if version == 0:
            url = 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
            response = requests.get(url)
            version = response.text
        download_url = "https://chromedriver.storage.googleapis.com/" + version +"/chromedriver_win32.zip"
        latest_driver_zip = wget.download(download_url,download_path)
        with zipfile.ZipFile(latest_driver_zip, 'r') as zip_ref:
            zip_ref.extractall()
        os.remove(latest_driver_zip)
        
        return True
    except Exception as e:
        traceback.print_exc(e)
        return False


if __name__=="__main__":
    chrome_memory,ok = get_chrome_and_driver_map()
    if ok:
        chrome_version,chromedriver_version,ok = get_chrome_and_chromedriver_version(chrome_memory)
        if ok:
            if chrome_version > chromedriver_version:
                ok = get_chrome_driver(chrome_driver_dir_path) 
                if ok:
                    print("Chromedriver is updated to latest version",flush=True)
                else:
                    print("Failed to update Latest Chrome Driver",flush=True)
            elif chrome_version < chromedriver_version:
                ok = get_chrome_driver(chrome_driver_dir_path,chrome_memory[chrome_version])
                if ok:
                    print("Chromedriver is updated to required version",flush=True)
                else:
                    print("Failed to update Chrome Driver",flush=True)
            else:
                print("Requirement already satisfied",flush=True)
        else:
            print("Failed to check and update driver",flush=True)
    else:
        print("internet error",flush=True)
        