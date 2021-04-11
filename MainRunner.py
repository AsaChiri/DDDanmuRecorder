
import datetime
import logging
import threading
import time
import traceback
from multiprocessing import Process, Value

from BiliLive import BiliLive
from DanmuRecorder import BiliDanmuRecorder


class MainRunner():
    def __init__(self, config):
        self.config = config
        self.prev_live_status = False
        self.bl = BiliLive(self.config)
        self.blr = None
        self.bdr = None

    def run(self):
        try:
            while True:
                if not self.prev_live_status and self.bl.live_status:                 
                    start = datetime.datetime.now()
                    self.bdr = BiliDanmuRecorder(self.config, start)
                    danmu_process = Process(
                        target=self.bdr.run)
                    danmu_process.start()
                    self.prev_live_status = True

                    danmu_process.join()
                else:
                    time.sleep(self.config['root']['check_interval'])
        except KeyboardInterrupt:
            return
        except Exception as e:
            logging.error('Error in Mainrunner:' +
                          str(e)+traceback.format_exc())

class MainThreadRunner(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.mr = MainRunner(config)

    def run(self):
        self.mr.run()