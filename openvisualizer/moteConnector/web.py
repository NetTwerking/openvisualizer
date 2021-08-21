from flask import Flask, render_template, url_for, request
# from STU_Notice import get_stu_notices
import csv

from werkzeug.utils import redirect
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
        return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2)
    elif request.method == 'GET':
        return render_template('quiz.html')

@app.route('/start_quiz', methods=['GET','POST'])
def Start_Quiz():
    _question = request.form['question']
    _option1 = request.form['option1']
    _option2 = request.form['option2']
    return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2)
   
@app.route('/results', methods=['GET','POST'])
def Show_Result():
    result_list = {}
    for mac in mac_list:
        read_dir = 'C:\\DelayTest\\' + mac + '.csv'
        f = open(read_dir, 'r')
        csv_reader = csv.reader(f)
        for line in csv_reader :
            print(line[1])
            result_list[mac] = line[1]
        f.close()
    return render_template('results.html', result_list = result_list, mac_list = mac_list) 

if __name__ == '__main__':
    app.run()