-- ###############################################################
-- # 1. TABLAS PRINCIPALES (ENTIDADES)
-- ###############################################################

-- Tabla para almacenar la información del hospital
CREATE TABLE Hospital (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    tipo VARCHAR(100)
);

-- Tabla para las áreas del hospital (Urgencias, Cardiología, etc.)
CREATE TABLE Area (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    capacidad INT,
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id)
);

-- Tabla para los médicos
CREATE TABLE Medico (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    especialidad VARCHAR(100),
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id)
);

-- Tabla para definir los roles del personal de enfermería
CREATE TABLE RolEnfermeria (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    nivelAutoridad VARCHAR(50),
    hospital_id INT,
    FOREIGN KEY (hospital_id) REFERENCES Hospital(id)
);

-- Tabla para el personal de enfermería
CREATE TABLE Enfermero (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    rol_enfermeria_id INT,
    FOREIGN KEY (rol_enfermeria_id) REFERENCES RolEnfermeria(id)
);

-- Tabla para la información de los pacientes
CREATE TABLE Paciente (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellidos VARCHAR(150) NOT NULL,
    fechaNacimiento DATE,
    genero VARCHAR(50),
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    medico_id INT,
    area_id INT,
    FOREIGN KEY (medico_id) REFERENCES Medico(id),
    FOREIGN KEY (area_id) REFERENCES Area(id)
);

-- Tabla para definir los turnos de trabajo
CREATE TABLE Turno (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha DATE,
    tipoTurno VARCHAR(50)
);

-- Tabla para los horarios específicos dentro de un turno
CREATE TABLE Horario (
    id SERIAL PRIMARY KEY,
    fechaInicio TIMESTAMP,
    horaInicio TIME,
    fechaFin TIMESTAMP,
    horaFin TIME,
    turno_id INT,
    FOREIGN KEY (turno_id) REFERENCES Turno(id)
);

-- Tabla para las actividades o procedimientos médicos
CREATE TABLE Actividad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    observaciones TEXT
);

-- Tabla para los tratamientos prescritos a pacientes
CREATE TABLE Tratamiento (
    id SERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL,
    fechaInicio DATE,
    fechaFin DATE,
    dosis VARCHAR(255),
    frecuencia VARCHAR(100),
    estado VARCHAR(50), -- (Ej: Activo, Finalizado, Suspendido)
    medico_id INT,
    paciente_id INT,
    FOREIGN KEY (medico_id) REFERENCES Medico(id),
    FOREIGN KEY (paciente_id) REFERENCES Paciente(id)
);

-- Tabla para el inventario de farmacia
CREATE TABLE InventarioFarmacia (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fechaActualizacion TIMESTAMP,
    capacidadAlmacenamiento INT,
    area_id INT UNIQUE, -- Relación 1 a 1 con Área
    FOREIGN KEY (area_id) REFERENCES Area(id)
);
--medicamento acutalizado
CREATE TABLE medicamento (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,           -- Ej: MED-001
    nombre VARCHAR(150) NOT NULL,
    tipo VARCHAR(50),                    -- Ej: Medicamento, Material, Solución
    presentacion VARCHAR(100),           -- Ej: Caja 20 tabs
    stock INTEGER DEFAULT 0,
    lote VARCHAR(100),
    fecha_caducidad DATE,                -- Cambio importante: DATE en lugar de String
    punto_reorden INTEGER DEFAULT 10,    -- Para las alertas de stock bajo
    inventario_id INTEGER,               -- Relación con la ubicación (Farmacia/Almacén)
    
    -- Definición de la clave foránea
    CONSTRAINT fk_inventario
      FOREIGN KEY(inventario_id) 
      REFERENCES inventariofarmacia(id)
);

-- Tabla para otros insumos médicos
CREATE TABLE Insumo (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    cantidad INT,
    fechaVencimiento DATE,
    inventario_id INT,
    FOREIGN KEY (inventario_id) REFERENCES InventarioFarmacia(id)
);


-- ###############################################################
-- # 2. TABLAS ASOCIATIVAS (PARA RELACIONES MUCHOS A MUCHOS)
-- ###############################################################

-- Tabla para asignar enfermeros a horarios
CREATE TABLE Enfermero_Horario (
    enfermero_id INT,
    horario_id INT,
    PRIMARY KEY (enfermero_id, horario_id),
    FOREIGN KEY (enfermero_id) REFERENCES Enfermero(id),
    FOREIGN KEY (horario_id) REFERENCES Horario(id)
);

