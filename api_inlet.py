from threading import Thread, Event
from time import sleep

import requests
from pylsl import StreamInlet, resolve_stream

host = 'http://127.0.0.1:8000'
ET_stream_name = 'Unity.ExampleStream'

# stop = False


def send_eeg():
    # global stop

    print("looking for eeg stream...")
    # first resolve a Motion stream on the lab network
    streams = resolve_stream('type', 'EEG')

    # # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    while True:
        sample, timestamp = inlet.pull_chunk()
        if len(timestamp) > 0:
            # print(timestamp + inlet.time_correction(), sample)
            response = requests.put(f'{host}/update_eeg',
                                    json={
                                        "eeg_data": sample,
                                        "timestamp": timestamp
                                    })
            #         print(timestamp)
            print(str(timestamp[-1]) + ' ' + str(response.json()))
            sleep(0.2)
        
        # if stop:
        #     break


def send_et():

    # global stop

    print("looking for a et stream...")
    streams = resolve_stream('name', ET_stream_name)

    inlet = StreamInlet(streams[0])
    print(inlet.info().name())

    while True:
        sample, timestamp = inlet.pull_sample()
        response = requests.put(f'{host}/update_et',
                                json={
                                    "timestamp": timestamp,
                                    "is_clicked": True
                                })

        print(str(timestamp) + ' ' + str(response.json()))
        sleep(0.1)

        # if stop:
        #     break


def send_api():
    global stop

    eeg = Thread(target=send_eeg)
    et = Thread(target=send_et)
    eeg.start()
    et.start()
    # sleep(5)
    # stop = True
    # et.join()
    # pr('end et')
    # eeg.join()
    # print("Done!")


if __name__ == '__main__':
    send_api()
