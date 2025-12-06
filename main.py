
import requests , os , psutil , sys , jwt , pickle , json , binascii , time , urllib3 , base64 , re , socket , threading , ssl , pytz , aiohttp
from protobuf_decoder.protobuf_decoder import Parser
from xC4 import * ; from xHeaders import *
from google.protobuf.timestamp_pb2 import Timestamp
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from Pb2 import DEcwHisPErMsG_pb2 , MajoRLoGinrEs_pb2 , PorTs_pb2 , MajoRLoGinrEq_pb2 , sQ_pb2 , Team_msg_pb2
from cfonts import render, say
import asyncio
import random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
import json

# VariabLes dyli 
#------------------------------------------#
online_writer = None
whisper_writer = None
spam_room = False
spammer_uid = None
spam_chat_id = None
spam_uid = None
Spy = False
Chat_Leave = False
fast_spam_running = False
fast_spam_task = None
custom_spam_running = False
custom_spam_task = None
spam_request_running = False
spam_request_task = None
vn_vip_spam_running = False
vn_vip_spam_task = None
vn_custom_spam_running = False
vn_custom_spam_task = None
lag_running = False
lag_task = None
#------------------------------------------#

# Emote mapping for evo commands
EMOTE_MAP = {
    1: 909000063, 
    2: 909045001, 
    3: 909000068, 
    4: 909000075, 
    5: 909000081, 
    6: 909042008,
    7: 909000090, 
    8: 909000098, 
    9: 909049010, 
    10: 909042007,
    11: 909040010,
    12: 909039011,
    13: 909000085,
    14: 909035007,
    15: 909051003,
    16: 909038012, 
    17: 909038010,
    18: 909033001,
    19: 909041005,
    20: 909035012,
    21: 909037011,
    22: 909033002
}
FRIEND_LIST = set()

BOT_ID = os.environ.get("BOT_ID", "bot17")
BOT_UID = os.environ.get("BOT_UID", "4322622244")          # UID default nếu chạy 1 bot bình thường
BOT_PASS = os.environ.get("BOT_PASS", "BoAra_DQY5DR2UWFO") # PASS default
import os

# Tạo thư mục nếu chưa tồn tại
os.makedirs("customers", exist_ok=True)

