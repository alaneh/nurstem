from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.secret_key = "clave_secreta_nurstem"

# --- CONFIGURACIÓN DE BASE DE DATOS (PostgreSQL) ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/nurstem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS ---
class RolEnfermeria(db.Model):
    __tablename__ = 'rolenfermeria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nivel_autoridad = db.Column('nivelautoridad', db.String(50))
    enfermeros = db.relationship('Enfermero', backref='rol', lazy=True)

class Enfermero(db.Model):
    __tablename__ = 'enfermero'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    rol_enfermeria_id = db.Column(db.Integer, db.ForeignKey('rolenfermeria.id'))

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer, default=10) # Default para evitar division por cero
    pacientes = db.relationship('Paciente', backref='area', lazy=True)

class Medico(db.Model):
    __tablename__ = 'medico'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    especialidad = db.Column(db.String(100))
    pacientes = db.relationship('Paciente', backref='medico', lazy=True)

class Paciente(db.Model):
    __tablename__ = 'paciente'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    fecha_nacimiento = db.Column('fechanacimiento', db.Date)
    genero = db.Column(db.String(50))
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    medico_id = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)

# Nuevos Modelos para Inventario (Simplificados para el Dashboard)
class InventarioFarmacia(db.Model):
    __tablename__ = 'inventariofarmacia'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # Mapeo exacto a las columnas de tu BD (que están en minúsculas en Postgres)
    fecha_actualizacion = db.Column('fechaactualizacion', db.DateTime, default=datetime.utcnow)
    capacidad_almacenamiento = db.Column('capacidadalmacenamiento', db.Integer)
    
    # Relación con Área (puede ser null si es el Almacén Central)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)
    
    # Relaciones ORM
    medicamentos = db.relationship('Medicamento', backref='ubicacion', lazy=True)
    area = db.relationship('Area', backref='inventario')
class Medicamento(db.Model):
    __tablename__ = 'medicamento'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True) # Ej: MED-001
    nombre = db.Column(db.String(150), nullable=False)
    tipo = db.Column(db.String(50)) # 'Medicamento', 'Material', 'Solucion'
    presentacion = db.Column(db.String(100)) # Ej: Caja 20 tabs
    stock = db.Column(db.Integer, default=0)
    lote = db.Column(db.String(100))
    fecha_caducidad = db.Column(db.Date)
    punto_reorden = db.Column(db.Integer, default=10) # Nivel para alerta
    
    inventario_id = db.Column(db.Integer, db.ForeignKey('inventariofarmacia.id'))

#Asignaciones (modulo 4)
class Turno(db.Model):
    __tablename__ = 'turno'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # --- CORRECCIÓN BASADA EN TU BASE DE DATOS ---
    # Eliminamos 'horario' y agregamos las columnas reales que tienes en la imagen
    fecha = db.Column(db.Date)
    tipoturno = db.Column(db.String(50)) 

    # NOTA: Como tu tabla tiene 'tipoturno' y 'fecha', 
    # es probable que tu base de datos considere un 'Turno' como algo específico de un día.

