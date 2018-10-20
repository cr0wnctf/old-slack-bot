from bottypes.command import *
from bottypes.command_descriptor import *
from bottypes.invalid_command import *
from handlers.handler_factory import *
from handlers.base_handler import *
from dateutil import parser
import time, urllib, json, requests, datetime
import pytz
from prettytable import PrettyTable
from twitter import Twitter, OAuth
import random

class UpcomingCommand(Command):
    """Shows the CTFs starting in the next 7 days."""

    def execute(self, slack_wrapper, args, channel_id, user_id):
        """Execute the ShowAvailableArch command."""

        profiles = ['SunTzuSec', '9000ipaddresses']

        # ...
        handler_factory.botserver.get_config_option("twitter_api_key")
        api = Twitter(
            auth=OAuth('asds',
                       'asdsa', 'asdsa',
                       'asdas'))

        # print(api.VerifyCredentials())
        tweet_set = []

        for ting in profiles:
            t = api.statuses.user_timeline(screen_name=ting, count=100)
            tweet_set.append(random.choice(t)['text'])

        msg = random.choice(tweet_set)

        slack_wrapper.post_message(channel_id, msg)



class TweetHandler(BaseHandler):
    """
    Shows information about syscalls for different architectures.

    Commands :
    # Show available architectures
    @ota_bot syscalls available

    # Show syscall information
    @ota_bot syscalls show x86 execve
    @ota_bot syscalls show x86 11
    """

    # Specify if messages from syscall handler should be posted to channel (0)
    # or per dm (1)
    MSGMODE = 0

    def __init__(self):

        self.commands = {
            "quote": CommandDesc(UpcomingCommand, "Get an inspirational quote", None, None),
        }


HandlerFactory.register("tweet_handler", TweetHandler())

