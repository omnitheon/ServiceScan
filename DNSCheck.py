import random
import dns.resolver  # dnspython
import datetime
from returnCurrentTime import currT
from XML_Cleaner import XML_Cleaner
#Check Version 2.0 - Last Updated in December 2020


def returnResolver(timeout):
    myResolver = dns.resolver.Resolver()
    myResolver.timeout = timeout
    myResolver.lifetime = timeout
    return myResolver

def run(DNS_CHECKS, teamNumber, timeout, retries, enableDebug):
    DNSCheck_RESULTS = {}
    myResolver = returnResolver(timeout)
    for hostname in list(DNS_CHECKS.keys()):
        checkID = random.choice(list(DNS_CHECKS[hostname].keys()))
        initDetail = "{} - {} - init Failure".format(currT(), checkID)
        checkResultDictionary = {
            checkID: {"hostname": hostname, "outcome": "Fail", "detail": initDetail}
            }
        targetIP = DNS_CHECKS[hostname][checkID]["checkTarget"].format(teamNumber)
        expectedIP = DNS_CHECKS[hostname][checkID]["expectedIP"].format(teamNumber)
        REQUEST = DNS_CHECKS[hostname][checkID]["record"]
        RECORD_TYPE = DNS_CHECKS[hostname][checkID]["recordType"]
        myResolver.nameservers = [targetIP]

        # MAKE DNS REQUEST
        for i in range(retries):
            try:
                # GET DNS RESPONSE
                result = myResolver.query(REQUEST, RECORD_TYPE)
                print('[{}] DNSCheck - received DNS Reply from {}...checking for validity'.format(currT(), targetIP)) if enableDebug == True else ''
                # CHECK DNS RESPONSE FOR MATCH
                result = result[0]
                if expectedIP in str(result):
                    print('[{}] DNSCheck - result good for host {}...requested record {} returned {}'.format(
                        currT(), targetIP, REQUEST, result)) if enableDebug == True else ''
                    checkResultDictionary[checkID]["outcome"] = "Pass"
                    checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - DNSCheck - result good for host {}...requested record {} returned {}'.format(currT(), checkID, targetIP, REQUEST, result))
                    break
                else:
                    print('[{}] DNSCheck - received unexpected IP reply value for host {}...requested record {}...expected {}...actual {}'.format(currT(), targetIP, REQUEST, expectedIP, result)) if enableDebug == True else ''
                    checkResultDictionary[checkID]["detail"] = XML_Cleaner('{} {} - DNSCheck - received unexpected IP reply value for host {}...requested record {}...expected {}...actual {}'.format(currT(), checkID, targetIP, REQUEST, expectedIP, result))
            except Exception as e:
                print('[{}] {}'.format(currT(),str(e))) if enableDebug == True else ''
                checkResultDictionary[checkID]["detail"]= XML_Cleaner('{} {} - DNSCheck Exception - {}'.format(currT(), checkID, str(e)))
        DNSCheck_RESULTS.update(checkResultDictionary)
    print("[{}] DNSCheck done . . .".format(currT()))
    return DNSCheck_RESULTS
