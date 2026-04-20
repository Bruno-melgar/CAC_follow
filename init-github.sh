#!/bin/bash

# Script para inicializar el repositorio de GitHub para el CAC Dashboard
# Ejecutar desde la carpeta deploy/

echo "=== Inicializando repositorio Git para CAC Dashboard ==="
echo ""

# Verificar si ya existe .git
if [ -d ".git" ]; then
    echo "¡Advertencia! Ya existe un repositorio git en esta carpeta."
    read -p "¿Quieres continuar? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        echo "Operación cancelada."
        exit 0
    fi
fi

# Inicializar git
echo "Inicializando repositorio git..."
git init

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    echo "Creando .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
EOF
fi

# Añadir todos los archivos
echo "Añadiendo archivos al staging..."
git add .

# Commit inicial
echo "Creando commit inicial..."
git commit -m "Initial commit: CAC Dashboard ready for Render deployment"

echo ""
echo "=== ¡Repositorio inicializado con éxito! ==="
echo ""
echo "Siguientes pasos:"
echo "1. Crea un nuevo repositorio en GitHub (github.com/new)"
echo "2. Ejecuta los siguientes comandos:"
echo ""
echo "   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Luego ve a render.com y conecta tu repositorio de GitHub"
echo ""
