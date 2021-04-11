import matplotlib.pyplot as plt
import jsonlines
import os
import sys
import datetime
import time
from itertools import groupby
import jieba
from collections import Counter
import wordcloud
import matplotlib
 
font = {'family': 'MicroSoft Yahei',
       'weight': 'regular',
       'size': 10}
 
matplotlib.rc("font", **font)

def parse_danmu(dir_name):
    danmu_list = []
    if os.path.exists(os.path.join(dir_name, 'danmu.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'danmu.jsonl')) as reader:
            for obj in reader:
                danmu_list.append({
                    "isSC": False,
                    "UL": obj['ul_info']['ul_level'],
                    "text": obj['text'],
                    "time": obj['properties']['time']//1000
                })
    if os.path.exists(os.path.join(dir_name, 'superchat.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'superchat.jsonl')) as reader:
            for obj in reader:
                danmu_list.append({
                    "isSC": True,
                    "text": obj['text'],
                    "time": obj['time']
                })
    danmu_list = sorted(danmu_list, key=lambda x: x['time'])
    return danmu_list


def parse_gift(dir_name):
    gift_list = []
    if os.path.exists(os.path.join(dir_name, 'gift.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'gift.jsonl')) as reader:
            for obj in reader:
                gift_list.append({
                    "isSilver": obj['coin_type'] == 'silver',
                    # "giftName": obj['gift_name'],
                    "price": obj['price'],
                    "num": obj['num'],
                    "cost": obj['total_coin'],
                    "time": obj['time']
                })
    if os.path.exists(os.path.join(dir_name, 'guard.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'guard.jsonl')) as reader:
            for obj in reader:
                gift_list.append({
                    "isSilver": False,
                    "giftName": obj['gift_name'],
                    "price": obj['price'],
                    "num": obj['num'],
                    "cost": obj['price']*obj['num'],
                    "time": obj['time']
                })
    if os.path.exists(os.path.join(dir_name, 'superchat.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'superchat.jsonl')) as reader:
            for obj in reader:
                gift_list.append({
                    "isSilver": False,
                    "giftName": "SuperChat",
                    "price": obj['price'],
                    "num": 1,
                    "cost": obj['price'],
                    "time": obj['time']
                })

    gift_list = sorted(gift_list, key=lambda x: x['time'])
    return gift_list

def plot_danmu(dir_name, interval=60, SC_ratio=1, min_UL=0):
    danmu_list = parse_danmu(dir_name)
    try:
        with open(os.path.join(dir_name, "live_end_time"), "r", encoding="utf-8") as f:
            end_timestamp = f.read()
            end_timestamp = end_timestamp.strip()
    except Exception:
        end_timestamp = danmu_list[-1]['time']

    start_time_str = "_".join(os.path.basename(dir_name).split("_")[1:])
    start_time = datetime.datetime.strptime(
        start_time_str, '%Y-%m-%d_%H-%M-%S')
    start_timestamp = int(start_time.timestamp())
    timestamp_list = list(
        range(0, end_timestamp-start_timestamp+interval, interval))
    time_list = [time.strftime("%H:%M:%S", time.gmtime(ts))
                 for ts in timestamp_list]
    count_list = [0]*len(timestamp_list)
    for k, g in groupby(danmu_list, key=lambda x: (x['time']-start_timestamp)//interval):
        num = 0
        for o in list(g):
            if o['isSC']:
                num += SC_ratio
            else:
                num += 1 if o['UL'] >= min_UL else 0
        count_list[k] = num
    l = os.path.basename(dir_name)
    room_id = l.split("_")[0]
    dt = "_".join(l.split("_")[1:])
    plt.title(f"房间号：{room_id} 场次：{dt} 弹幕曲线")
    plt.plot(time_list, count_list)
    plt.subplots_adjust(bottom=0.3)
    plt.xticks(range(0, len(time_list), max(
        1, len(time_list)//15)), rotation=30)
    plt.savefig(os.path.join(dir_name, "danmu.png"))
    plt.show()


def plot_gift(dir_name, interval=60, silver_ratio=0):
    gift_list = parse_gift(dir_name)
    try:
        with open(os.path.join(dir_name, "live_end_time"), "r", encoding="utf-8") as f:
            end_timestamp = f.read()
            end_timestamp = end_timestamp.strip()
    except Exception:
        end_timestamp = gift_list[-1]['time']

    start_time_str = "_".join(os.path.basename(dir_name).split("_")[1:])
    start_time = datetime.datetime.strptime(
        start_time_str, '%Y-%m-%d_%H-%M-%S')
    start_timestamp = int(start_time.timestamp())
    timestamp_list = list(
        range(0, end_timestamp-start_timestamp+interval, interval))
    time_list = [time.strftime("%H:%M:%S", time.gmtime(ts))
                 for ts in timestamp_list]
    count_list = [0]*len(timestamp_list)
    for k, g in groupby(gift_list, key=lambda x: (x['time']-start_timestamp)//interval):
        num = 0
        for o in list(g):
            num += o['cost']*(silver_ratio if o['isSilver'] else 1)
        count_list[k] = num
    l = os.path.basename(dir_name)
    room_id = l.split("_")[0]
    dt = "_".join(l.split("_")[1:])
    plt.title(f"房间号：{room_id} 场次：{dt} 礼物曲线")
    plt.plot(time_list, count_list)
    plt.xticks(range(0, len(time_list), max(
        1, len(time_list)//15)), rotation=30)
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(os.path.join(dir_name, "gift.png"))
    plt.show()


def generateClouds(output_words,output_file):
    w = wordcloud.WordCloud(font_path="msyh.ttc",)
    w.generate_from_frequencies(output_words)
    plt.imshow(w)
    plt.axis("off")
    plt.savefig(output_file)
    plt.show()

def summary(dir_name, topK=10):
    # 统计弹幕高频词和数量

    # 获取所有弹幕和醒目留言
    danmu_list = []
    if os.path.exists(os.path.join(dir_name, 'danmu.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'danmu.jsonl')) as reader:
            for obj in reader:
                danmu_list.append(obj['text'])
    common_danmu_num = len(danmu_list)
    if os.path.exists(os.path.join(dir_name, 'superchat.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'superchat.jsonl')) as reader:
            for obj in reader:
                danmu_list.append(obj['text'])
    sc_num = len(danmu_list) - common_danmu_num
    # 对文本进行分词
    seg_list = jieba.cut(" ".join(danmu_list))
    # 进行词频统计
    c = Counter()
    for x in seg_list:
        if len(x) > 1 and x != '\r\n':
            c[x] += 1
    try:
        high_freq_word_list = list(
            list(zip(*c.most_common(min(topK, len(c)))))[0])
    except IndexError:
        high_freq_word_list = []
    
    # 统计普通弹幕发送者用户信息
    danmu_user_dict = {}
    danmu_medal_dict = {}
    if os.path.exists(os.path.join(dir_name, 'danmu.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'danmu.jsonl')) as reader:
            for obj in reader:
                user_uid = obj['user_info']['user_id']
                user_name = obj['user_info']['user_name']
                user_ul = obj['ul_info']['ul_level']
                guard_level = obj['guard_level']
                if user_uid in danmu_user_dict:
                    danmu_user_dict[user_uid][3] += 1
                else:
                    danmu_user_dict[user_uid] = [
                        user_name, user_ul, guard_level, 1]
                    medal_liver_uid = obj['medal_info']['medal_liver_uid']
                    if medal_liver_uid != 0:
                        medal_name = obj['medal_info']['medal_name']
                        medal_level = obj['medal_info']['medal_level']
                        if medal_liver_uid in danmu_medal_dict:
                            danmu_medal_dict[medal_liver_uid][1].append(
                                medal_level)
                        else:
                            danmu_medal_dict[medal_liver_uid] = [ medal_name, [medal_level]]
    common_danmu_sender_num = len(danmu_user_dict)
    common_danmu_sender_num_guard_lv3 = len(
        list(filter(lambda x: x[2] == 3, danmu_user_dict.values())))
    common_danmu_sender_num_guard_lv2 = len(
        list(filter(lambda x: x[2] == 2, danmu_user_dict.values())))
    common_danmu_sender_num_guard_lv1 = len(
        list(filter(lambda x: x[2] == 1, danmu_user_dict.values())))
    common_danmu_sender_ul_avg = sum(
        [x[1] for x in danmu_user_dict.values()])/common_danmu_sender_num
    topK_common_danmu_sender = sorted(danmu_user_dict.items(
    ), key=lambda x: x[1][3], reverse=True)[:min(topK, common_danmu_sender_num)]

    common_danmu_medal_num = len(danmu_medal_dict)
    topK_common_danmu_medal = sorted(danmu_medal_dict.items(
    ), key=lambda x: len(x[1][1]), reverse=True)[:min(topK, common_danmu_medal_num)]

    # 进行打钱统计
    silver_total = 0
    gold_total = 0
    guard_num=[0,0,0,0]
    gift_user_dict = {}

    if os.path.exists(os.path.join(dir_name, 'gift.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'gift.jsonl')) as reader:
            for obj in reader:
                if obj['coin_type'] == 'silver':
                    silver_total += obj['total_coin']
                else:
                    gold_total += obj['total_coin']
                user_uid = obj['user_id']
                user_name = obj['user_name']
                if user_uid in gift_user_dict:
                    gift_user_dict[user_uid][1] += obj['total_coin']
                else:
                    gift_user_dict[user_uid] = [
                        user_name, obj['total_coin']]
    if os.path.exists(os.path.join(dir_name, 'guard.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'guard.jsonl')) as reader:
            for obj in reader:
                gold_total += obj['price']*obj['num']
                guard_num[obj['guard_level']]+=obj['num']
                user_uid = obj['user_id']
                user_name = obj['user_name']
                if user_uid in gift_user_dict:
                    gift_user_dict[user_uid][1] += obj['price']*obj['num']
                else:
                    gift_user_dict[user_uid] = [
                        user_name, obj['price']*obj['num']]
    if os.path.exists(os.path.join(dir_name, 'superchat.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'superchat.jsonl')) as reader:
            for obj in reader:
                gold_total += obj['price']*1000
                user_uid = obj['user_id']
                user_name = obj['user_name']
                if user_uid in gift_user_dict:
                    gift_user_dict[user_uid][1] += obj['price']*1000
                else:
                    gift_user_dict[user_uid] = [
                        user_name, obj['price']*1000]
    gift_sender_num = len(gift_user_dict)
    topK_gift_sender = sorted(gift_user_dict.items(
    ), key=lambda x: x[1][1], reverse=True)[:min(topK, gift_sender_num)]

    # 进行交互统计
    interaction_user_dict = {}
    interaction_medal_dict = {}
    if os.path.exists(os.path.join(dir_name, 'interaction.jsonl')):
        with jsonlines.open(os.path.join(dir_name, 'interaction.jsonl')) as reader:
            for obj in reader:
                if obj['msg_type'] == 1:
                    user_uid = obj['user_id']
                    user_name = obj['user_name']
                    if user_uid in interaction_user_dict:
                        interaction_user_dict[user_uid][1] += 1
                    else:
                        interaction_user_dict[user_uid] = [
                            user_name, 1]
                        medal_liver_uid = obj['medal_info']['medal_liver_uid']
                        if medal_liver_uid != 0:
                            medal_name = obj['medal_info']['medal_name']
                            medal_level = obj['medal_info']['medal_level']
                            if medal_liver_uid in interaction_medal_dict:
                                interaction_medal_dict[medal_liver_uid][1].append(
                                    medal_level)
                            else:
                                interaction_medal_dict[medal_liver_uid] = [
                                     medal_name, [medal_level]]

    interaction_num = len(interaction_user_dict)
    interaction_medal_num = len(interaction_medal_dict)
    topK_common_interaction_medal = sorted(interaction_medal_dict.items(
    ), key=lambda x: len(x[1][1]), reverse=True)[:min(topK, interaction_medal_num)]

    l = os.path.basename(dir_name)
    room_id = l.split("_")[0]
    dt = "_".join(l.split("_")[1:])
    nl = "\n"
    wordcloud_filename = os.path.join(dir_name,"danmu_wordcloud.png")
    generateClouds(c,wordcloud_filename)

    print(f"""
        房间号：{room_id} 场次：{dt} 直播数据统计

    本场直播一共发送了{common_danmu_num}条弹幕和{sc_num}条醒目留言。
    在这些弹幕和醒目留言中，高频的{topK}个关键词为：{"  ".join(high_freq_word_list)}。
    弹幕词云已生成到：{wordcloud_filename}。

    本场直播一共有{common_danmu_sender_num}位观众发送了弹幕，发送弹幕的观众平均UL等级为UL{common_danmu_sender_ul_avg:.2f}。
    其中舰长{common_danmu_sender_num_guard_lv3}位，提督{common_danmu_sender_num_guard_lv2}位，总督{common_danmu_sender_num_guard_lv1}位。
    发送弹幕最多的{topK}个观众为
        {f";{nl}        ".join([f"UID:{x[0]} 用户名：{x[1][0]} 发送弹幕数量：{x[1][3]}" for x in topK_common_danmu_sender])}。

    本场直播的观众佩戴的粉丝牌数量共有{common_danmu_medal_num}种。
    其中最常见的{topK}个粉丝牌为
        {f";{nl}        ".join([f"粉丝牌主播UID:{x[0]} 粉丝牌：{x[1][0]} 佩戴人数：{len(x[1][1])} 平均等级：{sum(x[1][1])/len(x[1][1]):.2f}" for x in topK_common_danmu_medal])}。

    本场直播观众共赠送了价值{silver_total}银瓜子的礼物和价值{gold_total}金瓜子即{gold_total/1000:.2f}元人民币的礼物。
    包括{sum(guard_num)}个大航海礼物，其中舰长{guard_num[3]}个，提督{guard_num[2]}个，总督{guard_num[1]}个。
    共有{gift_sender_num}个观众赠送了金瓜子礼物。
    赠送金瓜子礼物最多的{topK}个观众为
        {f";{nl}        ".join([f"UID:{x[0]} 用户名：{x[1][0]} 赠送礼物价值：{x[1][1]} 即{x[1][1]/1000:.2f}元人民币" for x in topK_gift_sender])}。

    本场直播共记录到{interaction_num}条互动记录。互动观众佩戴的粉丝牌数量共有{interaction_medal_num}种。
    其中最常见的{topK}个粉丝牌为
        {f";{nl}        ".join([f"粉丝牌主播UID:{x[0]} 粉丝牌：{x[1][0]} 佩戴人数：{len(x[1][1])} 平均等级：{sum(x[1][1])/len(x[1][1]):.2f}" for x in topK_common_interaction_medal])}。
    """)


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            data_path = sys.argv[1]
            if not os.path.exists(data_path):
                print("数据路径不存在！")
        else:
            data_path = "./data"
    except Exception as e:
        print("错误！")
        print("错误详情："+str(e))
        os.system('pause')
    while True:
        live_list = []
        for fname in os.listdir(data_path):
            if os.path.isdir(os.path.join(data_path, fname)):
                live_list.append(fname)
        print("有以下直播场次之数据可供选择：\n")
        for i, l in enumerate(live_list):
            room_id = l.split("_")[0]
            dt = "_".join(l.split("_")[1:])
            print(f"{i+1}:\t房间号：{room_id}\t开播时间：{dt}\n")
        ch = input("请选择需要处理的直播场次的编号，输入0退出\n").strip()
        if ch == "" or ch == "0" or int(ch) > len(live_list):
            sys.exit(0)
        fname = live_list[int(ch)-1]
        dir_name = os.path.join(data_path, fname)
        fh = input("请选择统计内容：\n1：弹幕\n2：礼物\n3：报表\n").strip()
        if fh == "1":
            interval = input("请输入统计间隔，单位为秒，留空则为默认值60：\n").strip()
            if interval == "":
                interval = 60
            else:
                interval = int(interval)
            SC_ratio = input("请输入SC计数比例，即一条SC看作几条弹幕，留空则为默认值1：\n").strip()
            if SC_ratio == "":
                SC_ratio = 1
            else:
                SC_ratio = float(SC_ratio)
            min_UL = input("请输入最低用户等级，低于此等级的普通弹幕将不会被记录，留空则为默认值0：\n").strip()
            if min_UL == "":
                min_UL = 0
            else:
                min_UL = int(min_UL)
            plot_danmu(dir_name, interval=interval,
                       SC_ratio=SC_ratio, min_UL=min_UL)
        elif fh == "2":
            interval = input("请输入统计间隔，单位为秒，留空则为默认值60：\n").strip()
            if interval == "":
                interval = 60
            else:
                interval = int(interval)
            silver_ratio = input(
                "请输入银瓜子比例，即银瓜子按多少比例折为金瓜子，留空则为默认值0，即不计银瓜子礼物：\n").strip()
            if silver_ratio == "":
                silver_ratio = 0
            else:
                silver_ratio = int(silver_ratio)
            plot_gift(dir_name, interval=interval, silver_ratio=silver_ratio)
        elif fh == "3":
            topK = input("请榜单大小，留空则为默认值10：\n").strip()
            if topK == "":
                topK = 10
            else:
                topK = int(topK)
            summary(dir_name,topK = topK)
        else:
            sys.exit(-1)
