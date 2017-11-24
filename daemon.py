#!/usr/bin/env python3
import os
import sys
import time

pidfile_path = "/tmp/thesis_bot.pid"


def getPID():
    if os.path.exists(pidfile_path):
        pidfile = open(pidfile_path)
        pid = pidfile.read().split("\n")[0]
        pidfile.close()
        if os.path.exists("/proc/"+pid):
            return int(pid)
    return False


def check():
    if os.path.exists(pidfile_path):
        pidfile = open(pidfile_path)
        pid = pidfile.read().split("\n")[0]
        pidfile.close()
        if os.path.exists("/proc/"+pid):
            return True
    return False


def start():
    isStarted = getPID()
    if isStarted:
        print("Daemon already started, PID: "+str(isStarted))
        return False
    else:
        fpid = os.fork()
        if fpid:
            pidfile = open(pidfile_path, "w")
            pidfile.write(str(fpid)+"\n")
            pidfile.close()
        else:
            import main
            main.main()

        time.sleep(2)
        pid = getPID()
        if pid:
            print("Daemon started, PID: " + str(pid))
        else:
            print("Starting failed")
        return pid


def stop():
    pid = getPID()
    if pid:
        print("Killing process " + str(pid) + "...")
        os.kill(pid, 15)
        time.sleep(2)
        pid = check()
        if not(pid):
            print("Success")
    else:
        print("Not running")

    return bool(pid)


def restart():
    status = check()
    if status:
        status = stop()
    if status:
        return True
    else:
        return start()


def daemonMain(argv):
    usage = "Usage: daemon.py start | stop | restart | check"
    if len(argv) != 2:
        print("Wrong number of arguments")
        print(usage)
    else:
        command = argv[1]
        if command == "start":
            return not start()
        elif command == "stop":
            return stop()
        elif command == "restart":
            return not restart()
        elif command == "check":
            isok = check()
            print(isok)
            return not isok
        else:
            print("Unknown command: "+command)
            print(usage)


if __name__ == "__main__":
    sys.exit(daemonMain(sys.argv))