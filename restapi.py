from flask import Flask,jsonify,request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import sessionmaker, relationship, joinedload
from sqlalchemy import func
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_SORT_KEYS'] = False
db = SQLAlchemy(app)
error_msg = {"status" : "failure", "reason": "give a valid input id"}

@app.errorhandler(400)
def error_fun(e):
    return error_msg,400


class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(300),nullable=False)
    description = db.Column(db.String(500),nullable=False)
    

    def __init__(self,name,description):
        self.name = name
        self.description = description
    
    @property
    def serializable(self):
        return {'name': self.name, 'description': self.description}


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(300),nullable=False)
    options = db.Column(db.String(500),nullable=False)
    correct_option = db.Column(db.String(30),nullable=False)
    points = db.Column(db.Integer,nullable=False)
    quiz_id = db.Column(db.Integer,db.ForeignKey('quiz.id'),nullable=False)
    quiz = db.relationship(Quiz,backref='questions')
    def __init__(self,name,options,correct_option,points,quiz):
        self.name=name
        self.options = options
        self.correct_option = correct_option
        self.points = points
        self.quiz_id = quiz

    @property
    def serializable(self):
        return {'id': self.id, 'name': self.name, 'options': self.options, 'correct_option':self.correct_option, 'quiz':self.quiz_id, 'points': self.points}

@app.route('/')
def index_html():
    search = False
    
    page = request.args.get('page', 1, type=int)

    quizes = Quiz.query.paginate(page=1, per_page=5,error_out=False)
    return render_template('index.html', quizes=quizes)
    # return render_template("index.html")

@app.route('/api/quiz/',methods=['POST'])
def index():
    content = request.get_json(silent=True)
    # print('----------------')
    print(type(content))
    # print('----------------')
    print(content.get('name'))
    if(bool(content)):
        #content = request.get_json(silent=True)
        
        try:
            new_quiz = Quiz(content['name'],content['description'])
            db.session.add(new_quiz)
            db.session.commit()
            print('trying to commit', new_quiz.id)
            return {"id":new_quiz.id, 'name':new_quiz.name,'description' : new_quiz.description}, 201
        except:
            return error_msg,400
    else:
        return error_msg,400

@app.route('/api/questions/',methods=['POST'])
def question_ind():
    content = request.get_json(silent=True)
    try:
        new_question = Question(content['name'],content['options'],content['correct_option'],content['points'],int(content['quiz']))
        print(new_question.quiz_id)
        if (len(db.session.query(Quiz).filter(Quiz.id == content['quiz']).all()) > 0): 
            db.session.add(new_question)
            db.session.commit()
            return {"id":new_question.id, 'name':new_question.name,'options' : new_question.options,'correct_option':new_question.correct_option,"quiz":new_question.quiz_id,'points':new_question.points}, 201
        else:
            return error_msg,400
    except Exception as e:
        return error_msg,400

@app.route('/api/questions/<id>',methods=['GET'])
def get_question(id):
    if str(id).isnumeric():
        new_question = db.session.query(Question).filter(Question.id == id).first()
        
        if new_question is not None:
            return {"id":new_question.id, 'name':new_question.name,'options' : new_question.options,'correct_option':new_question.correct_option,"quiz":new_question.quiz_id,'points':new_question.points}, 200
        else:
            return {},404
    else:
        return error_msg,400

@app.route('/api/quiz/<id>',methods=['GET'])
def get_quiz(id):
    if str(id).isnumeric():
        new_quiz = db.session.query(Quiz).filter(Quiz.id == id).first()
        if new_quiz is not None:
            return {"id":new_quiz.id, 'name':new_quiz.name, 'description':new_quiz.description}, 200
        else:
            return {},404
    else:
        return error_msg,400

@app.route('/api/quiz-questions/<id>',methods=['GET'])
def get_quiz_questions(id):
    if str(id).isnumeric():
        quiz = db.session.query(Quiz).options(joinedload(Quiz.questions)).filter(Quiz.id == id).first()
        if quiz is not None:
            # return dict(quiz.serializable,questions=[i.serializable for i in quiz.questions]), 200
            return render_template('/quiz.html',quiz=dict(quiz.serializable,questions=[i.serializable for i in quiz.questions]))
        else:
            return {},404
    else:
        return error_msg,400

if __name__=="__main__":
    db.create_all()
    app.run(host='0.0.0.0',port=8080,debug=True)