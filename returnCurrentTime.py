import datetime
def currT():
    return "{}".format(str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))