class Asignacion(db.Model):
    __tablename__ = 'asignacion'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    
    # Relaciones
    enfermero_id = db.Column(db.Integer, db.ForeignKey('enfermero.id'), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    turno_id = db.Column(db.Integer, db.ForeignKey('turno.id'), nullable=False)
    
    # Objetos para acceder a los datos (Jinja2)
    enfermero = db.relationship('Enfermero', backref='asignaciones')
    area = db.relationship('Area', backref='asignaciones')
    turno = db.relationship('Turno')
    
class Curso(db.Model):
    __tablename__ = 'curso'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    tipo = db.Column(db.String(50)) # 'Clínico', 'Humanización', 'Normativa'
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    cupo_max = db.Column(db.Integer, default=20)
    
    # Relación con inscripciones
    inscripciones = db.relationship('Inscripcion', backref='curso', lazy=True)

class Inscripcion(db.Model):
    __tablename__ = 'inscripcion'
    id = db.Column(db.Integer, primary_key=True)
    fecha_inscripcion = db.Column(db.Date, default=datetime.utcnow)
    calificacion = db.Column(db.Float, default=0.0)
    progreso = db.Column(db.Integer, default=0) # 0 a 100%
    estado = db.Column(db.String(20), default='Inscrito') # Inscrito, Completado, Aprobado
    
    enfermero_id = db.Column(db.Integer, db.ForeignKey('enfermero.id'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    
    # Relaciones para acceder a los datos
    enfermero = db.relationship('Enfermero', backref='cursos_inscritos')
    

### MODULOS DE USUARIO ###
class Triage(db.Model):
    __tablename__ = 'triage'
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.now)
    motivo_consulta = db.Column(db.Text)
    
    # Signos Vitales
    frecuencia_cardiaca = db.Column(db.Integer)
    saturacion_oxigeno = db.Column(db.Integer)
    temperatura = db.Column(db.Float)
    tension_arterial = db.Column(db.String(20))
    escala_dolor = db.Column(db.Integer)
    glucosa = db.Column(db.Integer)
    
    # Clasificación (1=Rojo, 2=Naranja, 3=Amarillo, 4=Verde, 5=Azul)
    nivel_urgencia = db.Column(db.Integer)
    
    # Relación
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    paciente = db.relationship('Paciente', backref='triages')

# --- MODELOS HOJA DE ENFERMERÍA ---

class HojaEnfermeria(db.Model):
    __tablename__ = 'hoja_enfermeria'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'))
    enfermero_id = db.Column(db.Integer, db.ForeignKey('enfermero.id'))
    
    # Relaciones
    vitales = db.relationship('RegistroVitales', backref='hoja', lazy=True)
    notas = db.relationship('NotaEnfermeria', backref='hoja', lazy=True)
    medicamentos_admin = db.relationship('AdministracionMedicamento', backref='hoja', lazy=True)

class RegistroVitales(db.Model):
    __tablename__ = 'registro_vitales'
    id = db.Column(db.Integer, primary_key=True)
    hora = db.Column(db.Time, nullable=False)
    ta_sistolica = db.Column(db.Integer)
    ta_diastolica = db.Column(db.Integer)
    frecuencia_cardiaca = db.Column(db.Integer)
    frecuencia_respiratoria = db.Column(db.Integer)
    temperatura = db.Column(db.Float)
    saturacion = db.Column(db.Integer)
    hoja_id = db.Column(db.Integer, db.ForeignKey('hoja_enfermeria.id'))

class NotaEnfermeria(db.Model):
    __tablename__ = 'nota_enfermeria'
    id = db.Column(db.Integer, primary_key=True)
    hora = db.Column(db.Time, nullable=False)
    nota = db.Column(db.Text, nullable=False)
    tipo = db.Column(db.String(50))
    hoja_id = db.Column(db.Integer, db.ForeignKey('hoja_enfermeria.id'))

class AdministracionMedicamento(db.Model):
    __tablename__ = 'administracion_medicamento'
    id = db.Column(db.Integer, primary_key=True)
    hora = db.Column(db.Time, nullable=False)
    medicamento_nombre = db.Column(db.String(150))
    dosis = db.Column(db.String(100))
    via = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    hoja_id = db.Column(db.Integer, db.ForeignKey('hoja_enfermeria.id'))

class HistorialConsumo(db.Model):
    __tablename__ = 'historial_consumo' # Coincide con tu tabla SQL
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.now)
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(100))
    
    # Claves foráneas (Foreign Keys)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamento.id'))
    enfermero_id = db.Column(db.Integer, db.ForeignKey('enfermero.id'))
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=True)
    
    # Relaciones (Para poder usar .producto, .enfermero en el HTML)
    producto = db.relationship('Medicamento', backref='consumos')
    enfermero = db.relationship('Enfermero', backref='consumos')
    paciente = db.relationship('Paciente', backref='consumos')










# --- RUTAS ---

@app.route('/')
def index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_dashboard')
def admin_dashboard():
    try:
        # 1. KPIs Generales
        total_pacientes = Paciente.query.count()
        total_enfermeros = Enfermero.query.filter_by(activo=True).count()
        
        # Urgencias: Contamos pacientes en área que contenga "Urgencia" en el nombre
        urgencias_count = Paciente.query.join(Area).filter(Area.nombre.ilike('%Urgencia%')).count()

        # Alertas de Stock (Medicamentos con menos de 10 unidades)
        alertas_stock = Medicamento.query.filter(Medicamento.stock < 15).all()
        count_alertas = len(alertas_stock)

        # 2. Datos de Ocupación por Área
        areas = Area.query.all()
        ocupacion_data = []
        
        for area in areas:
            # Cuántos pacientes hay en esta área
            pacientes_en_area = Paciente.query.filter_by(area_id=area.id).count()
            # Porcentaje
            porcentaje = 0
            if area.capacidad and area.capacidad > 0:
                porcentaje = int((pacientes_en_area / area.capacidad) * 100)
            
            # Color de la barra según saturación
            color_class = "fill-success" # Verde
            if porcentaje > 50: color_class = "fill-warning" # Amarillo
            if porcentaje > 80: color_class = "fill-danger"  # Rojo

            ocupacion_data.append({
                "nombre": area.nombre,
                "pacientes": pacientes_en_area,
                "capacidad": area.capacidad,
                "porcentaje": porcentaje,
                "color": color_class
            })

        # 3. Últimos Ingresos (Limitado a 5)
        ultimos_pacientes = Paciente.query.order_by(Paciente.id.desc()).limit(5).all()

        return render_template('admin_dashboard.html',
                               total_pacientes=total_pacientes,
                               total_enfermeros=total_enfermeros,
                               urgencias_count=urgencias_count,
                               count_alertas=count_alertas,
                               alertas_list=alertas_stock, # Pasamos la lista para mostrar detalle
                               ocupacion_data=ocupacion_data,
                               ultimos_pacientes=ultimos_pacientes,
                               fecha_actual=datetime.now().strftime("%d %B %Y"))

    except Exception as e:
        return f"<h3>Error en Dashboard:</h3> <p>{e}</p>"

