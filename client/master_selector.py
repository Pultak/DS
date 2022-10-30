# import the threading module
import threading
import broadcast_signaler

PING_PERIOD = 2

def main():
    bs = broadcast_signaler.BroadcastSignaler(PING_PERIOD)

    bs.start()

if __name__ == "__main__":
    main()


