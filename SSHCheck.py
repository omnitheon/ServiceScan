import random
from returnCurrentTime import currT
import paramiko 
import time
#Check Version 1.0

def run (SSHDS, USERDS, teamNumber, timeoutVal, debug):
    SSHCheck_RESULTS = {}
    for current_ssh_host in list(SSHDS.keys()):
        current_ssh_check = random.choice(list(SSHDS[current_ssh_host].keys()))
        IP = SSHDS[current_ssh_host][current_ssh_check]["checkTarget"].format(teamNumber)
        checkResult = {current_ssh_check:{"hostname":current_ssh_host,"outcome":"Fail","detail":"{} - {} - init Failure".format(currT(),current_ssh_check)}}
        randomScoredUsername = random.choice(list(USERDS.keys()))
        scoredPassword = USERDS[randomScoredUsername]
        commandToRun = SSHDS[current_ssh_host][current_ssh_check]["command"]
        expectedOutputString = SSHDS[current_ssh_host][current_ssh_check]["expectedOutputString"]
        if expectedOutputString == '~randomScoredUsername~': #variable for config file to represent the scored username.
            expectedOutputString = randomScoredUsername
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(IP, username=randomScoredUsername, password=scoredPassword,timeout=timeoutVal,banner_timeout=200)
            print('[{}] SSH request to {} succeeded.'.format(currT(),IP)) if debug==True else ''
            try:
                stdin, stdout, stderr = client.exec_command(commandToRun +'\n',1)
                print('[{}] SSH command {} ran on {}.'.format(currT(),commandToRun,IP)) if debug==True else ''
                endtime = time.time() + timeoutVal
                while not stdout.channel.eof_received:
                    time.sleep(0.1)
                    if time.time() > endtime:
                        stdout.channel.close()
                        break
                tmp = stdout.readlines()
                print('[{}] SSH command {} read from {}. Output:{}.'.format(currT(),commandToRun,IP,tmp)) if debug==True else ''
                if expectedOutputString in str(tmp) or 'root' in str(tmp):
                    print('[{}] SSH connection {} good.'.format(currT(),IP)) if debug==True else ''
                    checkResult[current_ssh_check]["outcome"] = "Pass"
                    checkResult[current_ssh_check]["detail"] = '{} - {} - SSH connection {} good.'.format(currT(),current_ssh_check,IP)
                else:
                    print('[{}] SSH command output mismatch on {} . Command:{} Expected:{} Actual:{}'.format(currT(),IP,commandToRun,expectedOutputString,tmp)) if debug==True else ''
                    checkResult[current_ssh_check]["detail"] = '{} - {} - SSH command output mismatch on {} . Command:{} Expected:{} Actual:{}'.format(currT(),current_ssh_check,IP,commandToRun,expectedOutputString,tmp)
                client.close()
            except Exception as e:
                print('[{}] SSH command on {} failed. Reason {}'.format(currT(),IP,str(e))) if debug==True else ''
                checkResult[current_ssh_check]["detail"] = '{} - {} - SSH command on {} failed. Reason {}'.format(currT(),current_ssh_check,IP,str(e))
                client.close()
        except paramiko.AuthenticationException:
            print ("[{}] SSH authentication Exception on {}!".format(currT(),IP)) if debug==True else ''
            checkResult[current_ssh_check]["detail"] = "{} - {} - SSH authentication Exception on {}!".format(currT(),current_ssh_check,IP)
            client.close()
        except Exception as e:
            print('[{}] SSH request to {} failed. Reason {}'.format(currT(),IP,str(e))) if debug==True else ''
            checkResult[current_ssh_check]["detail"] = '{} - {} - SSH request to {} failed. Reason {}'.format(currT(),current_ssh_check,IP,str(e))
            client.close()
        SSHCheck_RESULTS.update(checkResult)
    print("[{}] SSH done . . .".format(currT()))
    return SSHCheck_RESULTS
