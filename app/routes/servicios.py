from flask import Blueprint, request, jsonify, session
from app import db
from app.models import Usuario, rolEnum ##importamos la clase Usuario


