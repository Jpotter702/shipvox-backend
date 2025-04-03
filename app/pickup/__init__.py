from flask import Blueprint

bp = Blueprint('pickup', __name__)

from app.pickup import routes