# app/routes/ventas.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from app import db
from app.models import Venta, DetalleVenta, Cliente, Medicamento
from app.forms import VentaForm, DetalleVentaForm
from sqlalchemy import or_, func
from datetime import datetime, date

bp = Blueprint('ventas', __name__, url_prefix='/ventas')

# ============================================
# LISTAR VENTAS
# ============================================
@bp.route('/')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    filtro = request.args.get('filtro', 'todas')
    
    query = Venta.query
    
    if search:
        query = query.join(Cliente).filter(
            or_(
                Venta.numero_factura.ilike(f'%{search}%'),
                Cliente.nombre.ilike(f'%{search}%'),
                Cliente.apellidos.ilike(f'%{search}%'),
                Cliente.identificacion.ilike(f'%{search}%')
            )
        )
    
    if filtro == 'hoy':
        hoy = date.today()
        query = query.filter(func.date(Venta.fecha) == hoy)
    elif filtro == 'semana':
        from datetime import timedelta
        semana = date.today() - timedelta(days=7)
        query = query.filter(Venta.fecha >= semana)
    elif filtro == 'mes':
        from datetime import timedelta
        mes = date.today() - timedelta(days=30)
        query = query.filter(Venta.fecha >= mes)
    
    pagination = query.order_by(Venta.fecha.desc()).paginate(page=page, per_page=10, error_out=False)
    ventas = pagination.items
    
    # Estadísticas
    total_ventas_hoy = Venta.query.filter(func.date(Venta.fecha) == date.today()).count()
    monto_ventas_hoy = db.session.query(func.sum(Venta.total)).filter(func.date(Venta.fecha) == date.today()).scalar() or 0
    
    return render_template('ventas/listar.html', 
                         ventas=ventas, 
                         pagination=pagination,
                         search=search,
                         filtro=filtro,
                         total_ventas_hoy=total_ventas_hoy,
                         monto_ventas_hoy=monto_ventas_hoy)

