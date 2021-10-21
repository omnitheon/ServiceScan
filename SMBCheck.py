import random
from returnCurrentTime import currT
#Check Version 1.0

def run (SMBDS, USERDS, teamNumber, enableSMB2Support, timeoutValue, debug):
    SMBCheck_RESULTS = {}
    for current_smb_host in list(SMBDS.keys()):
        current_smb_check = random.choice(list(SMBDS[current_smb_host].keys()))
        IP = SMBDS[current_smb_host][current_smb_check]["checkTarget"].format(teamNumber)
        checkResult = {current_smb_check:{"hostname":current_smb_host,"outcome":"Fail","detail":"{} - {} - init Failure".format(currT(),current_smb_check)}}
        PORT = int(SMBDS[current_smb_host][current_smb_check]["targetPort"])
        randomScoredUsername = random.choice(list(USERDS.keys()))
        scoredPassword = USERDS[randomScoredUsername]
        targetHostname = SMBDS[current_smb_host][current_smb_check]["targetHostname"]
        targetShare = SMBDS[current_smb_host][current_smb_check]["targetShare"]
        targetPath = SMBDS[current_smb_host][current_smb_check]["targetPath"]
        targetFile = SMBDS[current_smb_host][current_smb_check]["targetFile"]
        try:
            smb_structs.SUPPORT_SMB2 = enableSMB2Support
            if PORT == 139:
                conn = SMBConnection(randomScoredUsername,scoredPassword,'scoringEngine',targetHostname, use_ntlm_v2 = True,is_direct_tcp=False)
            else:
                conn = SMBConnection(randomScoredUsername,scoredPassword,'scoringEngine',targetHostname, use_ntlm_v2 = True,is_direct_tcp=True)
            try:
                assert conn.connect(IP, PORT,timeout=timeoutValue)
                print('[{}] SMB connection successful with user:{} pass:{} on system:{}'.format(currT(),randomScoredUsername,scoredPassword,targetHostname)) if debug==True else ''
                items = conn.listPath(targetShare,targetPath)
                match = 0
                for each in items:
                    if targetFile.lower() == each.filename.lower():
                        match = 1
                if match == 1:
                    print('[{}] SMB file {} found on {}.'.format(currT(),targetPath,IP)) if debug==True else ''
                    checkResult[current_smb_check]["outcome"] = "Pass"
                    checkResult[current_smb_check]["detail"] = '{} - {} - SMB file {} found on {}.'.format(currT(),current_smb_check,targetPath,IP)
                else:
                    print('[{}] SMB file {} NOT found on {}.'.format(currT(),targetPath,IP)) if debug==True else ''
                    checkResult[current_smb_check]["detail"] = '{} - {} - SMB file {} NOT found on {}.'.format(currT(),current_smb_check,targetPath,IP)
            except Exception as e:
                print('[{}] Could not list files via SMB. IP:{} Reason: No shares available.'.format(currT(),IP)) if debug==True else ''
                checkResult[current_smb_check]["detail"] = '{} - {} - Could not list files via SMB. IP:{} Reason: Reason: No shares available.'.format(currT(),current_smb_check,IP)
        except Exception as e:
            print('[{}] Could not connect via SMB. IP:{}, User:{}, Pass:{} Reason: No response.'.format(currT(),IP,randomScoredUsername,scoredPassword)) if debug==True else ''
            checkResult[current_smb_check]["detail"] = '{} - {} - Could not connect via SMB. IP:{} User:{} Pass:{} Reason: No response.'.format(currT(),current_smb_check,IP,randomScoredUsername,scoredPassword)
        SMBCheck_RESULTS.update(checkResult)
    print("[{}] SMB done . . .".format(currT()))
    return SMBCheck_RESULTS