# app/routes/medicamentos.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models import Medicamento
from app.forms import MedicamentoForm
from datetime import datetime, date, timedelta
from sqlalchemy import or_
# bp = Blueprint('medicamentos', __name__)
bp = Blueprint('medicamentos', __name__, url_prefix='/medicamentos')

# ============================================
# LISTAR MEDICAMENTOS (READ - con filtros y paginación)
# ============================================
@bp.route('/')
@login_required
def listar():
    """Lista todos los medicamentos con filtros y paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    filtro = request.args.get('filtro', 'todos')
    ordenar = request.args.get('ordenar', 'nombre')
    hoy = datetime.now().date()
    # Consulta base
    query = Medicamento.query
    
    # Aplicar búsqueda
    if search:
        query = query.filter(
            or_(
                Medicamento.nombre.ilike(f'%{search}%'),
                Medicamento.nombre_generico.ilike(f'%{search}%'),
                Medicamento.laboratorio.ilike(f'%{search}%'),
                Medicamento.codigo_barras.ilike(f'%{search}%')
            )
        )
    
    # Aplicar filtros
    if filtro == 'stock_bajo':
        query = query.filter(Medicamento.stock <= Medicamento.stock_minimo)
    elif filtro == 'activos':
        query = query.filter(Medicamento.activo == True)
    elif filtro == 'inactivos':
        query = query.filter(Medicamento.activo == False)
    elif filtro == 'receta':
        query = query.filter(Medicamento.requiere_receta == True)
    elif filtro == 'por_vencer':
        # Medicamentos que vencen en los próximos 30 días
        from datetime import date, timedelta
        hoy = date.today()
        treinta_dias = hoy + timedelta(days=30)
        query = query.filter(
            Medicamento.fecha_vencimiento.between(hoy, treinta_dias)
        )
    
    # Aplicar ordenamiento
    if ordenar == 'nombre':
        query = query.order_by(Medicamento.nombre)
    elif ordenar == 'precio':
        query = query.order_by(Medicamento.precio_venta.desc())
    elif ordenar == 'stock':
        query = query.order_by(Medicamento.stock)
    elif ordenar == 'vencimiento':
        query = query.order_by(Medicamento.fecha_vencimiento.nulls_last())
    
    # Paginación
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    medicamentos = pagination.items
    
    # Estadísticas para el dashboard
    total_medicamentos = Medicamento.query.count()
    total_stock = db.session.query(db.func.sum(Medicamento.stock)).scalar() or 0
    valor_inventario = db.session.query(
        db.func.sum(Medicamento.stock * Medicamento.precio_compra)
    ).scalar() or 0
    stock_bajo = Medicamento.query.filter(Medicamento.stock <= Medicamento.stock_minimo).count()
    
    return render_template('medicamentos/listar.html',
                         medicamentos=medicamentos,
                         pagination=pagination,
                         search=search,
                         filtro=filtro,
                         ordenar=ordenar,
                         total_medicamentos=total_medicamentos,
                         total_stock=total_stock,
                         valor_inventario=valor_inventario,
                         stock_bajo=stock_bajo,
                         hoy=hoy)

# ============================================
# VER DETALLE DE MEDICAMENTO (READ - individual)
# ============================================
@bp.route('/<int:id>')
@login_required
def detalle(id):
    """Muestra el detalle de un medicamento específico"""
    medicamento = Medicamento.query.get_or_404(id)
    return render_template('medicamentos/detalle.html', medicamento=medicamento)

# ============================================
# CREAR MEDICAMENTO (CREATE)
# ============================================
# app/routes/medicamentos.py - En la función crear()

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear():
    """Crea un nuevo medicamento"""
    form = MedicamentoForm()
    
    # Cargar opciones para los selects
    from app.models import Categoria, Laboratorio
    form.categoria_id.choices = [(0, 'Seleccione una categoría')] + [(c.id, c.nombre) for c in Categoria.query.filter_by(activo=True).all()]
    form.laboratorio_id.choices = [(0, 'Seleccione un laboratorio')] + [(l.id, l.nombre) for l in Laboratorio.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        medicamento = Medicamento(
            codigo_barras=form.codigo_barras.data,
            nombre=form.nombre.data,
            nombre_generico=form.nombre_generico.data,
            descripcion=form.descripcion.data,
            presentacion=form.presentacion.data,
            concentracion=form.concentracion.data,
            categoria_id=form.categoria_id.data if form.categoria_id.data != 0 else None,
            laboratorio_id=form.laboratorio_id.data if form.laboratorio_id.data != 0 else None,
            precio_compra=form.precio_compra.data,
            precio_venta=form.precio_venta.data,
            stock=form.stock.data,
            stock_minimo=form.stock_minimo.data,
            stock_maximo=form.stock_maximo.data,
            ubicacion=form.ubicacion.data,
            requiere_receta=form.requiere_receta.data,
            fecha_vencimiento=form.fecha_vencimiento.data,
            creado_por_id=current_user.id,
            activo=True
        )
        
        try:
            db.session.add(medicamento)
            db.session.commit()
            flash(f'✅ Medicamento "{medicamento.nombre}" creado exitosamente!', 'success')
            return redirect(url_for('medicamentos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al crear el medicamento: {str(e)}', 'danger')
    
    return render_template('medicamentos/crear.html', form=form, titulo='Nuevo Medicamento')

# ============================================
# EDITAR MEDICAMENTO (UPDATE)
# ============================================
# app/routes/medicamentos.py - En la función editar()

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Edita un medicamento existente"""
    medicamento = Medicamento.query.get_or_404(id)
    form = MedicamentoForm(obj=medicamento)
    
    # Cargar opciones para los selects
    from app.models import Categoria, Laboratorio
    form.categoria_id.choices = [(0, 'Seleccione una categoría')] + [(c.id, c.nombre) for c in Categoria.query.filter_by(activo=True).all()]
    form.laboratorio_id.choices = [(0, 'Seleccione un laboratorio')] + [(l.id, l.nombre) for l in Laboratorio.query.filter_by(activo=True).all()]
    
    if form.validate_on_submit():
        medicamento.codigo_barras = form.codigo_barras.data
        medicamento.nombre = form.nombre.data
        medicamento.nombre_generico = form.nombre_generico.data
        medicamento.descripcion = form.descripcion.data
        medicamento.presentacion = form.presentacion.data
        medicamento.concentracion = form.concentracion.data
        medicamento.categoria_id = form.categoria_id.data if form.categoria_id.data != 0 else None
        medicamento.laboratorio_id = form.laboratorio_id.data if form.laboratorio_id.data != 0 else None
        medicamento.precio_compra = form.precio_compra.data
        medicamento.precio_venta = form.precio_venta.data
        medicamento.stock = form.stock.data
        medicamento.stock_minimo = form.stock_minimo.data
        medicamento.stock_maximo = form.stock_maximo.data
        medicamento.ubicacion = form.ubicacion.data
        medicamento.requiere_receta = form.requiere_receta.data
        medicamento.fecha_vencimiento = form.fecha_vencimiento.data
        medicamento.actualizado_por_id = current_user.id
        medicamento.fecha_actualizacion = datetime.utcnow()
        
        try:
            db.session.commit()
            flash(f'✅ Medicamento "{medicamento.nombre}" actualizado exitosamente!', 'success')
            return redirect(url_for('medicamentos.detalle', id=medicamento.id))
        except Exception as e:
            db.session.rollback()
            flash(f'❌ Error al actualizar el medicamento: {str(e)}', 'danger')
    
    return render_template('medicamentos/editar.html', form=form, medicamento=medicamento)
