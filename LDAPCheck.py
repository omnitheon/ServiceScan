import random
import ldap3
from returnCurrentTime import currT
#Check Version 1.0


def run (LDAPDS, USERDS, teamNumber, timeoutVal, debug):
    LDAPCheck_RESULTS = {}
    for current_ldap_host in list(LDAPDS.keys()):
        current_ldap_check = random.choice(list(LDAPDS[current_ldap_host].keys()))
        IP = LDAPDS[current_ldap_host][current_ldap_check]["checkTarget"].format(teamNumber)
        PORT = int(LDAPDS[current_ldap_host][current_ldap_check]["targetPort"])
        DOMAIN = LDAPDS[current_ldap_host][current_ldap_check]["targetDomain"]
        search_base = LDAPDS[current_ldap_host][current_ldap_check]["targetSearchBase"].replace("~",",")
        enableTLS = LDAPDS[current_ldap_host][current_ldap_check]["enableTLS"]
        attribute = ["sAMAccountName"]
        checkResult = {current_ldap_check:{"hostname":current_ldap_host,"outcome":"Fail","detail":"{} - {} - init Failure".format(currT(),current_ldap_check)}}
        randomScoredUsername = random.choice(list(USERDS.keys()))
        scoredPassword = USERDS[randomScoredUsername]
        randomUser = random.choice(list(USERDS.keys()))
        while randomUser == randomScoredUsername:
            randomUser = random.choice(list(USERDS.keys()))
        search_filter = "(&(objectClass=user)(sAMAccountName={}))".format(randomUser)

        for i in range(2):
            if enableTLS == "True":
                try:
                    conn = ldap3.Connection(ldap3.Server("ldaps://{}".format(IP), port=PORT, use_ssl=True, connect_timeout=timeoutVal), auto_bind=True, user="{}\\{}".format(DOMAIN,randomScoredUsername), password=scoredPassword, read_only=True)
                except Exception as e:
                    print('[{}] Could not connect via LDAPS. Host:{} Reason:{}'.format(currT(),IP,str(e))) if debug==True else ''
                    checkResult[current_ldap_check]['detail'] = '{} - {} - Could not connect via LDAPS. Host:{} Reason:{}'.format(currT(),current_ldap_check,IP,str(e))
                    continue
            else:
                try:
                    conn = ldap3.Connection(ldap3.Server("ldap://{}".format(IP), port=PORT, use_ssl=False, connect_timeout=timeoutVal), auto_bind=True, user="{}\\{}".format(DOMAIN,randomScoredUsername), password=scoredPassword, read_only=True)
                except Exception as e:
                    print('[{}] Could not connect via LDAP. Host:{} Reason:{}'.format(currT(),IP,str(e))) if debug==True else ''
                    checkResult[current_ldap_check]['detail'] = '{} - {} - Could not connect via LDAP. Host:{} Reason:{}'.format(currT(),current_ldap_check,IP,str(e))
                    continue
            break
        try:
            conn.search(search_base, search_filter, attributes=attribute)
            output = str(conn.entries)
            numResults = len(conn.entries)
            if numResults > 0:
                print("[{}] LDAP check successful for Host: {}".format(currT(),IP))  if debug==True else ''
                checkResult[current_ldap_check]["outcome"] = "Pass"
                checkResult[current_ldap_check]["detail"] = "{} - {} - LDAP check successful for Host: {}".format(currT(),current_ldap_check,IP)
            else:
                print("[{}] LDAP check failed to return any results for Host: {}".format(currT(),IP))  if debug==True else ''
                checkResult[current_ldap_check]["detail"] = "{} - {} - LDAP check failed to return any results for Host: {}".format(currT(),current_ldap_check,IP)
        except Exception as e:
            print("[{}] LDAP check failed, could not perform search on open connection for Host: {}".format(currT(),IP))  if debug==True else ''
            checkResult[current_ldap_check]["detail"] = "{} - {} - LDAP check failed, could not perform search on open connection for Host: {}".format(currT(),current_ldap_check,IP)
        LDAPCheck_RESULTS.update(checkResult)
    print("[{}] LDAP done . . .".format(currT()))
    return LDAPCheck_RESULTS