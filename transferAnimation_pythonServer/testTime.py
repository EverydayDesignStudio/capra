from datetime import datetime
import time
import json

data = {}

while (True):

    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)
    data['currentTime'] = dt_string

    with open('test.json', 'w') as outfile:
        json.dump(data, outfile)

    time.sleep(5)
