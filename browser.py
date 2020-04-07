from selenium import webdriver 
import selenium
import subprocess 
import  threading
import os, sys
import time
import socket
import struct
from tkinter import *
from PIL import ImageTk, Image
import functools
from tkinter import messagebox

#   ------------------------------------
#       Configurations for GUI
#   ------------------------------------
window = Tk()
window.geometry("500x100")
window.resizable(False, False)
window.title("MY CD VPN")

lbl_usrname = Label(window, text="Username")
lbl_usrname.grid(column=1, row=0)

txt_usrname = Entry(window,width=25)
txt_usrname.grid(column=2, row=0)


lbl_passwd = Label(window, text="Password")
lbl_passwd.grid(column=1, row=1)

txt_passwd = Entry(window,width=25)
txt_passwd.config(show='*')
txt_passwd.grid(column=2, row=1)

# -----------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------


#   ------------------------------------
#       Global Variables
#   ------------------------------------
global_ssh_proc = None
#   WebDriver PATH
currentScriptPATH = os.path.dirname(os.path.abspath(__file__))

exePath_chrome81      = currentScriptPATH + "\\chromedriver_win32\\chromedriver81.exe"
exePath_chrome80      = currentScriptPATH + "\\chromedriver_win32\\chromedriver80.exe"
exePath_chrome79      = currentScriptPATH + "\\chromedriver_win32\\chromedriver79.exe"

exePath_firefox_x64 = currentScriptPATH + "\\firefoxdriver_win64\\geckodriver.exe"
exePath_firefox_x32 = currentScriptPATH + "\\firefoxdriver_win32\\geckodriver.exe"

exePath_opera_x64   = currentScriptPATH + "\\operadriver_win64\\operadriver.exe"
exePath_opera_x32   = currentScriptPATH + "\\operadriver_win32\\operadriver.exe"

exePath_edge    = ''
#   Browsers Default (Installation) Executables PATH
firefox_PATH_x64 = r"c:\Program Files\Mozilla Firefox\firefox.exe"
firefox_PATH_x32 = r"c:\Program Files (x86)\Mozilla Firefox\firefox.exe"

chrome_PATH_x32 = "c:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
chrome_PATH_version = "c:\Program Files (x86)\Google\Chrome\Application\80"

opera_PATH_x64 = "c:\Program Files\Opera\launcher.exe"
opera_PATH_x32 = "c:\Program Files (x86)\Opera\launcher.exe"

opera_PATH_appData = r'c:\Users' + '\\' + str(os.getlogin()) + r'\AppData\Local\Programs\Opera\launcher.exe' # TODO
#   ------------------------------------
#       Configurations for SSH
#   ------------------------------------
def runSSH(usr_srv, passwd):
    print("\tStarting SSH Connection")
    # -l teo server-001.clusterdesktop.com -p 1484 -o stricthostkeychecking=no -o userknownhostsfile=NUL -o loglevel=ERROR
    # OS SYSTEM
    #ssh_cmd = 'start plink.exe -batch -ssh teo@server-001.clusterdesktop.com -P 1484 -D 19999 -pw "(00Basketball00)"'
    #os.system(ssh_cmd)

    ssh_exe_PATH = currentScriptPATH + "\\requirements\\plink.exe"
    sys.path.append(ssh_exe_PATH)

    ssh_cmd = ['start', ssh_exe_PATH, '-batch','-ssh', usr_srv, '-P', '22','-D','19999', '-pw', passwd, '-C', '-N']
    ssh_proc = subprocess.Popen(ssh_cmd, stdin=subprocess.PIPE ,shell=True)
    return 1

def checkSSH():
    print("\tChecking SSH")
    sen = struct.pack('BBB', 0x05, 0x01, 0x00)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', 19999))
    s.sendall(sen)
    data = s.recv(2)
    version, auth = struct.unpack('BB', data)
    return (version, auth)