-- Tabla para registrar qué enfermero realiza qué actividad
CREATE TABLE Enfermero_Actividad (
    enfermero_id INT,
    actividad_id INT,
    PRIMARY KEY (enfermero_id, actividad_id),
    FOREIGN KEY (enfermero_id) REFERENCES Enfermero(id),
    FOREIGN KEY (actividad_id) REFERENCES Actividad(id)
);

-- Tabla para relacionar pacientes con actividades
CREATE TABLE Paciente_Actividad (
    paciente_id INT,
    actividad_id INT,
    PRIMARY KEY (paciente_id, actividad_id),
    FOREIGN KEY (paciente_id) REFERENCES Paciente(id),
    FOREIGN KEY (actividad_id) REFERENCES Actividad(id)
);

-- Tabla para detallar qué medicamentos requiere un tratamiento
CREATE TABLE Tratamiento_Medicamento (
    tratamiento_id INT,
    medicamento_id INT,
    PRIMARY KEY (tratamiento_id, medicamento_id),
    FOREIGN KEY (tratamiento_id) REFERENCES Tratamiento(id),
    FOREIGN KEY (medicamento_id) REFERENCES Medicamento(id)
);

CREATE TABLE triage (
    id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    motivo_consulta TEXT,
    
    -- Signos Vitales
    frecuencia_cardiaca INT,
    saturacion_oxigeno INT,
    temperatura DECIMAL(4,1),
    tension_arterial VARCHAR(20),
    escala_dolor INT,
    glucosa INT,
    
    -- Clasificación
    nivel_urgencia INT, -- 1 (Rojo) a 5 (Azul)
    
    -- Relación con Paciente
    paciente_id INT,
    CONSTRAINT fk_paciente_triage 
      FOREIGN KEY(paciente_id) 
      REFERENCES paciente(id)
);

-- Tabla Principal: Hoja diaria por paciente
CREATE TABLE hoja_enfermeria (
    id SERIAL PRIMARY KEY,
    fecha DATE DEFAULT CURRENT_DATE,
    paciente_id INT,
    enfermero_id INT, -- Enfermero responsable del turno
    CONSTRAINT fk_hoja_paciente FOREIGN KEY(paciente_id) REFERENCES paciente(id),
    CONSTRAINT fk_hoja_enfermero FOREIGN KEY(enfermero_id) REFERENCES enfermero(id)
);

-- Tabla Detalle: Signos Vitales (Hora a hora)
CREATE TABLE registro_vitales (
    id SERIAL PRIMARY KEY,
    hora TIME NOT NULL,
    ta_sistolica INT,
    ta_diastolica INT,
    frecuencia_cardiaca INT,
    frecuencia_respiratoria INT,
    temperatura DECIMAL(4,1),
    saturacion INT,
    hoja_id INT,
    CONSTRAINT fk_vitales_hoja FOREIGN KEY(hoja_id) REFERENCES hoja_enfermeria(id)
);

-- Tabla Detalle: Notas de Enfermería
CREATE TABLE nota_enfermeria (
    id SERIAL PRIMARY KEY,
    hora TIME NOT NULL,
    nota TEXT NOT NULL,
    tipo VARCHAR(50), -- 'Ingreso', 'Procedimiento', 'Evolución', 'Indicación'
    hoja_id INT,
    CONSTRAINT fk_nota_hoja FOREIGN KEY(hoja_id) REFERENCES hoja_enfermeria(id)
);

-- Tabla Detalle: Administración de Medicamentos
CREATE TABLE administracion_medicamento (
    id SERIAL PRIMARY KEY,
    hora TIME NOT NULL,
    medicamento_nombre VARCHAR(150),
    dosis VARCHAR(100),
    via VARCHAR(50), -- Oral, IV, IM, etc.
    observaciones TEXT,
    hoja_id INT,
    CONSTRAINT fk_med_hoja FOREIGN KEY(hoja_id) REFERENCES hoja_enfermeria(id)
);
CREATE TABLE historial_consumo (
    id SERIAL PRIMARY KEY,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cantidad INT NOT NULL,
    motivo VARCHAR(100), -- Ej: 'Curación', 'Procedimiento', 'Merma'
    
    -- Relaciones
    medicamento_id INT, -- Referencia al producto (Medicamento o Material)
    enfermero_id INT,   -- Quién lo usó
    paciente_id INT,    -- (Opcional) A quién se lo aplicó
    
    CONSTRAINT fk_consumo_med FOREIGN KEY(medicamento_id) REFERENCES medicamento(id),
    CONSTRAINT fk_consumo_enf FOREIGN KEY(enfermero_id) REFERENCES enfermero(id),
    CONSTRAINT fk_consumo_pac FOREIGN KEY(paciente_id) REFERENCES paciente(id)
);