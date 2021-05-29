from os import closerange
import sys
import json
import requests
import time
import os

current_block = "0000000000000981c0f836cc249fb18744fd33458b85d00de3e7f8995f4543ec"
URL = "https://blockchain.info/rawblock/{}"
queue = []

def fetch_data(block: str) -> (int, str):
    try:
        r = requests.get(URL.format(block))
    except Exception as e:
        print("\tException Encountered: {}".format(e))
        # retry
        fetch_data(current_block)

    return (r.status_code, r.text)

# warning: this may cause some next blocks to get lost (if more than one next hash is present)
def get_next_block(block: str) -> str:
    block = json.loads(block)
    return block['next_block'][0]

def get_time(block: str) -> str:
    block = json.loads(block)
    datetime = block['time']
    datetime = time.localtime(int(datetime))
    return {
        "month":datetime.tm_mon,
        "day":datetime.tm_mday,
        "year":datetime.tm_year,
        "hour":datetime.tm_hour,
        "min":datetime.tm_min,
        "sec":datetime.tm_sec
    }

def save_data_to_file(data: list, filepath: str):
    print("\tSaving...")
    with open(filepath, "w+") as f:
        f.write(json.dumps(data))

if __name__ == "__main__":
    if sys.argv[2]:
        bound = True
    else:
        bound = False

    filepath = str(sys.argv[1])
    status, data = fetch_data(current_block)
    datetime = get_time(data)
    current_month = datetime['month'] if not bound else 0

    while datetime['year'] < 2020:
        status, data = fetch_data(current_block)

        if status == 200:
            print("[{}]\t{}-{}-{} {}:{}:{}".format(
                status,
                datetime['month'],
                datetime['day'],
                datetime['year'],
                datetime['hour'],
                datetime['min'],
                datetime['sec']
            ))
            datetime = get_time(data)
            queue.append(json.loads(data))
            
            if current_month != datetime['month']: # save to file and clear queue
                filename = os.path.join(filepath, "{}-{}.json".format(current_month,datetime['year']))
                save_data_to_file(queue, filename)
                queue = []

            current_block = get_next_block(data)
            current_month = datetime['month']
        else:
            print("[{}]".format(status))

        if bound:
            if datetime['day'] >= 25: break

        

