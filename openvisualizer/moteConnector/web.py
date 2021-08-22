from flask import Flask, render_template, url_for, request
# from STU_Notice import get_stu_notices
import csv

from werkzeug.utils import redirect
app = Flask(__name__)

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
    return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2, quiz_time = _time)
   
@app.route('/results', methods=['GET','POST'])
def Show_Result():
    return render_template('results.html') 

if __name__ == '__main__':
    app.run()