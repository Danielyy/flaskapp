from flask import Flask, flash, url_for
from flask import render_template
from flask import request, redirect
from wtforms import Form, validators, StringField, HiddenField, SubmitField, DateField
from flask_bootstrap import Bootstrap
import re
import datetime
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)
project_dir = os.path.abspath(os.path.dirname(__file__))
aiqiyi_key_store = os.path.join(project_dir, 'data/aiqiyi_key')
aiqiyi_log_store = os.path.join(project_dir, 'data/aiqiyi_log')
baidu_key_store = os.path.join(project_dir, 'data/baidu_key')
baidu_log_store = os.path.join(project_dir, 'data/baidu_log')
reg_key = r'^([A-Z0-9]{4}-){3}[A-Z0-9]{4}$'


class GetKey(Form):
    hidden_tag = HiddenField()
    date = DateField('选择兑换日期', [validators.DataRequired()])
    user = StringField('输入领取账户', [validators.DataRequired(), validators.Email()])
    submit = SubmitField('领取兑换码')


# 打开兑换码文件
def openfile(file):
    with open(file, 'r') as f:
        key_list = f.readlines()
    return key_list


# 更新兑换码文件
def writefile(file, update):
    with open(file, 'w') as f:
        f.writelines(update)
    return


# 保持领取日志
def logfile(file, value):
    with open(file, 'a') as f:
        f.write(value)
    return


# 读出还未使用的兑换码，兑换码末尾“0”的表示未使用，“1”表示已经使用
def read_no_used_key(key_list):
    keys = []
    for line in key_list:
        keycode = line.split(':')
        if "1" in keycode[1]:
            pass
        else:
            keys.append(keycode[0])
    return keys


# 读出已经使用过的兑换码
# def read_used_key(key_list):
#     keys = []
#     for line in key_list:
#         keycode = line.split(':')
#         if "0" in keycode[1]:
#             pass
#         else:
#             keys.append(keycode[0])
#     return keys


# 领取兑换码，把未使用兑换码改变成已使用
def set_key_used(key_list, inkey):
    for i in range(len(key_list)):
        re_match = re.match(inkey, key_list[i])
        if re_match:
            usekey = list(key_list[i].rstrip('\n'))
            usekey[len(usekey) - 1] = '1'
            key_list[i] = ''.join(usekey) + '\n'
        else:
            pass
    return key_list


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<activity>', methods=['GET', 'POST'])
def getkey(activity):
    if activity == 'aiqiyi':
        key_file = openfile(aiqiyi_key_store)
        update_file = aiqiyi_key_store
        log_file = aiqiyi_log_store
        activity_name = '爱奇艺兑换码领取'
    if activity == 'baidu':
        key_file = openfile(baidu_key_store)
        update_file = baidu_key_store
        log_file = baidu_log_store
        activity_name = '百度网盘兑换码领取'
    form = GetKey(request.form)
    numbers = len(read_no_used_key(key_file))
    form.date.data = datetime.date.today()
    if request.method == 'POST' and form.validate():
        get_date = form.date.data
        get_user = form.user.data
        try:
            get_key = re.match(reg_key, read_no_used_key(key_file).pop()).group()
            flash("本次领取的兑换码是：" + get_key)
            update_key = set_key_used(key_file, get_key)
            writefile(update_file, update_key)
            # 记录领取日志
            logs = get_key + "::" + get_date.strftime("%Y/%m/%d") + "::" + get_user + '\n'
            logfile(log_file, logs)
        except IndexError:
            flash("所有兑换码已经全部领取完成！")
        return redirect(url_for('getkey', activity=activity))
    return render_template('getkey.html', form=form, numbers=numbers, activity_name=activity_name)


if __name__ == '__main__':
    app.debug = True
    app.secret_key = '123456'
    app.run(host='0.0.0.0')