def checkSSH_proc(usrnsm, passwd):
    print("\tStarting CheckSSH process")
    while True:
        try:
            time.sleep(60)
            checkSSH()
        except ConnectionRefusedError as error:
            print(error)
            try:
                global_ssh_proc.kill()
                global_ssh_proc = runSSH(usrnsm, passwd)
            except Exception:
                global_ssh_proc = runSSH(usrnsm, passwd)



#   ------------------------------------
#       Configurations for Browsers
#   ------------------------------------
firefox_dic = {"binary_location":"", "webdriver_location":""}
chrome_dic = {"binary_location":"", "webdriver_location":""}
opera_dic = {"binary_location":"", "webdriver_location":""}

def prepareFirefox(exec_path):
    # Profile
    #binary = webdriver.firefox.firefox_binary = binary_location
    profile = webdriver.FirefoxProfile()
    profile.set_preference("network.proxy.socks", u'127.0.0.1')
    profile.set_preference("network.proxy.socks_port",19999)
    profile.set_preference("network.proxy.socks_remote_dns", 1)
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.socks_remote_dns", True)

    # Browser
    browser = webdriver.Firefox(profile, executable_path=exec_path)
    return browser

def prepareChrome(exec_path):
    # Profile
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=socks5://localhost:19999')
    browser = webdriver.Chrome(options=options, executable_path=exec_path)
    return browser

def prepareOpera(exec_path):
    # Profile
    options = webdriver.ChromeOptions()
    options.add_argument('--proxy-server=socks5://localhost:19999')
    # Browser
    browser = webdriver.Opera(options=options, executable_path=exec_path)
    return browser

# File Exists
def fileExists(pathToFile):
    exists = False
    try:
        f = open(pathToFile)
        exists = True
        f.close()
    except FileNotFoundError:
        #print("File not found")
        exists = False
    finally:
        return exists

# Check Browsers exist return PATH to browser
def checkFirefox_existsPATH():
    x64 = fileExists(firefox_PATH_x64)
    x32 = fileExists(firefox_PATH_x32)
    if(x64):
        print("Firefox Exists at: \t",firefox_PATH_x64 )
        firefox_dic["binary_location"] = firefox_PATH_x64
        firefox_dic["webdriver_location"] = exePath_firefox_x64
        return True
    elif(x32):
        print("Firefox Exists at: \t",firefox_PATH_x32 )
        firefox_dic["binary_location"] = firefox_PATH_x32
        firefox_dic["webdriver_location"] = exePath_firefox_x32
        return True
    else:
        print("its false")
        return False

def checkChrome_existsPATH():
    x32 = fileExists(chrome_PATH_x32)
    if(x32):
        print("Chrome Exists at: \t",chrome_PATH_x32 )
        chrome_dic["binary_location"] = chrome_PATH_x32
        chromeVersion = os.listdir(chrome_PATH_x32[:-10])[0]
        if("81." in chromeVersion):
            chrome_dic["webdriver_location"] = exePath_chrome81
        elif("80." in chromeVersion):
            chrome_dic["webdriver_location"] = exePath_chrome80
        elif("79." in chromeVersion):
            chrome_dic["webdriver_location"] = exePath_chrome79


        return True
    else:
        return False

def checkOpera_existsPATH():
    x64 = fileExists(opera_PATH_x64)
    x32 = fileExists(opera_PATH_x32)
    appData = fileExists(opera_PATH_appData)
    if(x64):
        print("Opera Exists at: \t",opera_PATH_x64 )
        opera_dic["binary_location"] = opera_PATH_x64
        opera_dic["webdriver_location"] = exePath_opera_x64
        return opera_PATH_x64
    elif(x32):
        print("Opera Exists at: \t",opera_PATH_x32 )
        opera_dic["binary_location"] = opera_PATH_x32
        opera_dic["webdriver_location"] = exePath_opera_x32
        return opera_PATH_x32
    elif(appData):
        print("Opera Exists at: \t",opera_PATH_appData )
        opera_dic["binary_location"] = opera_PATH_appData
        opera_dic["webdriver_location"] = exePath_opera_x32
        return opera_PATH_appData