# ============================================
# ELIMINAR MEDICAMENTO (DELETE - soft delete)
# ============================================
@bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    """Elimina (desactiva) un medicamento"""
    medicamento = Medicamento.query.get_or_404(id)
    
    # Soft delete - solo desactivamos
    medicamento.activo = False
    medicamento.actualizado_por_id = current_user.id
    
    try:
        db.session.commit()
        flash(f'✅ Medicamento "{medicamento.nombre}" desactivado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al desactivar el medicamento: {str(e)}', 'danger')
    
    return redirect(url_for('medicamentos.listar'))

# ============================================
# ACTIVAR MEDICAMENTO (UNDELETE)
# ============================================
@bp.route('/activar/<int:id>', methods=['POST'])
@login_required
def activar(id):
    """Activa un medicamento previamente desactivado"""
    medicamento = Medicamento.query.get_or_404(id)
    
    medicamento.activo = True
    medicamento.actualizado_por_id = current_user.id
    
    try:
        db.session.commit()
        flash(f'✅ Medicamento "{medicamento.nombre}" activado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al activar el medicamento: {str(e)}', 'danger')
    
    return redirect(url_for('medicamentos.listar'))

# ============================================
# ELIMINAR PERMANENTEMENTE (HARD DELETE - solo admin)
# ============================================
@bp.route('/eliminar-permanente/<int:id>', methods=['POST'])
@login_required
def eliminar_permanente(id):
    """Elimina físicamente un medicamento de la BD (solo admin)"""
    # Verificar si el usuario es admin (debes implementar roles)
    if not current_user.email == 'admin@farmacia.com':  # Temporal, implementa roles después
        flash('❌ No tienes permisos para realizar esta acción', 'danger')
        return redirect(url_for('medicamentos.listar'))
    
    medicamento = Medicamento.query.get_or_404(id)
    nombre = medicamento.nombre
    
    try:
        db.session.delete(medicamento)
        db.session.commit()
        flash(f'✅ Medicamento "{nombre}" eliminado permanentemente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al eliminar el medicamento: {str(e)}', 'danger')
    
    return redirect(url_for('medicamentos.listar'))

