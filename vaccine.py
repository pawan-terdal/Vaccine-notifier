import requests
import os
import json
import pandas as pd
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
import winsound
import sys



def notify(district):
    today = date.today()
    now = datetime.now()
    # dd/mm/YY
    tomorrow = date.today() + timedelta(days = 1)
    print("**********************************************************************\n")
    print("Script Run Time: " + now.strftime('%H:%M:%S'))
    print("Looking for slots on : " + tomorrow.strftime('%d-%m-%Y'))
    headers = {
        'authority': 'cdn-api.co-vin.in',
        'accept': '*/*',
        'access-control-request-method': 'GET',
        'access-control-request-headers': 'authorization',
        'origin': 'https://selfregistration.cowin.gov.in',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-dest': 'empty',
        'referer': 'https://selfregistration.cowin.gov.in/',
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('district_id', district),
        ('date', tomorrow.strftime("%d-%m-%Y")),
    )

    try:
        response = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict',
        headers=headers, params=params)
    except requests.exceptions.RequestException:
        print("Network error")
        return

    string_response = response.content.decode("utf-8")

    try:
        json_data = json.loads(string_response)
    except json.decoder.JSONDecodeError:
        print("Something went wrong. Skipping this iteration")
        return

    data = []
    for center in json_data['centers']:
        cur_data = []
        sessionData = []
        for session in center['sessions']:
            if (session['min_age_limit']) == 18:
                curSession = []
                curSession.append(session['date'])
                curSession.append(session['available_capacity_dose1'])
                sessionData.append(curSession)

        if len(sessionData) > 0:
            cur_data.append(center['center_id'])
            cur_data.append(center['name'])
            cur_data.append(center['pincode'])
            cur_data.append(sessionData)
            print(cur_data)
            print
            data.append(cur_data)
    print()
    df = pd.DataFrame(data, columns = ['Center_ID','Name', 'PinCode','Available_Capacity'])

    slots = df['Available_Capacity']
    for i in slots:
        for j in i:
            if j[1] > 5: # when more than 5 doses open up
                winsound.Beep(440, 2000)
                print("SLOTS AVAILABLE ! CHECK COVIN WEBSITE NOW !")

if __name__ == '__main__':
    i = 0
    dist_id = sys.argv[1:]
    print("District IDs given: ")
    if len(dist_id) == 0:
        print("No args given. Using bangalore urban, rural dist ids") # use my dist ids
        dist_id = ['294', '276', '265']
    print(dist_id)
    while 1:
        notify(dist_id[i])
        time.sleep(30)
        i = (i+1)%(len(dist_id))
