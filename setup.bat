@echo off
REM FishNet Platform - Windows Setup Script

echo 🌊 Setting up FishNet - Marine Biodiversity Platform
echo ==================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo 🐍 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📦 Installing Python packages...
pip install flask flask-sqlalchemy flask-cors pandas numpy requests python-dotenv psutil supabase

echo ✅ All packages installed successfully

REM Create necessary directories
echo 📁 Creating project directories...
if not exist "backend\app\static\css" mkdir backend\app\static\css
if not exist "backend\app\static\js" mkdir backend\app\static\js  
if not exist "backend\app\static\images" mkdir backend\app\static\images
if not exist "backend\app\templates" mkdir backend\app\templates
if not exist "backend\data\raw" mkdir backend\data\raw
if not exist "backend\data\processed" mkdir backend\data\processed
if not exist "backend\logs" mkdir backend\logs

echo ✅ Directories created

REM Initialize database
echo 🗄️ Initializing database...
cd backend
python -c "import sys; sys.path.append('.'); from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized')"

echo.
echo 🎉 FishNet Setup Complete!
echo =========================
echo.
echo 🚀 To start the application:
echo    1. cd backend
echo    2. venv\Scripts\activate  (if not already activated)
echo    3. python run.py
echo.
echo 🌐 Then open: http://localhost:5000
echo.
echo 📊 The platform includes:
echo    • Interactive dashboard with real marine data
echo    • Species detail pages with comprehensive visuals  
echo    • Real oceanographic data from Indian Ocean
echo    • eDNA sample analysis
echo    • Scientific and public policy tabs
echo    • Animated charts and maps
echo.
echo 🐋 Happy marine data exploration!
echo.
pause