import os
import datetime
import logging
import platform
import prettytable as pt
import threading

def get_log_level(config: dict) -> int:
    if config['root']['logger']['log_level'] == 'DEBUG':
        return logging.DEBUG
    if config['root']['logger']['log_level'] == 'INFO':
        return logging.INFO
    if config['root']['logger']['log_level'] == 'WARN':
        return logging.WARN
    if config['root']['logger']['log_level'] == 'ERROR':
        return logging.ERROR
    return logging.INFO


def check_and_create_dir(dirs: str) -> None:
    if not os.path.exists(dirs):
        os.mkdir(dirs)


def init_data_dir(room_id: str, global_start: datetime.datetime, root_dir: str = os.getcwd()) -> None:
    check_and_create_dir(os.path.join(root_dir, 'data'))
    check_and_create_dir(os.path.join(root_dir, 'data', room_id+'_'+global_start.strftime('%Y-%m-%d_%H-%M-%S')))
    return os.path.join(root_dir, 'data', room_id+'_'+global_start.strftime('%Y-%m-%d_%H-%M-%S'))

def print_log(runner_list: list) -> str:
    tb = pt.PrettyTable()
    tb.field_names = ["TID", "平台", "房间号", "直播状态"]
    for runner in runner_list:
        tb.add_row([runner.native_id, runner.mr.bl.site_name, runner.mr.bl.room_id, "是" if runner.mr.bl.live_status else "否"])
    print(
        f"    DanmukuRecorder  当前时间：{datetime.datetime.now()} 正在工作线程数：{threading.activeCount()}\n")
    print(tb)
    print("\n")
