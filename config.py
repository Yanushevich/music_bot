RADIO_LIST={}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}
LEAVE_RESPONSES = [
    "Диджей дроссельная заслонка закончил смену",
    "Побежал за пивом, надеюсь успеть до закрытия",
    "ББ",
    "Диджей-сет подошел к концу"
]
PLAY_RESPONSES = [
    "Сегодня ваши уши ласкает: ",
    "Внимание! Вы слушаете: ",
    "Йоу смотрите че нашел: ",
    "Диджей дабстеп играет для вас: "
]