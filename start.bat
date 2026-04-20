@echo off
REM ========================================
REM Pub-IA - Script de dEmarrage (Windows)
REM ========================================

echo.
echo ========================================
echo   Demarrage de l'infrastructure Pub-IA
echo ========================================
echo.

REM Verifier si Docker est installe
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Docker n'est pas installe.
    echo Veuillez l'installer d'abord:
    echo https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Verifier si .env existe
if not exist .env (
    echo ATTENTION: Fichier .env manquant !
    echo.
    set /p CREATE_ENV="Voulez-vous creer un .env a partir de .env.example ? (o/n) : "
    if /i "%CREATE_ENV%"=="o" (
        copy .env.example .env
        echo Fichier .env cree. N'oubliez pas de modifier les valeurs sensibles !
        echo.
    ) else (
        echo Veuillez creer un fichier .env avant de continuer.
        pause
        exit /b 1
    )
)

REM Arreter les containers existants
echo Arret des containers existants...
docker-compose down

echo.
echo Construction des images Docker...
docker-compose up -d --build

echo.
echo Attente du demarrage des services...
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo   Pub-IA est demarre !
echo ========================================
echo.
echo URLs :
echo   Frontend (Dashboard): http://localhost:5173
echo   Backend API:          http://localhost:8080
echo   Demo Chatbot:         http://localhost:3000
echo   Health Check:         http://localhost:8080/health
echo.
echo Commands utiles :
echo   docker-compose logs -f          # Voir les logs
echo   docker-compose down             # Arreter
echo   docker-compose restart          # Redemarrer
echo.
echo Documentation:
echo   README.md                       # Guide complet
echo   demo-chatbot\README.md          # Guide demo
echo.
echo ========================================
pause
