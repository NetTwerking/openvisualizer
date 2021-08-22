from flask import Flask, render_template, url_for, request
# from STU_Notice import get_stu_notices
import csv

from werkzeug.utils import redirect
import time

app = Flask(__name__)

mac_list = ['0x15']

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
    f5 = open('C:/DelayTest/time.txt', 'w')
    f5.write("%d" %(now.tm_min*60 + now.tm_sec+int(_time)))
    f5.close()
    return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2, quiz_time = _time)
   
@app.route('/results', methods=['GET','POST'])
def Show_Result():
    result_list = []
    for mac in mac_list:
        read_dir = 'C:\\DelayTest\\' + mac + '.csv'
        f = open(read_dir, 'r')
        csv_reader = csv.reader(f)
        for line in csv_reader :
            print(line[1])
            result_list.append([line[0],line[1],line[2]])
        f.close()

    result_list = sorted(result_list, key=lambda result : result[2])

    return render_template('results.html', result_list = result_list, mac_list = mac_list) 



if __name__ == '__main__':
    app.run()