#Rutas de personal

@app.route('/admin_personal')
def admin_personal():
    try:
        # Consultamos datos reales
        enfermeros = Enfermero.query.all()
        roles = RolEnfermeria.query.all()
        return render_template('admin_personal.html', enfermeros=enfermeros, roles=roles)
    except Exception as e:
        return f"<h2 style='color:red'>Error de Conexión a BD:</h2><p>{e}</p><p>Asegúrate de haber ejecutado el archivo nurstem.sql en tu base de datos primero.</p>"

@app.route('/guardar_enfermero', methods=['POST'])
def guardar_enfermero():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            apellidos = request.form['apellidos']
            telefono = request.form['telefono']
            direccion = request.form['direccion']
            rol_id = request.form['rol_id']
            
            nuevo_enfermero = Enfermero(
                nombre=nombre,
                apellidos=apellidos,
                telefono=telefono,
                direccion=direccion,
                rol_enfermeria_id=rol_id,
                activo=True
            )
            
            db.session.add(nuevo_enfermero)
            db.session.commit()
            flash('Personal registrado correctamente')
        except Exception as e:
            db.session.rollback() # Importante en Postgres si hay error
            flash(f'Error al guardar: {str(e)}')
            
        return redirect(url_for('admin_personal'))

@app.route('/baja_enfermero/<int:id>')
def baja_enfermero(id):
    try:
        enfermero = Enfermero.query.get_or_404(id)
        enfermero.activo = False
        db.session.commit()
        flash('El personal ha sido dado de baja.')
    except Exception as e:
        flash(f'Error al dar de baja: {str(e)}')
        
    return redirect(url_for('admin_personal'))

@app.route('/actualizar_enfermero', methods=['POST'])
def actualizar_enfermero():
    if request.method == 'POST':
        try:
            # Obtenemos el ID del campo oculto
            enfermero_id = request.form['id']
            
            # Buscamos al enfermero en la BD
            enfermero = Enfermero.query.get_or_404(enfermero_id)
            
            # Actualizamos sus datos con lo que viene del formulario
            enfermero.nombre = request.form['nombre']
            enfermero.apellidos = request.form['apellidos']
            enfermero.telefono = request.form['telefono']
            enfermero.direccion = request.form['direccion']
            enfermero.rol_enfermeria_id = request.form['rol_id']
            
            # Guardamos cambios
            db.session.commit()
            flash('Datos actualizados correctamente')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}')
            
        return redirect(url_for('admin_personal'))

@app.route('/admin_pacientes')
def admin_pacientes():
    pacientes = Paciente.query.all()
    areas = Area.query.all()
    medicos = Medico.query.all()
    return render_template('admin_pacientes.html', pacientes=pacientes, areas=areas, medicos=medicos)

@app.route('/guardar_paciente', methods=['POST'])
def guardar_paciente():
    if request.method == 'POST':
        try:
            # Convertir fecha de string (HTML) a objeto date (Python)
            fecha_str = request.form['fechaNacimiento']
            fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
            
            # Manejo de IDs vacíos (si no se selecciona área o médico)
            area_id = request.form['area_id'] if request.form['area_id'] else None
            medico_id = request.form['medico_id'] if request.form['medico_id'] else None

            nuevo_paciente = Paciente(
                nombre=request.form['nombre'],
                apellidos=request.form['apellidos'],
                fecha_nacimiento=fecha_obj,
                genero=request.form['genero'],
                telefono=request.form['telefono'],
                direccion=request.form['direccion'],
                area_id=area_id,
                medico_id=medico_id
            )
            
            db.session.add(nuevo_paciente)
            db.session.commit()
            flash('Paciente registrado correctamente')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar paciente: {str(e)}')
            
        return redirect(url_for('admin_pacientes'))

@app.route('/actualizar_paciente', methods=['POST'])
def actualizar_paciente():
    if request.method == 'POST':
        try:
            paciente_id = request.form['id']
            paciente = Paciente.query.get_or_404(paciente_id)
            
            # Actualizar campos básicos
            paciente.nombre = request.form['nombre']
            paciente.apellidos = request.form['apellidos']
            paciente.genero = request.form['genero']
            paciente.telefono = request.form['telefono']
            paciente.direccion = request.form['direccion']
            
            # Actualizar Fecha
            fecha_str = request.form['fechaNacimiento']
            if fecha_str:
                paciente.fecha_nacimiento = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            
            # Actualizar Relaciones
            paciente.area_id = request.form['area_id'] if request.form['area_id'] else None
            paciente.medico_id = request.form['medico_id'] if request.form['medico_id'] else None
            
            db.session.commit()
            flash('Datos del paciente actualizados')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar: {str(e)}')
            
        return redirect(url_for('admin_pacientes'))

