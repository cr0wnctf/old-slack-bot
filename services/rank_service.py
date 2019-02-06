# coding=utf-8
import datetime

import requests
from slackclient import SlackClient
from bs4 import BeautifulSoup

from server.botserver import BotServer
from services.base_service import BaseService
from util.loghandler import log
import time
import os


class RankService(BaseService):
    """
    Service to periodically check ctftime rank, and post any updates
    """

    def run_time_period(self):
        return 60 * 60  # Hourly

    def __init__(self, botserver: BotServer):
        self.lookup_add = ""
        self.add_id = 1

        self.team_name = u"the cr0wn"
        self.post_channel_id = "C92MFVBMY"
        self.slack_token = botserver.get_config_option("api_key")
        self.position_filename = "old-pos.txt"

    def run(self, botserver: BotServer):
        quote_page = 'https://ctftime.org/stats/{}'.format(self.lookup_add)
        page = requests.get(quote_page)
        soup = BeautifulSoup(page.text, 'html.parser')

        data = []
        table = soup.find('table', attrs={'class': 'table table-striped'})

        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])

        old_position = 0
        if os.path.isfile(self.position_filename):
            with open('old-pos.', 'r') as f:
                old_position = int(f.read().replace('\n', ''))

        position_changed = False

        position_found = -1
        points_found = -1
        events_found = -1

        for l in data:
            if len(l) > 1 and l[1] == self.team_name:
                position_found = int(l[0])
                points_found = float(l[2])
                events_found = int(l[3])

        if position_found is None:
            self.add_id += 1
            self.lookup_add = "2018?page={}".format(self.add_id)

        if old_position != position_found:
            position_changed = True

        with open(self.position_filename, "w") as f:
            f.write(str(position_found))

        ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

        if not position_changed:
            log.info("{} : Nothing changed, staying quiet".format(ts))
            return

        message = u"*------- 🚨 CTFTIME ALERT 🚨 -------*\n\n@channel\n" \
                  "*We moved from position {} to {} in the world! 🌍🌍🌍🌍🌍" \
                  "*\n\n*We have {} points in {} events.*\n\n" \
                  "https://ctftime.org/stats/".format(old_position, position_found, points_found, events_found)

        sc = SlackClient(self.slack_token)

        sc.api_call(
            "chat.postMessage",
            channel=self.post_channel_id,
            text=message
        )

        log.info("{} : sent update".format(ts))
