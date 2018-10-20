#!/usr/bin/env python3
from util.loghandler import *
from server.botserver import *
from server.consolethread import *


if __name__ == "__main__":
    log.info("Initializing threads...")

    server = BotServer()    
    #console = ConsoleThread(server)

    #console.start()
    server.start()

    # Server should be up and running. Quit when server shuts down
    server.join()
    #console.quit()

    log.info("Server has shut down. Quit")
