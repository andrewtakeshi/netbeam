from flask import Flask
from flask_bootstrap import Bootstrap
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretsecretkey"
Bootstrap(app)


@app.template_filter('ctime')
def unixtolocaltime(s):
    return time.asctime(time.localtime(int(s) / 1000))


@app.template_filter('gtime')
def unixtolocaltimereduced(s):
    return time.strftime("%H:%M:%S", time.localtime(int(s) / 1000))


@app.template_filter('getTrafficTime')
def getTrafficTime(output):
    retVal = set()

    for item in output.items():
        for k, v in item[1].items():
            if k == 'points':
                for point in v:
                    retVal.add(unixtolocaltimereduced(point[0]))

    return sorted(retVal)


@app.template_filter('getOtherTime')
def getOtherTime(output):
    retVal = set()

    for item in output.items():
        if item[0] == 'Discards':
            for k, v in item[1].items():
                if k == 'points':
                    for point in v:
                        retVal.add(unixtolocaltimereduced(point[0]))

    return sorted(retVal)


def getInGeneric(output, typestr):
    retVal = "["
    for item in output.items():
        if item[0] == typestr:
            for k, v in item[1].items():
                if k == 'points':
                    for point in v:
                        if point[1] is None:
                            retVal += f'{{x: {unixtolocaltimereduced(point[0])}, y: 0}}, '
                        else:
                            retVal += f'{{x: {unixtolocaltimereduced(point[0])}, y: {point[1]}}}, '

    retVal = retVal[0:-3] + "]"
    return retVal


def getOutGeneric(output, typestr):
    retVal = []
    for item in output.items():
        if item[0] == typestr:
            for k, v in item[1].items():
                if k == 'points':
                    for point in v:
                        if point[2] is None:
                            retVal.append(0)
                        else:
                            retVal.append(point[2])

    return retVal


@app.template_filter('getInTraffic')
def getInTraffic(output):
    print("inside getInTraffic")
    return getInGeneric(output, "Traffic")
    # retVal = []
    # for item in output.items():
    #     if item[0] == "Traffic":
    #         for k, v in item[1].items():
    #             if k == 'points':
    #                 for point in v:
    #                     if point[1] is None:
    #                         retVal.append(0)
    #                     else:
    #                         retVal.append(point[1])
    #
    # print(retVal)
    # return retVal


@app.template_filter('getOutTraffic')
def getOutTraffic(output):
    return getOutGeneric(output, "Traffic")


@app.template_filter('getInDiscards')
def getInDiscards(output):
    return getInGeneric(output, "Discards")


@app.template_filter('getOutDiscards')
def getOutDiscards(output):
    return getOutGeneric(output, "Discards")


@app.template_filter('getInUnicast')
def getInUnicast(output):
    return getInGeneric(output, "Unicast Packets")


@app.template_filter('getOutUnicast')
def getOutUnicast(output):
    return getOutGeneric(output, "Unicast Packets")


@app.template_filter('getInErrors')
def getInErrors(output):
    return getInGeneric(output, "Errors")


@app.template_filter('getOutErrors')
def getOutErrors(output):
    return getOutGeneric(output, "Errors")

