from unittest import result
from db.db import get_db
from flask import request, jsonify, Blueprint
import random

lottery_bp = Blueprint('lottery', __name__)
db = get_db()

def getCandidateByFormId(form_id):
    cursor = db.cursor()
    query = '''
    SELECT user_student_id
    from userform
    WHERE form_form_id = (%s);
    '''
    cursor.execute(query, [form_id])
    db.commit()

    result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return result

def getGiftAmountByFormId(form_id):
    cursor = db.cursor()
    query = '''
    SELECT  gift_name, COUNT(gift_name), gift_pic_url
    from gift
    WHERE form_form_id = (%s)
    GROUP BY gift_name, gift_pic_url;
    '''
    cursor.execute(query, [form_id])
    db.commit()

    result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return result

def getGiftDetailByFormId(form_id):
    cursor = db.cursor()
    query = '''
    SELECT gift_name, number
    FROM gift
    WHERE form_form_id = (%s);
    '''
    cursor.execute(query, [form_id])
    db.commit()

    result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return result

def getFormRunStatueByFormId(form_id):
    cursor = db.cursor()
    query = '''
    SELECT form_run_state
    FROM form
    WHERE form_id = (%s);
    '''
    cursor.execute(query, [form_id])
    db.commit()

    result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return result

def updateWinner(form_id, student_id, num, gift_name):
    cursor = db.cursor()
    query = '''
    UPDATE gift SET user_student_id = (%s)
    WHERE number = (%s) AND gift_name = (%s) AND form_form_id = (%s);
    '''
    cursor.execute(query, [student_id, num, gift_name, form_id])

    stateQuery = '''
    UPDATE form SET form_run_state = 'Closed'
    WHERE form_id = (%s);
    '''
    cursor.execute(stateQuery, [form_id])
    db.commit()

    # result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return 0

def getUserAvatar(student_id):
    cursor = db.cursor()
    query = '''
    SELECT user_avatar_url
    FROM USERS
    WHERE student_id = (%s); 
    '''
    cursor.execute(query, [student_id])
    db.commit()
    result = cursor.fetchone()[0]

    return result

def getClosedFormResult(form_id):
    cursor = db.cursor()
    query = '''
    SELECT gift.gift_name, gift.number,gift.gift_pic_url, users.student_id, users.user_avatar_url
    from gift join form ON form.form_id = gift.form_form_id 
    JOIN users ON gift.user_student_id = users.student_id
    WHERE form.form_id = (%s) AND form.form_run_state = 'Closed';
    '''
    cursor.execute(query, [form_id])
    db.commit()

    result = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return result

@lottery_bp.route('/GetCandidate', methods=["GET"])
def getCandidate():
    data = request.get_json()
    form_id = data["form_id"]
    results = getCandidateByFormId(form_id)  
    response = {
        "status": "",
        "data": {"candidates": [] },
        "message": "" 
        }

    # check whether the candidate list is empty
    if(len(results) == 0):
        response["status"] = "error"
        response["message"] = "The form does not exist or the number of the repliers is 0 !!!"
    else:
        for i in results:
            response["status"] = "success"
            response["data"]["candidates"].append(i["user_student_id"])
            response["message"] = "Get candidates successfully!!!"

    return jsonify(response)

@lottery_bp.route('/GetGift', methods=["GET"])
def getGift():
    req_json = request.get_json()
    form_id = req_json["form_id"]
    results = getGiftAmountByFormId(form_id)  
    response = {
        "status": "",
        "data": [],
        "message": "" 
        }

    if(len(results) == 0):
        response["status"] = "error"
        response["message"] = "The form does not exist!!!"
    else:
        response["status"] = "success"
        response["message"] = "Get gifts successfully!!!"
        for i in range(len(results)):
            data = {
                "gift_name": results[i]["gift_name"],
                "amount":results[i]["count"],
                "gift_pic_url": results[i]['gift_pic_url']
                }
            response["data"].append(data) 
  
            
    return jsonify(response)

@lottery_bp.route('/AutoLottery', methods=["GET"])
def autoLottery():
    num_of_lottery = 0
    candidate_list = []

    req_json = request.get_json()
    form_id = req_json["form_id"]

    get_gift = getGiftAmountByFormId(form_id)  
    get_candidate = getCandidateByFormId(form_id) 
    get_gift_detail = getGiftDetailByFormId(form_id)
    get_run_state = getFormRunStatueByFormId(form_id)
    response = {
        "status": "",
        "data": {"lottery_results": [] },
        "message": ""
    }
    if(get_run_state == []):
        response["status"] = "error"
        response["message"] = "The form does not exist!!!"
    elif (get_run_state[0]["form_run_state"] == "WaitForDraw"):
        # lottery_list = []
        for i in get_candidate:
            candidate_list.append(i["user_student_id"])


        for i in range(len(get_gift)):
            num_of_lottery += get_gift[i]["count"]

        lottery_list = random.sample(candidate_list, num_of_lottery)
        for i in range(len(get_gift_detail)):
            prize = {
                "gift": get_gift_detail[i]["gift_name"],
                "number": get_gift_detail[i]["number"],
                "winner": lottery_list[i],
                "winner_avatar_url": getUserAvatar(lottery_list[i])
            }
            response["data"]["lottery_results"].append(prize)
            response["status"] = "success"
            response["message"] = "The draw is complete and the result is stored in database!!!"
            updateWinner(form_id, lottery_list[i], get_gift_detail[i]["number"], get_gift_detail[i]["gift_name"])
    else:
        response["status"] = "error"
        if(get_run_state[0]["form_run_state"] == "Closed"):
            response["message"] = "The form has been closed!!!"
        elif(get_run_state[0]["form_run_state"] == "Open"):
            response["message"] = "The form is still open!!!"

    return jsonify(response)

@lottery_bp.route('/GetLotteryResults', methods=["GET"])
def getLotteryResults():
    req_json = request.get_json()
    form_id = req_json["form_id"]
    response = {
        "status": "",
        "data": {'results':[]},
        "message": ""
    }
    form_run_state = getFormRunStatueByFormId(form_id)[0]["form_run_state"]
    if(form_run_state == 'Closed'):
        result = getClosedFormResult(form_id)
        if(len(result) != 0):
            for row in result:
                temp_data = {
                    "gift_name": row["gift_name"],
                    "gift_pic_url":row["gift_pic_url"],
                    "number": row["number"],
                    "student_id": row["student_id"],
                    "user_avatar_url": row["user_avatar_url"]
                }
                response["data"]["results"].append(temp_data)
            response["status"] = "success"
            response["message"] = "Get lottery results successfully!!!"
        else:
            response["status"] = 'error'
            response["message"] = 'You haven\'t entered the lottery yet!!!!!'
    else:
        response["status"] = 'error'
        response["message"] = 'The form is still open.'

    return jsonify(response)
