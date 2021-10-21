import random
import ftplib
import datetime
import os 
import time
from returnCurrentTime import currT
from XML_Cleaner import XML_Cleaner
from booleanConverter import booleanConverter
#Check Version 2.0 - Last Updated in December 2020

def run(FTP_CHECKS, USERDS, teamNumber, timeoutVal, retries, enableDebug):
    FTPCheck_RESULTS = {}
    for hostname in list(FTP_CHECKS.keys()):

        # PREP CHECK VALUES
        checkID = random.choice(list(FTP_CHECKS[hostname].keys()))
        targetIP = FTP_CHECKS[hostname][checkID]["checkTarget"].format(teamNumber)
        PORT = int(FTP_CHECKS[hostname][checkID]["targetPort"]) #Probably not needed
        targetFilePath = FTP_CHECKS[hostname][checkID]["targetFilePath"]
        fileContents = FTP_CHECKS[hostname][checkID]["fileContents"]
        fileContents = FTP_CHECKS[hostname][checkID]["fileContents"]
        enableFTPS = booleanConverter(FTP_CHECKS[hostname][checkID]["enableFTPS"])
        enableAUTH = booleanConverter(FTP_CHECKS[hostname][checkID]["enableAUTH"])

        initDetail = "{} - {} - init Failure".format(currT(),checkID)
        checkResultDictionary = {
            checkID:{"hostname":hostname, "outcome":"Fail", "detail":initDetail}
            }

        if enableAUTH:
            randomScoredUsername = random.choice(list(USERDS.keys()))
            randomScoredPassword = USERDS[randomScoredUsername]
        else:
            randomScoredUsername = "anonymous"
            randomScoredPassword = "anonymous"

        tempPayloadFile = "ftpTemp.txt"
        tempPayloadFileHandle = open(tempPayloadFile, 'w')
        tempPayloadFileHandle.write(fileContents)
        tempPayloadFileHandle.close()
        uploadedBytes = open(tempPayloadFile, 'rb')
        # Connect and Upload file to server
        for i in range(retries):
            try:
                if enableFTPS:
                    print('[{}] FTPCheck - **SSL/TLS CHECK ENABLED** Attempting SSL/TLS handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    session = ftplib.FTP_TLS(host=targetIP, timeout=timeoutVal)
                else:
                    session = ftplib.FTP(host=targetIP, timeout=timeoutVal)
                session.set_debuglevel(1) if enableDebug==True else ''
                print(session.getwelcome())
                time.sleep(1)
                session.login(user=randomScoredUsername, passwd=randomScoredPassword)
                time.sleep(1)
                if enableFTPS:
                    print('[{}] FTPCheck - **SSL/TLS CHECK ENABLED** Setting up secure data connection... for host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    try:
                        session.prot_p()
                        session.nlst()
                    except Exception as e:
                        print('[{}] FTPCheck Exception - {} for host {} while attempting to set up a secure data connection....'.format(currT(),str(e),targetIP)) if enableDebug == True else ''
                        checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - FTPCheck Exception - {} for host {} while attempting to set up a secure data connection....'.format(currT(),checkID,str(e),targetIP))
                        FTPCheck_RESULTS.update(checkResultDictionary)
                        continue
                print('[{}] FTPCheck - successfully connected to host {}...checking validity of the service...'.format(currT(),targetIP)) if enableDebug == True else ''
                
                try:
                    upload_response_text = session.storlines('STOR {}'.format(targetFilePath), uploadedBytes) 
                except Exception as e:
                    print('[{}] FTPCheck Exception - {} for host {} while attempting to upload via STOR lines...'.format(currT(),str(e),targetIP)) if enableDebug == True else ''
                    checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - FTPCheck Exception - {} for host {} while attempting to upload via STOR lines...'.format(currT(),checkID,str(e),targetIP))
                    FTPCheck_RESULTS.update(checkResultDictionary)
                    continue
                # Success code is 226
                
                if not upload_response_text.startswith('226'):
                    print("[{}] FTPCheck Exception - expected upload_response_code was 226...received {}...".format(currT(),upload_response_text)) if enableDebug==True else ''
                    checkResultDictionary[checkID]["detail"] = XML_Cleaner("{} {} - FTPCheck Exception - expected upload_response_code was 226...received {}...".format(currT(),checkID,upload_response_text))
                    continue
                else:
                    downloaded_lines = []
                    download_response_text = session.retrlines('RETR {0}'.format(targetFilePath), downloaded_lines.append)
                    session.close()
                    # Success code is 226
                    if not download_response_text.startswith('226'):
                        print("[{}] FTPCheck Exception - expected download_response_code was 226...received {}...".format(currT(),upload_response_text)) if enableDebug==True else ''
                        checkResultDictionary[checkID]["detail"] = XML_Cleaner("{} {} - FTPCheck Exception - expected download_response_code was 226...received {}...".format(currT(),checkID,upload_response_text))
                        continue
                    else:
                        downloaded_data = ''.join(downloaded_lines)
                        if downloaded_data != fileContents:
                            print("[{}] FTPCheck Exception - uploaded contents do not match downloaded contents..expected payload {}...actual payload {}...".format(currT(),fileContents,downloaded_data)) if enableDebug==True else ''
                            checkResultDictionary[checkID]["detail"] = XML_Cleaner("{} {} - FTPCheck Exception - uploaded contents do not match downloaded contents..expected payload {}...actual payload {}...".format(currT(),checkID,fileContents,downloaded_data))
                            continue
                        else:
                            print("[{}] FTPCheck -  request to {} succeeded.".format(currT(),targetIP)) if enableDebug==True else ''
                            checkResultDictionary[checkID]["detail"] = XML_Cleaner("{} {} - FTPCheck -  request to {} succeeded.".format(currT(),checkID,targetIP))
                            checkResultDictionary[checkID]["outcome"] = "Pass"
                            break
            except Exception as e:
                print('[{}] FTPCheck Exception - {} for host {}'.format(currT(),str(e),targetIP)) if enableDebug == True else ''
                checkResultDictionary[checkID]["detail"]= XML_Cleaner('{} {} - FTPCheck Exception - {} for host {}...'.format(currT(),checkID,str(e),targetIP))
        uploadedBytes.close()
        FTPCheck_RESULTS.update(checkResultDictionary)
    try:
        os.remove(tempPayloadFile)
    except:
        a=1
    print("[{}] FTP done . . .".format(currT()))
    return FTPCheck_RESULTS