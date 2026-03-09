# app/routes/clientes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Cliente
from app.forms import ClienteForm
from sqlalchemy import or_

bp = Blueprint('clientes', __name__, url_prefix='/clientes')

@bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Cliente.query
    
    if search:
        query = query.filter(
            or_(
                Cliente.nombre.ilike(f'%{search}%'),
                Cliente.apellidos.ilike(f'%{search}%'),
                Cliente.identificacion.ilike(f'%{search}%'),
                Cliente.email.ilike(f'%{search}%')
            )
        )
    
    pagination = query.paginate(page=page, per_page=10, error_out=False)
    clientes = pagination.items
    
    return render_template('clientes/listar.html', 
                         clientes=clientes, 
                         pagination=pagination,
                         search=search)

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    form = ClienteForm()
    
    if form.validate_on_submit():
        cliente = Cliente(
            tipo_identificacion=form.tipo_identificacion.data,
            identificacion=form.identificacion.data,
            nombre=form.nombre.data,
            apellidos=form.apellidos.data,
            telefono=form.telefono.data,
            email=form.email.data,
            direccion=form.direccion.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            observaciones=form.observaciones.data,
            creado_por_id=current_user.id
        )
        db.session.add(cliente)
        db.session.commit()
        flash(f'✅ Cliente {cliente.nombre_completo} creado exitosamente!', 'success')
        return redirect(url_for('clientes.listar'))
    
    return render_template('clientes/crear.html', form=form)

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    cliente = Cliente.query.get_or_404(id)
    form = ClienteForm(obj=cliente)
    
    if form.validate_on_submit():
        cliente.tipo_identificacion = form.tipo_identificacion.data
        cliente.identificacion = form.identificacion.data
        cliente.nombre = form.nombre.data
        cliente.apellidos = form.apellidos.data
        cliente.telefono = form.telefono.data
        cliente.email = form.email.data
        cliente.direccion = form.direccion.data
        cliente.fecha_nacimiento = form.fecha_nacimiento.data
        cliente.observaciones = form.observaciones.data
        
        db.session.commit()
        flash(f'✅ Cliente actualizado exitosamente!', 'success')
        return redirect(url_for('clientes.detalle', id=cliente.id))
    
    return render_template('clientes/editar.html', form=form, cliente=cliente)

@bp.route('/<int:id>')
@login_required
def detalle(id):
    cliente = Cliente.query.get_or_404(id)
    ventas = cliente.ventas.limit(10).all()
    return render_template('clientes/detalle.html', cliente=cliente, ventas=ventas)

@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.activo = False
    db.session.commit()
    flash(f'✅ Cliente desactivado exitosamente!', 'success')
    return redirect(url_for('clientes.listar'))

@bp.route('/activar/<int:id>', methods=['POST'])
@login_required
def activar(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.activo = True
    db.session.commit()
    flash(f'✅ Cliente activado exitosamente!', 'success')
    return redirect(url_for('clientes.listar'))

@bp.route('/buscar')
@login_required
def buscar():
    term = request.args.get('q', '')
    if len(term) < 2:
        return jsonify([])
    
    clientes = Cliente.query.filter(
        or_(
            Cliente.nombre.ilike(f'%{term}%'),
            Cliente.apellidos.ilike(f'%{term}%'),
            Cliente.identificacion.ilike(f'%{term}%')
        )
    ).limit(10).all()
    
    results = [{
        'id': c.id,
        'text': f"{c.nombre_completo} - {c.identificacion}",
        'identificacion': c.identificacion
    } for c in clientes]
    
    return jsonify(results)