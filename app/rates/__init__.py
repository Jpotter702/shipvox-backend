from flask import Blueprint

bp = Blueprint('rates', __name__)

from app.rates import routes