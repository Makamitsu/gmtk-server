from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from random import randrange, choice
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
limiter = Limiter(
    app,
    key_func=get_remote_address, # get users IP address.
)

db = SQLAlchemy(app)

class GameContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    contact = db.Column(db.String(100), nullable=False)

    data_dict = db.Column(db.String(500), nullable=False)
    
    ## Results
    next_player_name = db.Column(db.String(50), nullable=True)
    next_player_choice = db.Column(db.Integer, nullable=True)
    over = db.Column(db.Integer, nullable=False, default=False)

    def __repr__(self):
        return f"Player {self.name} with id: {self.id}"

db.create_all()

@app.route('/status')
def status():
    return "OK"

@app.route('/startGame')
#@limiter.limit("1/minute")
def startGame():
    result = GameContent.query.filter_by(over=False).first()

    if result is None:
        results = GameContent.query.limit(10).all()
        print(results)
        result = choice(results)
    print(result)

    return json.dumps({
        "id": result.id,
        "data_dict": result.data_dict
        })

# {
#     "game_content_id": 15,
#     "name": "",
#     "contact": "",
#     "choice": 1,
#     "data_dict": "{'plop': 'blabla'}"
# }

@app.route('/endGame', methods=['POST'])
#@limiter.limit("1/minute")
def endGame():
    update = False
    data = request.get_json()
    previousGameContent = GameContent.query.filter_by(id=data['game_content_id']).first()
    if previousGameContent is not None:
        if not previousGameContent.over:
            previousGameContent.next_player = data['name']
            previousGameContent.next_player_choice = data['choice']
            previousGameContent.over = True
            update = True
            send_result(previousGameContent)

    newGameContent = GameContent(
        name = data['name'],
        contact = data['contact'],
        data_dict = str(data['data_dict'])
        )
    db.session.add(newGameContent)
    db.session.commit()

    return "SUCCESS_UPDATE" if update else "SUCCESS_NO_UPDATE"


def send_result(gameContent):
    #Todo
    pass


def populate():
    newGameContent = GameContent(
        name = "josh",
        contact = "plop",
        data_dict = '{"message1": "Oooh ooh! All you bases are belong to me", "message2": "I will scramble you all!"}'
        )
    db.session.add(newGameContent)
    
    newGameContent = GameContent(
        name = "josh 2",
        contact = "plop 2",
        data_dict = '{"message1": "Oooh ooh! All you bases are belong to me twice", "message2": "I will scramble twice you all!"}'
        )
    db.session.add(newGameContent)

    db.session.commit()

if __name__ == '__main__':
    app.run()