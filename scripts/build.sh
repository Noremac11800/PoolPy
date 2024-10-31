pyinstaller --name "poolpy" --onefile --windowed ./app/main.py --add-data "./poolpy/assets:." --splash ./poolpy/assets/splash.png

pyinstaller --name "poolpy" --onefile --windowed ./main.py --add-data "./poolpy/assets:." --icon="./poolpy/assets/icon.icns"
