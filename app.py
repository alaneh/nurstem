from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "clave_secreta_nurstem"

# --- CONFIGURACIÓN DE BASE DE DATOS (PostgreSQL) ---
# Asegúrate de que tu contraseña sea 'admin123'. Si es otra, cámbiala aquí.
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin123@localhost/nurstem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODELOS (Mapeo exacto con nurstem.sql) ---

class RolEnfermeria(db.Model):
    # Definimos el nombre exacto de la tabla en SQL
    __tablename__ = 'rolenfermeria' # Ojo: Postgres suele normalizar a minúsculas si no usaste comillas en el CREATE
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    
    # CORRECCIÓN: En tu SQL la columna se llama 'nivelAutoridad' (camelCase)
    # El primer argumento string le dice a SQLAlchemy cómo buscarla en la BD real.
    nivel_autoridad = db.Column('nivelautoridad', db.String(50)) 
    
    # Relación (Esto no crea columna, es para Python)
    enfermeros = db.relationship('Enfermero', backref='rol', lazy=True)

class Enfermero(db.Model):
    __tablename__ = 'enfermero'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(150), nullable=False)
    telefono = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    
    # Coincide con tu SQL: rol_enfermeria_id
    rol_enfermeria_id = db.Column(db.Integer, db.ForeignKey('rolenfermeria.id'))

# --- RUTAS ---

@app.route('/')
def index():
    return redirect(url_for('admin_personal'))

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
        except Exception as e:
            print(f"Advertencia de inicialización: {e}")

    app.run(debug=True, port=5000)