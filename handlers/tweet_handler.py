from bottypes.command import *
from bottypes.command_descriptor import *
from bottypes.invalid_command import *
from handlers.handler_factory import *
import handlers.handler_factory as handler_factory
from handlers.base_handler import *
from dateutil import parser
import time, urllib, json, requests, datetime
import pytz
from prettytable import PrettyTable
from twitter import Twitter, OAuth
import random

class UpcomingCommand(Command):
    """Shows the CTFs starting in the next 7 days."""

    @classmethod
    def execute(cls, slack_wrapper, args, channel_id, user_id, user_is_admin):
        """Execute the ShowAvailableArch command."""

        profiles = ['SunTzuSec', '9000ipaddresses']

        # ...
        access_token = handler_factory.botserver.get_config_option("twitter_access_token")
        access_secret = handler_factory.botserver.get_config_option("twitter_access_secret")
        consumer_secret = handler_factory.botserver.get_config_option("twitter_consumer_secret")
        consumer_key = handler_factory.botserver.get_config_option("twitter_consumer_key")


        api = Twitter(
                auth=OAuth(access_token,access_secret, consumer_key, consumer_secret)
            )

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


handler_factory.register("tweet_handler", TweetHandler())
