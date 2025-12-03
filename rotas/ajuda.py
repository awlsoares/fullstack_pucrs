from flask import Blueprint, render_template, request, redirect, url_for, flash

ajuda_bp = Blueprint('ajuda', __name__, url_prefix='/ajuda')

@ajuda_bp.route('/ajuda', methods=['GET',])
def propostas():
    return render_template('ajuda/propostas.html')