def runFirefox():
    usrnsm = txt_usrname.get()
    passwd = txt_passwd.get()
    try:
        checkSSH()
    except ConnectionRefusedError as error:
        print("Got Exception ", error)
        global_ssh_proc = runSSH(usrnsm, passwd)
        threading._start_new_thread(checkSSH_proc,(usrnsm, passwd))


    if(checkFirefox_existsPATH()):
        sys.path.append(print(firefox_dic["binary_location"]))
        sys.path.append(print(firefox_dic["webdriver_location"]))
        # does NOT need print ! ! ! 
        return prepareFirefox(firefox_dic["webdriver_location"])

def runChrome():
    usrnsm = txt_usrname.get()
    passwd = txt_passwd.get()
    try:
        checkSSH()
    except ConnectionRefusedError as error:
        print("Got Exception ", error)
        global_ssh_proc = runSSH(usrnsm, passwd)
        threading._start_new_thread(checkSSH_proc,(usrnsm, passwd))

    if(checkChrome_existsPATH()):
        sys.path.append(print(chrome_dic["binary_location"]))
        sys.path.append(print(chrome_dic["webdriver_location"]))

        # does NOT need print ! ! ! 
        prepareChrome(chrome_dic["webdriver_location"]) 

def runOpera():
    usrnsm = txt_usrname.get()
    passwd = txt_passwd.get()
    try:
        checkSSH()
    except ConnectionRefusedError as error:
        print("Got Exception ", error)
        global_ssh_proc = runSSH(usrnsm, passwd)
        threading._start_new_thread(checkSSH_proc,(usrnsm, passwd))

    if(checkOpera_existsPATH()):
        sys.path.append(print(opera_dic["binary_location"]))
        sys.path.append(print(opera_dic["webdriver_location"]))
        # does NOT need print ! ! ! 
        prepareOpera(opera_dic["webdriver_location"])

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        try:
            #global_ssh_proc.stdin.write()
            global_ssh_proc.kill()
        except:
            print("could not kill the SSH process")
        finally:
            window.destroy()


# -----------------------------------------------------------------------------------------------------------------------------------------------------
#                   ! ! ! 
# Should be after declaration of Functions ! ! ! 
#                   ! ! ! 
# -----------------------------------------------------------------------------------------------------------------------------------------------------
img = Image.open(currentScriptPATH + "\\icons\\opera_color.png") #.convert('L')
img = img.resize((50, 50),  Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
panel = Button(window, image = img, command=runOpera)
if(checkOpera_existsPATH()):
    panel['state']='active'
else:
    panel['state']='disabled'
panel.grid(column=0, row=2)

img2 = Image.open(currentScriptPATH + "\\icons\\chrome_color.png")
img2 = img2.resize((50, 50),  Image.ANTIALIAS)
img2 = ImageTk.PhotoImage(img2)
panel = Button(window, image = img2, command=runChrome)
if(checkChrome_existsPATH()):
    panel['state']='active'
else:
    panel['state']='disabled'
panel.grid(column=1, row=2)

img3 = Image.open(currentScriptPATH + "\\icons\\firefox_color.png")
img3 = img3.resize((50, 50),  Image.ANTIALIAS)
img3 = ImageTk.PhotoImage(img3)
panel = Button(window, image = img3, command=runFirefox)
if(checkFirefox_existsPATH()):
    panel['state']='active'
else:
    panel['state']='disabled'
panel.grid(column=2, row=2)

img4 = Image.open(currentScriptPATH + "\\icons\\ie_color.png")
img4 = img4.resize((50, 50),  Image.ANTIALIAS)
img4 = ImageTk.PhotoImage(img4)
panel = Button(window, image = img4)
panel['state']='disabled'
panel.grid(column=3, row=2)

window.rowconfigure(2, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(0, weight=1)
window.columnconfigure(0,weight=1)
window.columnconfigure(1,weight=1)
window.columnconfigure(2,weight=1)
window.columnconfigure(3,weight=1)

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()




