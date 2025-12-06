import os
import json
import threading
import time
from datetime import datetime, timedelta
import requests
import telebot

# ==========================
# CONFIG
# ==========================

BOT_TOKEN = "8569857409:AAEiWTtD_rgxHcJYlr70pjPtENuNn2-2Vc4"
ADMIN_CHAT_ID = -1003302847425  # Telegram user id của admin

BOTS_FILE = "bots.json"
CUSTOMERS_DIR = "customers"
DATA_FILE = os.path.join(CUSTOMERS_DIR, "data.json")
EVENT_LOG_FILE = "event_log.txt"

ADD_JWT_API = "http://103.139.155.35:5000/api/guest_login"
ADDFR_API = "https://ffbd-v2.vercel.app/addfr"
RMFR_API = "https://ffbd-v2.vercel.app/rm"

MAX_USERS_PER_BOT = 3  # mỗi bot tối đa 3 users

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)
data_lock = threading.Lock()


# ==========================
# FILE UTILITIES
# ==========================

def ensure_customers_dir():
    if not os.path.exists(CUSTOMERS_DIR):
        os.makedirs(CUSTOMERS_DIR, exist_ok=True)


def load_bots():
    """Read bots.json"""
    if not os.path.exists(BOTS_FILE):
        return []
    try:
        with open(BOTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except:
        return []


def load_customers_data():
    """
    {
        "customers": [
            {
                "uid": 123,
                "assigned_bot": "bot2",
                "name": "...",
                "social": "...",
                "days": 30,
                "added_at": "YYYY-MM-DD HH:MM:SS",
                "expire_at": "YYYY-MM-DD HH:MM:SS"
            }
        ]
    }
    """
    ensure_customers_dir()
    if not os.path.exists(DATA_FILE):
        return {"customers": []}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        return {"customers": []}

    if "customers" not in data or not isinstance(data["customers"], list):
        data["customers"] = []

    return data


def save_customers_data(data):
    ensure_customers_dir()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def customers_bot_file(bot_id):
    return os.path.join(CUSTOMERS_DIR, f"customers_{bot_id}.json")


def load_customers_bot(bot_id):
    path = customers_bot_file(bot_id)
    if not os.path.exists(path):
        return {"bot_id": bot_id, "uids": []}

    try:
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
    except:
        return {"bot_id": bot_id, "uids": []}

    uids = []
    for u in d.get("uids", []):
        try:
            uids.append(int(u))
        except:
            pass

    return {"bot_id": d.get("bot_id", bot_id), "uids": uids}


def save_customers_bot(bot_id, obj):
    path = customers_bot_file(bot_id)
    safe = {"bot_id": bot_id, "uids": obj.get("uids", [])}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(safe, f, ensure_ascii=False, indent=2)


def uid_exists_in_any_bot(uid_str):
    if not uid_str.isdigit():
        return False
    uid = int(uid_str)

    ensure_customers_dir()
    for fn in os.listdir(CUSTOMERS_DIR):
        if fn.startswith("customers_bot") and fn.endswith(".json"):
            try:
                with open(os.path.join(CUSTOMERS_DIR, fn), "r", encoding="utf-8") as f:
                    d = json.load(f)
                if uid in [int(x) for x in d.get("uids", [])]:
                    return True
            except:
                pass
    return False


def find_bots_containing_uid(uid_str):
    if not uid_str.isdigit():
        return []
    uid = int(uid_str)
    result = []

    for fn in os.listdir(CUSTOMERS_DIR):
        if fn.startswith("customers_bot") and fn.endswith(".json"):
            try:
                p = os.path.join(CUSTOMERS_DIR, fn)
                with open(p, "r", encoding="utf-8") as f:
                    d = json.load(f)
                if uid in [int(x) for x in d.get("uids", [])]:
                    if d.get("bot_id"):
                        result.append(d["bot_id"])
            except:
                pass

    return result


# ==========================
# TIME
# ==========================

def parse_time(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_date_short(dt):
    return f"{dt.day}.{dt.month}.{str(dt.year)[-2:]}"


# ==========================
# JWT / FRIEND API
# ==========================

def get_bot_info_by_id(bot_id, bots):
    for b in bots:
        if b.get("bot_id") == bot_id:
            return b
    return None


def get_jwt_for_bot(bot_uid, bot_pass):
    for attempt in range(3):  # retry 3 lần
        try:
            params = {"uid": str(bot_uid), "password": bot_pass}
            r = requests.get(ADD_JWT_API, params=params, timeout=15)

            if r.status_code != 200:
                err = f"JWT request failed (HTTP {r.status_code})"
            else:
                data = r.json()
                token = data.get("parsed_response", {}).get("token")
                if token:
                    return token, None
                err = "JWT missing token"

        except Exception as e:
            err = str(e)

        time.sleep(0.5)  # delay nhẹ giữa các lần retry

    return None, err  # 3 lần đều fail


def send_friend_request(bot_info, target_uid):
    bot_uid = bot_info["uid"]
    bot_pass = bot_info["password"]

    jwt, err = get_jwt_for_bot(bot_uid, bot_pass)
    if not jwt:
        return False, err

    for attempt in range(3):  # retry add friend 3 lần
        try:
            r = requests.get(ADDFR_API, params={"uid": target_uid, "jwt": jwt}, timeout=15)
            data = r.json()

            if data.get("status") == "success":
                return True, data.get("message", "")

            if "BR_FRIEND_DUPLICATE" in str(data.get("details", "")):
                return True, "BR_FRIEND_DUPLICATE"

            err = str(data)

        except Exception as e:
            err = str(e)

        time.sleep(0.5)

    return False, err  # vẫn fail sau 3 lượt



def remove_friend(bot_info, target_uid):
    bot_uid = bot_info["uid"]
    bot_pass = bot_info["password"]

    jwt, err = get_jwt_for_bot(bot_uid, bot_pass)
    if not jwt:
        return False, err

    try:
        r = requests.get(RMFR_API, params={"uid": target_uid, "jwt": jwt}, timeout=15)
        data = r.json()
        if data.get("status") == "success":
            return True, data.get("message", "")
        return False, str(data)
    except Exception as e:
        return False, str(e)


def remove_uid_from_specific_bots(uid_str, bots, bot_ids):
    results = []
    if uid_str.isdigit():
        uid = int(uid_str)
    else:
        uid = None

    for bot_id in bot_ids:
        bot_info = get_bot_info_by_id(bot_id, bots)
        if not bot_info:
            results.append({"bot_id": bot_id, "ok": False, "msg": "Bot not found"})
            continue

        ok, msg = remove_friend(bot_info, uid_str)

        cf = load_customers_bot(bot_id)
        if uid in cf["uids"]:
            cf["uids"].remove(uid)
            save_customers_bot(bot_id, cf)

        results.append({"bot_id": bot_id, "ok": ok, "msg": msg})

    return results


# ==========================
# CHỌN BOT (không role)
# ==========================

def choose_bot(bots):
    """Chọn bot đầu tiên còn slot."""
    for b in bots:
        bot_id = b["bot_id"]
        cf = load_customers_bot(bot_id)
        if len(cf["uids"]) < MAX_USERS_PER_BOT:
            return b
    return None


# ==========================
# AUTO EXPIRE
# ==========================

def expiry_worker():
    while True:
        try:
            with data_lock:
                bots = load_bots()
                data = load_customers_data()
                customers = data["customers"]

                new_list = []
                today = datetime.now()

                for c in customers:
                    uid = str(c["uid"])
                    exp = parse_time(c["expire_at"])

                    if exp > today:
                        new_list.append(c)
                        continue

                    bot_ids = find_bots_containing_uid(uid)

                    if bot_ids:
                        logs = remove_uid_from_specific_bots(uid, bots, bot_ids)
                        ok = len([x for x in logs if x["ok"]])

                        bot.send_message(
                            ADMIN_CHAT_ID,
                            f"Thông báo hết hạn\nUID {uid}\nThời gian: {format_date_short(today)}\n"
                            f"Đã xóa khỏi {len(bot_ids)} bot (OK: {ok})"
                        )

                data["customers"] = new_list
                save_customers_data(data)

        except Exception as e:
            print("expiry err:", e)

        time.sleep(60)


# ==========================
# PRIVATE CHECK
# ==========================

def is_private(msg):
    return msg.chat.type == "private"


def require_private(func):
    def wrapper(message):
        if not is_private(message):
            return
        return func(message)
    return wrapper


# ==========================
# COMMANDS
# ==========================

@bot.message_handler(commands=["start"])
@require_private
def cmd_start(message):
    bot.send_message(message.chat.id,
        "/add ten mxh uid so_ngay\n"
        "/remove uid\n"
        "/check\n"
        "/check uid\n"
        "/checkbot\n"
        "/checkbot bot1\n"
        "/log uid"
    )


@bot.message_handler(commands=["add"])
@require_private
def cmd_add(message):
    parts = message.text.split()

    # /add name social uid days [bot_id]
    if len(parts) < 5:
        bot.send_message(message.chat.id, "Sai cú pháp. /add ten mxh uid so_ngay [bot]")
        return

    days_str = parts[-1]
    uid_str = parts[-2]
    social = parts[-3]
    name = " ".join(parts[1:-3])

    forced_bot = None
    # Nếu có bot chỉ định
    if "bot" in days_str.lower():
        forced_bot = days_str
        days_str = parts[-2]
        uid_str = parts[-3]
        social = parts[-4]
        name = " ".join(parts[1:-4])


    if not uid_str.isdigit():
        bot.send_message(message.chat.id, "UID phải là số.")
        return

    try:
        days = int(days_str)
    except:
        bot.send_message(message.chat.id, "Ngày không hợp lệ.")
        return

    with data_lock:
        bots = load_bots()
        data = load_customers_data()
        customers = data["customers"]

        # check tồn tại
        if any(str(c["uid"]) == uid_str for c in customers):
            bot.send_message(message.chat.id, "UID đã tồn tại trong data.json.")
            return

        if uid_exists_in_any_bot(uid_str):
            bot.send_message(message.chat.id, "UID đã tồn tại trong customers_botX.json.")
            return

        if forced_bot:
            chosen = get_bot_info_by_id(forced_bot, bots)
            if not chosen:
                bot.send_message(message.chat.id, f"Bot {forced_bot} không tồn tại.")
                return
        else:
            chosen = choose_bot(bots)

        if not chosen:
            bot.send_message(message.chat.id, "Không còn bot nào trống slot.")
            return

        bot_id = chosen["bot_id"]

        ok, msg = send_friend_request(chosen, uid_str)

        if not ok:
            bot.send_message(
                message.chat.id,
                f"Đã thêm khách\nTên: {name}\nMXH: {social}\nUID: {uid_str}\n"
                f"Bot: {bot_id}\nNgày: {days}\nHết hạn: N/A\n"
                f"KB: {ok} - {msg}\n(API retry 3 lần vẫn thất bại)"
            )
            return  # không lưu nếu fail

        # API SUCCESS → mới lưu vào file
        cf = load_customers_bot(bot_id)
        uid = int(uid_str)
        cf["uids"].append(uid)
        save_customers_bot(bot_id, cf)

        now = datetime.now()
        expire = now + timedelta(days=days)

        customers.append({
            "uid": uid,
            "assigned_bot": bot_id,
            "name": name,
            "social": social,
            "days": days,
            "added_at": format_time(now),
            "expire_at": format_time(expire),
        })
        save_customers_data(data)

        bot.send_message(
            message.chat.id,
            f"Đã thêm khách\nTên: {name}\nMXH: {social}\nUID: {uid_str}\n"
            f"Bot: {bot_id}\nNgày: {days}\nHết hạn: {format_date_short(expire)}\n"
            f"KB: {ok} - {msg}"
        )


@bot.message_handler(commands=["remove"])
@require_private
def cmd_remove(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Cú pháp: /remove uid")
        return

    uid_str = parts[1]
    if not uid_str.isdigit():
        bot.send_message(message.chat.id, "UID phải là số.")
        return

    with data_lock:
        bots = load_bots()
        data = load_customers_data()
        customers = data["customers"]

        new_list = [c for c in customers if str(c["uid"]) != uid_str]
        existed_data = len(new_list) != len(customers)

        data["customers"] = new_list
        save_customers_data(data)

        bot_ids = find_bots_containing_uid(uid_str)
        existed_file = len(bot_ids) > 0

        logs = []
        if existed_file:
            logs = remove_uid_from_specific_bots(uid_str, bots, bot_ids)

    if not existed_data and not existed_file:
        bot.send_message(message.chat.id, "UID không tồn tại.")
        return

    lines = [f"{r['bot_id']}: {r['ok']} - {r['msg']}" for r in logs]
    bot.send_message(message.chat.id, "Đã xóa UID:\n" + "\n".join(lines))


@bot.message_handler(commands=["check"])
@require_private
def cmd_check(message):
    parts = message.text.split()
    with data_lock:
        data = load_customers_data()
        customers = data["customers"]

    if len(parts) == 1:
        if not customers:
            bot.send_message(message.chat.id, "Không có khách.")
            return

        today = datetime.now()
        lines = []
        for c in customers:
            exp = parse_time(c["expire_at"])
            left = (exp - today).days
            lines.append(
                f"{c['name']} ({c['social']}) - UID {c['uid']} - Bot {c['assigned_bot']} - "
                f"{c['days']} ngày - còn {left} ngày - hết hạn {format_date_short(exp)}"
            )
        bot.send_message(message.chat.id, "\n".join(lines))
        return

    else:
        uid_str = parts[1]
        m = [c for c in customers if str(c["uid"]) == uid_str]
        if not m:
            bot.send_message(message.chat.id, "Không tìm thấy UID.")
            return

        c = m[0]
        exp = parse_time(c["expire_at"])
        add = parse_time(c["added_at"])
        left = (exp - datetime.now()).days

        bot.send_message(
            message.chat.id,
            f"UID {uid_str}\nTên: {c['name']}\nMXH: {c['social']}\n"
            f"Bot: {c['assigned_bot']}\nGói: {c['days']} ngày\n"
            f"Ngày thêm: {format_date_short(add)}\n"
            f"Ngày hết hạn: {format_date_short(exp)}\n"
            f"Còn lại: {left} ngày"
        )


@bot.message_handler(commands=["checkbot"])
@require_private
def cmd_checkbot(message):
    parts = message.text.split()
    with data_lock:
        bots = load_bots()
        data = load_customers_data()
        customers = data["customers"]

    if len(parts) == 1:
        total = 0
        lines = []

        for b in bots:
            bot_id = b["bot_id"]
            cf = load_customers_bot(bot_id)
            n = len(cf["uids"])
            total += n
            lines.append(f"{bot_id}: {n} users")

        bot.send_message(
            message.chat.id,
            f"Tổng bot: {len(bots)}\nTổng users: {total}\n\n" + "\n".join(lines)
        )
        return

    else:
        bot_id = parts[1]
        cf = load_customers_bot(bot_id)
        uids = cf["uids"]

        if not uids:
            bot.send_message(message.chat.id, f"{bot_id}: 0 users")
            return

        info = {int(c["uid"]): c for c in customers}

        lines = []
        for u in uids:
            if u in info:
                c = info[u]
                lines.append(f"- {u} ({c['name']} / {c['social']} / {c['days']} ngày)")
            else:
                lines.append(f"- {u}")

        bot.send_message(
            message.chat.id,
            f"{bot_id}: {len(uids)} users\n" + "\n".join(lines)
        )


@bot.message_handler(commands=["log"])
@require_private
def cmd_log(message):
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(message.chat.id, "Cú pháp: /log uid")
        return

    uid = parts[1]
    if not os.path.exists(EVENT_LOG_FILE):
        bot.send_message(message.chat.id, "Không tìm thấy file log.")
        return

    try:
        with open(EVENT_LOG_FILE, "r", encoding="utf-8") as f:
            lines = [x.strip("\n") for x in f if uid in x]
    except:
        bot.send_message(message.chat.id, "Lỗi đọc log.")
        return

    if not lines:
        bot.send_message(message.chat.id, "Không có log cho UID này.")
        return

    chunk = ""
    for line in lines:
        if len(chunk) + len(line) > 3500:
            bot.send_message(message.chat.id, chunk)
            chunk = ""
        chunk += line + "\n"

    if chunk:
        bot.send_message(message.chat.id, chunk)


# ==========================
# MAIN
# ==========================

def log_watcher():
    """Theo dõi file event_log.txt và gửi dòng mới vào admin"""
    try:
        # Nếu file không tồn tại, tạo file rỗng
        if not os.path.exists(EVENT_LOG_FILE):
            open(EVENT_LOG_FILE, "w", encoding="utf-8").close()

        with open(EVENT_LOG_FILE, "r", encoding="utf-8") as f:
            # Nhảy đến cuối file
            f.seek(0, os.SEEK_END)

            while True:
                line = f.readline()
                if line:
                    line = line.strip()
                    if line:
                        try:
                            bot.send_message(ADMIN_CHAT_ID, line)
                        except Exception as e:
                            print("Error sending log:", e)
                else:
                    time.sleep(0.2)

    except Exception as e:
        print("Log watcher error:", e)

def main():
    threading.Thread(target=expiry_worker, daemon=True).start()
    threading.Thread(target=log_watcher, daemon=True).start()

    print("Bot running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)



if __name__ == "__main__":
    main()
