# 사용자 명령어 인터페이스
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes, CallbackQueryHandler
import modules.telegram_bot as tb
from modules.soil_moisture_control import activate_water_pump
from modules.water_tank_monitor import get_current_tank_level_percent
from modules.light_control_system import turn_on_led_with_brightness, switch_to_auto_mode, turn_off_led
import asyncio


# 처음 접속 시 안내 메세지
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ("안녕하세요!\n"
           "똑똑한 식물 관리 플랫폼\n"
           "\"Smart Plant Pot\" 입니다.\n"
           "\n"
           "다음 버튼을 선택해주세요.")

    # GUI 버튼으로 선택지 구성
    keyboard = [
        [
            InlineKeyboardButton("1. 도움말", callback_data="help"),
            InlineKeyboardButton("2. 식물 설정", callback_data="plant_setting"),
        ],
        [
            InlineKeyboardButton("3. 식물 상태 분석", callback_data="get_analysis"),
            InlineKeyboardButton("4. 타임랩스 조회", callback_data="get_timelapse"),
        ],
        [
            InlineKeyboardButton("5. 물주기 설정", callback_data="water_setting"),
            InlineKeyboardButton("6. 조명 설정", callback_data="light_setting"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 메시지 전송
    await update.message.reply_text(msg, reply_markup=reply_markup)


# 버튼 클릭 이벤트 핸들러
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # 버튼 클릭 시 로딩 표시 제거
    await query.answer()

    response_msg = ""

    # 버튼의 callback_data에 따라 동작 수행
    if query.data == "help":
        response_msg = (
            "명령어 도움말\n\n"
            "1. 도움말\n"
            "사용 가능한 기능에 대한 설명\n"
            "2. 식물 설정\n"
            "관리 대상 식물 정보를 입력\n"
            "3. 식물 상태 분석\n"
            "현재 상태 분석 리포트 제공\n"
            "4. 타임랩스 조회\n"
            "촬영된 식물의 타임랩스 확인\n"
            "5. 물주기 설정\n"
            "수동 물주기 및 물탱크 잔여량 확인\n"
            "6. 조명 설정\n"
            "조명 ON/OFF 제어 및 자동 모드 전환"
        )

    elif query.data == "plant_setting":
        # 식물 선택 버튼 생성
        keyboard = [
            [
                InlineKeyboardButton("1. 관엽식물", callback_data="plant_1"),
                InlineKeyboardButton("2. 허브/채소류", callback_data="plant_2"),
            ],
            [
                InlineKeyboardButton("3. 다육식물/선인장", callback_data="plant_3"),
                InlineKeyboardButton("4. 화초류", callback_data="plant_4"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_msg = "식물을 선택해주세요."

    elif query.data.startswith("plant_"):
        chat_id = query.message.chat_id
        # 선택한 식물에 대해 파일 생성 및 데이터 쓰기
        # 식물 유형 추출 (예: "1", "2", "3", "4")
        plant_type = query.data.split("_")[1]

        # 파일명: ../threshold/threshold.txt
        file_path = "/home/pi/SmartPlantPot/threshold/threshold.txt"

        # 식물 유형에 따른 다르게 내용 작성
        # "토양수분 조도 온도 습도" 순으로 작성
        if plant_type == "1":  # 관엽식물
            content = "50\n800\n21\n50"
        elif plant_type == "2":  # 허브/채소류
            content = "60\n3700\n20\n60"
        elif plant_type == "3":  # 다육식물/선인장
            content = "20\n4500\n27\n20"
        elif plant_type == "4":  # 화초류
            content = "50\n2000\n20\n55"

        # 파일 생성 및 데이터 쓰기
        with open(file_path, "w") as file:
            file.write(content)

        response_msg = ("식물이 선택되었습니다.\n"
                        "\n"
                        "메뉴로 돌아가시려면 \"/start\"를 입력해주세요.")

        # 버튼을 제거하여 빈 키보드로 업데이트
        reply_markup = InlineKeyboardMarkup([])

    elif query.data == "get_analysis":
        chat_id = query.message.chat_id

        # 분석 결과 메시지 먼저 전송
        await query.message.reply_text("식물 상태 분석 결과입니다.")

        # 식물 상태 분석 이미지 전송
        result = await tb.send_image(chat_id)

        # 이미지를 성공적으로 보냈는지 확인
        if result is None:
            # 분석 결과가 없을 경우 알림 메시지 추가 전송
            await query.message.reply_text(
                "분석 결과 이미지를 찾을 수 없습니다."
            )

        await query.message.reply_text("메뉴로 돌아가시려면 \"/start\"를 입력해주세요.")


    elif query.data == "get_timelapse":
        chat_id = query.message.chat_id

        # 메시지 먼저 전송
        await query.message.reply_text("타임랩스를 가져오는 중입니다.")

        # 타임랩스 영상 전송
        result = await tb.send_video(chat_id)
        print("user_interface.py: 타임랩스 전송 성공 여부: ", result)

        await query.message.reply_text("메뉴로 돌아가시려면 \"/start\"를 입력해주세요.")

    elif query.data == "water_setting":
        # 물주기 버튼 생성
        keyboard = [
            [
                InlineKeyboardButton("1. 수동 물주기", callback_data="water_pour"),
            ],
            [
                InlineKeyboardButton("2. 물탱크 잔여량 확인", callback_data="water_tank"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_msg = "버튼을 선택해주세요."

    elif query.data.startswith("water_"):
        # 물주기 버튼 옵션
        if query.data == "water_pour":  # 수동 물주기
            response_msg = (
                "수동 물주기가 작동합니다.\n\n"
                "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
            )
            activate_water_pump()  # 물주기 함수 호출

        elif query.data == "water_tank":  # 물탱크 잔여량 확인
            water_tank = get_current_tank_level_percent()

            response_msg = "현재 물탱크 잔여량입니다."
            response_msg = (
                f"현재 물탱크 잔여량은 {water_tank}입니다.\n\n"
                "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
            )

        keyboard = [
            [
                InlineKeyboardButton("1. 수동 물주기", callback_data="water_pour"),
            ],
            [
                InlineKeyboardButton("2. 물탱크 잔여량 확인", callback_data="water_tank"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    elif query.data == "light_setting":
        # 조명 관리 버튼 생성
        keyboard = [
            [
                InlineKeyboardButton("1. 조명 Off", callback_data="light_off"),
            ],
            [
                InlineKeyboardButton("2. 조명 25% On", callback_data="light_25"),
                InlineKeyboardButton("3. 조명 50% On", callback_data="light_50"),
            ],
            [
                InlineKeyboardButton("4. 조명 75% On", callback_data="light_75"),
                InlineKeyboardButton("5. 조명 100% On", callback_data="light_100"),
            ],
            [
                InlineKeyboardButton("6. 자동 모드로 전환", callback_data="light_auto"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        response_msg = "버튼을 선택해주세요."

    elif query.data.startswith("light_"):
        # 조명 관리
        if query.data == "light_off":  # 조명 끄기
            if turn_off_led():
                response_msg = (
                    "조명을 OFF시켰습니다.\n"
                    "자동 모드로 돌아가려면 자동 모드 전환을 선택해주세요.\n\n"
                    "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
                )
            else:
                response_msg = "조명 설정에 실패했습니다. 다시 시도해주세요."

        elif query.data == "light_25":  # 25% 밝기
            if turn_on_led_with_brightness(25):  # 함수 호출 성공 여부 확인
                response_msg = (
                    "조명 밝기를 25%로 설정합니다.\n"
                    "자동 모드로 돌아가려면 자동 모드 전환을 선택해주세요.\n\n"
                    "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
                )
            else:
                response_msg = "조명 설정에 실패했습니다. 다시 시도해주세요."

        elif query.data == "light_50":  # 50% 밝기
            if turn_on_led_with_brightness(50):
                response_msg = (
                    "조명 밝기를 50%로 설정합니다.\n"
                    "자동 모드로 돌아가려면 자동 모드 전환을 선택해주세요.\n\n"
                    "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
                )
            else:
                response_msg = "조명 설정에 실패했습니다. 다시 시도해주세요."

        elif query.data == "light_75":  # 75% 밝기
            if turn_on_led_with_brightness(75):
                response_msg = (
                    "조명 밝기를 75%로 설정합니다.\n"
                    "자동 모드로 돌아가려면 자동 모드 전환을 선택해주세요.\n\n"
                    "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
                )
            else:
                response_msg = "조명 설정에 실패했습니다. 다시 시도해주세요."

        elif query.data == "light_100":  # 100% 밝기
            if turn_on_led_with_brightness(100):
                response_msg = (
                    "조명 밝기를 100%로 설정합니다.\n"
                    "자동 모드로 돌아가려면 자동 모드 전환을 선택해주세요.\n\n"
                    "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
                )
            else:
                response_msg = "조명 설정에 실패했습니다. 다시 시도해주세요."

        elif query.data == "light_auto":  # 자동 모드 전환
            if switch_to_auto_mode():
                response_msg = (
                    "자동 모드로 전환되었습니다.\n"
                    "이제 조도에 따라 자동으로 조명이 조절됩니다.\n\n"
                    "메뉴로 돌아가시려면 \"/start\"를 입력해주세요."
                )
            else:
                response_msg = "모드 전환에 실패했습니다. 다시 시도해주세요."

        keyboard = [
            [
                InlineKeyboardButton("1. 조명 Off", callback_data="light_off"),
            ],
            [
                InlineKeyboardButton("2. 조명 25% On", callback_data="light_25"),
                InlineKeyboardButton("3. 조명 50% On", callback_data="light_50"),
            ],
            [
                InlineKeyboardButton("4. 조명 75% On", callback_data="light_75"),
                InlineKeyboardButton("5. 조명 100% On", callback_data="light_100"),
            ],
            [
                InlineKeyboardButton("6. 자동 모드로 전환", callback_data="light_auto"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    # 클릭한 버튼에 대한 응답 메시지 전송
    if response_msg:
        # "식물 설정" 메뉴를 클릭했을 때만 식물 선택 버튼을 전송
        if query.data == "help":
            # 기존 버튼을 유지하도록 설정
            await query.edit_message_text(response_msg, reply_markup=query.message.reply_markup)
        else:
            # 메시지와 함께 식물 선택 버튼을 갱신
            await query.edit_message_text(response_msg, reply_markup=reply_markup)


# 사용자 메시지 처리 핸들러 (임의의 메시지에 응답)
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 사용자가 보낸 임의의 메시지에 대해 응답
    await update.message.reply_text("안녕하세요! \n똑똑한 식물 관리 플랫폼\n\"SmartPlantPot\" 입니다.\n시작을 위해 \"/start\"를 입력해주세요.")


# 알 수 없는 명령어 처리 핸들러
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("잘못된 명령어입니다.\n시작을 위해 \"/start\"를 입력해주세요.")


# 메인 함수
async def main():
    # 어플리케이션 생성
    application = Application.builder().token(tb.load_telegram()[0]).build()

    # 핸들러 추가
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # 애플리케이션 실행
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    print("user_interface.py: 텔레그램 봇 실행 중...")

    try:
        while True:
            await asyncio.sleep(1)  # 대기 상태 유지
    except KeyboardInterrupt:
        print("user_interface.py: 텔레그램 봇 종료 중...")
        await application.stop()


# 프로그램 실행
if __name__ == "__main__":
    asyncio.run(main())
