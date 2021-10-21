def XML_Cleaner(originalString):
    originalString = originalString.replace("<","").replace(">","").replace(";","").replace("&","amp").replace("{","").replace("}","")
    originalString = originalString.replace("[","").replace("]","").replace("'b","").replace("'","").replace("/"," ").replace("(","").replace(")","")
    return originalString