from db.db import get_db
from flask import Blueprint, request, session, jsonify
from flasgger.utils import swag_from
import psycopg2.extras  # get the results in form of dictionary
import json
import datetime

form_bp = Blueprint('form', __name__)
db = get_db()

# DAO


def replied(student_id):
    # input: User.student_id
    # output: Form.{form_title, form_picture, form_end_date, form_run_state, form_id}
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''SELECT Form.form_title, Form.form_pic_url, Form.form_end_date, Form.form_run_state, Form_form_id
    from UserForm
    JOIN Users on student_id = UserForm.User_student_id
    JOIN Form on form_id = UserForm.Form_form_id
    WHERE Form.form_delete_state='0' AND Users.student_id = %s
    '''
    cursor.execute(query, [student_id])
    db.commit()
    return cursor.fetchall()


def win_lottery_check(form_id, student_id):
    # input: Userform.form_id, student_id
    # output: "未中獎"/"中獎"
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''SELECT *
        FROM gift
        WHERE form_form_id = %s AND user_student_id= %s
        '''
    cursor.execute(query, (form_id, student_id))
    rows = cursor.fetchall()

    if rows != []:
        return "中獎"
    return "未中獎"


def deleteForm(form_id):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''UPDATE Form
    SET form_delete_state = '1'
    WHERE form_id = %s
    '''
    cursor.execute(query, [form_id])
    db.commit()
    return True


def closeForm(form_id):
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = '''UPDATE Form
    SET form_run_state='Closed'
    WHERE form_id = %s
    '''
    cursor.execute(query, [form_id])
    db.commit()
    return True

def created(student_id):
    # input: User.student_id
    # output: Form.{form_id, form_title, form_pic_url, form_create_date, form_end_date, form_run_state}
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        query = """
        SELECT form_id, form_title, form_pic_url, form_create_date, form_end_date, form_run_state
        FROM Form 
        WHERE User_student_id = %s AND form_delete_state = 0;
        """
        cursor.execute(query, [student_id])
        db.commit()
        return cursor.fetchall()
    except:
        db.rollback()
        return 'failed to retrieve form.'
    finally:
        db.close()

def addForm(form_title, questioncontent, form_create_date, form_end_date, student_id, form_pic_url):
    # input: request.get_json[form_title, questioncontent, form_end_date, form_pic_url], session.get(student_id), datetime.now
    # output: 
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try: 
        query = """
        INSERT INTO Form(form_id, form_title, questioncontent, form_create_date, form_end_date, form_run_state, form_delete_state, User_student_id, form_pic_url)
        SELECT MAX(form_id)+1 , %s, %s, %s, %s, 'Open', 0, %s, %s FROM Form;
        """
        cursor.execute(query, [form_title, questioncontent, form_create_date, form_end_date, student_id, form_pic_url])
        db.commit()
        return True
    except:
        db.rollback()
        return False
    finally:
        db.close()

# route


@ form_bp.route('/SurveyManagement', methods=["GET"])
@ swag_from('replier_form_specs.yml', methods=["GET"])
def returnReplierForm():
    # req_json = request.get_json()
    student_id = session.get('student_id')
    # student_id = req_json["student_id"]
    results = replied(student_id)  # list
    response = []
    for result in results:  # result: psycopg2.extras.DictRow
        result_dict = dict(result)
        form_id = result_dict['form_form_id']
        result_dict['winning_status'] = win_lottery_check(form_id, student_id)
        response.append(result_dict)
    return jsonify(response)


@ form_bp.route('/SurveyManagement', methods=["PUT"])
@ swag_from('modify_form_specs.yml', methods=["PUT"])
def modifyForm():
    req_json = request.get_json()
    form_id = req_json["form_id"]
    action = req_json["action"]
    response_return = {
        "status": "",
        "message": ""
    }
    if action == "delete":
        deleteForm(form_id)
        response_return["status"] = "success"
        response_return["message"] = "Deleted form"
    elif action == "close":
        closeForm(form_id)
        response_return["status"] = "success"
        response_return["message"] = "Closed form"
    return jsonify(response_return)

@ form_bp.route('/SurveyManagement/author', methods=['GET'])
def returnAuthorForm():
    # student_id = 'r10725051'  # test data
    student_id = session.get('student_id')
    results = created(student_id)
    return jsonify(results)

@ form_bp.route('/SurveyManagement/new', methods=['GET','POST'])
def createForm(): 
    # form_title = 'addForm測試'  # test data
    # questioncontent = json.dumps([{'測試測試':'我是測試怪'}], ensure_ascii=False)  # test data
    # form_create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # test data
    # form_end_date = datetime.datetime(2022,9,10,23,59,59)  # test data
    # student_id = 'r10725051'  # test data
    # form_pic_url = 'https://imgur.com/gallery/ewCdEP9'  # test data
    req_json = request.get_json(force=True)
    form_title = req_json['form_title'] 
    questioncontent = json.dumps(request.get_json()['questioncontent'], ensure_ascii=False) 
    form_create_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    form_end_date = req_json['form_end_date']
    student_id = session.get('student_id')
    form_pic_url = req_json['form_picture'] 
    response_return = {
        "status":"",
        "message":""
    }
    if addForm(form_title, questioncontent, form_create_date, form_end_date, student_id, form_pic_url):
        response_return["status"] = 'success'
        response_return["message"] = 'Form added.'
    else:
        response_return["status"] = 'fail'
        response_return["message"] = 'Form aborted.'
    return jsonify(response_return)