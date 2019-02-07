import threading
import time

import websocket
from slackclient.server import SlackConnectionError

import handlers.handler_factory as handler_factory

from bottypes.invalid_console_command import *
from util.slack_wrapper import *
from util.loghandler import log
from services.enabled_services import enabled_services

# This pointless line is quite important. This registers all the handlers so no delete plox until a rewrite
from handlers import *


class BotServer(threading.Thread):

    # Global lock for locking global data in bot server
    thread_lock = threading.Lock()
    user_list = {}

    def __init__(self):
        log.debug("Parse config file and initialize threading...")
        threading.Thread.__init__(self)
        self.running = False
        self.config = {}
        self.bot_name = ""
        self.bot_id = ""
        self.bot_at = ""
        self.slack_wrapper = None
        self.service_stack = []

    @staticmethod
    def lock():
        """Acquire global lock for working with global (not thread-safe) data."""
        BotServer.thread_lock.acquire()

    @staticmethod
    def release():
        """Release global lock after accessing global (not thread-safe) data."""
        BotServer.thread_lock.release()

    def quit(self):
        """Inform the application that it is quitting."""
        log.info("Shutting down")
        self.running = False

    def load_config(self):
        """Load configuration file."""
        self.lock()
        with open("./config.json") as f:
            self.config = json.load(f)
        self.release()

    def get_config_option(self, option):
        """Get configuration option."""
        self.lock()
        result = self.config.get(option)
        self.release()

        return result

    def set_config_option(self, option, value):
        """Set configuration option."""
        self.lock()

        try:
            if option in self.config:
                self.config[option] = value
                log.info("Updated configuration: {} => {}".format(option, value))

                with open("./config.json", "w") as f:
                    json.dump(self.config, f)
            else:
                raise InvalidConsoleCommand("The specified configuration option doesn't exist: {}".format(option))
        finally:
            self.release()

    def parse_slack_message(self, message_list):
        """
        The Slack Real Time Messaging API is an events firehose.
        Return (message, channel, user) if the message is directed at the bot,
        otherwise return (None, None, None).
        """
        for msg in message_list:
            if msg.get("type") == "message" and "subtype" not in msg:
                if self.bot_at in msg.get("text", ""):
                    # Return text after the @ mention, whitespace removed
                    return msg['text'].split(self.bot_at)[1].strip(), msg['channel'], msg['user']
                elif msg.get("text", "").startswith("!"):
                    # Return text after the !
                    return msg['text'][1:].strip(), msg['channel'], msg['user']

        return None, None, None

    def parse_slack_reaction(self, message_list):
        for msg in message_list:
            msgtype = msg.get("type")

            if msgtype == "reaction_removed" or msgtype == "reaction_added":
                # Ignore reactions from the bot itself
                if msg["user"] == self.bot_id:
                    continue

                if msg["item"]:
                    return msg["reaction"], msg["item"]["channel"], msg["item"]["ts"], msg["user"]

        return None, None, None, None

    def load_bot_data(self):
        """
        Fetches the bot user information such as
        bot_name, bot_id and bot_at.
        """
        log.debug("Resolving bot user in slack")
        self.bot_name = self.slack_wrapper.username
        self.bot_id = self.slack_wrapper.user_id
        self.bot_at = "<@{}>".format(self.bot_id)
        log.debug("Found bot user {} ({})".format(self.bot_name, self.bot_id))
        self.running = True

    def start_services(self):
        for service in enabled_services:
            log.info("[Services] Enabling {}".format(service.__name__))
            s = service(self, self.slack_wrapper)
            self.service_stack.append(s)
            s.start()

    def stop_services(self):
        for service in self.service_stack:
            service.cancel()

    def run(self):
        log.info("Starting server thread...")

        self.running = True
        self.load_config()
        self.slack_wrapper = SlackWrapper(self.get_config_option("api_key"))
        self.start_services()

        while self.running:
            try:
                if self.slack_wrapper.connected:
                    log.info("Connection successful...")
                    self.load_bot_data()
                    read_websocket_delay = 1  # 1 second delay between reading from firehose

                    # Might even pass the bot server for handlers?
                    log.info("Initializing handlers...")
                    handler_factory.initialize(self.slack_wrapper, self)

                    # Main loop
                    log.info("Bot is running...")
                    while self.running:
                        message = self.slack_wrapper.read()
                        if message:
                            reaction, channel, ts, reaction_user = self.parse_slack_reaction(message)

                            if reaction:
                                log.debug("Received reaction : {} ({})".format(reaction, channel))
                                handler_factory.process_reaction(
                                    self.slack_wrapper, reaction, ts, channel, reaction_user)

                            command, channel, user = self.parse_slack_message(message)

                            if command:
                                log.debug("Received bot command : {} ({})".format(command, channel))
                                handler_factory.process(self.slack_wrapper, command, channel, user)

                            time.sleep(read_websocket_delay)
                else:
                    log.error("Connection failed. Invalid slack token or bot id?")
                    self.running = False
            except websocket._exceptions.WebSocketConnectionClosedException:
                log.exception("Web socket error. Executing reconnect...")
            except SlackConnectionError:
                # Try to reconnect if slackclient auto_reconnect didn't work out. Keep an eye on the logfiles,
                # and remove the superfluous exception handling if auto_reconnect works.
                log.exception("Slack connection error. Trying manual reconnect in 5 seconds...")
                time.sleep(5)
        self.stop_services()
        log.info("Shutdown complete...")
