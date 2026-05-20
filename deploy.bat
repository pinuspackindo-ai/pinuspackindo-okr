@echo off
cd /d "C:\1. Audit\1. PINUS\5. PROJECT\2. Tools Purchase (OKR) v.1"
echo.
echo ================================================
echo   PINUS PACKINDO - AUTO DEPLOY
echo ================================================
echo.
echo [1/3] Mendeteksi perubahan file...
git add .
git diff --cached --quiet
if %errorlevel%==0 (
    echo   Tidak ada perubahan baru.
    goto done
)
echo [2/3] Menyimpan perubahan...
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set tgl=%%c-%%b-%%a
for /f "tokens=1 delims= " %%a in ('time /t') do set jam=%%a
git commit -m "Update %tgl% %jam%"
echo [3/3] Mengirim ke GitHub (Vercel akan auto-deploy)...
git push origin main
echo.
echo ================================================
echo   SELESAI! Vercel sedang deploy otomatis.
echo   Cek: https://pinus-tools.vercel.app
echo ================================================
:done
echo.
pause
