import flask
from flask import Flask, request, jsonify, make_response
from logic_y1 import gui_logic_y1, GUILogicY1
from flask_cors import CORS
# 前端请求入口


app = Flask(__name__)
cors = CORS(app, resources=r"/*", methods=["*"], origins="*")


@app.after_request
def after(response):
    resp = make_response(response)
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp
@app.route('/deduce', methods=['POST'])
def deduce():
    presumptions = request.json['presumptions']
    rule = request.json['rule']
    name_instance = request.json['name_instance']
    gui_logic_y1.logic_api.deduce(presumptions, rule, name_instance)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/instance', methods=['POST'])
def instance():
    conclusion_id = request.json['conclusion_id']
    name_instance = request.json['name_instance']
    gui_logic_y1.logic_api.instance(conclusion_id, name_instance)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/introduce', methods=['POST'])
def introduce():
    conclusion_id = request.json['conclusion_id']
    quantifier = request.json['quantifier']
    free_bound = request.json['free_bound']
    gui_logic_y1.logic_api.introduce(conclusion_id, quantifier, free_bound)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/select', methods=['POST'])
def select():
    conclusion_id = request.json['conclusion_id']
    first = request.json['first']
    last = request.json['last']
    name = request.json['name']
    gui_logic_y1.logic_api.select(conclusion_id, first, last, name)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/use', methods=['POST'])
def use():
    assume_or_axiom = request.json['assume_or_axiom']
    index = request.json['index']
    gui_logic_y1.logic_api.use(assume_or_axiom, index)
    return jsonify(str(gui_logic_y1.logic_api.env.mode))

@app.route('/qed', methods=['POST'])
def qed():
    gui_logic_y1.logic_api.qed()
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/bra', methods=['POST'])
def bra():
    off_on = request.json['off_on']
    conclusion_id = request.json['conclusion_id']
    first = request.json['first']
    last = request.json['last']
    gui_logic_y1.logic_api.bra(off_on, conclusion_id, first, last)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/conclude', methods=['POST'])
def conclude():
    assumption_ids = request.json['assumption_ids']
    gui_logic_y1.logic_api.conclude(assumption_ids)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/eqrepl', methods=['POST'])
def eqrepl():
    equal_id = request.json['equal_id']
    conclusion_id = request.json['conclusion_id']
    first = request.json['first']
    last = request.json['last']
    old_side = request.json['old_side']
    gui_logic_y1.logic_api.eqrepl(equal_id, conclusion_id, first, last, old_side)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/write_line', methods=['POST'])
def write_line():
    expression = request.json['expression']
    gui_logic_y1.logic_api.write(expression)
    return str(gui_logic_y1.logic_api.env.mode)

@app.route('/read', methods=['POST'])
def read():
    items = request.json['items']
    result = gui_logic_y1.logic_api.env.read(*items)
    print(result)
    return jsonify(result)

@app.route('/cp2tp', methods=['POST'])
def cp2tp():
    conclusion_id = request.json['conclusion_id']
    first = request.json['first']
    last = request.json['last']
    text = request.json['text']
    first, last, cfirst, clast = gui_logic_y1.logic_api.char_pos_to_token_pos(conclusion_id, first, last, text)
    return jsonify([first, last, cfirst, clast])

def run():
    app.run()

if __name__ == '__main__':
    app.run(debug=True)