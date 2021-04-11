import datetime
import json
import logging
import os
import sys
import time
from multiprocessing import freeze_support

import utils
from MainRunner import MainThreadRunner

if __name__ == "__main__":
    freeze_support()

    try:
        if len(sys.argv) > 1:
            all_config_filename = sys.argv[1]
            with open(all_config_filename, "r", encoding="UTF-8") as f:
                all_config = json.load(f)
        else:
            with open("config.json", "r", encoding="UTF-8") as f:
                all_config = json.load(f)
    except Exception as e:
        print("解析配置文件时出现错误，请检查配置文件！")
        print("错误详情："+str(e))
        os.system('pause')

    utils.check_and_create_dir(all_config['root']['logger']['log_path'])
    logging.basicConfig(level=utils.get_log_level(all_config),
                        format='%(asctime)s %(thread)d %(threadName)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        handlers=[logging.FileHandler(os.path.join(all_config['root']['logger']['log_path'], "Main_"+datetime.datetime.now(
                        ).strftime('%Y-%m-%d_%H-%M-%S')+'.log'), "a", encoding="utf-8")])

    runner_list = []
    for room_id in all_config['room_ids']:
        config = {
            'root': all_config['root'],
            'spec': {"room_id":room_id}
        }
        tr = MainThreadRunner(config)
        tr.setDaemon(True)
        runner_list.append(tr)


    for tr in runner_list:
        tr.start()
        time.sleep(10)
    
    while True:
        utils.print_log(runner_list)
        time.sleep(all_config['root']['print_interval'])
