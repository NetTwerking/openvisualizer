
from flask import Flask, render_template, request
# from STU_Notice import get_stu_notices
import csv
import datetime

from werkzeug.utils import redirect
import time

app = Flask(__name__)

mac_list = ['0x15','0xa1','0x65','0xee','0xe8','0xa4'] # mac list -> 직접 등록 필요
x_label = ["o", "x"] # 문제 입력 없을 시 기본 값

quiz = ["결과입니다"]

# home page #
@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def Show_Clicker():
    return render_template('index.html')

# make a quiz page #
@app.route('/quiz', methods=['GET','POST'])
def Show_Quiz():
    if request.method == 'POST': # form으로 입력 받은 정보 넘겨주기 
        _question = request.form['question']
        _option1 = request.form['option1']
        _option2 = request.form['option2']
        _time = request.form['quiz_time']
        return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2, quiz_time = _time)
    elif request.method == 'GET':
        return render_template('quiz.html')

# show quiz #
@app.route('/start_quiz', methods=['GET','POST'])
def Start_Quiz(): # Show_Quiz()에서 넘겨온 정보 출력
    _question = request.form['question']
    quiz[0] = _question # 결과 페이지 출력에서 사용될 문자열 받아오기
    _option1 = request.form['option1']
    x_label[0] = _option1
    _option2 = request.form['option2']
    x_label[1] = _option2
    _time = request.form['quiz_time']
    now = time.localtime()
    f5 = open('C:/DelayTest/time.txt', 'w') # 퀴즈 시간값 파일 저장으로 넘겨줌 경로 주의
    f5.write("%d" %(now.tm_min*60 + now.tm_sec+int(_time)))
    f5.close()
    return render_template('start_quiz.html', question=_question, option1 = _option1, option2 = _option2, quiz_time = _time)
   
# result page #
@app.route('/results', methods=['GET','POST'])
def Show_Result():
    result_list = []
<<<<<<< HEAD
    for mac in mac_list:
        read_dir = 'C:/DelayTest/' + mac + '.csv'
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
    #x_label = [option_o, option_x]
    colors = ['#0d6efd', '#ff9999']

=======
>>>>>>> 6cea75aade06d4e17f279a1910dc6ede7e8e2421
    o = 0
    x = 0

    # 응답 결과 집계 #
    for mac in mac_list:
        read_dir = 'C:/DelayTest/' + mac + '.csv'
        f = open(read_dir, 'r')
        csv_reader = csv.reader(f)
        for line in csv_reader :
            print(line[1])
            result_list.append([line[0],line[1],line[2]])
            if line[1] == "O":
                o = o+1
            else:
                x = x+1
        f.close()
        
        o_ratio = int(o/(o+x)*100)
        x_ratio = int(x/(o+x)*100)

    # html 넘겨주기 #
    result_list = sorted(result_list, key=lambda result : result[2])
    date = datetime.datetime.now().replace(microsecond=0) # 현재 시간

    # 등수 출력용 임의 코드, 수정 필요 #
    for i in range(0, 6):
        result_list[i].append(str(i+1));

    return render_template('results.html', result_list = result_list, mac_list = mac_list, date = date, o = o_ratio, x = x_ratio,
    question = quiz[0], option1 = x_label[0], option2 = x_label[1]) 


if __name__ == '__main__':
    app.run()
