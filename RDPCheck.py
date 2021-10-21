import random
from returnCurrentTime import currT
import os
#Check Version 1.0

def run (RDPDS, USERDS, teamNumber, platform, timeoutVal, debug):
    RDPCheck_RESULTS = {}
    for current_rdp_host in list(RDPDS.keys()):
        current_rdp_check = random.choice(list(RDPDS[current_rdp_host].keys()))
        IP = RDPDS[current_rdp_host][current_rdp_check]["checkTarget"].format(teamNumber)
        PORT = RDPDS[current_rdp_host][current_rdp_check]["targetPort"]
        DOMAIN = RDPDS[current_rdp_host][current_rdp_check]["targetDomain"]
        checkResult = {current_rdp_check:{"hostname":current_rdp_host,"outcome":"Fail","detail":"{} - {} - init Failure".format(currT(),current_rdp_check)}}
        randomScoredUsername = random.choice(list(USERDS.keys()))
        scoredPassword = USERDS[randomScoredUsername]
        if platform == "Linux":
            rdpCommand = 'xfreerdp /cert-ignore +auth-only /u:{}\\\\{} /p:{} /v:{}:{} /timeout:{}000 >/dev/null 2>&1'.format(DOMAIN,randomScoredUsername,scoredPassword,IP,PORT,timeoutVal)
            result = os.system(rdpCommand)
            rdpCommand = 'xfreerdp /cert-ignore +auth-only /u:{}\\\\{} /p:{} /v:{}:{} /timeout:{}000'.format(DOMAIN,randomScoredUsername,scoredPassword,IP,PORT,timeoutVal)
        else:
            #windows is currently broken
            rdpCommand = 'reg add "HKEY_CURRENT_USER\\Software\\Microsoft\\Terminal Server Client" /v "AuthenticationLevelOverride" /t "REG_DWORD" /d 0 /f'
            #print(rdpCommand) if debug==True else ''
            #os.system(rdpCommand)
            rdpCommand = 'cmdkey.exe /generic:{} /user:{}\\\\{} /pass:{}'.format(IP,DOMAIN,randomScoredUsername,scoredPassword)
            #print(rdpCommand) if debug==True else ''
            #os.system(rdpCommand)
            rdpCommand = 'mstsc.exe /v {}:{} /f /noConsentPrompt'.format(IP,PORT)
        try:
            #print(rdpCommand) if debug==True else ''
            #result = os.system(rdpCommand)
            if platform == "Windows":
                result = 1
            if result == 0:
                print('[{}] RDP request to {} succeeded.'.format(currT(),IP)) if debug==True else ''
                checkResult[current_rdp_check]["outcome"] = "Pass"
                checkResult[current_rdp_check]["detail"] = '{} - {} - RDP request to {} succeeded.'.format(currT(),current_rdp_check,IP)
            else:
                print('[{}] Could not connect via RDP on Host {}. Command: (({})), Exit status (({}))'.format(currT(),IP,rdpCommand,result)) if debug==True else ''
                checkResult[current_rdp_check]["detail"] = '{} - {} - Could not connect via RDP on Host {}. Command: (({})), Exit status (({}))'.format(currT(),current_rdp_check,IP,rdpCommand,result)
        except Exception as e:
            print('[{}] Could not create RDP object. Reason:{}'.format(currT(),str(e))) if debug==True else ''
            checkResult[current_rdp_check]["detail"] = '{} - {} - Could not create RDP object on Host {}. Reason:{}'.format(currT(),current_rdp_check,IP,str(e))
        RDPCheck_RESULTS.update(checkResult)
    print("[{}] RDP done . . .".format(currT()))
    return RDPCheck_RESULTS