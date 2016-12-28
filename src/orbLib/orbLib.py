import httplib
import sys
from urllib import urlencode

AMBIENT_ORB_DEVID = 'RKF-5Y7-AH5'


def setColor(colorCode, anim=0, comment="No Comment", devID=AMBIENT_ORB_DEVID):
    connection = httplib.HTTPConnection("www.myambient.com:8080")
    getRequest="/java/my_devices/submitdata.jsp?"+ \
                       urlencode({'devID':devID,'anim':int(anim),'color':int(colorCode),'comment':comment})
    #print getRequest
    connection.request("GET",getRequest)
    responseOb = connection.getresponse()
    return responseOb.read()


if __name__ == "__main__":
    print setColor((int)(sys.argv[1]),"set+by+orbLib.py")