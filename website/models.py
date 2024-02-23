from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))

class Calendario(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    oremattina = db.Column(db.String(5))
    orepomeriggio = db.Column(db.String(5))
    numeroslot = db.Column(db.Integer)
    sloteliminati = db.Column(db.String(150))
    allievo = db.relationship("Allievo", backref='calendario', uselist = True)

class Allievo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nome = db.Column(db.String(150))
    cognome = db.Column(db.String(150))
    giornonascita = db.Column(db.Integer)
    mesenascita = db.Column(db.Integer)
    annonascita = db.Column(db.Integer)
    livello = db.Column(db.String(150))
    numeroallenamenti = db.Column(db.Integer)
    id_calendario = db.Column(db.Integer, db.ForeignKey('calendario.id'))