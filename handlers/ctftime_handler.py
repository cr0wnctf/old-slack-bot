from bottypes.command import *
from bottypes.command_descriptor import *
from bottypes.invalid_command import *
from handlers.handler_factory import *
from handlers.base_handler import *
from dateutil import parser
from decimal import *
import time, urllib, json, requests, datetime
import pytz
from prettytable import PrettyTable

class UpcomingCommand(Command):
    """Shows the CTFs starting in the next 7 days."""

    def execute(self, slack_wrapper, args, channel_id, user_id):
        """Execute the ShowAvailableArch command."""
        try:
            days = int(args[0])
        except Exception:
            days = 7

        start_time = int(time.time()) - 86400 * 10
        end_time = int(time.time()) + (days * 86400)
        url = "https://ctftime.org/api/v1/events/?limit=20&start={}&finish={}".format(start_time, end_time)
        with urllib.request.urlopen(url) as u:
            response = u.read()
        upcomingctfs = json.loads(response)
        bst = pytz.timezone('Europe/London')
        now = datetime.datetime.now(tz=bst)

        msg = ""

        msg += "*Upcoming CTFs* \n\n"

        for ctf in upcomingctfs:


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

class HowLongCommand(Command):
    """Shows information about the requested syscall."""

    def execute(self, slack_wrapper, args, channel_id, user_id):
            self.send_message(slack_wrapper, channel_id, user_id,
                             "Specified architecture not available: `{}`".format(args[0]))


class CTFTimeScoreCalc(Command):

    def execute(self, slack_wrapper, args, channel_id, user_id):
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
    def execute(self, slack_wrapper, args, channel_id, user_id):
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
            "score": CommandDesc(CTFTimeScoreCalc, "Calculate CTFTime points from a CTF", ["Our Score", "Our Placing", "Best Score", "Number of teams", "Weight"], None),
        }


HandlerFactory.register("ctftime", CTFTimeHandler())
