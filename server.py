from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from bson import ObjectId
import nlp_engine
from data import train_clf

app = Flask('__name__')

client = MongoClient()
db = client.test  # Database used
qa_Col = db.QA  # Collections for Questions Answers
log_Col = db.Log  # Collections for logs


@app.route('/')
@app.route('/index')
def user_template():
    return render_template('users.html')


@app.route('/admin')
def admin_template():
    return render_template('admin.html')


@app.route('/log', methods=['POST'])
def start_logging():
    _id = log_Col.insert(
        {
            "name": request.form['name'],
            "date": request.form['date'],
            "Verified": False
        })
    return str(_id)


@app.route('/log/resp', methods=['POST'])
def record_resp():
    log_Col.update({"_id": ObjectId(request.form['_id'])},
                   {"$push": {"convo":
                       {
                           "id": request.form['_id'] + "_" + request.form['id'],
                           "Response": request.form['resp'],
                           "Time": request.form['time'],
                       }}})
    return 'OK'


@app.route('/log/entry', methods=['POST'])
def record_entry():
    log_Col.update({"_id": ObjectId(request.form['_id'])},
                   {"$push": {"convo":
                       {
                           "Entry": request.form['entry'],
                           "Time": request.form['time']
                       }}})
    try:
        confirm_ans = request.form['confirmed']
        response_clf = nlp_engine.classify_response(confirm_ans)
        response = nlp_engine.get_confirmed_response_json(response_clf, confirm_ans)
    except KeyError:
        response = nlp_engine.retrieve_response(request.form['entry'])
    if isinstance(response, tuple):
        return '{} {}'.format(response[0], response[1])
    return response


@app.route('/retrieve')
def retrieve():
    output = []
    for t in log_Col.find():
        output.append({'_id': str(t['_id']), 'name': t['name'], 'date': t['date'], 'Verified': t['Verified']})
    return jsonify({'result': output})


@app.route('/retrieve/convo', methods=['GET'])
def retrieve_convo():
    output = log_Col.find_one({'_id': ObjectId(request.args['_id'])})
    global convo
    global convoid
    convo = output['convo']
    convoid = request.args['_id']
    return jsonify({'result': output['convo']})


@app.route('/retrieve/convo/review', methods=['GET'])
def retrieve_review():
    output = log_Col.find_one({'_id': ObjectId(convoid)})['convo'][int(request.args['number'])]
    response = jsonify({'result': output})
    return response


@app.route('/retrieve/convo/review/info', methods=['POST'])
def set_info():
    log_Col.update_one({
        "_id": ObjectId(request.form['_id']), "convo.id": request.form['convoId']},
        {
            "$set": {
                "Verified": True,
                "convo.$.Label": int(request.form['quality']),
                "convo.$.Explaination": request.form['explain'],
                "convo.$.Classification": request.form['classification'],
                "convo.$.Corpus": request.form.getlist('answer[]'),
                "convo.$.Alternative": request.form.getlist('alternative[]')
            }
        })
    if request.form['classification'] != "Select Classification":
        # nlp_engine.update_training_data(request.form['classification'],request.form['question'],request.form.getlist('answer[]'),request.form.getlist('alternative[]'))
        if request.form.getlist('answer[]') or request.form.getlist('alternative[]'):
            if request.form['classification'] == 'Bot Profile':
                classification = 'botprofile'
            else:
                classification = request.form['classification']
            classification = classification.lower().replace(" ", "")
            nlp_engine.update_training_data(request.form['classification'], request.form['question'],
                                            request.form.getlist('answer[]'), request.form.getlist('alternative[]'))
            # test_nlp.retrain_partial_clf(classification,request.form['question'],request.form.getlist('answer[]'),request.form.getlist('alternative[]'),request.form['quality'])
            train_clf.retrain_clf(classification, request.form['question'])
            nlp_engine.update_classifier()
    return 'ok'


@app.route('/retrieve/corpus', methods=['GET'])
def retrieve_corpus():
    if request.args['classification'] == 'Bot Profile':
        return jsonify(nlp_engine.retrieve_corpus('botprofile'))
    return jsonify(nlp_engine.retrieve_corpus(request.args['classification']))


if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5005)