@app.route('/eliminar_paciente/<int:id>')
def eliminar_paciente(id):
    try:
        paciente = Paciente.query.get_or_404(id)
        # Aquí usamos borrado físico porque la tabla SQL no tiene columna 'activo'
        db.session.delete(paciente) 
        db.session.commit()
        flash('Paciente eliminado del sistema.')
    except Exception as e:
        flash(f'Error al eliminar: {str(e)}')
    return redirect(url_for('admin_pacientes'))

#ASIGNACIONES
@app.route('/admin_asignaciones')
def admin_asignaciones():
    # 1. Obtener filtros de la URL (si existen), sino usar defaults
    fecha_str = request.args.get('fecha')
    turno_id = request.args.get('turno_id')
    
    if fecha_str:
        fecha_filtro = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    else:
        fecha_filtro = datetime.now().date()
        
    # 2. Consultar catálogos para los dropdowns
    areas = Area.query.all()
    turnos = Turno.query.all()
    
    # Personal disponible (Activos)
    enfermeros = Enfermero.query.filter_by(activo=True).all()
    
    # 3. Consultar Asignaciones Existentes para esa fecha (y turno si se seleccionó)
    query = Asignacion.query.filter_by(fecha=fecha_filtro)
    if turno_id:
        query = query.filter_by(turno_id=turno_id)
    asignaciones = query.all()

    # 4. Estructurar datos para el Tablero Kanban (Organizar por Área)
    # Diccionario: { area_id: [lista_de_asignaciones] }
    tablero = {area.id: [] for area in areas}
    for asig in asignaciones:
        if asig.area_id in tablero:
            tablero[asig.area_id].append(asig)

    return render_template('admin_asignaciones.html', 
                           areas=areas, 
                           turnos=turnos, 
                           enfermeros=enfermeros,
                           tablero=tablero,
                           fecha_actual=fecha_filtro,
                           turno_seleccionado=int(turno_id) if turno_id else None)

@app.route('/guardar_asignacion', methods=['POST'])
def guardar_asignacion():
    if request.method == 'POST':
        try:
            fecha_obj = datetime.strptime(request.form['fecha'], '%Y-%m-%d').date()
            
            # Validar que el enfermero no esté ya asignado ese día en ese turno
            existe = Asignacion.query.filter_by(
                fecha=fecha_obj,
                turno_id=request.form['turno_id'],
                enfermero_id=request.form['enfermero_id']
            ).first()
            
            if existe:
                flash('¡Error! Este enfermero ya tiene asignación en ese turno.', 'error')
            else:
                nueva_asig = Asignacion(
                    fecha=fecha_obj,
                    area_id=request.form['area_id'],
                    enfermero_id=request.form['enfermero_id'],
                    turno_id=request.form['turno_id']
                )
                db.session.add(nueva_asig)
                db.session.commit()
                flash('Asignación creada correctamente', 'success')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error al asignar: {str(e)}', 'error')
            
        # Mantener la fecha seleccionada en la redirección
        return redirect(url_for('admin_asignaciones', fecha=request.form['fecha'], turno_id=request.form['turno_id']))

@app.route('/eliminar_asignacion/<int:id>')
def eliminar_asignacion(id):
    try:
        asig = Asignacion.query.get_or_404(id)
        fecha_redir = asig.fecha
        db.session.delete(asig)
        db.session.commit()
        flash('Asignación eliminada (Enfermero liberado)', 'warning')
        return redirect(url_for('admin_asignaciones', fecha=fecha_redir))
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'error')
        return redirect(url_for('admin_asignaciones'))

#RUTAS DE INVENTARIO

@app.route('/admin_inventario')
def admin_inventario():
    # 1. Filtros (Opcional: por tipo)
    filtro_tipo = request.args.get('tipo')
    
    query = Medicamento.query
    if filtro_tipo:
        query = query.filter_by(tipo=filtro_tipo)
        
    productos = query.order_by(Medicamento.nombre).all()
    
    # Obtener almacenes para el select de "Nueva Alta"
    almacenes = InventarioFarmacia.query.all()
    
    # Contador de alertas para las tabs
    alertas_count = Medicamento.query.filter(Medicamento.stock <= Medicamento.punto_reorden).count()
    
    return render_template('admin_inventario.html', 
                           productos=productos, 
                           almacenes=almacenes,
                           alertas_count=alertas_count,
                           filtro_actual=filtro_tipo)

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if request.method == 'POST':
        try:
            # Convertir fecha caducidad
            caducidad = None
            if request.form['fecha_caducidad']:
                caducidad = datetime.strptime(request.form['fecha_caducidad'], '%Y-%m-%d').date()
            
            nuevo_prod = Medicamento(
                codigo=request.form['codigo'],
                nombre=request.form['nombre'],
                tipo=request.form['tipo'],
                presentacion=request.form['presentacion'],
                stock=request.form['stock'],
                lote=request.form['lote'],
                fecha_caducidad=caducidad,
                punto_reorden=request.form['punto_reorden'],
                inventario_id=request.form['inventario_id']
            )
            
            db.session.add(nuevo_prod)
            db.session.commit()
            flash('Producto registrado correctamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar producto: {str(e)}', 'error')
            
        return redirect(url_for('admin_inventario'))

