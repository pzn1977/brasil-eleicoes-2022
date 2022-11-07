import os
import pickle
import pprint
import sys

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} filename filename ...")
    print(f"Usage: {sys.argv[0]} --binary filename")
    os._exit(1)

if sys.argv[1] == "--binary":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} --binary filename")
        quit()

    fh = open(sys.argv[2], "rb")
    d = pickle.load(fh)
    fh.close()
    sys.stdout.buffer.write(d)

else:

    for i in range(1, len(sys.argv)):
        print(f"** dump file '{sys.argv[i]} **")
        fh = open(sys.argv[i], "rb")
        d = pickle.load(fh)
        fh.close()
        pprint.pprint(d)
