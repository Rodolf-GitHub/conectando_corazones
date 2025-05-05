# Comandos Alembic 🚀

## Comandos Básicos (Similares a Django)

### Crear Migraciones
```bash
# Crear una nueva migración automática detectando cambios en modelos
alembic revision --autogenerate -m "initial"

# Crear una migración vacía (para escribir manualmente)
alembic revision -m "nombre_migracion_manual"
```

### Aplicar Migraciones
```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Aplicar migraciones hasta una específica
alembic upgrade <revision_id>
```

### Revertir Migraciones
```bash
# Retroceder todas las migraciones
alembic downgrade base

# Retroceder una migración
alembic downgrade -1

# Retroceder N migraciones
alembic downgrade -N

#elimina todas las migraciones
rm -rf alembic/versions/*
```

### Consultar Estado
```bash
# Ver estado actual de las migraciones
alembic current

# Ver historial de migraciones
alembic history

# Ver migraciones pendientes
alembic history --indicate-current
```

## Comandos Avanzados 🔧

### Inicialización
```bash
# Inicializar alembic en un proyecto nuevo
alembic init alembic
```

### Verificación y SQL
```bash
# Verificar el siguiente cambio sin aplicarlo
alembic upgrade head --sql

# Generar SQL para una revisión específica
alembic upgrade <revision_id> --sql

# Marcar una migración como completada sin ejecutarla
alembic stamp <revision_id>
```

## Mejores Prácticas 💡

1. **Seguridad**
   - Siempre haz un backup de la base de datos antes de migrar
   - En producción, revisa el SQL generado antes de aplicar

2. **Nombrado**
   - Usa nombres descriptivos para las migraciones
   - Incluye el tipo de cambio en el nombre (ej: "add_user_email")

3. **Revisión**
   - Revisa el archivo de migración generado antes de aplicarlo
   - Verifica que los tipos de datos sean correctos

4. **Control de Versiones**
   - Incluye los archivos de migración en el control de versiones
   - No modifiques migraciones ya aplicadas

## Ejemplos Comunes 📝

### Agregar una columna
```bash
alembic revision --autogenerate -m "add_user_email"
```

### Crear una nueva tabla
```bash
alembic revision --autogenerate -m "create_products_table"
```

### Modificar una columna existente
```bash
alembic revision --autogenerate -m "modify_user_email_unique"
```

## Solución de Problemas 🔍

- Si las migraciones no detectan cambios, verifica que tus modelos estén importados correctamente
- Para problemas de dependencias circulares, usa `op.create_foreign_key()` en una migración separada
- Si necesitas ejecutar código personalizado, puedes agregarlo en las funciones `upgrade()` y `downgrade()`