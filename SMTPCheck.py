import random
from returnCurrentTime import currT
from email.mime.text import MIMEText
import smtplib
from XML_Cleaner import XML_Cleaner
from booleanConverter import booleanConverter
#Check Version 2.0 - Last Updated in December 2020

def run (SMTP_CHECKS, USERDS, teamNumber, timeoutVal, retries, enableDebug):
    SMTPCheck_RESULTS = {}
    for hostname in list(SMTP_CHECKS.keys()):
        checkID = random.choice(list(SMTP_CHECKS[hostname].keys()))
        targetIP = SMTP_CHECKS[hostname][checkID]["checkTarget"].format(teamNumber)
        PORT = int(SMTP_CHECKS[hostname][checkID]["targetPort"])
        DOMAIN = SMTP_CHECKS[hostname][checkID]["targetDomain"]
        enableSMTPoverTLS = booleanConverter(SMTP_CHECKS[hostname][checkID]["enableTLS"])
        enableSMTPoverSSL = booleanConverter(SMTP_CHECKS[hostname][checkID]["enableSSL"])
        AuthenticatedSMTPEnabled = booleanConverter(SMTP_CHECKS[hostname][checkID]["enableAUTH"])

        initDetail = "{} - {} - init Failure".format(currT(),checkID)
        checkResult = {
            checkID:{"hostname":hostname, "outcome":"Fail", "detail":initDetail}
            }

        randomSenderUsername = random.choice(list(USERDS.keys()))
        receiverUsername = random.choice(list(USERDS.keys()))

        #Make sure sender isn't receiver
        while receiverUsername == randomSenderUsername:
            receiverUsername = random.choice(list(USERDS.keys())) 
        
        senderPassword = USERDS[randomSenderUsername]
        senderEmailAddress = "{}@{}".format(randomSenderUsername,DOMAIN)
        receiverEmailAddress = "{}@{}".format(receiverUsername,DOMAIN)
        print("[{}] SMTPCheck - Sending mail as {} to recepient {}".format(currT(),senderEmailAddress, receiverEmailAddress)) if enableDebug==True else ''
        
        #Email Subjects
        availableSubjets = ["Just received your email...", "I love you :)", "Purchasing Order", 
                            "Meeting from before", "Touchpoint", "1:1", "Need help", "Project Overview", 
                            "Malware", "DONT OPEN!!!!", "HELP!", "SOW", "Contract", "Wannacry?"]
        
        #Email Payload
        title = "SMTP Service Check {}".format(currT())
        tmp = '<h2><font color="red">{}</font></h2>\n'.format(title)
        message = MIMEText(tmp, 'html')
        message['From'] = '{}'.format(senderEmailAddress)
        message['To'] = '{}'.format(receiverEmailAddress)
        message['Subject'] = random.choice(availableSubjets)
        body = message.as_string()

        # Send email
        for i in range(retries):
            try:
                if enableSMTPoverSSL:
                    print('[{}] SMTPCheck - **SSL CHECK ENABLED** Attempting SSL handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    server = smtplib.SMTP_SSL(host=targetIP,port=PORT,timeout=timeoutVal)
                else:
                    server = smtplib.SMTP(host=targetIP,port=PORT,timeout=timeoutVal)
                server.ehlo()
                #server.set_debuglevel(2) if enableDebug == True else ''
                print('[{}] SMTPCheck - successfully built a connection with host {}...checking for service validity'.format(currT(), targetIP)) if enableDebug == True else ''
                if enableSMTPoverTLS:
                    print('[{}] SMTPCheck - **TLS CHECK ENABLED** Attempting TLS handshake with host {}...'.format(currT(), targetIP)) if enableDebug == True else ''
                    try:
                        server.starttls()
                        server.ehlo() #Send EHLO again after TLS
                    except Exception as e:
                        print('[{}] SMTPCheck Exception - received {} when starting TLS with host {}...'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                        checkResult[checkID]["detail"] = XML_Cleaner('{} {} - SMTPCheck Exception - received {} when starting TLS with host {}...'.format(currT(),checkID,str(e),targetIP))
                        server.quit()
                        continue
                
                if AuthenticatedSMTPEnabled: 
                    try: 
                        server.login(randomSenderUsername,senderPassword)
                    except Exception as e:
                        print('[{}] SMTPCheck Exception - received {} when authenticating as user {} on host {}...'.format(currT(),str(e),randomSenderUsername,targetIP)) if enableDebug==True else ''
                        checkResult[checkID]["detail"] = XML_Cleaner('{} {} - SMTPCheck Exception - received {} when authenticating with user {} on host {}...'.format(currT(),checkID,str(e),randomSenderUsername,targetIP))
                        server.quit()
                        continue
                try:
                    server.sendmail(senderEmailAddress,receiverEmailAddress,body)
                    print('[{}] SMTPCheck - succeeded for host {}'.format(currT(),targetIP)) if enableDebug==True else ''
                    checkResult[checkID]["detail"] = XML_Cleaner('{} {} - SMTPCheck - succeeded for host {}'.format(currT(),checkID,targetIP))
                    checkResult[checkID]["outcome"] = "Pass"
                    server.quit()
                    break
                except Exception as e:
                    print('[{}] SMTPCheck Exception - received {} when sending mail from {} to user {} for host {}...'.format(currT(),str(e),senderEmailAddress,receiverEmailAddress,targetIP)) if enableDebug==True else ''
                    checkResult[checkID]["detail"] = XML_Cleaner('{} {} - SMTPCheck Exception - received {} when sending mail from {} to user {} for host {}...'.format(currT(),checkID,str(e),senderEmailAddress,receiverEmailAddress,targetIP))
                    server.quit()
                    continue
            except Exception as e:
                print('[{}] SMTPCheck Exception - received {} when beginning handshake with host {}...'.format(currT(),str(e),targetIP)) if enableDebug==True else ''
                checkResult[checkID]["detail"] = XML_Cleaner('{} {} - SMTPCheck Exception - received {} when beginning handshake with host {}...'.format(currT(),checkID,str(e),targetIP))
                continue 

        SMTPCheck_RESULTS.update(checkResult)
    print("[{}] SMTP done . . .".format(currT()))
    return SMTPCheck_RESULTS
