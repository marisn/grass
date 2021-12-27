# Client responsible for running particles
import importlib.util
import json

from random import randint
from time import sleep

from grass.script import core


class ParticleClient():
    """Runs in a client performing actual Particle fittness evaluation.
    Performs communication with main node to obtain Particle parameters
    and posts back Particle evaluation results"""

    def __init__(self, partfile, server):
        """Load a Particle implementation from a provided file"""
        spec = importlib.util.spec_from_file_location("particle", partfile)
        particle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(particle)
        self.particle = particle.Particle()

    def run_particle(self, params):
        """Runs clients provided implementation of Particle"""
        try:
            res = self.particle.run(params=params)
        except Exception as e:
            msg = "Exception during particle run"
            try:
                self.particle.cleanup()
            except AttributeError:
                msg += " and cleanup function is not implemented"
            self.fatal_error(msg, e)
            raise e
        try:
            self.particle.cleanup()
        except AttributeError:
            # cleanup function is not mandatory
            pass
        except Exception as e:
            self.fatal_error("Exception in particle cleanup", e)
            raise e
        return res

    def fatal_error(self, msg, e):
        """Signal back to the server process a fatal problem with Particle"""
        # Print warning also here
        core.error(msg)
        # TODO: send error and exception to the server process

    def get_particle(self):
        """Fetches a new particle parameter set"""
        # data = fetch from self.server
        # state = json.loads(data)
        ret = {"params": {"foo": 1, "bar": 2, "count": self.count}}
        if self.count < 10:
            self.count += 1
            if self.count % 2 == 0:
                ret["wait"] = True
            else:
                ret["wait"] = False
            ret["stop"] = False
        else:
            ret["wait"] = False
            ret["stop"] = True
        return ret
    
    def post_particle(self, result):
        """Posts back particle run outcome"""
        print("sending result to the main process:", result)

    def run(self):
        """Main loop"""
        self.count = 0
        while True:
            try:
                state = self.get_particle()
            except Exception as e:
                core.error("Error while obtaining particle from server", e)
                break
            if state["stop"]:
                # There are no more particles to process
                print("Stopping...")
                break
            if state["wait"]:
                # There are no more unprocessed particles at this step
                # but there might be more steps
                duration = randint(5, 30)
                print(f"Waiting {duration} seconds...")
                sleep(duration)
                continue
            try:
                res = self.run_particle(state["params"])
            except Exception:
                # There has been an error during run
                print("There was an error...")
                break
            # Report back particle result
            try:
                self.post_particle(res)
            except Exception as e:
                core.error("Exception while sending particle run result.", e)
                break
