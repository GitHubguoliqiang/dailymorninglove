from main import *
import datetime
import json
import random
import threading
import time
import os.path
from Tools import *
import requests


class WeChat_Notice:
                 # 传入 app_id, app_secret, 配置文件的路径, 每日定时提醒时间(列表形式,多个时间都会提醒) , token_path存放access_token的文件目录
    def __init__(self, app_id, app_secret, config_path, notice_time:list=None, token_path='.\\data\\access_token.json'):
        self.access_token = None
        self.app_id = app_id
        self.app_secret = app_secret
        self.token_path = token_path
        self.save_dir = os.path.dirname(token_path)
        self.read_Loc_token()
        self.config_path = config_path
        # 初始化不同天气给予不同的提醒
        self.weather_chn_dict = {
            "CLEAR_DAY": ["晴（白天）", "今天天气适合晒太阳哦 ^_^ "],
            "CLEAR_NIGHT": ["晴（夜间）", "今天天气阳光正暖哦,又是开心的一天~"],
            "PARTLY_CLOUDY_DAY": ["多云（白天）", "今天多云,可以去锻炼锻炼~"],
            "PARTLY_CLOUDY_NIGHT": ["多云（夜间）", "多云天气，凉风嗖嗖~"],
            "CLOUDY": ["阴", "大阴天也不能影响心情哦~"],
            "LIGHT_HAZE": ["轻度雾霾", "轻度雾霾,注意戴口罩哦~"],
            "MODERATE_HAZE": ["中度雾霾", "雾霾有点重,少外出哦~"],
            "HEAVY_HAZE": ["重度雾霾", "重度霾,还是不要不出啦 -_- ~"],
            "LIGHT_RAIN": ["小雨", "小雨滴滴答答,心里嘻嘻哈哈~"],
            "MODERATE_RAIN": ["中雨", "出门一定要记得带好伞哦~"],
            "HEAVY_RAIN": ["大雨", "这么大的雨,哪里都不要去,哼~"],
            "STORM_RAIN": ["暴雨", "暴雨就在家躺平看风景趴~"],
            "LIGHT_SNOW": ["小雪", "有雪来啦,但是要注意保暖哦~"],
            "MODERATE_SNOW": ["中雪", "这个天气最适合玩雪啦,但是衣服可别忘了加厚哦~~"],
            "HEAVY_SNOW": ["大雪", "下大雪啦,明天可以出去打雪仗~"],
            "DUST": ["浮尘", "不多说啦，今天必须戴好口罩哦!"],
            "SAND": ["沙尘", "沙尘天气,就不要出去当仙人掌咯~"],
            "WIND": ["大风", "北风呼呼哪里来，你也不要想着往哪里去，穿好衣服哦~"],

        }
        if notice_time != None:
            threading.Thread(target=self.clock_Notice, args=(notice_time,)).start()
        print(f'程序已激活,日志文件已经开始保存......')

    # 读取本地是否存放token,如果未存放/过期就重新获取
    def read_Loc_token(self):
        try:
            with open(self.token_path, 'r', encoding='utf-8') as file:
                data = eval(file.read().strip())
                access_token = data["access_token"]
                over_time = data["over_time"]
                now_tsp = int(time.time())
                if over_time - now_tsp < 10:
                    self.read_Token()
                else:
                    self.access_token = access_token
        except Exception as e:
            self.read_Token()

    # 从微信服务端获取access_token的方法
    def read_Token(self):
        try:
            api = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}'
            res = requests.get(api, verify=False, timeout=90)
            print(res.text)
            if res.json()["access_token"]:
                access_token = res.json()["access_token"]  # access_token
                expires_in = res.json()["expires_in"]  # 有效时间(秒)
                read_time = int(time.time())  # 获取 token 时间戳
                over_time = read_time + expires_in  # access_token过期时间戳
                mkdir(self.save_dir)
                with open(self.token_path, 'w+', encoding='utf-8') as f:
                    f.write(
                        str({"access_token": access_token, "over_time": over_time, "read_time": read_time}).replace("'",
                                                                                                                    '"'))
                self.access_token = access_token
                print(f'获取Access_token成功\nAccess_token:{access_token}\n有效时间:{expires_in}')
            else:
                print(f'获取Access_token失败\n原因:{res.json()["errmsg"]}')
            return res.json()

        except Exception as e:
            print(f'更新AccessToken错误,原因{e},请检查配置文件的appid/app_secret')

    # 发送天气信息
    def template_Msg(self, open_id, template_id, user_name, user_nickname, together_time, address, longitude,
                     dailysteps,
                     caiyun_token, my_name, other_notice,birthday, font_color):
        name_list = [user_name, user_nickname]
        user_name = random.choice(name_list)
        while True:
            tog_days = read_time_dif(together_time)
            weather_inf = read_weather(caiyun_token, longitude, dailysteps)
            if weather_inf["status"] != "ok":
                return False
            data = weather_inf["result"]["daily"]
            weather = data["skycon_08h_20h"][0]["value"]
            weather = self.weather_chn_dict[weather]
            max_tem = data["temperature"][0]["max"]
            min_tem = data["temperature"][0]["min"]
            avg_tem = data["temperature"][0]["avg"]
            air_quality = data["air_quality"]["aqi"][0]["avg"]["chn"]
            wind = data["wind_08h_20h"][0]["avg"]["speed"]
            visibility = data["visibility"][0]["avg"]
            now_hour = time.localtime(time.time()).tm_hour
            if 5 <= now_hour < 11:
                say = '早上好~'
            elif 11 <= now_hour < 14:
                say = '中午好~'
            elif 14 <= now_hour < 19:
                say = '下午好~'
            else:
                say = '晚上好~'

            try:
                msg = {

                    "touser": open_id,
                    "template_id": template_id,
                    "url": f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}",

                    "topcolor": font_color[0],

                    "data": {

                        "name": {

                            "value": user_name,

                            "color": font_color[1]

                        },

                        "say": {

                            "value": say,

                            "color": font_color[2]

                        },

                        "time_days": {

                            "value": tog_days["days"],

                            "color": font_color[3]

                        },

                        "time_hours": {

                            "value": tog_days["other_hours"],

                            "color": font_color[3]

                        },

                        "address": {

                            "value": address,

                            "color": font_color[4]

                        },

                        "weather": {

                            "value": weather[0],

                            "color": font_color[5]

                        },

                        "max_tem": {

                            "value": f'{max_tem:.2f}℃',

                            "color": font_color[6]

                        },
                        "min_tem": {

                            "value": f'{min_tem:.2f}℃',

                            "color": font_color[7]

                        },
                        "wind": {

                            "value": f'{wind:.2f}m/s',

                            "color": font_color[8]

                        },
                        "visibility": {

                            "value": f'{visibility:.2f}m',

                            "color": font_color[9]

                        },
                        "air_quality": {

                            "value": air_quality,

                            "color": font_color[10]

                        },
                        "notice": {

                            "value": read_love_msg(),

                            "color": font_color[11]

                        },
                        "my_name": {

                            "value": my_name,

                            "color": font_color[12]

                        },

                        "other": {

                            "value": f'\n{weather[1]}' + other_notice,

                            "color": font_color[13]

                        },
                        "birthday": {

                            "value": read_birthday_time(birthday),

                            "color": font_color[14]

                        }

                    }

                }
                url = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.access_token}'
                res = requests.post(url, json=msg, verify=False, timeout=2)
                if res.status_code != 200:
                    print(f'服务器网络错误，代码:{res.status_code}')
                if res.json()["errcode"] == 0:
                    print(f'推送成功----{datetime.datetime.now()}')
                    save_logging(open_id)
                    return True
                elif res.json()["errcode"] == 40001:
                    print(f'Access_Token失效,正在更新中...')
                    self.read_Token()
                    pass
                else:
                    print(f'推送消息失败:{res.json()["errmsg"]}')

            except Exception as e:
                import traceback

                traceback.print_exc()
                print(e)
                pass

    # 每日定时发送
    def clock_Notice(self, notice_time: list):
        time_list = []
        for time_ in notice_time:
            time_hour, time_min = int(time_.split(':')[0]), int(time_.split(':')[1])
            time_list.append(f'{time_hour}.{time_min}')
        while True:
            timeArray = time.localtime(time.time())
            now_time = f'{int(timeArray.tm_hour)}.{int(timeArray.tm_min)}'
            if now_time in time_list:
                threading.Thread(target=self.read_loc_template_Msg, args=(self.config_path,)).start()
                print('推送中...')
                time.sleep(60)
                self.read_loc_template_Msg(self.config_path)
            else:
                time.sleep(30)
                print(f'当前时间{datetime.datetime.now()},程序运行中,推送配置目录:{self.config_path}......')
                pass

    # 读取本地配置的信息并发送天气信息
    def read_loc_template_Msg(self, config_path):
        cfg_dict = read_config(config_path)
        user_inf = cfg_dict['user_inf']
        font_color = cfg_dict['font_color']
        user_inf_list = [value for key, value in user_inf.items()]
        font_color_list = [value for key, value in font_color.items()]
        self.template_Msg(*user_inf_list, font_color_list)


def main(config_path):
    cfg_dict = read_config(config_path)
    app_id = cfg_dict["wechat_cfg"]["app_id"]
    app_secret = cfg_dict["wechat_cfg"]["app_secret"]
    open_id = cfg_dict["user_inf"]["open_id"]
    notice_time = cfg_dict["notice_time"]
    WeChat_Notice(app_id=app_id, app_secret=app_secret, notice_time=notice_time, config_path=config_path)


if __name__ == '__main__':
    # 获取配置文件夹中的配置
    # 如果多个配置，就运行多个线程(海王专属)
    path_list = get_all_file('.\\config')
    for path in path_list:
        threading.Thread(target=main, args=(path,)).start()

