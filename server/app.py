#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes')
def get_heroes():
    heros = []
    for hero in Hero.query.all():
        hero_dict = hero.to_dict()
        del hero_dict["hero_powers"]
        heros.append(hero_dict)

    response = make_response(
        heros,
        200,
        {"Content-Type": "application/json"}
    )

    return response

@app.route('/heroes/<int:id>')
def get_hero_by_id(id):
    hero = Hero.query.filter(Hero.id == id).first()
    if hero:
        hero_dict = hero.to_dict()
        return make_response(hero_dict, 200)
    else:
        return make_response({"error": "Hero not found"}, 404)  


@app.route('/powers')
def get_powers():
    powers = []
    for power in Power.query.all():
        power_dict = power.to_dict()
        del power_dict["hero_powers"]
        powers.append(power_dict)

    response = make_response(
        powers,
        200,
        {"Content-Type": "application/json"}
    )

    return response

@app.route('/powers/<int:id>')
def get_power_by_id(id):
    power = Power.query.filter(Power.id == id).first()
    if power:
        power_dict = power.to_dict()
        del power_dict['hero_powers'] 
        return make_response(power_dict, 200)
    else:
        return make_response({"error": "Power not found"}, 404)


@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.filter(Power.id == id).first()

    if not power:
        return make_response({"error": "Power not found"}, 404)

    data = request.get_json()
    description = data.get("description")

  
    if not description or len(description) < 20:
        return make_response({"errors": ["validation errors"]}, 400)

   
    power.description = description
    db.session.commit()

    return make_response({
        "id": power.id,
        "name": power.name,
        "description": power.description
    }, 200)


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    strength = data.get("strength")
    power_id = data.get("power_id")
    hero_id = data.get("hero_id")

   
    if strength not in ["Strong", "Weak", "Average"]:
        return make_response({"errors": ["validation errors"]}, 400)

    hero = Hero.query.filter(Hero.id == hero_id).first()
    power = Power.query.filter(Power.id == power_id).first()

    if not hero or not power:
        return make_response({"errors": ["Hero or Power not found"]}, 404)

    
    hero_power = HeroPower(strength=strength, hero_id=hero_id, power_id=power_id)
    db.session.add(hero_power)
    db.session.commit()

    return make_response({
        "id": hero_power.id,
        "hero_id": hero.id,
        "power_id": power.id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
    }, 200)



if __name__ == '__main__':
    app.run(port=5555, debug=True)