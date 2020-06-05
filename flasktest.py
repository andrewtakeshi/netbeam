# import sys
# import io
from webapp import app
from flask import render_template, url_for, render_template, redirect, request
from webapp.templates.forms import HostForm
from test import getTrafficByTimeRangeFlask

@app.route('/', methods=('GET', 'POST'))
def index():
    form = HostForm()

    if form.validate_on_submit():
        return redirect(url_for('results', hostname = form.hostname.data, timeperiod = form.timeperiod.data))
        # return redirect(url_for('results', messages=messages))

    return render_template('index.html', form=form)


@app.route('/results?hostname=<path:hostname>&timeperiod=<path:timeperiod>')
def results(hostname, timeperiod):
    print("Inside of results")



    outputDict = getTrafficByTimeRangeFlask(hostname, timeperiod)

    return render_template('results.html', output=outputDict)






