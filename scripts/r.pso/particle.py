# Šis ir lieki!
# An implementation of a single particle abstract class
from abc import ABC, abstractmethod


class ParticleException(Exception):
    """Raise in case of particle run error to signal failure"""
    def __init__(self, message, errors):
        # TODO: store kwargs
        super().__init__(message)
        self.errors = errors


class Particle(ABC):
    """An abstract class implementing a single particle"""

    def __init__(self, regat):
        regat.register(self)

    @abstractmethod
    def run(self, params):
        """This function should do all heavy lifting.
        Particle parameters are passed as 'params' parameter."""
        raise NotImplementedError

    @abstractmethod
    def cleanup(self, exception):
        """An optional cleanup function to call if run raises an exception.
        The rised ParticleException is passed as 'exception' parameter."""
        raise NotImplementedError
