import random
from returnCurrentTime import currT
import poplib
from XML_Cleaner import XML_Cleaner
from booleanConverter import booleanConverter
#Check Version 2.0 - Last Updated in December 2020

def run (POP3_CHECKS, USERDS, teamNumber, timeoutVal, retries, enableDebug):
    POP3Check_RESULTS = {}
    for hostname in list(POP3_CHECKS.keys()):
        checkID = random.choice(list(POP3_CHECKS[hostname].keys()))
        targetIP = POP3_CHECKS[hostname][checkID]["checkTarget"].format(teamNumber)
        PORT = POP3_CHECKS[hostname][checkID]["targetPort"]
        DOMAIN = POP3_CHECKS[hostname][checkID]["targetDomain"]
        OS = POP3_CHECKS[hostname][checkID]["targetOS"]
        enablePOP3overSSL = booleanConverter(POP3_CHECKS[hostname][checkID]["enableSSL"])
        enablePOP3overTLS = booleanConverter(POP3_CHECKS[hostname][checkID]["enableTLS"])

        initDetail = "{} - {} - init Failure".format(currT(),checkID)
        checkResult = {
            checkID:{"hostname":hostname,"outcome":"Fail","detail":initDetail}
        }
        if OS == "windows":
            randomSenderUsername = random.choice(list(USERDS.keys()))
            randomSenderPassword = USERDS[randomSenderUsername]
            randomSenderUsername = randomSenderUsername + "@{}".format(DOMAIN)
        else:
            randomSenderUsername = random.choice(list(USERDS.keys()))
            randomSenderPassword = USERDS[randomSenderUsername]
        for i in range(retries):
            try:
                if enablePOP3overSSL:
                    print('[{}] POP3Check - **SSL CHECK ENABLED** Attempting SSL handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    server = poplib.POP3_SSL(targetIP,port=PORT,timeout=timeoutVal)
                else:
                    server = poplib.POP3(targetIP,port=PORT,timeout=timeoutVal)
                server.set_debuglevel(1) if enableDebug == True else ''
                print('[{}] POP3Check - successfully built a connection with host {}...checking for service validity'.format(currT(), targetIP)) if enableDebug == True else ''
                if enablePOP3overTLS:
                    print('[{}] POP3Check - **TLS CHECK ENABLED** Attempting TLS handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    try:
                        server.stls()
                    except Exception as e:
                        print('[{}] POP3Check Exception - received {} when starting TLS with host {}...'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                        checkResult[checkID]["detail"] = XML_Cleaner('{} {} - POP3Check Exception - received {} when starting TLS with host {}...'.format(currT(),checkID,str(e),targetIP))
                        server.quit()
                        continue
                try:
                    # Login Info
                    server.user(randomSenderUsername)                  
                    server.pass_(randomSenderPassword)
                    print('[{}] POP3Check - successfully logged in as {} using password {} and selected INBOX for host {}'.format(currT(), randomSenderUsername, randomSenderPassword, targetIP)) if enableDebug == True else ''
                    try:
                        numberOfEmailMessages = len(server.list()[1])
                        if numberOfEmailMessages < 0:
                            print('[{}] POP3Check Exception - Not enough messages found via search operation for host {}'.format(currT(),targetIP)) if enableDebug==True else ''
                            checkResult[checkID]['detail'] = XML_Cleaner('{} {} - POP3Check Exception - Not enough messages found via search operation for host {}'.format(currT(),checkID,targetIP))
                            server.quit()
                            continue
                        else:
                            print("[{}] POP3Check - succeeded for host {}".format(currT(),targetIP))  if enableDebug==True else ''
                            checkResult[checkID]['detail'] = XML_Cleaner("{} {} - POP3Check - succeeded for host {}".format(currT(),checkID,targetIP))
                            checkResult[checkID]["outcome"] = "Pass"
                            server.quit()
                            break
                    except Exception as e:
                        print('[{}] POP3Check Exception - received {} when searching inbox for messages for host {}'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                        checkResult[checkID]['detail'] = XML_Cleaner('{} {} - POP3Check Exception - received {} when searching inbox for messages for host {}'.format(currT(),checkID,str(e),targetIP))
                        server.quit()
                        continue
                except Exception as e:  
                    print('[{}] POP3Check Exception - received {} when attempting authentication as {} and inbox selection for host {}...'.format(currT(),str(e),randomSenderUsername,targetIP)) if enableDebug==True else ''
                    checkResult[checkID]['detail'] = XML_Cleaner('{} {} - POP3Check Exception - received {} when attempting authentication as {} and inbox selection for host {}...'.format(currT(),checkID,str(e),randomSenderUsername,targetIP))
                    server.quit()
                    continue
            except Exception as e:
                print('[{}] POP3Check Exception - received {} when beginning handshake with host {}...'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                checkResult[checkID]['detail'] = XML_Cleaner('{} {} - POP3Check Exception - received {} when beginning handshake with host {}...'.format(currT(),checkID,str(e),targetIP))
                continue
        POP3Check_RESULTS.update(checkResult)
    print("[{}] POP3 done . . .".format(currT()))
    return POP3Check_RESULTS