@app.route('/movimiento_stock', methods=['POST'])
def movimiento_stock():
    if request.method == 'POST':
        try:
            prod_id = request.form['producto_id']
            tipo_mov = request.form['tipo_movimiento'] # 'entrada' o 'salida'
            cantidad = int(request.form['cantidad'])
            
            producto = Medicamento.query.get_or_404(prod_id)
            
            if tipo_mov == 'entrada':
                producto.stock += cantidad
                flash(f'Se agregaron {cantidad} unidades a {producto.nombre}', 'success')
            elif tipo_mov == 'salida':
                if producto.stock >= cantidad:
                    producto.stock -= cantidad
                    flash(f'Se retiraron {cantidad} unidades de {producto.nombre}', 'warning')
                else:
                    flash('Error: Stock insuficiente para realizar la salida.', 'error')
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error en movimiento: {str(e)}', 'error')
            
        return redirect(url_for('admin_inventario'))

#RUTAS DE CAPACITACION

@app.route('/admin_capacitacion')
def admin_capacitacion():
    # 1. Obtener Cursos y calcular inscritos
    cursos = Curso.query.all()
    
    # 2. Datos para estadísticas del header
    total_cursos = len(cursos)
    # Contamos cuántas inscripciones hay en total
    total_becas = Inscripcion.query.count() 
    
    # 3. Obtener listado de evaluaciones (Historial)
    # Filtramos las que ya tienen progreso o calificación
    evaluaciones = Inscripcion.query.order_by(Inscripcion.fecha_inscripcion.desc()).all()
    
    return render_template('admin_capacitacion.html', 
                           cursos=cursos,
                           evaluaciones=evaluaciones,
                           total_cursos=total_cursos,
                           total_becas=total_becas)

