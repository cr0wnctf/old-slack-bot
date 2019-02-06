from abc import ABC, abstractmethod
from server.botserver import BotServer


class BaseService(ABC):
    """
    Abstract class that every service should inherit from
    """

    @abstractmethod
    def run(self, bot_server: BotServer):
        """
        Method called periodically by service handler
        :param bot_server: Reference to the running bot_server
        :return: None
        """
        pass

    @abstractmethod
    def run_time_period(self):
        """
        Method called by service handler to know how often to schedule this service to repeat.

        Give values in seconds.
        :return:
        """
        pass