# ============================================
# NUEVA VENTA (CARRITO)
# ============================================
@bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    form = VentaForm()
    
    # Cargar opciones para selects
    form.cliente_id.choices = [(c.id, f"{c.nombre_completo} - {c.identificacion}") 
                               for c in Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()]
    
    # Inicializar carrito en sesión si no existe
    if 'carrito' not in session:
        session['carrito'] = []
    
    if request.method == 'POST':
        if 'agregar_item' in request.form:
            # Procesar agregar item al carrito
            medicamento_id = int(request.form.get('medicamento_id'))
            cantidad = int(request.form.get('cantidad', 1))
            
            medicamento = Medicamento.query.get_or_404(medicamento_id)
            
            if medicamento.stock < cantidad:
                flash(f'❌ Stock insuficiente. Disponible: {medicamento.stock}', 'danger')
            else:
                # Verificar si ya está en el carrito
                encontrado = False
                for item in session['carrito']:
                    if item['medicamento_id'] == medicamento_id:
                        item['cantidad'] += cantidad
                        item['subtotal'] = item['cantidad'] * item['precio']
                        encontrado = True
                        break
                
                if not encontrado:
                    item = {
                        'medicamento_id': medicamento.id,
                        'nombre': medicamento.nombre,
                        'precio': medicamento.precio_venta,
                        'cantidad': cantidad,
                        'subtotal': medicamento.precio_venta * cantidad
                    }
                    session['carrito'].append(item)
                
                session.modified = True
                flash(f'✅ {medicamento.nombre} agregado al carrito', 'success')
        
        elif 'quitar_item' in request.form:
            # Quitar item del carrito
            index = int(request.form.get('item_index'))
            if 0 <= index < len(session['carrito']):
                item = session['carrito'].pop(index)
                session.modified = True
                flash(f'✅ {item["nombre"]} quitado del carrito', 'success')
        
        elif 'vaciar_carrito' in request.form:
            # Vaciar carrito
            session['carrito'] = []
            session.modified = True
            flash('✅ Carrito vaciado', 'success')
        
        elif form.validate_on_submit() and session['carrito']:
            # Procesar venta completa
            try:
                # Crear venta
                venta = Venta(
                    numero_factura=Venta().generar_numero_factura(),
                    cliente_id=form.cliente_id.data,
                    usuario_id=current_user.id,
                    forma_pago=form.forma_pago.data,
                    descuento=form.descuento.data or 0,
                    observaciones=form.observaciones.data
                )
                db.session.add(venta)
                db.session.flush()  # Para obtener el ID
                
                # Procesar items del carrito
                for item in session['carrito']:
                    medicamento = Medicamento.query.get(item['medicamento_id'])
                    
                    # Verificar stock nuevamente
                    if medicamento.stock < item['cantidad']:
                        raise ValueError(f'Stock insuficiente para {medicamento.nombre}')
                    
                    detalle = DetalleVenta(
                        venta_id=venta.id,
                        medicamento_id=item['medicamento_id'],
                        cantidad=item['cantidad'],
                        precio_unitario=item['precio'],
                        subtotal=item['subtotal']
                    )
                    db.session.add(detalle)
                    
                    # Actualizar stock
                    medicamento.stock -= item['cantidad']
                
                # Calcular totales
                venta.calcular_totales()
                
                db.session.commit()
                
                # Limpiar carrito
                session['carrito'] = []
                session.modified = True
                
                flash(f'✅ Venta {venta.numero_factura} procesada exitosamente!', 'success')
                return redirect(url_for('ventas.detalle', id=venta.id))
                
            except Exception as e:
                db.session.rollback()
                flash(f'❌ Error al procesar venta: {str(e)}', 'danger')
    
    # Calcular totales del carrito
    subtotal = sum(item['subtotal'] for item in session['carrito'])
    iva = subtotal * 0.12
    descuento = form.descuento.data if form.descuento.data else 0
    total = subtotal + iva - descuento
    
    return render_template('ventas/nueva.html', 
                         form=form, 
                         carrito=session['carrito'],
                         subtotal=subtotal,
                         iva=iva,
                         total=total)

# ============================================
# DETALLE DE VENTA
# ============================================
@bp.route('/<int:id>')
@login_required
def detalle(id):
    venta = Venta.query.get_or_404(id)
    return render_template('ventas/detalle.html', venta=venta)

# ============================================
# ANULAR VENTA
# ============================================
@bp.route('/anular/<int:id>', methods=['POST'])
@login_required
def anular(id):
    venta = Venta.query.get_or_404(id)
    
    if venta.estado == 'ANULADA':
        flash('❌ Esta venta ya está anulada', 'danger')
        return redirect(url_for('ventas.detalle', id=id))
    
    try:
        # Restaurar stock
        for detalle in venta.detalles:
            medicamento = Medicamento.query.get(detalle.medicamento_id)
            medicamento.stock += detalle.cantidad
        
        venta.estado = 'ANULADA'
        db.session.commit()
        flash(f'✅ Venta {venta.numero_factura} anulada exitosamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'❌ Error al anular venta: {str(e)}', 'danger')
    
    return redirect(url_for('ventas.detalle', id=id))

# ============================================
# BUSCAR PRODUCTOS (AJAX)
# ============================================
@bp.route('/buscar-productos')
@login_required
def buscar_productos():
    term = request.args.get('q', '')
    if len(term) < 2:
        return jsonify([])
    
    medicamentos = Medicamento.query.filter(
        or_(
            Medicamento.nombre.ilike(f'%{term}%'),
            Medicamento.codigo_barras.ilike(f'%{term}%')
        )
    ).filter(Medicamento.stock > 0).limit(10).all()
    
    results = [{
        'id': m.id,
        'text': f"{m.nombre} - Stock: {m.stock} - ${m.precio_venta}",
        'precio': m.precio_venta,
        'stock': m.stock
    } for m in medicamentos]
    
    return jsonify(results)