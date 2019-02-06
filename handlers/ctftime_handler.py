import datetime
import json
import time

import pytz
import requests
from dateutil import parser

import handlers.handler_factory as handler_factory
from bottypes.command_descriptor import *
from handlers.base_handler import *


class UpcomingCommand(Command):
    """Shows the CTFs starting in the next 7 days."""

    @classmethod
    def execute(cls, slack_wrapper, args, channel_id, user_id, user_is_admin):
        """Find the upcoming CTFs and print them"""
        try:
            days = int(args[0])
        except:
            days = 7

        start_time = int(time.time()) - 86400 * 10
        end_time = int(time.time()) + (days * 86400)
        url = "https://ctftime.org/api/v1/events/?limit=20&start={}&finish={}".format(start_time, end_time)
        print("URL = {}".format(url))
        req = requests.get(url, headers={'User-Agent': "Otters inc."})

        if req.status_code != 200:
            msg = "Unable to get upcoming events :("
            slack_wrapper.post_message(channel_id, msg)
            return

        upcoming_ctfs = json.loads(req.text)
        bst = pytz.timezone('Europe/London')
        now = datetime.datetime.now(tz=bst)

        msg = ""

        msg += "*Upcoming CTFs* \n\n"

        for ctf in upcoming_ctfs:
            start = parser.parse(ctf['start'])

            local_dt = start.astimezone(bst)
            local_start = bst.normalize(local_dt)
            local_start = local_start.strftime('%a %d %b %H:%M')

            end = parser.parse(ctf['finish'])
            local_dt = end.astimezone(bst)
            local_end = bst.normalize(local_dt)
            local_end = local_end.strftime('%a %d %b %H:%M')

            if end >= now:
                msg += "*{}*\n".format(ctf['title'])
                msg += "{}\t to \t{}\n".format(local_start, local_end)
                msg += "Teams: {}\n".format(ctf['participants'])
                msg += "Type: {}\n".format(ctf['format'])
                msg += "{}\n".format(ctf['url'])
                msg += "\n\n"

        msg += ""

        slack_wrapper.post_message(channel_id, msg)


class CTFTimeScoreCalc(Command):

    @classmethod
    def execute(cls, slack_wrapper, args, channel_id, user_id, user_is_admin):
        if len(args) < 5:
            slack_wrapper.post_message(channel_id, "Please supply all args")
        else:
            score = int(args[0])
            place = int(args[1])
            best_score = int(args[2])
            num_teams = int(args[3])
            weight = float(args[4])

            points_coef = score / best_score
            place_coef = 1 / place

            total = ((points_coef + place_coef) * weight) / (1 / (1 + (place / num_teams)))

            message = str("Total CTFTime points: {:.5}".format(total))
            slack_wrapper.post_message(channel_id, message)


class CTFTimePosition(Command):
    @classmethod
    def execute(cls, slack_wrapper, args, channel_id, user_id, user_is_admin):
        pass


class CTFTimeHandler(BaseHandler):
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
            "upcoming": CommandDesc(UpcomingCommand, "Shows the upcoming CTFs in the next 7 days", None, None),
            "score": CommandDesc(CTFTimeScoreCalc, "Calculate CTFTime points from a CTF",
                                 ["Our Score", "Our Placing", "Best Score", "Number of teams", "Weight"], None),
        }


handler_factory.register("ctftime", CTFTimeHandler())
