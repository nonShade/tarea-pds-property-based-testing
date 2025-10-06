# CRUD de Usuarios con Property-Based Testing

Este proyecto implementa un prototipo funcional de un sistema CRUD (Create, Read, Update, Delete) para usuarios, con un enfoque especial en **property-based testing** utilizando la librería Hypothesis de Python.

## Estructura del Proyecto

```
user-crud-property-testing/
├── src/
│   └── user_crud/
│       ├── __init__.py
│       ├── models.py       # Modelo de Usuario
│       └── crud.py         # Operaciones CRUD
├── tests/
│   ├── test_create_properties.py    # Pruebas para CREATE
│   ├── test_read_properties.py      # Pruebas para READ
│   ├── test_update_properties.py    # Pruebas para UPDATE
│   └── test_delete_properties.py    # Pruebas para DELETE
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Características Implementadas

### Modelo de Usuario
- **ID único**: Generado automáticamente con UUID
- **Nombre**: String no vacío
- **Email**: Formato válido y único en el sistema
- **Edad**: Entero entre 0 y 150 años
- **Timestamps**: created_at y updated_at

### Operaciones CRUD
- **Create**: Crear nuevo usuario con validaciones
- **Read**: Buscar por ID, email, obtener todos los usuarios
- **Update**: Actualizar campos específicos manteniendo la integridad
- **Delete**: Eliminar usuarios individualmente o todos

## Property-Based Testing

El proyecto implementa pruebas basadas en propiedades que verifican invariantes del sistema en lugar de casos específicos:

### Pruebas para CREATE
- **Unicidad de IDs**: Todos los usuarios creados tienen IDs únicos
- **Normalización de datos**: Emails en minúsculas, nombres sin espacios extra
- **Validación de emails duplicados**: No se permiten emails duplicados
- **Manejo de datos inválidos**: Rechaza correctamente datos inválidos

### Pruebas para READ
- **Consistencia de recuperación**: Los usuarios creados siempre son recuperables
- **Búsqueda case-insensitive**: Los emails se encuentran independientemente de mayúsculas
- **Manejo de casos inexistentes**: Retorna None para IDs/emails inexistentes
- **Integridad de la lista**: get_all() retorna exactamente los usuarios creados

### Pruebas para UPDATE
- **Preservación de ID**: El ID nunca cambia durante actualizaciones
- **Actualización selectiva**: Solo los campos especificados cambian
- **Validación de emails duplicados**: No permite actualizar a email existente
- **Timestamp de actualización**: updated_at se establece correctamente

### Pruebas para DELETE
- **Eliminación efectiva**: Los usuarios eliminados no son recuperables
- **Consistencia del contador**: count() refleja correctamente las eliminaciones
- **No afectación de otros usuarios**: Solo el usuario especificado se elimina
- **Reutilización de emails**: Permite crear nuevos usuarios con emails previamente eliminados

## Instalación y Uso

### Prerrequisitos
- Python 3.8+
- pip

### Instalación
```bash
# Clonar el repositorio
git clone <url-del-repositorio>
cd user-crud-property-testing

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar las Pruebas
```bash
# Ejecutar todas las pruebas
PYTHONPATH=src python -m pytest tests/ -v

# Ejecutar pruebas específicas
PYTHONPATH=src python -m pytest tests/test_create_properties.py -v
PYTHONPATH=src python -m pytest tests/test_read_properties.py -v
PYTHONPATH=src python -m pytest tests/test_update_properties.py -v
PYTHONPATH=src python -m pytest tests/test_delete_properties.py -v

# Ejecutar con más detalles de Hypothesis
PYTHONPATH=src python -m pytest tests/ -v --hypothesis-show-statistics
```

## Ventajas del Property-Based Testing

### Comparación con Testing Tradicional

**Testing Tradicional (Ejemplo-based)**:
```python
def test_create_user():
    crud = UserCRUD()
    user = crud.create("Juan", "juan@test.com", 25)
    assert user.name == "Juan"
    assert user.email == "juan@test.com"
    assert user.age == 25
```

**Property-Based Testing (con Hypothesis)**:
```python
@given(
    name=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    email=st.emails(),
    age=st.integers(min_value=0, max_value=150)
)
def test_create_user_properties(name, email, age):
    crud = UserCRUD()
    user = crud.create(name, email, age)
    
    # Propiedades que SIEMPRE deben cumplirse
    assert user.id is not None
    assert len(user.id) > 0
    assert user.name == name.strip()
    assert user.email == email.lower()
    assert crud.exists(user.id)
```

## Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación
- **Hypothesis 6.88+**: Framework para property-based testing
- **pytest 7.4+**: Framework de testing
- **dataclasses**: Para definición de modelos
- **UUID**: Para generación de identificadores únicos
- **datetime**: Para manejo de timestamps

## Estructura de las Pruebas

Cada archivo de pruebas sigue un patrón consistente:

1. **Importaciones y setup**
2. **Pruebas principales con @given decorator**
3. **Pruebas de casos extremos**
4. **Pruebas de validación de errores**
5. **Pruebas de estado vacío/inicial**
