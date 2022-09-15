from pylsl import StreamInlet, resolve_stream


def main():
    # first resolve a marker stream on the lab network
    print("looking for a marker stream...")
    streams = resolve_stream('name', 'ERN')

    # create a new inlet to read from the stream
    inlet = StreamInlet(streams[0])

    while True:

        sample, timestamp = inlet.pull_sample()

        print(f"action at {timestamp} is {bool(sample[0])}")


if __name__ == '__main__':
    main()