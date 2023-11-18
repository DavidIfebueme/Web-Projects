from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

# application instance that receives client requests
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polling.db' # TO be updated with the actual postgres db link
db = SQLAlchemy(app)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    options = db.relationship('Option', backref='poll', lazy=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Poll('{self.title}', '{self.start_date}', '{self.end_date}')"

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    option_index = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Vote('{self.poll_id}', '{self.option_index}', '{self.user_id}')"

@app.route("/")
def index():
    return jsonify({'message': 'Welcome to the Polling App'}), 200

@app.route('/create_poll', methods=['POST'])
def create_poll():
    data = request.get_json()

    # validate and sanitize form data
    if not data['title']:
        return jsonify({'message': 'Title cannot be empty'}), 400
    if not data['start_date']:
        return jsonify({'message': 'Start date cannot be empty'}), 400
    if not data['end_date']:
        return jsonify({'message': 'End date cannot be empty'}), 400
    if data['start_date'] > data['end_date']:
        return jsonify({'message': 'Start date cannot be greater than end date'}), 400
    elif data['start_date'] == data['end_date']:
        return jsonify({'message': 'Start date cannot be equal to end date'}), 400
    else:
        pass        

    poll = Poll(title=data['title'], start_date=data['start_date'], end_date=data['end_date'])
    db.session.add(poll)
    db.session.commit()

    return jsonify({'message': 'Poll created successfully'}), 201

@app.route('/vote/<int:poll_id>/int:option_index', methods=['POST'])
def vote(poll_id, option_index):
    poll = Poll.query.get_or_404(poll_id)
    if option_index < 0 or option_index >= len(poll.options):
        return jsonify({'error': 'Invalid option index'}), 400
    
    user_id = request.args.get('user_id')
    existing_vote = Vote.query.filter_by(poll_id=poll_id, user_id=user_id).first()
    if existing_vote:
        return jsonify({'error': 'You have already voted'}), 400

    new_vote = Vote(poll_id=poll_id, option_index=option_index, user_id=user_id) 
    db.session.add(new_vote)
    db.session.commit()

    return jsonify({'message': 'Vote submitted successfully'}), 201   


if __name__ == '__main__':
    app.run(debug=True)   