# app/routes/main.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Medicamento
from datetime import datetime, date, timedelta
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
def index():
    # Fecha actual
    # Contar medicamentos con stock bajo
    stock_bajo = Medicamento.query.filter(Medicamento.stock <= Medicamento.stock_minimo).count()
    
    # Contar medicamentos por vencer (próximos 30 días)
    hoy = datetime.now().date()
    treinta_dias = hoy + timedelta(days=30)
    por_vencer = Medicamento.query.filter(
        Medicamento.fecha_vencimiento.between(hoy, treinta_dias)
    ).count()
    
    return render_template('index.html', 
                         stock_bajo=stock_bajo, 
                         por_vencer=por_vencer,
                         hoy=hoy)  # ← Agregar esto