import logging
from abc import ABC
from threading import Thread, Event


logger = logging.getLogger(__name__)


def verify_run(method):
    """
    A decorator that works in tandem with a Runner class to check the runner class's "continue_run" property to see if
    the decorated method should be called or not.
    :param method: The method for which continue_run will be verified before executing.
    :return: The wrapped method.
    """
    def check(instance, *args, **kwargs):
        if instance.continue_run:
            return method(instance, *args, **kwargs)
    return check


class Runner(ABC, Thread):

    """
    An abstract class that inherits from the Thread class to provide stop implementation to classes that are meant to
    run in separate threads and/or contain threadpool executors.
    """

    def __init__(self):
        super().__init__()
        self._stop_run = Event()

    def stop(self) -> None:
        """
        Sets the stop_run flag to true.
        """
        self._stop_run.set()
        logger.info(f'Stopping {self.__class__.__name__}')

    @property
    def continue_run(self) -> bool:
        """
        Indicates if the stop run flag is set.
        :return: The current value of the 'is_set' value of the stop run flag.
        """
        return not self._stop_run.is_set()
