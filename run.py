#!/usr/bin/env python3
from server.botserver import BotServer
from util.loghandler import log


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