@app.route('/guardar_curso', methods=['POST'])
def guardar_curso():
    if request.method == 'POST':
        try:
            # Convertir fechas
            f_inicio = datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d').date() if request.form['fecha_inicio'] else None
            # Fecha fin opcional (si es curso permanente)
            f_fin_str = request.form.get('fecha_fin')
            f_fin = datetime.strptime(f_fin_str, '%Y-%m-%d').date() if f_fin_str else None

            nuevo_curso = Curso(
                nombre=request.form['nombre'],
                descripcion=request.form['descripcion'],
                tipo=request.form['tipo'],
                cupo_max=request.form['cupo'],
                fecha_inicio=f_inicio,
                fecha_fin=f_fin
            )
            
            db.session.add(nuevo_curso)
            db.session.commit()
            flash('Curso publicado exitosamente', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear curso: {str(e)}', 'error')
            
        return redirect(url_for('admin_capacitacion'))

# Opción para inscribir personal (puedes agregar un botón en el futuro)
@app.route('/inscribir_demo', methods=['GET'])
def inscribir_demo():
    # Esta ruta es solo para generar datos de prueba rápidos si lo necesitas
    try:
        enf = Enfermero.query.first()
        cur = Curso.query.first()
        if enf and cur:
            ins = Inscripcion(enfermero_id=enf.id, curso_id=cur.id, progreso=50, estado="En Curso")
            db.session.add(ins)
            db.session.commit()
            flash('Inscripción de prueba creada')
    except:
        pass
    return redirect(url_for('admin_capacitacion'))


# --- RUTA USER DASHBOARD ---

@app.route('/user_dashboard')
def user_dashboard():
    # -----------------------------------------------------------------
    # SIMULACIÓN DE LOGIN: Asumimos que entra el Enfermero #1
    # Para probar con otros, cambia este número por otro ID existente.
    current_user_id = 1 
    # -----------------------------------------------------------------
    
    # 1. Obtener datos del enfermero
    enfermero = Enfermero.query.get(current_user_id)
    if not enfermero:
        return "<h3>Error: No existe el enfermero con ID 1. Crea personal primero en el Admin.</h3>"
    
    # 2. Buscar si tiene ASIGNACIÓN para el día de HOY
    hoy = datetime.now().date()
    asignacion = Asignacion.query.filter_by(
        enfermero_id=current_user_id, 
        fecha=hoy
    ).first()
    
    # Variables por defecto (si no tiene turno hoy)
    pacientes_asignados = []
    area_nombre = "Sin Asignación"
    turno_nombre = "--"
    
    if asignacion:
        area_nombre = asignacion.area.nombre
        turno_nombre = asignacion.turno.nombre
        
        # 3. Filtrar PACIENTES que estén en esa misma Área
        pacientes_asignados = Paciente.query.filter_by(area_id=asignacion.area_id).all()

    return render_template('user_dashboard.html', 
                           usuario=enfermero,
                           pacientes=pacientes_asignados,
                           area_actual=area_nombre,
                           turno_actual=turno_nombre,
                           fecha_actual=hoy)

#RUTAS TRIAGE
@app.route('/triage_ingreso')
def triage_ingreso():
    return render_template('triage_ingreso.html')

@app.route('/guardar_triage', methods=['POST'])
def guardar_triage():
    if request.method == 'POST':
        try:
            # 1. Primero creamos o actualizamos al PACIENTE
            # (En un sistema real, buscarías si ya existe, aquí creamos uno nuevo por simplicidad)
            nuevo_paciente = Paciente(
                nombre=request.form['nombre'],
                apellidos=request.form['apellidos'],
                genero=request.form['genero'],
                # Edad es un cálculo, pero si tu modelo Paciente pide fecha_nacimiento, 
                # podrías estimarla o dejarla null. Aquí lo dejamos pendiente o guardamos null.
                fecha_nacimiento=None 
            )
            db.session.add(nuevo_paciente)
            db.session.flush() # Esto genera el ID del paciente sin hacer commit final aún
            
            # 2. Guardamos el registro de TRIAGE vinculado al paciente
            nuevo_triage = Triage(
                paciente_id=nuevo_paciente.id,
                motivo_consulta=request.form['motivo'],
                
                # Signos Vitales
                frecuencia_cardiaca=request.form['hr'] or None,
                saturacion_oxigeno=request.form['spo2'] or None,
                temperatura=request.form['temp'] or None,
                tension_arterial=f"{request.form['sys']}/{request.form['dia']}", # Guardamos como "120/80"
                escala_dolor=request.form['pain'] or None,
                glucosa=request.form['glucosa'] or None,
                
                # Nivel (Radio Button)
                nivel_urgencia=request.form['triageLevel']
            )
            
            db.session.add(nuevo_triage)
            db.session.commit()
            
            flash('Paciente ingresado y clasificado correctamente.', 'success')
            return redirect(url_for('triage_ingreso'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar triage: {str(e)}', 'error')
            return redirect(url_for('triage_ingreso'))



#

#RUTAS DE HOJA DE ENFERMERIA
@app.route('/hoja_enfermeria/<int:paciente_id>')
def hoja_view(paciente_id):
    # 1. Obtener Paciente
    paciente = Paciente.query.get_or_404(paciente_id)
    
    # 2. Buscar si ya existe una hoja para HOY
    hoy = datetime.now().date()
    hoja = HojaEnfermeria.query.filter_by(paciente_id=paciente_id, fecha=hoy).first()
    
    # 3. Si no existe, la creamos automáticamente (vinculada al usuario actual ID 1)
    if not hoja:
        nueva_hoja = HojaEnfermeria(paciente_id=paciente_id, enfermero_id=1, fecha=hoy)
        db.session.add(nueva_hoja)
        db.session.commit()
        hoja = nueva_hoja
    
    # 4. Obtener catálogo de medicamentos para el select
    catalogo_meds = Medicamento.query.all()
    
    return render_template('hoja_enfermeria.html', 
                           paciente=paciente, 
                           hoja=hoja, 
                           medicamentos=catalogo_meds,
                           now=datetime.now()) # Para poner hora default en inputs

@app.route('/guardar_registro_clinico', methods=['POST'])
def guardar_registro_clinico():
    if request.method == 'POST':
        try:
            tipo_registro = request.form['tipo_registro'] # 'vitales', 'nota', 'medicamento'
            hoja_id = request.form['hoja_id']
            paciente_id = request.form['paciente_id']
            hora_actual = datetime.now().time()
            
            if tipo_registro == 'vitales':
                nuevo = RegistroVitales(
                    hora=hora_actual,
                    ta_sistolica=request.form['ta_sys'],
                    ta_diastolica=request.form['ta_dia'],
                    frecuencia_cardiaca=request.form['fc'],
                    frecuencia_respiratoria=request.form['fr'],
                    temperatura=request.form['temp'],
                    saturacion=request.form['spo2'],
                    hoja_id=hoja_id
                )
                db.session.add(nuevo)
                flash('Signos vitales registrados.', 'success')

            elif tipo_registro == 'nota':
                nuevo = NotaEnfermeria(
                    hora=hora_actual,
                    nota=request.form['nota_texto'],
                    tipo=request.form['tipo_nota'],
                    hoja_id=hoja_id
                )
                db.session.add(nuevo)
                flash('Nota de evolución agregada.', 'success')
                
            elif tipo_registro == 'medicamento':
                # Puede venir de un select o texto libre
                nombre_med = request.form.get('nombre_med_select') or request.form.get('nombre_med_text')
                
                nuevo = AdministracionMedicamento(
                    hora=hora_actual,
                    medicamento_nombre=nombre_med,
                    dosis=request.form['dosis'],
                    via=request.form['via'],
                    observaciones=request.form['obs_med'],
                    hoja_id=hoja_id
                )
                db.session.add(nuevo)
                
                # Descontar stock (Lógica simple)
                med_obj = Medicamento.query.filter_by(nombre=nombre_med).first()
                if med_obj and med_obj.stock > 0:
                    med_obj.stock -= 1
                
                flash('Medicamento registrado y descontado del stock.', 'success')

            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar: {str(e)}', 'error')
            
        return redirect(url_for('hoja_view', paciente_id=paciente_id))


#RUTAS DE Consumo de insumos

@app.route('/consumo_insumos')
def consumo_insumos():
    # 1. Simulación de usuario logueado (Enfermero ID 1)
    current_user_id = 1
    
    # 2. Obtener lista de insumos (Filtramos por Material y Soluciones, excluyendo medicamentos puros si quieres)
    # O mostramos todo. Aquí filtramos para mostrar solo 'Material' y 'Solucion' para este módulo.
    insumos = Medicamento.query.filter(Medicamento.tipo.in_(['Material', 'Solucion'])).order_by(Medicamento.nombre).all()
    
    # 3. Obtener pacientes del área donde está asignado el enfermero hoy
    hoy = datetime.now().date()
    asignacion = Asignacion.query.filter_by(enfermero_id=current_user_id, fecha=hoy).first()
    
    pacientes = []
    area_nombre = "Sin Asignación"
    if asignacion:
        pacientes = Paciente.query.filter_by(area_id=asignacion.area_id).all()
        area_nombre = asignacion.area.nombre
        
    # 4. Historial reciente de este enfermero (últimos 10)
    historial = HistorialConsumo.query.filter_by(enfermero_id=current_user_id)\
                .order_by(HistorialConsumo.fecha_hora.desc()).limit(10).all()

    return render_template('consumo_insumos.html', 
                           insumos=insumos, 
                           pacientes=pacientes, 
                           historial=historial,
                           area_actual=area_nombre,
                           now=datetime.now())


###RUTAS DE PORTAL DE CAPACITACION
@app.route('/registrar_consumo_rapido', methods=['POST'])
def registrar_consumo_rapido():
    if request.method == 'POST':
        try:
            prod_id = request.form['producto_id']
            cantidad = int(request.form['cantidad'])
            paciente_id = request.form.get('paciente_id') # Puede venir vacío si es uso general
            motivo = request.form['motivo']
            
            # Validaciones
            if not paciente_id: paciente_id = None
            
            producto = Medicamento.query.get(prod_id)
            
            if producto and producto.stock >= cantidad:
                # 1. Descontar Stock
                producto.stock -= cantidad
                
                # 2. Guardar Historial
                nuevo_consumo = HistorialConsumo(
                    cantidad=cantidad,
                    motivo=motivo,
                    medicamento_id=prod_id,
                    enfermero_id=1, # ID simulado
                    paciente_id=paciente_id
                )
                db.session.add(nuevo_consumo)
                db.session.commit()
                flash(f'Salida registrada: {cantidad}x {producto.nombre}', 'success')
            else:
                flash(f'Error: Stock insuficiente de {producto.nombre} (Disponible: {producto.stock})', 'error')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar: {str(e)}', 'error')
            
        return redirect(url_for('consumo_insumos'))

# --- RUTAS PORTAL CAPACITACIÓN (USUARIO) ---

@app.route('/portal_capacitacion')
def portal_capacitacion():
    # 1. Simulación de usuario (Enfermero ID 1)
    current_user_id = 1
    enfermero = Enfermero.query.get(current_user_id)
    
    # 2. Obtener mis inscripciones (Activas e Históricas)
    mis_inscripciones = Inscripcion.query.filter_by(enfermero_id=current_user_id).all()
    
    # Lista de IDs de cursos en los que ya estoy
    mis_cursos_ids = [ins.curso_id for ins in mis_inscripciones]
    
    # 3. Obtener cursos disponibles (Los que NO están en mi lista)
    # Usamos el operador ~ (not) con in_
    cursos_disponibles = Curso.query.filter( ~Curso.id.in_(mis_cursos_ids) if mis_cursos_ids else True ).all()

    return render_template('portal_capacitacion.html', 
                           usuario=enfermero,
                           mis_cursos=mis_inscripciones,
                           oferta=cursos_disponibles)

@app.route('/inscribirme_curso/<int:curso_id>')
def inscribirme_curso(curso_id):
    try:
        # Usuario Simulado ID 1
        nueva_inscripcion = Inscripcion(
            enfermero_id=1,
            curso_id=curso_id,
            progreso=0,
            calificacion=0.0,
            estado='En Curso'
        )
        db.session.add(nueva_inscripcion)
        db.session.commit()
        flash('¡Inscripción exitosa! Puedes comenzar el curso ahora.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al inscribir: {str(e)}', 'error')
        
    return redirect(url_for('portal_capacitacion'))

@app.route('/actualizar_progreso', methods=['POST'])
def actualizar_progreso():
    if request.method == 'POST':
        try:
            inscripcion_id = request.form['inscripcion_id']
            nuevo_avance = int(request.form['nuevo_avance'])
            
            # Buscar registro
            ins = Inscripcion.query.get(inscripcion_id)
            
            if ins:
                ins.progreso = nuevo_avance
                
                # Si llega a 100%, marcamos como completado y simulamos calificación
                if nuevo_avance >= 100:
                    ins.estado = 'Completado'
                    ins.calificacion = 95.0 # Calificación simulada automática
                    flash('¡Felicidades! Has completado el curso.', 'success')
                else:
                    flash('Progreso guardado.', 'success')
                    
                db.session.commit()
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            
    return redirect(url_for('portal_capacitacion'))

















# --- INICIALIZADOR ---
if __name__ == '__main__':
    with app.app_context():
        # db.create_all() -> NOTA: Como ya tienes el SQL externo,
        # lo ideal es que las tablas ya existan. 
        # Si usas db.create_all() y las tablas ya existen en Postgres, no hará nada malo.
        # Pero si NO existen, las creará basándose en estas clases (que son una versión simplificada del SQL completo).
        
        # Para evitar conflictos con tu script SQL completo, intentamos solo insertar datos si está vacío
        try:
            db.create_all() 
            if not Curso.query.first():
                cursos = [
                    Curso(nombre="Actualización de Medicamentos IV", tipo="Clínico", cupo_max=20, descripcion="Protocolos para nuevos fármacos en terapia intensiva.", fecha_inicio=datetime(2026, 1, 10)),
                    Curso(nombre="Educación en Compasión", tipo="Humanización", cupo_max=50, descripcion="Taller práctico sobre empatía y psicología del dolor.", fecha_inicio=datetime(2026, 2, 20)),
                    Curso(nombre="Manejo de Residuos (RPBI)", tipo="Normativa", cupo_max=100, descripcion="Certificación obligatoria anual.", fecha_inicio=datetime(2026, 1, 1))
                ]
                db.session.add_all(cursos)
                db.session.commit()
                print("Cursos iniciales creados.")
            # Crear Turnos por defecto (Solo si no existen)
            if not Turno.query.first():
                # Como tu BD pide fecha y tipo, insertamos valores genéricos o NULL si lo permite
                # Para un catálogo base, usaremos nombres descriptivos en 'nombre'
                turnos = [
                    Turno(nombre="Matutino", tipoturno="Matutino"),
                    Turno(nombre="Vespertino", tipoturno="Vespertino"),
                    Turno(nombre="Nocturno", tipoturno="Nocturno"),
                    Turno(nombre="Jornada Acumulada", tipoturno="Fines de Semana")
                ]
                db.session.add_all(turnos)
                db.session.commit()
                print("Turnos creados correctamente.")
            #Datos semilla para areas y medicos
            # Crear Áreas Básicas
            if not Area.query.first():
                areas = [
                    Area(nombre="Urgencias"),
                    Area(nombre="Pediatría"),
                    Area(nombre="Consulta Externa"),
                    Area(nombre="Terapia Intensiva")
                ]
                db.session.add_all(areas)
                db.session.commit()
                print("Áreas creadas.")

            # Crear Médicos Básicos
            if not Medico.query.first():
                medicos = [
                    Medico(nombre="Dr. Chapatin", apellidos="Gómez", especialidad="General"),
                    Medico(nombre="Dra. House", apellidos="Gregory", especialidad="Diagnóstico")
                ]
                db.session.add_all(medicos)
                db.session.commit()
                print("Médicos creados.")
            # Datos semilla solo si no hay roles
            if not RolEnfermeria.query.first():
                roles = [
                    RolEnfermeria(nombre="Jefe de Piso", nivel_autoridad="Alto"),
                    RolEnfermeria(nombre="Enfermero General", nivel_autoridad="Medio"),
                    RolEnfermeria(nombre="Auxiliar", nivel_autoridad="Bajo")
                ]
                db.session.add_all(roles)
                db.session.commit()
                print("Roles iniciales insertados.")
            # Crear Inventario y Medicamentos Demo si no existen
            if not Medicamento.query.first():
                inv = InventarioFarmacia(nombre="Almacén Central")
                db.session.add(inv)
                db.session.commit()
                
                meds = [
                    Medicamento(nombre="Paracetamol 500mg", stock=120, inventario_id=inv.id),
                    Medicamento(nombre="Insulina Glargina", stock=2, inventario_id=inv.id), # Alerta
                    Medicamento(nombre="Gasas Estériles", stock=5, inventario_id=inv.id),   # Alerta
                    Medicamento(nombre="Ketorolaco", stock=50, inventario_id=inv.id)
                ]
                db.session.add_all(meds)
                db.session.commit()
                print("Datos de farmacia creados.")
        except Exception as e:
            print(f"Advertencia de inicialización: {e}")

    app.run(debug=True, port=5000)