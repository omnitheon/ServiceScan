import random
from returnCurrentTime import currT
import socket 
import imaplib
from XML_Cleaner import XML_Cleaner
from booleanConverter import booleanConverter
#Check Version 2.0 - Last Updated in December 2020

def run (IMAP4_CHECKS, USERDS, teamNumber, timeoutVal, retries, enableDebug):
    IMAPCheck_RESULTS = {}
    for hostname in list(IMAP4_CHECKS.keys()):
        checkID = random.choice(list(IMAP4_CHECKS[hostname].keys()))
        targetIP = IMAP4_CHECKS[hostname][checkID]["checkTarget"].format(teamNumber)
        PORT = int(IMAP4_CHECKS[hostname][checkID]["targetPort"])
        DOMAIN = IMAP4_CHECKS[hostname][checkID]["targetDomain"]
        OS = IMAP4_CHECKS[hostname][checkID]["targetOS"]
        enableIMAP4overSSL = booleanConverter(IMAP4_CHECKS[hostname][checkID]["enableSSL"])
        enableIMAP4overTLS = booleanConverter(IMAP4_CHECKS[hostname][checkID]["enableTLS"])
        socket.setdefaulttimeout(timeoutVal)

        initDetail = "{} - {} - init Failure".format(currT(),checkID)
        checkResult = {
            checkID:{"hostname":hostname,"outcome":"Fail","detail":initDetail}
            }

        if OS == "windows" or OS == "win" or OS == "w":
            randomSenderUsername = random.choice(list(USERDS.keys()))
            randomSenderPassword = USERDS[randomSenderUsername]
            randomSenderUsername = randomSenderUsername + "@{}".format(DOMAIN)
        else:
            randomSenderUsername = random.choice(list(USERDS.keys()))
            randomSenderPassword = USERDS[randomSenderUsername]

        
        for i in range(retries):
            try:
                if enableIMAP4overSSL:
                    print('[{}] IMAP4Check - **SSL CHECK ENABLED** Attempting SSL handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    server = imaplib.IMAP4_SSL(targetIP, PORT)
                else:
                    server = imaplib.IMAP4(targetIP, PORT)
                print('[{}] IMAP4Check - successfully built a connection with host {}...checking for service validity'.format(currT(), targetIP)) if enableDebug == True else ''
                server.debug = 3 if enableDebug == True else ''
                if enableIMAP4overTLS:
                    print('[{}] IMAP4Check - **TLS CHECK ENABLED** Attempting TLS handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    try:
                        server.starttls()
                    except Exception as e:
                        print('[{}] IMAP4Check Exception - received {} when starting TLS with host {}...'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                        checkResult[checkID]["detail"] = XML_Cleaner('{} {} - IMAP4Check Exception - received {} when starting TLS with host {}...'.format(currT(),checkID,str(e),targetIP))
                        server.close()
                        server.logout()
                        continue
                try:
                    server.login(randomSenderUsername,randomSenderPassword)
                    server.select() #Select INBOX
                    print('[{}] IMAP4Check - successfully logged in as {} using password {} and selected INBOX for host {}'.format(currT(), randomSenderUsername, randomSenderPassword, targetIP)) if enableDebug == True else ''
                    try:
                        typ, data = server.search(None, 'ALL')
                        if len(server.search(None, 'All')[1][0].split()) < 0:
                            print('[{}] IMAP4Check Exception - Not enough messages found via search operation for host {}'.format(currT(),targetIP)) if enableDebug==True else ''
                            checkResult[checkID]['detail'] = XML_Cleaner('{} {} - IMAP4Check Exception - Not enough messages found via search operation for host {}'.format(currT(),checkID,targetIP))
                            server.close()
                            server.logout()
                            continue
                        else:
                            print("[{}] IMAP4Check - succeeded for host {}".format(currT(),targetIP))  if enableDebug==True else ''
                            checkResult[checkID]['detail'] = XML_Cleaner("{} {} - IMAP4Check - succeeded for host {}".format(currT(),checkID,targetIP))
                            checkResult[checkID]["outcome"] = "Pass"
                            server.close()
                            server.logout()
                            break
                    except Exception as e:
                        print('[{}] IMAP4Check Exception - received {} when searching inbox for messages for host {}'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                        checkResult[checkID]['detail'] = XML_Cleaner('{} {} - IMAP4Check Exception - received {} when searching inbox for messages for host {}'.format(currT(),checkID,str(e),targetIP))
                        server.close()
                        server.logout()
                        continue
                except Exception as e:
                    print('[{}] IMAP4Check Exception - received {} when attempting authentication as {} and inbox selection for host {}...'.format(currT(),str(e),randomSenderUsername,targetIP)) if enableDebug==True else ''
                    checkResult[checkID]['detail'] = XML_Cleaner('{} {} - IMAP4Check Exception - received {} when attempting authentication and inbox selection for host {}...'.format(currT(),checkID,str(e),targetIP))
                    server.close()
                    server.logout()
                    continue
            except Exception as e:
                print('[{}] IMAP4Check Exception - received {} when beginning handshake with host {}...'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                checkResult[checkID]['detail'] = XML_Cleaner('{} {} - IMAP4Check Exception - received {} when beginning handshake with host {}...'.format(currT(),checkID,str(e),targetIP))
                continue

            
        IMAPCheck_RESULTS.update(checkResult)
    print("[{}] IMAP4 done . . .".format(currT()))
    return IMAPCheck_RESULTS