from webapp import app
from flask import render_template, url_for, render_template, redirect, request, jsonify
from webapp.templates.forms import pscheduler_form
# from test import getTrafficByTimeRangeFlask
import re
import json
import time
import subprocess
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_pscheduler(endpoint):
    """
    Queries the endpoint to see if it is running pScheduler. Does this through the API provided by pScheduler.
    :param endpoint: Endpoint to be queried.
    :return: True if endpoint is running pScheduler, False otherwise.
    """
    if not endpoint.__contains__('https'):
        endpoint = 'https://' + endpoint
    response = requests.get(f'{endpoint}/pscheduler', verify=False).content.decode('utf8')
    return response.__contains__('pScheduler API server')


def get_source_info(source):
    """
    Pings the source address to get an IP address.
    Returns JSON formatted to match that returned by *_to_d3 defs.
    :param source:
    :return:
    """
    ping_process = subprocess.run(['ping', '-c', '1', source], stdout=subprocess.PIPE, universal_newlines=True)
    line = ping_process.stdout.splitlines()[0]
    re_res = re.search(r'([0-9]{1,3}\.){3}[0-9]{1,3}', line)
    ip = line[re_res.regs[0][0]:re_res.regs[0][1]]
    return {
        "success": 1,
        "query": 1,
        "ttl": 0,
        "ip": ip,
        "rtt": 0
    }

def pscheduler_to_d3(source, dest, numRuns = 1):
    """
        Tries to run a pScheduler traceroute from source to destination.
        The source must also be running pScheduler, as must the server/machine running this code.
        If the source is running pScheduler, a traceroute is scheduled, run, and the results converted into
        JSON ingestible by the d3 visualisation.
        :param source: Source for traceroute
        :param dest: Destination for traceroute.
        :param numRuns: Number of times to run the traceroute.
        :return: JSON ingestible by the d3 visualisation if the traceroute is successful. None otherwise.
        """

    # Check the source
    if not check_pscheduler(source):
        return None

    i = 0
    processList = []

    # Schedule traceroute using pscheduler (allows for remote sources)
    for _ in range(numRuns):
        processList.append(subprocess.Popen(['pscheduler', 'task', 'trace', '-s', source, '-d', dest],
                                            stdout=subprocess.PIPE, universal_newlines=True))

    for process in processList:
        process.wait()

    source_info = get_source_info(source)

    output = []

    # Process every line in the traceroute.
    for process in processList:
        output.append(dict())
        output[i]['ts'] = int(time.time())
        output[i]['val'] = []
        output[i]['val'].append(source_info)
        for line in process.communicate()[0].splitlines():
            # print(line)
            # Filter out for only lines that match the traceroute results.
            if re.match(r'^\s*[0-9]+\s+', line):
                split = line.split()
                # Common to all hops
                toAdd = {
                    "success": 1,
                    "query": 1,
                    "ttl": int(split[0])
                }
                # Server didn't respond. Only add the 'common' items.
                if split[1] == "No" or split[1] == "*":
                    output[i]['val'].append(toAdd)
                # Server responded. Do some additional parsing.
                else:
                    # Extract IP address
                    ip = re.search(r'\(?([0-9]{1,3}\.){3}[0-9]{1,3}\)?', line)
                    ip = line[ip.regs[0][0]: ip.regs[0][1]]
                    ip = re.sub(r'\(|\)', '', ip)

                    # Extract RTT
                    rtt = re.findall(r'[0-9]+\.?[0-9]* ms', line)
                    rtt = float(re.sub(r'm|s|\s', '', rtt[0]))

                    toAdd['ip'] = ip
                    toAdd['rtt'] = rtt

                    output[i]['val'].append(toAdd)
        i += 1
        process.stdout.close()
        process.kill()

    # Convert to an actual JSON (takes care of some formatting).
    # output = json.dumps(output)

    return output


@app.route('/', methods=('GET', 'POST'))
def index():
    form = pscheduler_form()

    if form.validate_on_submit():
        return redirect(url_for('pscheduler_query', source = form.pscheduler_source.data,
                                dest = form.pscheduler_dest.data, numRuns=form.numberRuns.data))

    return render_template('index.html', form=form)


# @app.route('/results?hostname=<path:hostname>&timeperiod=<path:timeperiod>')
# def results(hostname, timeperiod):
#     print("Inside of results")
#
#
#
#     outputDict = getTrafficByTimeRangeFlask(hostname, timeperiod)
#
#     return render_template('results.html', output=outputDict)


@app.route('/pscheduler_query', methods=['POST'])
def pscheduler_query():
    source = request.form['pscheduler_source']
    dest = request.form['pscheduler_dest']
    numRuns = int(request.form['numRuns'])

    render_template('pscheduler_query.html')

    output = pscheduler_to_d3(source, dest, numRuns)
    print(output)

    return render_template('pscheduler_query.html', output=output)








