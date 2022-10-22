from main import *

if __name__ == '__main__':
    config_path = '.\\config\\config_format.cfg'
    cfg_dict = read_config(config_path)
    app_id = cfg_dict["wechat_cfg"]["app_id"]
    app_secret = cfg_dict["wechat_cfg"]["app_secret"]
    notice_time = cfg_dict["notice_time"]
    test = WeChat_Notice(app_id=app_id, app_secret=app_secret, notice_time=notice_time,config_path=config_path)
    test.read_loc_template_Msg(config_path)