# ============================================
# AJUSTAR STOCK (INCREMENTAR/DECREMENTAR)
# ============================================
@bp.route('/ajustar-stock/<int:id>', methods=['POST'])
@login_required
def ajustar_stock(id):
    """Ajusta el stock de un medicamento (entrada/salida)"""
    medicamento = Medicamento.query.get_or_404(id)
    
    try:
        cantidad = int(request.form.get('cantidad', 0))
        tipo = request.form.get('tipo', 'entrada')
        motivo = request.form.get('motivo', '')
        
        if tipo == 'entrada':
            medicamento.stock += cantidad
            flash_msg = f'✅ Se agregaron {cantidad} unidades al stock'
        else:  # salida
            if medicamento.stock >= cantidad:
                medicamento.stock -= cantidad
                flash_msg = f'✅ Se retiraron {cantidad} unidades del stock'
            else:
                flash(f'❌ Stock insuficiente. Stock actual: {medicamento.stock}', 'danger')
                return redirect(url_for('medicamentos.detalle', id=id))
        
        medicamento.actualizado_por_id = current_user.id
        db.session.commit()
        flash(flash_msg, 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al ajustar stock: {str(e)}', 'danger')
    
    return redirect(url_for('medicamentos.detalle', id=id))

# ============================================
# BÚSQUEDA RÁPIDA AJAX (para autocompletado)
# ============================================
@bp.route('/buscar')
@login_required
def buscar():
    """API de búsqueda rápida para autocompletado"""
    term = request.args.get('q', '')
    if len(term) < 2:
        return jsonify([])
    
    medicamentos = Medicamento.query.filter(
        or_(
            Medicamento.nombre.ilike(f'%{term}%'),
            Medicamento.codigo_barras.ilike(f'%{term}%')
        )
    ).limit(10).all()
    
    results = [{
        'id': m.id,
        'text': f"{m.nombre} - Stock: {m.stock}",
        'precio': m.precio_venta
    } for m in medicamentos]
    
    return jsonify(results)

# ============================================
# EXPORTAR LISTA (CSV)
# ============================================
@bp.route('/exportar')
@login_required
def exportar():
    """Exporta la lista de medicamentos a CSV"""
    import csv
    from flask import Response
    
    medicamentos = Medicamento.query.all()
    
    # Crear respuesta CSV
    output = []
    output.append(['ID', 'Código Barras', 'Nombre', 'Laboratorio', 
                   'Stock', 'Precio Compra', 'Precio Venta', 'Requiere Receta'])
    
    for m in medicamentos:
        output.append([
            m.id, m.codigo_barras, m.nombre, m.laboratorio,
            m.stock, m.precio_compra, m.precio_venta, 
            'Sí' if m.requiere_receta else 'No'
        ])
    
    # Crear respuesta
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerows(output)
    
    response = Response(si.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=medicamentos.csv'
    return response