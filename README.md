# Discord-бот, проигрывающий интернет-радио из списка
**ВАЖНО:** 
* Помимо зависимостей, указанных в requirements.txt, требует установки ffmpeg
> При python >= 3.13 также необходимо установить audioop
>
```shell
pip install audioop-lts
```
* Токен бота необходимо записать в config_token.py (добавлен в .gitignore)
```
TOKEN = ['ваш_токен']
```
* Список радиостанций хранится в cogs/stations.csv
> Формат:
> ```
> название;ссылка_на_потоковое_аудио;ссылка_на_информацию_о_треке
> ```
> Ссылка на информацию о треке необязательна, на данный момент используется только у станций [Radio Record](https://app-api.radiorecord.ru/), полученных с помощью extra/parse_radio.py. Помимо этого в текущем конфиге есть станции - Шансон, Europa Plus Уфа, Studio 21
* Необходимо, чтобы сервер имел доступ в Discord

### Команды:
* _/play_ - включить станцию (выбор из списка)
* _/pause_ - поставить поток на паузу/продолжить воспроизведение с места остановки
* _/stop_ - остановить поток
* _/leave_ - выйти из голосового канала
* _/refresh_ - обновить список радио из cogs/stations.csv

### Установка на Linux
```shell
cd /opt
git clone https://github.com/Yanushevich/music_bot.git
sudo apt install python3 python3-pip python3-venv ffmpeg -y
cd music_bot/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install audioop-lts
nano /etc/systemd/system/music_bot.service
```
### music_bot.service
```ini
[Unit]
Description=Discord Bot
After=network.target

[Service]
User=root
WorkingDirectory=/opt/music_bot
ExecStart=/opt/music_bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
### Включение сервиса
```shell
sudo systemctl daemon-reload
sudo systemctl start music_bot
sudo systemctl enable music_bot
```