# Cách 2: Đường dẫn tuyệt đối (nếu cần)
FRIEND_LIST_FILE = os.path.join("customers", f"customers_{BOT_ID}.json")
# Load friend list nếu đã tồn tại
try:
    with open(FRIEND_LIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Có thể bạn lưu dạng list hoặc dạng object, ta chuẩn hóa về set UID
        if isinstance(data, dict) and "uids" in data:
            FRIEND_LIST = set(data["uids"])
        elif isinstance(data, list):
            FRIEND_LIST = set(data)
        else:
            FRIEND_LIST = set()
except Exception:
    FRIEND_LIST = set()

server2 = "vn"         # server FF: vn, sg, bd, in...
key2 = "shopboara206"  # key truy cập API like2.vercel
BYPASS_TOKEN = "xxxx"  # token bypass của bạn
TarGeT = "14026442005"        # tuỳ mục đích bạn cần

# ==================== BOARA LIKE SYSTEM (DÙNG 20/100/150/200 API) ====================

def save_friend_list():
    try:
        data = {
            "bot_id": BOT_ID,
            "uids": list(FRIEND_LIST)
        }
        with open(FRIEND_LIST_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[{BOT_ID}] Error saving friend list:", e)

def load_customer_expire(uid):
    try:
        with open("customers/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        for c in data["customers"]:
            if str(c["uid"]) == str(uid):
                expire_at = datetime.strptime(c["expire_at"], "%Y-%m-%d %H:%M:%S")
                now = datetime.now()
                diff = expire_at - now

                days = diff.days
                hours = diff.seconds // 3600

                return days, hours, expire_at.strftime("%Y-%m-%d %H:%M:%S")
        return None
    except Exception as e:
        print("EXPIRE ERROR:", e)
        return None

def masked_uid(uid):
    uid = str(uid)
    if len(uid) <= 6:
        return uid  # quá ngắn, không mask

    return uid[:4] + "xxxxxxx"

def fix_num(x):
    try:
        x = int(x)
        return f"{x:,}"
    except:
        return str(x)

# Helper functions for ghost join
def dec_to_hex(decimal):
    """Convert decimal to hex string"""
    hex_str = hex(decimal)[2:]
    return hex_str.upper() if len(hex_str) % 2 == 0 else '0' + hex_str.upper()

async def encrypt_packet(packet_hex, key, iv):
    """Encrypt packet using AES CBC"""
    cipher = AES.new(key, AES.MODE_CBC, iv)
    packet_bytes = bytes.fromhex(packet_hex)
    padded_packet = pad(packet_bytes, AES.block_size)
    encrypted = cipher.encrypt(padded_packet)
    return encrypted.hex()

async def nmnmmmmn(packet_hex, key, iv):
    """Wrapper for encrypt_packet"""
    return await encrypt_packet(packet_hex, key, iv)

async def ghost_join_packet(player_id, secret_code, key, iv):
    """Create ghost join packet"""
    try:
        # Create a simple packet structure for joining
        # This is a basic implementation - adjust based on your needs
        packet_data = f"01{dec_to_hex(len(secret_code))}{secret_code.encode().hex()}"
        
        # Encrypt the packet
        encrypted_packet = await encrypt_packet(packet_data, key, iv)
        
        # Create header
        header_length = len(encrypted_packet) // 2
        header_length_hex = dec_to_hex(header_length)
        
        # Build final packet based on header length
        if len(header_length_hex) == 2:
            final_packet = "0515000000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 3:
            final_packet = "051500000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 4:
            final_packet = "05150000" + header_length_hex + encrypted_packet
        elif len(header_length_hex) == 5:
            final_packet = "0515000" + header_length_hex + encrypted_packet
        else:
            final_packet = "0515000000" + header_length_hex + encrypted_packet
            
        return bytes.fromhex(final_packet)
        
    except Exception as e:
        print(f"Error creating ghost join packet: {e}")
        return None

async def lag_worker(team_code, key, iv, region):
    """Một worker lag chạy join/leave liên tục"""
    while lag_running:
        try:
            join_packet = await GenJoinSquadsPacket(team_code, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', join_packet)
            await asyncio.sleep(0.005)

            leave_packet = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', leave_packet)
            await asyncio.sleep(0.005)

        except:
            await asyncio.sleep(0.01)

async def lag_team_loop(team_code, key, iv, region):
    global lag_running
    lag_running = True

    start = time.time()
    workers = []

    # 5 luồng lag song song
    for _ in range(5):
        workers.append(asyncio.create_task(lag_worker(team_code, key, iv, region)))

    # Chạy 40s auto stop
    while lag_running:
        if time.time() - start >= 40:
            lag_running = False
            break
        await asyncio.sleep(0.1)

    for w in workers:
        w.cancel()


#CHAT WITH AI
def talk_with_ai(question):
    url = f"https://gemini-api-api-v2.vercel.app/prince/api/v1/ask?key=prince&ask={question}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        msg = data["message"]["content"]
        return msg
    else:
        return "An error occurred while connecting to the server."
#SPAM REQUESTS
def spam_requests(player_id):
    # This URL now correctly points to the Flask app you provided
    url = f"https://like2.vercel.app/send_requests?uid={player_id}&server={server2}&key={key2}"
    try:
        res = requests.get(url, timeout=20) # Added a timeout
        if res.status_code == 200:
            data = res.json()
            # Return a more descriptive message based on the API's JSON response
            return f"API Status: Success [{data.get('success_count', 0)}] Failed [{data.get('failed_count', 0)}]"
        else:
            # Return the error status from the API
            return f"API Error: Status {res.status_code}"
    except requests.exceptions.RequestException as e:
        # Handle cases where the API isn't running or is unreachable
        print(f"Could not connect to spam API: {e}")
        return "Failed to connect to spam API."
####################################

# ** NEW INFO FUNCTION using the new API **
def newinfo(uid):
    try:
        url = f"https://r1-gg.vercel.app/info/vn/{uid}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return {"status": "error", "message": f"API status {response.status_code}"}

        data = response.json()

        # Kiểm tra đúng cấu trúc JSON
        if "basicinfo" not in data:
            return {"status": "wrong_id"}

        b = data["basicinfo"]

        return {
            "status": "ok",
            "info": {
                "AccountName": b.get("nickname", "Unknown"),
                "AccountLevel": b.get("level", "N/A"),
                "AccountLikes": b.get("liked", "N/A"),
                "AccountRegion": b.get("region", "VN"),
                "AccountUid": b.get("accountid", uid)
            }
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

####################################
#CHECK ACCOUNT IS BANNED

Hr = {
    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 11; ASUS_Z01QD Build/PI)",
    'Connection': "Keep-Alive",
    'Accept-Encoding': "gzip",
    'Content-Type': "application/x-www-form-urlencoded",
    'Expect': "100-continue",
    'X-Unity-Version': "2018.4.11f1",
    'X-GA': "v1 1",
    'ReleaseVersion': "OB51"}

# ---- Random Colores ----
def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]",
        "[A52A2A]", "[800080]", "[000000]", "[808080]", "[C0C0C0]", "[FFC0CB]", "[FFD700]", "[ADD8E6]",
        "[90EE90]", "[D2691E]", "[DC143C]", "[00CED1]", "[9400D3]", "[F08080]", "[20B2AA]", "[FF1493]",
        "[7CFC00]", "[B22222]", "[FF4500]", "[DAA520]", "[00BFFF]", "[00FF7F]", "[4682B4]", "[6495ED]",
        "[5F9EA0]", "[DDA0DD]", "[E6E6FA]", "[B0C4DE]", "[556B2F]", "[8FBC8F]", "[2E8B57]", "[3CB371]",
        "[6B8E23]", "[808000]", "[B8860B]", "[CD5C5C]", "[8B0000]", "[FF6347]", "[FF8C00]", "[BDB76B]",
        "[9932CC]", "[8A2BE2]", "[4B0082]", "[6A5ACD]", "[7B68EE]", "[4169E1]", "[1E90FF]", "[191970]",
        "[00008B]", "[000080]", "[008080]", "[008B8B]", "[B0E0E6]", "[AFEEEE]", "[E0FFFF]", "[F5F5DC]",
        "[FAEBD7]"
    ]
    return random.choice(colors)

async def encrypted_proto(encoded_hex):
    key = b'Yg&tc%DEuh6%Zc^8'
    iv = b'6oyZDr22E3ychjM%'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_message = pad(encoded_hex, AES.block_size)
    encrypted_payload = cipher.encrypt(padded_message)
    return encrypted_payload
    
async def GeNeRaTeAccEss(uid , password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    headers = {
        "Host": "100067.connect.garena.com",
        "User-Agent": (await Ua()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close"}
    data = {
        "uid": uid,
        "password": password,
        "response_type": "token",
        "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=Hr, data=data) as response:
            if response.status != 200: return "Failed to get access token"
            data = await response.json()
            open_id = data.get("open_id")
            access_token = data.get("access_token")
            return (open_id, access_token) if open_id and access_token else (None, None)

async def EncRypTMajoRLoGin(open_id, access_token):
    major_login = MajoRLoGinrEq_pb2.MajorLogin()
    major_login.event_time = str(datetime.now())[:-7]
    major_login.game_name = "free fire"
    major_login.platform_id = 1
    major_login.client_version = "1.118.1"
    major_login.system_software = "Android OS 9 / API-28 (PQ3B.190801.10101846/G9650ZHU2ARC6)"
    major_login.system_hardware = "Handheld"
    major_login.telecom_operator = "Verizon"
    major_login.network_type = "WIFI"
    major_login.screen_width = 1920
    major_login.screen_height = 1080
    major_login.screen_dpi = "280"
    major_login.processor_details = "ARM64 FP ASIMD AES VMH | 2865 | 4"
    major_login.memory = 3003
    major_login.gpu_renderer = "Adreno (TM) 640"
    major_login.gpu_version = "OpenGL ES 3.1 v1.46"
    major_login.unique_device_id = "Google|34a7dcdf-a7d5-4cb6-8d7e-3b0e448a0c57"
    major_login.client_ip = "223.191.51.89"
    major_login.language = "en"
    major_login.open_id = open_id
    major_login.open_id_type = "4"
    major_login.device_type = "Handheld"
    memory_available = major_login.memory_available
    memory_available.version = 55
    memory_available.hidden_value = 81
    major_login.access_token = access_token
    major_login.platform_sdk_id = 1
    major_login.network_operator_a = "Verizon"
    major_login.network_type_a = "WIFI"
    major_login.client_using_version = "7428b253defc164018c604a1ebbfebdf"
    major_login.external_storage_total = 36235
    major_login.external_storage_available = 31335
    major_login.internal_storage_total = 2519
    major_login.internal_storage_available = 703
    major_login.game_disk_storage_available = 25010
    major_login.game_disk_storage_total = 26628
    major_login.external_sdcard_avail_storage = 32992
    major_login.external_sdcard_total_storage = 36235
    major_login.login_by = 3
    major_login.library_path = "/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/lib/arm64"
    major_login.reg_avatar = 1
    major_login.library_token = "5b892aaabd688e571f688053118a162b|/data/app/com.dts.freefireth-YPKM8jHEwAJlhpmhDhv5MQ==/base.apk"
    major_login.channel_type = 3
    major_login.cpu_type = 2
    major_login.cpu_architecture = "64"
    major_login.client_version_code = "2019118695"
    major_login.graphics_api = "OpenGLES2"
    major_login.supported_astc_bitset = 16383
    major_login.login_open_id_type = 4
    major_login.analytics_detail = b"FwQVTgUPX1UaUllDDwcWCRBpWA0FUgsvA1snWlBaO1kFYg=="
    major_login.loading_time = 13564
    major_login.release_channel = "android"
    major_login.extra_info = "KqsHTymw5/5GB23YGniUYN2/q47GATrq7eFeRatf0NkwLKEMQ0PK5BKEk72dPflAxUlEBir6Vtey83XqF593qsl8hwY="
    major_login.android_engine_init_flag = 110009
    major_login.if_push = 1
    major_login.is_vpn = 1
    major_login.origin_platform_type = "4"
    major_login.primary_platform_type = "4"
    string = major_login.SerializeToString()
    return  await encrypted_proto(string)

async def MajorLogin(payload):
    url = "https://loginbp.ggblueshark.com/MajorLogin"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def GetLoginData(base_url, payload, token):
    url = f"{base_url}/GetLoginData"
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    Hr['Authorization']= f"Bearer {token}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=Hr, ssl=ssl_context) as response:
            if response.status == 200: return await response.read()
            return None

async def DecRypTMajoRLoGin(MajoRLoGinResPonsE):
    proto = MajoRLoGinrEs_pb2.MajorLoginRes()
    proto.ParseFromString(MajoRLoGinResPonsE)
    return proto

async def DecRypTLoGinDaTa(LoGinDaTa):
    proto = PorTs_pb2.GetLoginData()
    proto.ParseFromString(LoGinDaTa)
    return proto

async def DecodeWhisperMessage(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = DEcwHisPErMsG_pb2.DecodeWhisper()
    proto.ParseFromString(packet)
    return proto
    
async def decode_team_packet(hex_packet):
    packet = bytes.fromhex(hex_packet)
    proto = sQ_pb2.recieved_chat()
    proto.ParseFromString(packet)
    return proto
    
async def xAuThSTarTuP(TarGeT, token, timestamp, key, iv):
    uid_hex = hex(TarGeT)[2:]
    uid_length = len(uid_hex)
    encrypted_timestamp = await DecodE_HeX(timestamp)
    encrypted_account_token = token.encode().hex()
    encrypted_packet = await EnC_PacKeT(encrypted_account_token, key, iv)
    encrypted_packet_length = hex(len(encrypted_packet) // 2)[2:]
    if uid_length == 9: headers = '0000000'
    elif uid_length == 8: headers = '00000000'
    elif uid_length == 10: headers = '000000'
    elif uid_length == 7: headers = '000000000'
    else: print('Unexpected length') ; headers = '0000000'
    return f"0115{headers}{uid_hex}{encrypted_timestamp}00000{encrypted_packet_length}{encrypted_packet}"
     
async def cHTypE(H):
    if not H: return 'Squid'
    elif H == 1: return 'CLan'
    elif H == 2: return 'PrivaTe'
    
async def SEndMsG(H , message , Uid , chat_id , key , iv):
    TypE = await cHTypE(H)

    msg_packet = None  # default value

    if TypE == 'Squid':
        msg_packet = await xSEndMsgsQ(message , chat_id , key , iv)

    elif TypE == 'CLan':
        msg_packet = await xSEndMsg(message , 1 , chat_id , chat_id , key , iv)

    elif TypE == 'PrivaTe':
        msg_packet = await xSEndMsg(message , 2 , Uid , Uid , key , iv)

    return msg_packet



async def SEndPacKeT(OnLinE, ChaT, TypE, PacKeT):
    try:
        if TypE == 'ChaT' and ChaT:
            whisper_writer.write(PacKeT)
            await whisper_writer.drain()
        elif TypE == 'OnLine':
            online_writer.write(PacKeT)
            await online_writer.drain()
    except:
        pass

async def safe_send_message(chat_type, message, target_uid, chat_id, key, iv, max_retries=3):
    """Safely send message with retry mechanism"""
    for attempt in range(max_retries):
        try:
            P = await SEndMsG(chat_type, message, target_uid, chat_id, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
            return True
        except Exception as e:
            print(f"Failed to send message (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(0.5)  # Wait before retry
    return False

async def fast_emote_spam(uids, emote_id, key, iv, region):
    """Fast emote spam function that sends emotes rapidly"""
    global fast_spam_running
    count = 0
    max_count = 25  # Spam 25 times
    
    while fast_spam_running and count < max_count:
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, int(emote_id), key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                await asyncio.sleep(0.1)  # 0.1 seconds interval between spam cycles

# NEW FUNCTION: Custom emote spam with specified times
async def custom_emote_spam(uid, emote_id, times, key, iv, region):
    """Custom emote spam function that sends emotes specified number of times"""
    global custom_spam_running
    count = 0
    
    while custom_spam_running and count < times:
        try:
            uid_int = int(uid)
            H = await Emote_k(uid_int, int(emote_id), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            count += 1
            await asyncio.sleep(0.1)  # 0.1 seconds interval between emotes
        except Exception as e:
            break

# NEW FUNCTION: Faster spam request loop - Sends exactly 30 requests quickly
async def spam_request_loop(uid, target_uid, key, iv, region):
    """Spam request function that creates group and sends join requests in loop - FASTER VERSION"""
    global spam_request_running
    count = 0
    max_requests = 30  # Send exactly 30 requests
    
    while spam_request_running and count < max_requests:
        try:
            # Create squad
            PAc = await OpEnSq(key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
            await asyncio.sleep(0.2)  # Reduced delay
            
            # Send invite
            V = await SEnd_InV(5, int(target_uid), key, iv, region)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
            
            # Leave squad immediately without waiting
            E = await ExiT(None, key, iv)
            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
            # Shorter delay between requests
            await asyncio.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
            
        except Exception as e:
            await asyncio.sleep(0.5)
        with open("event_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{BOT_ID}] UID {uid} -> Send Spam Request to UID {target_uid}\n")
# NEW FUNCTION: Evolution emote spam with mapping
async def evo_emote_spam(uids, number, key, iv, region):
    """Send evolution emotes based on number mapping"""
    try:
        emote_id = EMOTE_MAP.get(int(number))
        if not emote_id:
            return False, f"Invalid number! Use 1-22 only."
        
        success_count = 0
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                success_count += 1
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f"Error sending evo emote to {uid}: {e}")
        
        return True, f"Sent evolution emote {number} (ID: {emote_id}) to {success_count} player(s)"
    
    except Exception as e:
        return False, f"Error in evo_emote_spam: {str(e)}"

# NEW FUNCTION: Fast evolution emote spam
async def vn_vip_emote_spam(uids, number, key, iv, region):
    """Fast evolution emote spam function"""
    global vn_vip_spam_running
    count = 0
    max_count = 25  # Spam 25 times
    
    emote_id = EMOTE_MAP.get(int(number))
    if not emote_id:
        return False, f"Số không hợp lệ! Chỉ sử ⅾụng từ 1 đến 22."
    
    while vn_vip_spam_running and count < max_count:
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                print(f"Error in vn_vip_emote_spam for uid {uid}: {e}")
        
        count += 1
        await asyncio.sleep(0.1)  # CHANGED: 0.5 seconds to 0.1 seconds
    
    return True, f"Completed fast evolution emote spam {count} times"

# NEW FUNCTION: Custom evolution emote spam with specified times
async def vn_custom_emote_spam(uids, number, times, key, iv, region):
    """Custom evolution emote spam with specified repeat times"""
    global vn_custom_spam_running
    count = 0
    
    emote_id = EMOTE_MAP.get(int(number))
    if not emote_id:
        return False, f"Invalid number! Use 1-22 only."
    
    while vn_custom_spam_running and count < times:
        for uid in uids:
            try:
                uid_int = int(uid)
                H = await Emote_k(uid_int, emote_id, key, iv, region)
                await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
            except Exception as e:
                print(f"Error in vn_custom_emote_spam for uid {uid}: {e}")
        
        count += 1
        await asyncio.sleep(0.1)  # CHANGED: 0.5 seconds to 0.1 seconds
    
    return True, f"Completed custom evolution emote spam {count} times"

async def TcPOnLine(ip, port, key, iv, AutHToKen, reconnect_delay=0.5):
    global online_writer , spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , XX , uid , Spy,data2, Chat_Leave, fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task, spam_request_running, spam_request_task, vn_vip_spam_running, vn_vip_spam_task, vn_custom_spam_running, vn_custom_spam_task, lag_running, lag_task
    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            online_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            online_writer.write(bytes_payload)
            await online_writer.drain()
            while True:
                data2 = await reader.read(9999)
                if not data2: break
                
                if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                    try:
                        packet = await DeCode_PackEt(data2.hex()[10:])
                        # ============================
                        # LẤY DANH SÁCH BẠN BÈ TỪ GÓI 0500
                        # ============================
                        global FRIEND_LIST
                        if "FriendList" in packet:
                            FRIEND_LIST = [u["uid"] for u in packet["FriendList"]]
                            print("[F-LIST] Loaded", len(FRIEND_LIST), "friends")

                        packet = json.loads(packet)
                        OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                        JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                        await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , JoinCHaT)


                        message = f'[B][C]{get_random_color()}\n- WeLComE To Emote Bot ! '
                        P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                        await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)

                    except:
                        if data2.hex().startswith('0500') and len(data2.hex()) > 1000:
                            try:
                                packet = await DeCode_PackEt(data2.hex()[10:])
                                packet = json.loads(packet)
                                OwNer_UiD , CHaT_CoDe , SQuAD_CoDe = await GeTSQDaTa(packet)

                                JoinCHaT = await AutH_Chat(3 , OwNer_UiD , CHaT_CoDe, key,iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , JoinCHaT)


                                message = f'[B][C]{get_random_color()}\n- WeLComE To Emote Bot ! \n\n{get_random_color()}- Commands : @a {xMsGFixinG('player_uid')} {xMsGFixinG('909000001')}\n\n[00FF00]Dev : @{xMsGFixinG('ROSHAN')}'
                                P = await SEndMsG(0 , message , OwNer_UiD , OwNer_UiD , key , iv)
                                await SEndPacKeT(whisper_writer , online_writer , 'ChaT' , P)
                            except:
                                pass

            online_writer.close() ; await online_writer.wait_closed() ; online_writer = None

        except Exception as e: online_writer = None
        await asyncio.sleep(reconnect_delay)
                            
async def TcPChaT(ip, port, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region , reconnect_delay=0.5):
    global spam_room , whisper_writer , spammer_uid , spam_chat_id , spam_uid , online_writer , chat_id , XX , uid , Spy,data2, Chat_Leave, fast_spam_running, fast_spam_task, custom_spam_running, custom_spam_task, spam_request_running, spam_request_task, vn_vip_spam_running, vn_vip_spam_task, vn_custom_spam_running, vn_custom_spam_task, lag_running, lag_task

    while True:
        try:
            reader , writer = await asyncio.open_connection(ip, int(port))
            whisper_writer = writer
            bytes_payload = bytes.fromhex(AutHToKen)
            whisper_writer.write(bytes_payload)
            await whisper_writer.drain()
            ready_event.set()
            if LoGinDaTaUncRypTinG.Clan_ID:
                clan_id = LoGinDaTaUncRypTinG.Clan_ID
                clan_compiled_data = LoGinDaTaUncRypTinG.Clan_Compiled_Data
                print('\n - TarGeT BoT in CLan ! ')
                print(f' - Clan Uid > {clan_id}')
                print(f' - BoT ConnEcTed WiTh CLan ChaT SuccEssFuLy ! ')
                pK = await AuthClan(clan_id , clan_compiled_data , key , iv)
                if whisper_writer: whisper_writer.write(pK) ; await whisper_writer.drain()
            while True:
                data = await reader.read(9999)
                if not data: break
                
                if data.hex().startswith("120000"):

                    msg = await DeCode_PackEt(data.hex()[10:])
                    chatdata = json.loads(msg)
                    try:
                        response = await DecodeWhisperMessage(data.hex()[10:])
                        uid = response.Data.uid
                        chat_id = response.Data.Chat_ID
                        XX = response.Data.chat_type
                        inPuTMsG = response.Data.msg.lower()
                        if "Chào bạn mới. Hôm nào làm ván nhỉ?" in inPuTMsG:
                            try:
                                api = f"https://danger-info-alpha.vercel.app/accinfo?uid={uid}&key=DANGERxINFO"
                                r = requests.get(api, timeout=10).json()
                                name = r.get("name", "bạn")

                                reply = f"[00FF00]Chào {name}! Rất vui được làm quen.\n\nMình là bot do @boaraoffical tạo~\n\nBạn vui lòng dùng lệnh help, menu, hoặc hi để gọi mình nhé!"
                                P = await SEndMsG(response.Data.chat_type, reply, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                            except Exception as e:
                                print("AUTO-REPLY ERROR:", e)

                    except:
                        response = None

                    if response:
                        # ALL COMMANDS NOW WORK IN ALL CHAT TYPES (SQUAD, GUILD, PRIVATE)
                        
                        # AI Command - /ai
                        if inPuTMsG.strip().startswith('/ai '):
                            print('Processing AI command in any chat type')
                            
                            question = inPuTMsG[4:].strip()
                            if question:
                                initial_message = f"[B][C]{get_random_color()}\n🤖 AI is thinking...\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                # Use ThreadPoolExecutor to avoid blocking the async loop
                                loop = asyncio.get_event_loop()
                                with ThreadPoolExecutor() as executor:
                                    ai_response = await loop.run_in_executor(executor, talk_with_ai, question)
                                
                                # Format the AI response
                                ai_message = f"""
[B][C][00FF00]🤖 AI Response:

[FFFFFF]{ai_response}

[C][B][FFB300]Question: [FFFFFF]{question}
"""
                                await safe_send_message(response.Data.chat_type, ai_message, uid, chat_id, key, iv)
                            else:
                                error_msg = f"[B][C][FF0000]❌ ERROR! Please provide a question after /ai\nExample: /ai What is Free Fire?\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

#                         if inPuTMsG.strip().lower().startswith("/info"):

#                             # luôn tạo parts, bất kể user nhập đúng hay sai
#                             parts = inPuTMsG.strip().split()

#                             # nếu chỉ nhập /info không có UID
#                             if len(parts) < 2:
#                                 err = "[FF0000]USAGE: /info <uid>"
#                                 await safe_send_message(response.Data.chat_type, err, uid, chat_id, key, iv)
#                                 return

#                         target_uid = parts[1]

#                         # gửi thông báo loading
#                         load = f"[b][c][008080]Fetching info for UID: {target_uid}..."
#                         await safe_send_message(response.Data.chat_type, load, uid, chat_id, key, iv)

#                         # chạy API trong threadpool
#                         loop = asyncio.get_event_loop()
#                         with ThreadPoolExecutor() as exe:
#                             resp = await loop.run_in_executor(exe, newinfo, target_uid)

#                         # nếu API fail
#                         if resp["status"] != "ok":
#                             msg = "[FF0000]INVALID UID OR API ERROR"
#                             await safe_send_message(response.Data.chat_type, msg, uid, chat_id, key, iv)
#                             return

#                         info = resp["info"]

#                         msg = f"""
# [b][c][00ff00]PLAYER INFO (VN)

# [ffffff]Name: [00ff00]{info['AccountName']}
# [ffffff]UID: [00ff00]{info['AccountUid']}
# [ffffff]Region: [00ff00]{info['AccountRegion']}
# [ffffff]Level: [00ff00]{info['AccountLevel']}
# [ffffff]Likes: [00ff00]{info['AccountLikes']}
# """
#                         await safe_send_message(response.Data.chat_type, msg, uid, chat_id, key, iv)



                        # Invite Command - /inv (creates 5-player group and sends request)
                        if inPuTMsG.strip().lower().startswith("join "):
                            parts = inPuTMsG.strip().split()

                            # Sai cú pháp
                            if len(parts) != 2:
                                msg = "[B][C][FF0000]Sai cú pháp!\n[B][C][FFFFFF]join [teamcode]"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, "ChaT", P)
                                continue

                            team_code = parts[1]

                            # Thực hiện join
                            try:
                                join_packet = await GenJoinSquadsPacket(team_code, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, "OnLine", join_packet)

                                msg = f"\n\n[B][C][FFFFFF]Đã gửi yêu cầu join teamcode {team_code}\n\n"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, "ChaT", P)

                            except:
                                msg = f"[B][C][FF0000]Join team {team_code} thất bại!"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, "ChaT", P)

                            continue
                                                # -------------------- CUSTOM LIKE COMMAND --------------------
                        parts = inPuTMsG.strip().split()

                        if len(parts) >= 1 and parts[0].lower() == "like":
                            try:
                                if len(parts) < 2:
                                    msg = "[FF0000]Sai cú pháp!\nDùng: like [uid]"
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                target_uid = parts[1]

                                # kiểm tra uid hợp lệ
                                if not target_uid.isdigit() or not (8 <= len(target_uid) <= 11):
                                    msg = "[FF0000]UID không hợp lệ!"
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue
                                masked = masked_uid(target_uid)
                                msg = f"[00FF00]Đang gửi like đến UID: {masked}"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                # --------------------- API LIKE MỚI ---------------------
                                api_url = f"https://your-like-api/like?uid={target_uid}"

                                try:
                                    r = requests.get(api_url, timeout=12)
                                    data_like = r.json()
                                except:
                                    msg = "[FF0000]API lỗi hoặc không phản hồi."
                                    P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                    continue

                                # ---- PARSE RESULT ----
                                if "Failse" in data_like:
                                    if data_like["Failse"] == "Max likes today":
                                        msg = "[FF0000]Max likes hôm nay!"
                                    else:
                                        msg = f"[FF0000]{data_like['Failse']}"
                                else:
                                    msg = f"[00FF00]Đã gửi like thành công đến {masked}"

                                # SEND RESULT
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                            except Exception as e:
                                print("LIKE ERROR:", e)
                                continue




                        if inPuTMsG.startswith(("6")):
                            # Process /6 command - Create 4 player group
                            initial_message = f"\n\n[B][C][B][C][FFFFFF]Đã Gửi ɭời Mời Vào Nhóm 6...\n\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite for 4 players
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(6, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(6, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f"[B][C][00FF00]✅ THÀNH CÔNG! Lời mời Nhóm 6 người chơi đã được gửi thành công đến  {uid}!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                        if inPuTMsG.startswith(("3")):
                            # Process /3 command - Create 3 player group
                            initial_message = f"\n\n[B][C][FFFFFF]Đã Gửi ɭời Mời Vào Nhóm 3...\n\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite for 6 players
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(3, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(3, uid, key, iv, region)
                            await asyncio.sleep(0.3)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f"[B][C][00FF00]✅ THÀNH CÔNG! Lời mời Nhóm 6 người chơi đã được gửi thành công đến {uid}!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                        if inPuTMsG.startswith(("5")):
                            # Process /5 command in any chat type
                            initial_message = f"\n\n[B][C][FFFFFF]Đã Gửi ɭời Mời Vào Nhóm 5...\n\n"
                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                            
                            # Fast squad creation and invite
                            PAc = await OpEnSq(key, iv, region)
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', PAc)
                            
                            C = await cHSq(5, uid, key, iv, region)
                            await asyncio.sleep(0.3)  # Reduced delay
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', C)
                            
                            V = await SEnd_InV(5, uid, key, iv, region)
                            await asyncio.sleep(0.3)  # Reduced delay
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', V)
                            
                            E = await ExiT(None, key, iv)
                            await asyncio.sleep(3.5)  # Reduced from 3 seconds
                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', E)
                            
                            # SUCCESS MESSAGE
                            success_message = f"[B][C][00FF00]✅ THÀNH CÔNG! Lời mời nhóm đã được gửi thành công đến {uid}!\n"
                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                        # FIXED JOIN COMMAND
                        if inPuTMsG.startswith('join'):
                            CodE = None
                            # Process /join command in any chat type
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]Cách sử ⅾụng:\n\n[B][C][FFFFFF]join [teamcode]\n\nVí ⅾụ: join 984734\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)                                
                                try:
                                    # Try using the regular join method first
                                    EM = await GenJoinSquadsPacket(CodE, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'OnLine', EM)
                                    
                                    # SUCCESS MESSAGE
                                    success_message = f"[B][C][FFFFFF]Đã tham gia teamcode: {CodE}!\n"
                                    await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                                    
                                except Exception as e:
                                    print(f"Regular join failed, trying ghost join: {e}")
                                    # If regular join fails, try ghost join
                                    try:
                                        # Get bot's UID from global context or login data
                                        bot_uid = LoGinDaTaUncRypTinG.AccountUID if hasattr(LoGinDaTaUncRypTinG, 'AccountUID') else TarGeT
                                        
                                        ghost_packet = await ghost_join_packet(bot_uid, CodE, key, iv)
                                        if ghost_packet:
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ghost_packet)
                                            success_message = f"[B][C][00FF00]✅ THÀNH CÔNG! Ghost gia nhập đội với mã : {CodE}!\n"
                                            await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                                        else:
                                            error_msg = f"[B][C][FF0000]❌ LỖI! Không tạo được gói tin ghost join .\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                            
                                    except Exception as ghost_error:
                                        print(f"Ghost join also failed: {ghost_error}")
                                        error_msg = f"[B][C][FF0000]❌ ERROR! Failed to join squad: {str(ghost_error)}\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW GHOST COMMAND
                        if inPuTMsG.strip().startswith('/ghost'):
                            # Process /ghost command in any chat type
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]❌ ERROR! Usage: /ghost (team_code)\nExample: /ghost ABC123\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                CodE = parts[1]
                                initial_message = f"[B][C]{get_random_color()}\nGhost joining squad with code: {CodE}...\n"
                                await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                
                                try:
                                    # Get bot's UID from global context or login data
                                    bot_uid = LoGinDaTaUncRypTinG.AccountUID if hasattr(LoGinDaTaUncRypTinG, 'AccountUID') else TarGeT
                                    
                                    ghost_packet = await ghost_join_packet(bot_uid, CodE, key, iv)
                                    if ghost_packet:
                                        await SEndPacKeT(whisper_writer, online_writer, 'OnLine', ghost_packet)
                                        success_message = f"[B][C][00FF00]✅ SUCCESS! Ghost joined squad with code: {CodE}!\n"
                                        await safe_send_message(response.Data.chat_type, success_message, uid, chat_id, key, iv)
                                    else:
                                        error_msg = f"[B][C][FF0000]❌ ERROR! Failed to create ghost join packet.\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        
                                except Exception as e:
                                    error_msg = f"[B][C][FF0000]❌ ERROR! Ghost join failed: {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW LAG COMMAND
                        if inPuTMsG.strip().startswith('lag'):
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]Cách dùng:\n\n[B][C][FFFFFF]lag [team_code]\n\nVí ⅾụ: lag 483841"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                team_code = parts[1]

                                # Stop task cũ nếu tồn tại
                                if lag_task and not lag_task.done():
                                    lag_running = False
                                    lag_task.cancel()
                                    await asyncio.sleep(0.1)

                                # Start lag mới
                                lag_running = True
                                lag_task = asyncio.create_task(lag_team_loop(team_code, key, iv, region))

                                # Gửi thông báo bắt đầu
                                success_msg = (
                                    f"[B][C][FF0000]Bắt đầu lag team [FFFFFF]{team_code}\n\n"
                                    f"[B][C][FF0000]Thời gian: 40 giây\n\n"
                                    f"[B][C][FFFFFF]Bot sẽ tự dừng sau khi hoàn tất."
                                )
                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                with open("event_log.txt", "a", encoding="utf-8") as f:
                                        f.write(f"[{BOT_ID}] UID {uid} -> Send Lag To Teamcode {team_code}\n")
                        # Spam request command - works in all chat types
                        if inPuTMsG.strip().startswith('spam '):
                            print('Processing spam request in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]Cách sử ⅾụng: spam [uid]\n\nVí ⅾụ: spam 1738672506\n"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                try:
                                    target_uid = parts[1]
                                    
                                    # Stop any existing spam request
                                    if spam_request_task and not spam_request_task.done():
                                        spam_request_running = False
                                        spam_request_task.cancel()
                                        await asyncio.sleep(0.1)
                                    
                                    # Start new spam request
                                    spam_request_running = True
                                    spam_request_task = asyncio.create_task(spam_request_loop(target_uid, key, iv, region))
                                    
                                    # SUCCESS MESSAGE
                                    success_msg = f"\n\n[B][C][FF0000]Đã Gửi Spam Đến UID [B][C][FFFFFF]{target_uid}!"
                                    await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                        
                                except Exception as e:
                                    error_msg = f"[B][C][FF0000]Lỗi {str(e)}\n"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)

                        # NEW EVO COMMANDS
                        if inPuTMsG.strip().startswith('e '):
                            print('Processing evo command in any chat type')
                            
                            parts = inPuTMsG.strip().split()
                            if len(parts) < 2:
                                error_msg = f"[B][C][FF0000]Cách sử ⅾụng: e [uid1-4] [1-22]\n\nVí ⅾụ: e 1738672506 2143424256 38277... 1\n\nLưu ý: Phải mời bot vào nhóm trước bằng lệnh 'join teamcode'"
                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                            else:
                                # Parse uids and number
                                uids = []
                                number = None
                                
                                for part in parts[1:]:
                                    if part.isdigit():
                                        if len(part) <= 2:  # Number should be 1-22 (1 or 2 digits)
                                            number = part
                                        else:
                                            uids.append(part)
                                    else:
                                        break
                                
                                if not number and parts[-1].isdigit() and len(parts[-1]) <= 2:
                                    number = parts[-1]  
                                
                                if not uids or not number:
                                    error_msg = f"[B][C][FF0000]Cách sử ⅾụng:\n\n[B][C][FFFFFF]e [uid1] [uid2] [uid3] [uid4] [1-22]"
                                    await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                else:
                                    try:
                                        number_int = int(number)
                                        if number_int not in EMOTE_MAP:
                                            error_msg = f"[B][C][FF0000]Lỗi:\n\n[B][C][FF0000]Chỉ chọn số từ 1-22!\n"
                                            await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        else:
                                            initial_message = f"[B][C]{get_random_color()}\nSending evolution emote {number_int}...\n"
                                            await safe_send_message(response.Data.chat_type, initial_message, uid, chat_id, key, iv)
                                            
                                            success, result_msg = await evo_emote_spam(uids, number_int, key, iv, region)
                                            
                                            if success:
                                                success_msg = f"[B][C][00FF00]✅ SUCCESS! {result_msg}\n"
                                                await safe_send_message(response.Data.chat_type, success_msg, uid, chat_id, key, iv)
                                            else:
                                                error_msg = f"[B][C][FF0000]❌ ERROR! {result_msg}\n"
                                                await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                            
                                    except ValueError:
                                        error_msg = f"[B][C][FF0000]❌ ERROR! Invalid number format! Use 1-21 only.\n"
                                        await safe_send_message(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                        if inPuTMsG.strip().startswith('f '):
                            try:
                                parts = inPuTMsG.strip().split()
                                if len(parts) < 2:
                                    message = f"[B][C][FF0000]Vui Lòng Nhập 1 UID!\n\n[B][C][FFFFFF]Ví ⅾụ: f 1738672506"
                                    P = await SEndMsG(response.Data.chat_type, message, uid, chat_id, key, iv)
                                    await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                raw_uids = parts[1:6]
                                validated_uids = []
                                invalid_found = False
                                for u in raw_uids:
                                    if not u.isdigit():
                                        error_msg = f"[B][C][FF0000]Cách sử ⅾụng:\n\n[B][C][FFFFFF]f [uid]"
                                        P = await SEndMsG(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                        invalid_found = True
                                    if not (8 <= len(u) <= 11):
                                        error_msg = f"[B][C][FF0000]Cách sử ⅾụng:\n\n[B][C][FFFFFF]f [uid]"
                                        P = await SEndMsG(response.Data.chat_type, error_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)
                                        invalid_found = True
                                    validated_uids.append(int(u))
                                if invalid_found:
                                    continue
                                target_uids = validated_uids
                                default_emotes = [
                                    909045001, 909035007, 909049010, 909041005, 909038010,
                                    909039011, 909040010, 909000081, 909000085, 909000063,
                                    909000075, 909033001, 909000090, 909000068, 909000098,
                                    909051003, 909037011, 909038012, 909035012, 909042008,
                                    909033002, 909042007
                                ]

                                msg = f"[B][C][FF0000]Đang thực hiện hành động...\n\n[B][C][FFFFFF]UID: {len(target_uids)}"
                                P = await SEndMsG(response.Data.chat_type, msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', P)

                                async def emote_for_uid(target_uid):
                                    try:
                                        for emo_id in default_emotes:
                                            H = await Emote_k(target_uid, emo_id, key, iv, region)
                                            await SEndPacKeT(whisper_writer, online_writer, 'OnLine', H)
                                            await asyncio.sleep(7)

                                        done_msg = f"[B][C][FFDE21]Hoàn tất chuỗi emote cho UID {target_uid}"
                                        D = await SEndMsG(response.Data.chat_type, done_msg, uid, chat_id, key, iv)
                                        await SEndPacKeT(whisper_writer, online_writer, 'ChaT', D)
                                    except Exception as e:
                                        print(f"Error")

                                tasks = [asyncio.create_task(emote_for_uid(t_uid)) for t_uid in target_uids]
                                await asyncio.gather(*tasks)

                                finish_msg = f"[B][C][FFDE21]Hoàn tất toàn bộ emote cho UID{len(target_uids)}"
                                F = await SEndMsG(response.Data.chat_type, finish_msg, uid, chat_id, key, iv)
                                await SEndPacKeT(whisper_writer, online_writer, 'ChaT', F)

                            except Exception as e:
                                print(f"Error")        

                        # FIXED HELP MENU SYSTEM - Now detects commands properly
                        if inPuTMsG.strip().lower() in ("help", "menu", "hi", "bot"):
                            FRIEND_LIST.add(uid)
                            exp = load_customer_expire(uid)
                            if exp:
                                days, hours, exp_time = exp
                            
                            masked = masked_uid(uid)
                            with open("event_log.txt", "a", encoding="utf-8") as f:
                                f.write(f"[{BOT_ID}] Added -> UID {uid}\n")
                            save_friend_list()

                            # Menu 1 - Basic Commands
                            menu1 = f'''[C][B][FFFFFF]UID: {masked}
[C][B][FFFFFF]Hết hạn: {days} ngày {hours} giờ


[C][B][FFED29]                  BẢNG LỆNH


[FF0000]LIKE:                      [FFFFFF]like uid

[FF0000]TEAM 3:                [FFFFFF]3
[FF0000]TEAM 5:                [FFFFFF]5
[FF0000]TEAM 6:                [FFFFFF]6

[FF0000]LAG:                       [FFFFFF]lag teamcode
[FF0000]SPAM:                   [FFFFFF]spam uid

[FF0000]MỜI BOT:             [FFFFFF]join teamcode
[FF0000]HĐ:                      [FFFFFF]e [uid1-4] [1-22]
[FF0000]FULL HĐ:             [FFFFFF]f [uid1-4]


[C][B][FFED29]         Tiҡtok: @boaraoffical
'''
                            
                            await safe_send_message(response.Data.chat_type, menu1, uid, chat_id, key, iv)
                        response = None
                            
            whisper_writer.close() ; await whisper_writer.wait_closed() ; whisper_writer = None      	
        except Exception as e: print(f"ErroR {ip}:{port} - {e}") ; whisper_writer = None
        await asyncio.sleep(reconnect_delay)

async def MaiiiinE():
    Uid = BOT_UID
    Pw = BOT_PASS

    

    open_id , access_token = await GeNeRaTeAccEss(Uid , Pw)
    if not open_id or not access_token: print("ErroR - InvaLid AccounT") ; return None
    
    PyL = await EncRypTMajoRLoGin(open_id , access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE: print("TarGeT AccounT => BannEd / NoT ReGisTeReD ! ") ; return None
    
    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    region = MajoRLoGinauTh.region

    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp
    
    LoGinDaTa = await GetLoginData(UrL , PyL , ToKen)
    if not LoGinDaTa: print("ErroR - GeTinG PorTs From LoGin DaTa !") ; return None
    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP , OnLineporT = OnLinePorTs.split(":")
    ChaTiP , ChaTporT = ChaTPorTs.split(":")
    acc_name = LoGinDaTaUncRypTinG.AccountName
    #print(acc_name)
    equie_emote(ToKen,UrL)
    AutHToKen = await xAuThSTarTuP(int(TarGeT) , ToKen , int(timestamp) , key , iv)
    ready_event = asyncio.Event()
    
    task1 = asyncio.create_task(TcPChaT(ChaTiP, ChaTporT , AutHToKen , key , iv , LoGinDaTaUncRypTinG , ready_event ,region))
     
    await ready_event.wait()
    await asyncio.sleep(1)
    task2 = asyncio.create_task(TcPOnLine(OnLineiP , OnLineporT , key , iv , AutHToKen))
    print(f"\033[{BOT_ID}] -> {BOT_UID}: STATUS ONLINE ✅\033[0m")
    await asyncio.gather(task1 , task2)
    
async def StarTinG():
    while True:
        try: await asyncio.wait_for(MaiiiinE() , timeout = 7 * 60 * 60)
        except asyncio.TimeoutError: print("Token ExpiRed ! , ResTartinG")
        except Exception as e: print(f"{e} => ResTarTinG ...")

if __name__ == '__main__':
    asyncio.run(StarTinG())