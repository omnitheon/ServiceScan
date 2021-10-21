import random
from returnCurrentTime import currT
import urllib3
import ssl
from XML_Cleaner import XML_Cleaner
#Check Version 2.0 - Last Updated in December 2020

#Disable SSL errors for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings()

#User Agents for Get Requests
'''
userAgents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Safari/605.1.15',
                  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
                  'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0'
                  ]
'''
userAgents = ['Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)']

def run (HTTPS_CHECKS, teamNumber, timeoutValue, retries, debug):
    HTTPSCheck_RESULTS = {}
    for hostname in list(HTTPS_CHECKS.keys()):

        checkID = random.choice(list(HTTPS_CHECKS[hostname].keys()))
        initDetail = "{} - {} - init Failure".format(currT(), checkID)
        checkResultDictionary = {
            checkID:{"hostname":hostname,"outcome":"Fail","detail":initDetail}
            }
        response = 0 #Initialize response since the get request might time out before a value is returned.
        targetIP = HTTPS_CHECKS[hostname][checkID]["checkTarget"].format(teamNumber)
        PORT = HTTPS_CHECKS[hostname][checkID]["port"]
        PATH = HTTPS_CHECKS[hostname][checkID]["path"]
        EXPECTED_STRING = HTTPS_CHECKS[hostname][checkID]["md5"]
        
        for i in range(retries):
            try:
                HTTPSrequest = 'https://{}:{}{}'.format(targetIP,PORT,PATH)
                response = urllib3.PoolManager(ssl_version=ssl.PROTOCOL_TLSv1_2,cert_reqs = ssl.CERT_NONE)
                response = response.request("GET",HTTPSrequest,timeout=urllib3.Timeout(connect=float(timeoutValue), read=float(timeoutValue)), retries=False,headers = {'User-agent': random.choice(userAgents)})
                if EXPECTED_STRING in str(response._body):
                    print('[{}] HTTPSCheck - success, received a reply from {} and the expected string was found in the HTTPS response...'.format(currT(),targetIP)) if debug==True else ''
                    checkResultDictionary[checkID]["outcome"] = "Pass"
                    checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - HTTPSCheck - success, received a reply from {} and the expected string was found in the HTTPS response...'.format(currT(),checkID,targetIP))
                    break
                else:
                    print('[{}] HTTPSCheck Exception -  received a reply from {} but did not see expected data in HTTPS response'.format(currT(),targetIP,PORT,PATH)) if debug==True else ''
                    checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - HTTPSCheck Exception - received a reply from {} but did not see expected data in HTTPS response'.format(currT(),checkID,targetIP))
                    continue
            except Exception as e:
                print('[{}] HTTPSCheck Exception - when requesting resources for host {}...the following exception was thrown...{}...'.format(currT(),targetIP,str(type(e)))) if debug==True else ''
                checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - HTTPSCheck Exception - when requesting resources for host {}...the following exception was thrown...{}...'.format(currT(),checkID,targetIP,type(e)))
                continue
        
        HTTPSCheck_RESULTS.update(checkResultDictionary)
    print("[{}] HTTPS done . . .".format(currT()))
    return HTTPSCheck_RESULTS
