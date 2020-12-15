import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paging_questions(request, selected_question):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  _questions = [question.format() for question in selected_question]
  curr_questions = _questions[start:end]
  return curr_questions


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)
  
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/categories')
def get_category():
        categories = Category.query.all()
        categories_obj = {}
        for category in categories:
            categories_obj[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categories_obj
        })


@app.route('/questions')
def get_allquestions():
  q = Question.query.all()
  total_of_questions = len(q)
  current_question = paging_questions(request, q)
  categories = Category.query.all()
  categories_obj = {}
  for category in categories:
    categories_obj[category.id] = category.type

  return jsonify({
            'success': True,
            'questions': current_question,
            'total_questions': total_of_questions,
            'categories': categories_obj
        })


@app.route('/questions/<int:id>', methods=['DELETE'])
def delete_question(id):
  try:

            question = Question.query.filter_by(id=id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify({
                'success': True,
                'deleted': id
            })

  except:
    abort(400)


@app.route('/questions', methods=['POST'])
def post_question():
        req=request.get_json()
        if (req.get('searchTerm')):
            search_term=req.get('searchTerm')
            selected_question=Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()

            if (len(selected_question) == 0):
                abort(404)

            result=paging_questions(request, selected_question)
            return jsonify({
                'success': True,
                'questions': result,
                'total_questions': len(Question.query.all())
            })
        else:
            _question=req.get('question')
            _answer=req.get('answer')
            _difficulty=req.get('difficulty')
            _category=req.get('category')

            try:
                question=Question(question=_question, answer=_answer,
                                  difficulty=_difficulty, category=_category)
                question.insert()

                selected_question=Question.query.order_by(Question.id).all()
                current_questions=paging_questions(request, selected_question)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'question_created': question.question,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

            except:
                abort(400)



@app.route('/categories/<int:id>/questions')
def get_questionsbycategory(id):
        _category=Category.query.filter_by(id=id).one_or_none()
        selection=Question.query.filter_by(category=_category.id).all()
        paging=paging_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': paging,
            'total_questions': len(Question.query.all()),
            'current_category': _category.type
        })

@app.route('/quizzes', methods=['POST'])
def get_random_quiz_question():
        req=request.get_json()
        previous_questions=req.get('previous_questions')
        quiz_category=req.get('quiz_category')
        if (quiz_category['id'] == 0):
            previous_questions=Question.query.all()
        else:
            previous_questions=Question.query.filter_by(
                quiz_category=quiz_category['id']).all()

        total_of_questions=len(previous_questions)
        def get_random():
            return previous_questions[random.randrange(0, len(previous_questions), 1)]
        def check_if_used(question):
            Is_used=False
            for q in previous_questions:
                if (q == question.id):
                    Is_used=True

            return Is_used
        question=get_random()

        while (check_if_used(question)):
            question=get_random()
            if (len(previous_questions) == total_of_questions):
                return jsonify({
                    'success': True
                })

        return jsonify({
            'success': True,
            'question': question.format()
        })

@app.errorhandler(404)
def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

@app.errorhandler(400)
def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

return app
