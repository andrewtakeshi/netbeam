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


@app.template_filter('getTimeVals')
def getTimeValues(output):
    retVal = set()

    for item in output.items():
        for k, v in item[1].items():
            if k == 'points':
                for point in v:
                    retVal.add(unixtolocaltimereduced(point[0]))

    return sorted(retVal)


