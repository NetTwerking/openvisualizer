from flask import Flask, render_template, url_for, request, send_file
# from STU_Notice import get_stu_notices
import csv
from io import BytesIO
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import matplotlib.pyplot as plt
import datetime

from werkzeug.utils import redirect
import time

app = Flask(__name__)

mac_list = ['0x15','0xa1','0x65','0xee','0xe8','0xa4']

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def Show_Clicker():
    return render_template('index.html')

@app.route('/quiz', methods=['GET','POST'])
def Show_Quiz():
    if request.method == 'POST':
        _question = request.form['question']
        _option1 = request.form['option1']
        _option2 = request.form['option2']
        _time = request.form['quiz_time']
        return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2, quiz_time = _time)
    elif request.method == 'GET':
        return render_template('quiz.html')

@app.route('/start_quiz', methods=['GET','POST'])
def Start_Quiz():
    _question = request.form['question']
    _option1 = request.form['option1']
    _option2 = request.form['option2']
    _time = request.form['quiz_time']
    now = time.localtime()
    f5 = open('/Users/songjihye/Desktop/time.txt', 'w')
    f5.write("%d" %(now.tm_min*60 + now.tm_sec+int(_time)))
    f5.close()
    return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2, quiz_time = _time)
   
@app.route('/results', methods=['GET','POST'])
def Show_Result():
    result_list = []
    for mac in mac_list:
        read_dir = '/Users/songjihye/Desktop/' + mac + '.csv'
        f = open(read_dir, 'r')
        csv_reader = csv.reader(f)
        for line in csv_reader :
            print(line[1])
            result_list.append([line[0],line[1],line[2]])
        f.close()

    result_list = sorted(result_list, key=lambda result : result[2])
    date = datetime.datetime.now().replace(microsecond=0)

    return render_template('results.html', result_list = result_list, mac_list = mac_list, date = date) 

@app.route('/plot')
def plot():
    plt.switch_backend('Agg')

    #통계 내기
    x_data = [1, 2]
    x_label = ['o', 'x']
    colors = ['#0d6efd', '#ff9999']

    o = 0
    x = 0

    for mac in mac_list:
        read_dir = '/Users/songjihye/Desktop/' + mac + '.csv'
        f = open(read_dir, 'r')
        csv_reader = csv.reader(f)
        for line in csv_reader :
            if line[1] == "O":
                o = o+1
            else:
                x = x+1
        f.close()

    y = [o,x]

    # 그림판 준비, 막대 그래프
    fig, axis = plt.subplots(1)

    # 그리기
    #plt.subplot(1,2,1)
    #plt.xticks(x_data,x_label)
    #axis[0].bar(x_data,y,color=colors,width=0.4)
    #axis[0].set_title("Answer List")
    canvas = FigureCanvas(fig)
    
    ratio = []
    ratio.append(int(o/(o+x)*100))
    ratio.append(int(x/(o+x)*100))
    explode = [0.05, 0.05]

    axis.pie(ratio, labels=x_label, colors=colors, explode=explode, shadow=True, autopct='%.1f%%')

    # 그려진 img 파일 내용을 html 랜더링 쪽에 전송한다.
    img = BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


if __name__ == '__main__':
    app.run()

