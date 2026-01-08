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