from flask import Flask, render_template, url_for
# from STU_Notice import get_stu_notices
import csv
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def Show_Clicker():
    import ParserData
    COUNT = ParserData.ParserData.COUNT
    return render_template('index.html', count = COUNT)

@app.route('/quiz', methods=['GET','POST'])
def Show_Quiz():
    #f = open('C:\DelayTest\clicker.csv', 'r')
    #rdr = csv.reader(f)
    #data = []
    #for i in rdr:
        #data.append(i)

    return render_template('quiz.html')

@app.route('/results', methods=['GET','POST'])
def Show_Result():
    #f = open('C:\DelayTest\clicker.csv', 'r')
    #rdr = csv.reader(f)
    #data = []
    #for i in rdr:
        #data.append(i)

    return render_template('results.html') 

if __name__ == '__main__':
    app.run()