import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Select
import json, os, asyncio, aiohttp, datetime, re, random, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io, requests, colorsys, pytz

# ═══════════════════════════════════════════════════════
#  KONFIGURASI
# ═══════════════════════════════════════════════════════
TOKEN                   = os.environ["TOKEN"]
OWNER_ID                = int(os.environ["OWNER_ID"])
SPAM_CHANNEL_ID         = int(os.environ["SPAM_CHANNEL_ID"])
TIKTOK_USERNAME         = os.environ["TIKTOK_USERNAME"]
TIKTOK_CHECK_CHANNEL_ID = int(os.environ["TIKTOK_CHECK_CHANNEL_ID"])
TICKET_CHANNEL_ID       = int(os.environ["TICKET_CHANNEL_ID"])
VOICE_CATEGORY_ID       = int(os.environ["VOICE_CATEGORY_ID"])
ADMIN_BANK_ID           = "483284166268420096"   # ID admin bank — sumber hadiah game

WIB = pytz.timezone("Asia/Jakarta")

# ═══════════════════════════════════════════════════════
#  FILE DATABASE
# ═══════════════════════════════════════════════════════
DATA_FILE        = "data.json"
LAST_TIKTOK_FILE = "last_tiktok.json"
YOUTUBE_FILE     = "youtube.json"
TICKET_FILE      = "tickets.json"
VERIF_FILE       = "verif.json"
WARN_FILE        = "warns.json"
GIVEAWAY_FILE    = "giveaways.json"
QUOTE_FILE       = "quotes.json"
SETTINGS_FILE    = "settings.json"
AFK_FILE         = "afk.json"
BANNER_FILE      = "banners.json"
CUSTOM_CMD_FILE  = "custom_commands.json"
COIN_FILE        = "coins.json"
MARKET_FILE      = "market.json"
INVENTORY_FILE   = "inventory.json"
DAILY_FILE       = "daily.json"
HISTORY_FILE     = "history.json"
DUEL_FILE        = "duel.json"
ACTIVITY_FILE    = "activity.json"   # tracking aktivitas game harian untuk pajak
REACT_ROLE_FILE  = "react_roles.json"
AUTOMOD_FILE     = "automod.json"
WELCOME_CFG_FILE = "welcome_config.json"
POLLS_FILE       = "polls.json"
JOIN_TRACKING_FILE = "join_tracking.json"   # tracking kapan user join server
BCASH_REWARD_FILE  = "bcash_reward_channels.json"  # channel yang beri Bcash saat pesan

# ═══════════════════════════════════════════════════════
#  LEVEL CONFIG
# ═══════════════════════════════════════════════════════
LEVEL_CONFIG = {
    1: {"name": "Bot",          "xp_required": 0,    "color": (108, 117, 125)},
    2: {"name": "Side Brother", "xp_required": 100,  "color": (23, 162, 184)},
    3: {"name": "Member",       "xp_required": 300,  "color": (40, 167, 69)},
    4: {"name": "Brother",      "xp_required": 700,  "color": (255, 193, 7)},
    5: {"name": "Big Brother",  "xp_required": 1500, "color": (220, 53, 69)},
}
XP_PER_MESSAGE = 10

# Banner rarity config per level range
BANNER_RARITY = {
    "Common":    {"levels": [1, 2],    "color": (150, 150, 150), "chance": 60},
    "Uncommon":  {"levels": [2, 3],    "color": (80, 200, 80),   "chance": 25},
    "Rare":      {"levels": [3, 4],    "color": (80, 120, 255),  "chance": 10},
    "Epic":      {"levels": [4, 5],    "color": (180, 80, 255),  "chance": 4},
    "Legendary": {"levels": [5, 5],    "color": (255, 200, 0),   "chance": 1},
}

# ═══════════════════════════════════════════════════════
#  QUOTES DATABASE (100 quotes)
# ═══════════════════════════════════════════════════════
DEFAULT_QUOTES = [
    "Jangan hitung hari, buat setiap hari diperhitungkan.",
    "Kesuksesan adalah jumlah dari usaha-usaha kecil yang diulang setiap hari.",
    "Jatuh tujuh kali, bangkit delapan kali.",
    "Mimpi tidak bekerja kecuali kamu bekerja.",
    "Setiap hari adalah kesempatan baru untuk menjadi lebih baik.",
    "Kegagalan adalah awal dari kesuksesan.",
    "Percayai prosesnya, hasil tidak pernah mengkhianati usaha.",
    "Jangan takut gagal, takutlah tidak pernah mencoba.",
    "Orang sukses melakukan apa yang orang malas hindari.",
    "Kamu lebih kuat dari yang kamu kira.",
    "Mulailah dari mana kamu berada, gunakan apa yang kamu punya.",
    "Satu langkah kecil hari ini lebih baik dari seribu rencana besok.",
    "Karakter terbentuk bukan saat hidup mudah, tapi saat menghadapi cobaan.",
    "Jangan bandingkan perjalananmu dengan orang lain.",
    "Waktu yang kamu nikmati adalah waktu yang tidak terbuang.",
    "Kesabaran adalah kunci dari segala keberhasilan.",
    "Berani bermimpi besar, tapi mulai dari langkah kecil.",
    "Hidup terlalu singkat untuk menyimpan dendam.",
    "Bersyukur adalah magnet untuk hal-hal baik.",
    "Versi terbaik dari dirimu sedang menunggumu di depan.",
    "Tidak ada jalan pintas menuju tempat yang layak dituju.",
    "Disiplin adalah jembatan antara tujuan dan pencapaian.",
    "Keberanian bukan ketiadaan rasa takut, tapi tetap melangkah meski takut.",
    "Hidup bukan tentang menemukan dirimu, tapi menciptakan dirimu.",
    "Setiap orang punya cerita, jangan nilai buku dari sampulnya.",
    "Yang kamu pikirkan, itulah yang akan menjadi kenyataanmu.",
    "Jangan menunggu sempurna, mulai saja dulu.",
    "Masa depan milik mereka yang percaya pada keindahan impian mereka.",
    "Ribuan mil dimulai dari satu langkah.",
    "Kebahagiaan bukan tujuan, melainkan cara menjalani hidup.",
    "Jadilah perubahan yang ingin kamu lihat di dunia.",
    "Jika kamu tidak bisa terbang, larilah. Jika tidak bisa lari, berjalanlah.",
    "Tidak ada yang impossible bagi mereka yang mau berusaha.",
    "Hidup adalah 10% apa yang terjadi padamu dan 90% bagaimana kamu meresponsnya.",
    "Orang hebat tidak lahir, mereka dibentuk.",
    "Kamu tidak perlu jadi hebat untuk memulai, tapi kamu perlu memulai untuk jadi hebat.",
    "Belajarlah dari kemarin, hiduplah untuk hari ini, berharaplah untuk esok.",
    "Jangan biarkan ketakutan masa lalu merusak kebahagiaan masa depan.",
    "Senyum adalah senjata paling murah namun paling efektif.",
    "Jadikan setiap momen berarti, karena waktu tidak bisa diputar kembali.",
    "Tekad yang kuat adalah kunci membuka pintu kesempatan.",
    "Kegagalan hanya berakhir saat kamu berhenti mencoba.",
    "Impian tanpa tindakan hanyalah angan-angan.",
    "Jadilah cahaya di tengah kegelapan.",
    "Kamu adalah arsitek dari takdirmu sendiri.",
    "Keberhasilan sejati adalah membantu orang lain berhasil.",
    "Jangan biarkan suara keraguan mengalahkan suara harapan.",
    "Kreativitas lahir dari keberanian untuk berbeda.",
    "Yang membedakan pemenang dan pecundang hanyalah kemauan.",
    "Hidup singkat, buat setiap detiknya layak dikenang.",
    "Kepercayaan diri adalah modal utama meraih sukses.",
    "Kamu tidak bisa kembali ke awal, tapi bisa mulai dari sini.",
    "Jadikan kritik sebagai bahan bakar, bukan racun.",
    "Setiap matahari terbit membawa kesempatan baru.",
    "Kesederhanaan adalah keanggunan sejati.",
    "Orang yang tidak pernah salah adalah orang yang tidak pernah mencoba.",
    "Pikiran positif menghasilkan energi positif.",
    "Jangan takut berbeda, jadilah unik.",
    "Kerendahan hati adalah mahkota orang yang bijak.",
    "Bertumbuh itu menyakitkan, tapi tidak bertumbuh lebih menyakitkan.",
    "Doa tanpa usaha adalah omong kosong, usaha tanpa doa adalah kesombongan.",
    "Yang kamu tanam hari ini akan kamu panen esok hari.",
    "Jadilah orang yang kamu butuhkan saat kamu kecil.",
    "Hidup bukan tentang menghindari badai, tapi belajar menari di tengah hujan.",
    "Keikhlasan adalah kunci ketenangan jiwa.",
    "Jangan takut bermimpi, takutlah tidak berani mewujudkannya.",
    "Setiap kesulitan pasti ada kemudahan.",
    "Waktu adalah investasi paling berharga.",
    "Jangan biarkan orang lain mendefinisikan siapa dirimu.",
    "Kamu bisa mengubah arah angin, tapi kamu bisa mengatur layarmu.",
    "Ribuan kegagalan adalah tangga menuju satu kesuksesan.",
    "Jadilah produktif, bukan sekedar sibuk.",
    "Hargai prosesnya, bukan hanya hasilnya.",
    "Diam bukan berarti lemah, kadang diam adalah strategi.",
    "Jangan tunda kebaikan, lakukan sekarang.",
    "Yang membuat kamu berbeda adalah kekuatanmu, bukan kelemahanmu.",
    "Kesehatan adalah investasi terbaik.",
    "Bukan tentang seberapa keras kamu jatuh, tapi seberapa cepat kamu bangkit.",
    "Jadikan pengalaman buruk sebagai pelajaran terbaik.",
    "Fokus pada apa yang bisa kamu kendalikan.",
    "Berikan yang terbaik, sisanya biarkan Tuhan yang mengurus.",
    "Keberanian adalah otot, semakin sering dilatih semakin kuat.",
    "Satu buku bisa mengubah hidupmu.",
    "Jangan remehkan kekuatan niat yang tulus.",
    "Setiap orang adalah guru, setiap tempat adalah sekolah.",
    "Hidup itu singkat, jangan habiskan untuk hal yang tidak bermakna.",
    "Kepedulianmu kepada orang lain adalah cerminan hatimu.",
    "Jadilah versi terbaik dirimu, bukan tiruan terbaik orang lain.",
    "Kamu tidak perlu izin siapapun untuk menjadi dirimu sendiri.",
    "Semangat pagi adalah bensin untuk hari yang produktif.",
    "Percayalah, semua akan indah pada waktunya.",
    "Jangan berhenti belajar karena hidup tidak pernah berhenti mengajar.",
    "Ketulusan hati adalah harta yang tidak ternilai.",
    "Jadikan hidupmu sebagai inspirasi, bukan sensasi.",
    "Yang penting bukan seberapa lama kamu hidup, tapi seberapa bermakna hidupmu.",
    "Teruslah berjalan meski jalannya terjal, karena pemandangan terbaik ada di puncak.",
    "Jangan biarkan masa lalu mencuri masa depanmu.",
    "Kamu adalah keajaiban yang sedang berjalan.",
]

# ═══════════════════════════════════════════════════════
#  BOT INIT
# ═══════════════════════════════════════════════════════
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
active_voice_rooms = {}

WELCOME_BONUS_FILE = "welcome_bonus.json"   # track siapa yg sudah dapat bonus
WELCOME_BONUS_AMOUNT = 50                   # 50 Bcash untuk pemain baru
FIRSTPLAY_BONUS_FILE = "firstplay.json"     # track siapa yg sudah dapat bonus first-play di #spam
FIRSTPLAY_BONUS_AMOUNT = 10                 # 10 Bcash tiap pertama coba main game di #spam

def load_welcome_bonus():
    return load_json(WELCOME_BONUS_FILE, default={})

def save_welcome_bonus(d):
    save_json(WELCOME_BONUS_FILE, d)

def load_firstplay():
    return load_json(FIRSTPLAY_BONUS_FILE, default={})

def save_firstplay(d):
    save_json(FIRSTPLAY_BONUS_FILE, d)

def give_firstplay_bonus(uid: str, display_name: str) -> int:
    """Beri bonus 10 Bcash saat user pertama kali mencoba game di #spam. Return jumlah bonus (0 jika sudah dapat)."""
    uid = str(uid)
    data = load_firstplay()
    if uid in data:
        return 0
    data[uid] = True
    save_firstplay(data)
    ensure_coins(uid)
    # Mint Bcash baru untuk bonus firstplay
    add_coins(uid, FIRSTPLAY_BONUS_AMOUNT)
    mint_coins(FIRSTPLAY_BONUS_AMOUNT)
    log_history(uid, "🎮 Bonus pertama main game", +FIRSTPLAY_BONUS_AMOUNT)
    return FIRSTPLAY_BONUS_AMOUNT

# ═══════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════
def is_admin(member) -> bool:
    """Cek apakah user adalah admin/owner. Aman dipakai di DM (discord.User) maupun server (discord.Member)."""
    # Cek owner ID terlebih dahulu — selalu true tidak peduli konteks
    if member.id == OWNER_ID:
        return True
    # Cek berdasarkan environment variable OWNER_ID (failsafe jika OWNER_ID belum di-set)
    try:
        owner_id_env = int(os.environ.get("OWNER_ID", "0"))
        if member.id == owner_id_env:
            return True
    except Exception:
        pass
    # Jika sudah discord.Member (di server), langsung cek permissions
    if isinstance(member, discord.Member):
        return member.guild_permissions.administrator or member.guild_permissions.manage_guild
    # discord.User (dari DM) → cari member object di semua guild yang bot ikuti
    for guild in bot.guilds:
        m = guild.get_member(member.id)
        if m:
            if m.id == OWNER_ID:
                return True
            if m.guild_permissions.administrator or m.guild_permissions.manage_guild:
                return True
    return False

def is_game_channel(ctx) -> bool:
    """Cek apakah command dijalankan di channel game (SPAM_CHANNEL_ID). DM selalu ditolak."""
    if isinstance(ctx.channel, discord.DMChannel):
        return False
    return ctx.channel.id == SPAM_CHANNEL_ID

def game_channel_msg(ctx):
    return f"⚠️ {ctx.author.mention} Command ini hanya bisa digunakan di <#{SPAM_CHANNEL_ID}>!"

def load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_data():         return load_json(DATA_FILE)
def save_data(d):        save_json(DATA_FILE, d)
def load_last_tiktok():  return load_json(LAST_TIKTOK_FILE)
def save_last_tiktok(d): save_json(LAST_TIKTOK_FILE, d)
def load_youtube():      return load_json(YOUTUBE_FILE)
def save_youtube(d):     save_json(YOUTUBE_FILE, d)
def load_tickets():      return load_json(TICKET_FILE)
def save_tickets(d):     save_json(TICKET_FILE, d)
def load_verif():        return load_json(VERIF_FILE)
def save_verif(d):       save_json(VERIF_FILE, d)
def load_warns():        return load_json(WARN_FILE)
def save_warns(d):       save_json(WARN_FILE, d)
def load_giveaways():    return load_json(GIVEAWAY_FILE)
def save_giveaways(d):   save_json(GIVEAWAY_FILE, d)
def load_settings():     return load_json(SETTINGS_FILE)
def save_settings(d):    save_json(SETTINGS_FILE, d)
def load_afk():          return load_json(AFK_FILE)
def save_afk(d):         save_json(AFK_FILE, d)
def load_banners():      return load_json(BANNER_FILE)
def save_banners(d):     save_json(BANNER_FILE, d)
def load_react_roles():  return load_json(REACT_ROLE_FILE, default={})
def save_react_roles(d): save_json(REACT_ROLE_FILE, d)
def load_automod():      return load_json(AUTOMOD_FILE, default={"enabled": True, "threshold": 5, "interval": 5, "mute_duration": 60})
def save_automod(d):     save_json(AUTOMOD_FILE, d)
def load_welcome_cfg():  return load_json(WELCOME_CFG_FILE, default={"welcome_channel": None, "leave_channel": None})
def save_welcome_cfg(d): save_json(WELCOME_CFG_FILE, d)
def load_polls():        return load_json(POLLS_FILE, default={})
def save_polls(d):       save_json(POLLS_FILE, d)
def load_join_tracking():  return load_json(JOIN_TRACKING_FILE, default={})
def save_join_tracking(d): save_json(JOIN_TRACKING_FILE, d)
def load_bcash_reward_channels(): return load_json(BCASH_REWARD_FILE, default={})
def save_bcash_reward_channels(d): save_json(BCASH_REWARD_FILE, d)

def load_quotes():
    q = load_json(QUOTE_FILE, default=[])
    if not q:
        save_json(QUOTE_FILE, DEFAULT_QUOTES)
        return DEFAULT_QUOTES
    return q

def get_level(xp):
    current_level = 1
    for lvl in sorted(LEVEL_CONFIG.keys(), reverse=True):
        if xp >= LEVEL_CONFIG[lvl]["xp_required"]:
            current_level = lvl
            break
    return current_level

def get_xp_for_next_level(level):
    next_level = level + 1
    if next_level > max(LEVEL_CONFIG.keys()):
        return None
    return LEVEL_CONFIG[next_level]["xp_required"]

# ═══════════════════════════════════════════════════════
#  BANNER GENERATOR — Anime Style
# ═══════════════════════════════════════════════════════
RARITY_ORDER = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]

def assign_banner(user_id: int, level: int) -> dict:
    """Tentukan rarity banner berdasarkan level, lalu generate seed unik per user."""
    banners = load_banners()
    uid = str(user_id)

    # Jika sudah punya banner dan belum level up, return yang ada
    if uid in banners:
        stored = banners[uid]
        current_rarity_idx = RARITY_ORDER.index(stored["rarity"])
        # Upgrade banner jika level naik ke threshold baru
        new_rarity = get_rarity_for_level(level)
        new_rarity_idx = RARITY_ORDER.index(new_rarity)
        if new_rarity_idx > current_rarity_idx:
            stored["rarity"] = new_rarity
            stored["rarity_color"] = BANNER_RARITY[new_rarity]["color"]
            banners[uid] = stored
            save_banners(banners)
        return banners[uid]

    # Banner baru — seed unik dari user_id
    rarity = get_rarity_for_level(level)
    seed = user_id % 1000  # 0-999 untuk variasi warna
    banners[uid] = {
        "rarity": rarity,
        "rarity_color": BANNER_RARITY[rarity]["color"],
        "seed": seed,
        "theme": seed % 8,  # 8 tema anime berbeda
    }
    save_banners(banners)
    return banners[uid]

def get_rarity_for_level(level: int) -> str:
    if level >= 5:
        return random.choices(
            ["Legendary", "Epic", "Rare"],
            weights=[20, 50, 30]
        )[0]
    elif level >= 4:
        return random.choices(
            ["Epic", "Rare", "Uncommon"],
            weights=[25, 45, 30]
        )[0]
    elif level >= 3:
        return random.choices(
            ["Rare", "Uncommon", "Common"],
            weights=[20, 50, 30]
        )[0]
    elif level >= 2:
        return random.choices(
            ["Uncommon", "Common"],
            weights=[35, 65]
        )[0]
    else:
        return "Common"

def draw_anime_banner(draw, W, H, theme: int, seed: int, rarity: str):
    """Generate banner anime-style berdasarkan tema dan seed."""
    random.seed(seed)
    rc = BANNER_RARITY[rarity]["color"]

    themes = {
        0: draw_theme_sakura,
        1: draw_theme_galaxy,
        2: draw_theme_cyber,
        3: draw_theme_ocean,
        4: draw_theme_fire,
        5: draw_theme_forest,
        6: draw_theme_moonlight,
        7: draw_theme_aurora,
    }
    fn = themes.get(theme % 8, draw_theme_galaxy)
    fn(draw, W, H, rc, seed)

def draw_theme_sakura(draw, W, H, rc, seed):
    random.seed(seed)
    # Gradient pink-putih
    for y in range(H):
        r = int(255 - (y/H)*60)
        g = int(180 - (y/H)*80)
        b = int(200 - (y/H)*50)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Bunga sakura
    for _ in range(18):
        x, y = random.randint(0,W), random.randint(0,H)
        size = random.randint(6,18)
        for petal in range(5):
            angle = petal * 72
            px = x + int(size * math.cos(math.radians(angle)))
            py = y + int(size * math.sin(math.radians(angle)))
            draw.ellipse([px-size//3, py-size//3, px+size//3, py+size//3],
                         fill=(255, 180+random.randint(-20,20), 200, 180))
    # Kelopak jatuh
    for _ in range(30):
        x,y = random.randint(0,W), random.randint(0,H)
        draw.ellipse([x,y,x+5,y+8], fill=(255,200,210))

def draw_theme_galaxy(draw, W, H, rc, seed):
    random.seed(seed)
    # Gradient gelap ungu-biru
    for y in range(H):
        r = int(10 + (y/H)*30)
        g = int(5 + (y/H)*20)
        b = int(40 + (y/H)*60)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Bintang
    for _ in range(80):
        x,y = random.randint(0,W), random.randint(0,H)
        s = random.choice([1,1,1,2,3])
        br = random.randint(180,255)
        draw.ellipse([x,y,x+s,y+s], fill=(br,br,br))
    # Nebula warna
    for _ in range(6):
        x,y = random.randint(0,W), random.randint(0,H)
        r2 = random.randint(30,80)
        col = (random.randint(80,180), random.randint(40,120), random.randint(150,255), 60)
        for dr in range(r2,0,-5):
            alpha = int(80*(1-dr/r2))
            draw.ellipse([x-dr,y-dr,x+dr,y+dr],
                         fill=(col[0],col[1],col[2]))

def draw_theme_cyber(draw, W, H, rc, seed):
    random.seed(seed)
    # Latar hitam
    draw.rectangle([0,0,W,H], fill=(5,5,15))
    # Grid
    for x in range(0,W,30):
        draw.line([(x,0),(x,H)], fill=(0,80,120,40), width=1)
    for y in range(0,H,20):
        draw.line([(0,y),(W,y)], fill=(0,80,120,40), width=1)
    # Garis neon
    for _ in range(8):
        x1,y1 = random.randint(0,W), random.randint(0,H)
        x2,y2 = random.randint(0,W), random.randint(0,H)
        col = random.choice([(0,255,200),(255,0,128),(0,180,255),(200,0,255)])
        draw.line([(x1,y1),(x2,y2)], fill=col, width=2)
    # Hexagon
    for _ in range(5):
        cx,cy = random.randint(20,W-20), random.randint(10,H-10)
        r2 = random.randint(15,35)
        pts = [(cx+int(r2*math.cos(math.radians(60*i))),
                cy+int(r2*math.sin(math.radians(60*i)))) for i in range(6)]
        draw.polygon(pts, outline=(0,255,200), fill=None)

def draw_theme_ocean(draw, W, H, rc, seed):
    random.seed(seed)
    for y in range(H):
        r = int(0 + (y/H)*20)
        g = int(80 + (y/H)*60)
        b = int(150 + (y/H)*80)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Gelombang
    for wave in range(5):
        pts = []
        offset = random.randint(0,30)
        for x in range(0,W+1,5):
            y2 = int(H*0.3 + wave*25 + 15*math.sin((x+offset*wave)/30))
            pts.append((x,y2))
        pts += [(W,H),(0,H)]
        alpha_col = (0,100+wave*15,180+wave*10)
        draw.polygon(pts, fill=alpha_col)
    # Gelembung
    for _ in range(20):
        x,y = random.randint(0,W), random.randint(0,H)
        r2 = random.randint(3,12)
        draw.ellipse([x-r2,y-r2,x+r2,y+r2], outline=(180,230,255), width=1)

def draw_theme_fire(draw, W, H, rc, seed):
    random.seed(seed)
    for y in range(H):
        r = min(255,int(150+(y/H)*100))
        g = int(50*(1-y/H))
        b = 0
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Lidah api
    for _ in range(12):
        cx = random.randint(0,W)
        h2 = random.randint(H//4, H)
        w2 = random.randint(10,40)
        pts = [(cx-w2,H),(cx+w2,H),(cx+w2//3,H-h2),(cx-w2//3,H-h2)]
        col = random.choice([(255,200,0),(255,120,0),(255,60,0)])
        draw.polygon(pts, fill=col)
    # Percikan
    for _ in range(40):
        x,y = random.randint(0,W), random.randint(0,H)
        draw.ellipse([x,y,x+3,y+3], fill=(255,220,100))

def draw_theme_forest(draw, W, H, rc, seed):
    random.seed(seed)
    for y in range(H):
        r = int(20+(y/H)*30)
        g = int(60+(y/H)*80)
        b = int(20+(y/H)*20)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Pohon
    for _ in range(8):
        cx = random.randint(0,W)
        h2 = random.randint(40,H)
        w2 = random.randint(20,50)
        # Batang
        draw.rectangle([cx-5,H-h2//2,cx+5,H], fill=(80,50,20))
        # Daun
        for layer in range(3):
            lh = h2-layer*15
            lw = w2-layer*8
            pts = [(cx,H-h2-layer*20),(cx-lw,H-lh//2),(cx+lw,H-lh//2)]
            col = (random.randint(30,80),random.randint(120,180),random.randint(30,70))
            draw.polygon(pts, fill=col)
    # Kunang-kunang
    for _ in range(20):
        x,y = random.randint(0,W), random.randint(0,H//2)
        draw.ellipse([x,y,x+4,y+4], fill=(220,255,100))

def draw_theme_moonlight(draw, W, H, rc, seed):
    random.seed(seed)
    for y in range(H):
        r = int(10+(y/H)*20)
        g = int(10+(y/H)*20)
        b = int(40+(y/H)*60)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Bulan
    draw.ellipse([W-80,5,W-20,55], fill=(255,250,200))
    draw.ellipse([W-65,5,W-10,55], fill=(20,20,60))
    # Bintang
    for _ in range(60):
        x,y = random.randint(0,W), random.randint(0,H*2//3)
        s = random.choice([1,1,2])
        br = random.randint(150,255)
        draw.ellipse([x,y,x+s,y+s], fill=(br,br,br))
    # Pantulan di air
    for i in range(3):
        y2 = H-10-i*8
        draw.line([(W//2-30+i*5,y2),(W//2+30-i*5,y2)], fill=(255,250,150), width=2)

def draw_theme_aurora(draw, W, H, rc, seed):
    random.seed(seed)
    for y in range(H):
        r = int(5+(y/H)*15)
        g = int(10+(y/H)*30)
        b = int(30+(y/H)*50)
        draw.line([(0,y),(W,y)], fill=(r,g,b))
    # Aurora curtain
    colors = [(0,255,150),(0,200,255),(150,0,255),(255,100,200)]
    for i, col in enumerate(colors):
        for x in range(0,W,4):
            wave_h = int(H*0.5 + 40*math.sin((x/W*4*math.pi)+i))
            draw.line([(x,0),(x,wave_h)],
                      fill=(col[0],col[1],col[2]), width=3)
    # Bintang
    for _ in range(50):
        x,y = random.randint(0,W), random.randint(0,H//2)
        br = random.randint(150,255)
        draw.ellipse([x,y,x+2,y+2], fill=(br,br,br))

# ═══════════════════════════════════════════════════════
#  RANK CARD GENERATOR — Diperbaiki
# ═══════════════════════════════════════════════════════
def create_rank_card(username, avatar_bytes, xp, level, user_id):
    W, H = 760, 220
    card = Image.new("RGBA", (W, H), (0,0,0,255))
    draw = ImageDraw.Draw(card)

    # Banner
    banner_data = assign_banner(user_id, level)
    theme = banner_data.get("theme", 0)
    seed  = banner_data.get("seed", 0)
    rarity = banner_data.get("rarity", "Common")
    draw_anime_banner(draw, W, H, theme, seed, rarity)

    # Overlay gelap semi-transparan bawah
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    ov_draw = ImageDraw.Draw(overlay)
    ov_draw.rectangle([0, H//2, W, H], fill=(0,0,0,160))
    card = Image.alpha_composite(card, overlay)
    draw = ImageDraw.Draw(card)

    level_color = LEVEL_CONFIG[level]["color"]
    rc = BANNER_RARITY[rarity]["color"]

    # Avatar
    avatar_size = 110
    av_x, av_y = 20, H//2 - avatar_size//2
    try:
        av_img = Image.open(io.BytesIO(avatar_bytes)).resize((avatar_size, avatar_size)).convert("RGBA")
        mask = Image.new("L", (avatar_size, avatar_size), 0)
        ImageDraw.Draw(mask).ellipse((0,0,avatar_size,avatar_size), fill=255)
        av_img.putalpha(mask)
        # Border avatar
        border_size = avatar_size + 6
        border_img = Image.new("RGBA", (border_size, border_size), (0,0,0,0))
        ImageDraw.Draw(border_img).ellipse((0,0,border_size,border_size), fill=(*rc,255))
        card.paste(border_img, (av_x-3, av_y-3), border_img)
        card.paste(av_img, (av_x, av_y), av_img)
    except Exception:
        draw.ellipse([av_x,av_y,av_x+avatar_size,av_y+avatar_size], fill=(60,60,80))

    # Font
    try:
        font_name  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_level = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_xp    = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception:
        font_name = font_level = font_small = font_xp = ImageFont.load_default()

    tx = av_x + avatar_size + 18
    ty = H//2 - 10

    # Username
    draw.text((tx, ty - 50), username[:20], fill=(255,255,255), font=font_name)

    # Level badge
    badge_text = f"LV.{level}"
    badge_w = 60
    draw.rounded_rectangle([tx, ty-20, tx+badge_w, ty+4], radius=8, fill=(*level_color,220))
    draw.text((tx+8, ty-18), badge_text, fill=(255,255,255), font=font_level)

    # Level name
    draw.text((tx+badge_w+10, ty-18), LEVEL_CONFIG[level]['name'], fill=(*level_color,), font=font_level)

    # Rarity badge
    rarity_colors = {
        "Common": (150,150,150), "Uncommon": (80,200,80),
        "Rare": (80,120,255), "Epic": (180,80,255), "Legendary": (255,200,0)
    }
    rc2 = rarity_colors.get(rarity, (150,150,150))
    draw.rounded_rectangle([tx, ty+10, tx+100, ty+30], radius=6, fill=(*rc2,200))
    draw.text((tx+6, ty+12), f"✦ {rarity}", fill=(255,255,255), font=font_xp)

    # XP bar
    bar_x = tx
    bar_y = ty + 40
    bar_w = W - tx - 20
    bar_h = 16

    next_xp = get_xp_for_next_level(level)
    progress = min(xp / next_xp, 1.0) if next_xp else 1.0
    xp_text = f"{xp} / {next_xp} XP" if next_xp else f"{xp} XP  ✦ MAX"

    # Bar background
    draw.rounded_rectangle([bar_x, bar_y, bar_x+bar_w, bar_y+bar_h], radius=8, fill=(40,40,60))
    # Bar fill
    fill_w = max(int(bar_w * progress), 0)
    if fill_w > 0:
        # Gradient bar
        for i in range(fill_w):
            t = i / max(fill_w,1)
            r2 = int(level_color[0]*0.6 + level_color[0]*0.4*t)
            g2 = int(level_color[1]*0.6 + level_color[1]*0.4*t)
            b2 = int(level_color[2]*0.6 + level_color[2]*0.4*t)
            draw.line([(bar_x+i, bar_y+1),(bar_x+i, bar_y+bar_h-1)], fill=(r2,g2,b2))
        # Shine
        draw.rounded_rectangle([bar_x, bar_y, bar_x+fill_w, bar_y+bar_h//2], radius=6, fill=(255,255,255,40))

    # XP text di dalam bar
    draw.text((bar_x+5, bar_y+1), xp_text, fill=(220,220,220), font=font_xp)

    # Footer
    draw.text((W-160, H-20), "✦ Asisten Lurah BFL", fill=(200,200,200,180), font=font_xp)

    buf = io.BytesIO()
    card.save(buf, format="PNG")
    buf.seek(0)
    return buf

# ═══════════════════════════════════════════════════════
#  VERIF VIEW
# ═══════════════════════════════════════════════════════
class VerifView(View):
    def __init__(self, applicant_id: int, guild_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.guild_id     = guild_id
        self.chosen_role  = None

    @discord.ui.select(
        placeholder="Pilih role yang akan diberikan...",
        options=[
            discord.SelectOption(label="Moderator", value="Moderator", emoji="🛡️"),
            discord.SelectOption(label="Stream",    value="Stream",    emoji="🎥"),
            discord.SelectOption(label="Clipper",   value="Clipper",   emoji="✂️"),
        ]
    )
    async def select_role(self, interaction: discord.Interaction, select: Select):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Hanya owner.", ephemeral=True)
            return
        self.chosen_role = select.values[0]
        await interaction.response.send_message(f"Role **{self.chosen_role}** dipilih. Klik ACC.", ephemeral=True)

    @discord.ui.button(label="✅ ACC", style=discord.ButtonStyle.success)
    async def acc_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Hanya owner.", ephemeral=True)
            return
        if not self.chosen_role:
            await interaction.response.send_message("⚠️ Pilih role dulu.", ephemeral=True)
            return
        guild = bot.get_guild(self.guild_id)
        if not guild:
            await interaction.response.send_message("❌ Server tidak ditemukan.", ephemeral=True)
            return
        try:
            member = guild.get_member(self.applicant_id) or await guild.fetch_member(self.applicant_id)
        except Exception:
            await interaction.response.send_message("❌ Member tidak ditemukan.", ephemeral=True)
            return
        role = discord.utils.get(guild.roles, name=self.chosen_role)
        if not role:
            await interaction.response.send_message(f"❌ Role **{self.chosen_role}** tidak ada.", ephemeral=True)
            return
        await member.add_roles(role)
        try:
            await member.send(f"🎉 Verifikasi **disetujui**! Role **{self.chosen_role}** telah diberikan.")
        except Exception:
            pass
        await interaction.response.edit_message(
            content=f"✅ Role **{self.chosen_role}** → **{member.display_name}**.", view=None)
        verif = load_verif()
        verif.pop(str(self.applicant_id), None)
        save_verif(verif)

    @discord.ui.button(label="❌ REJECT", style=discord.ButtonStyle.danger)
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message("❌ Hanya owner.", ephemeral=True)
            return
        guild  = bot.get_guild(self.guild_id)
        member = None
        if guild:
            try:
                member = guild.get_member(self.applicant_id) or await guild.fetch_member(self.applicant_id)
            except Exception:
                pass
        if member:
            try:
                await member.send("❌ Verifikasi **ditolak**. Coba lagi dengan bukti lebih jelas.")
            except Exception:
                pass
        name = member.display_name if member else str(self.applicant_id)
        await interaction.response.edit_message(content=f"❌ Verifikasi **{name}** ditolak.", view=None)
        verif = load_verif()
        verif.pop(str(self.applicant_id), None)
        save_verif(verif)

# ═══════════════════════════════════════════════════════
#  TICKET VIEW
# ═══════════════════════════════════════════════════════
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📩 Buat Laporan / Diskusi", style=discord.ButtonStyle.primary, custom_id="buat_ticket")
    async def buat_ticket(self, interaction: discord.Interaction, button: Button):
        guild   = interaction.guild
        member  = interaction.user
        tickets = load_tickets()

        for tid, tdata in tickets.items():
            if tdata["user_id"] == member.id and tdata["status"] == "open":
                await interaction.response.send_message(f"⚠️ Ticket aktif: <#{tid}>", ephemeral=True)
                return

        await interaction.response.defer(ephemeral=True)
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }
            for role in guild.roles:
                if role.permissions.administrator or role.permissions.manage_guild:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            ticket_channel = await guild.create_text_channel(
                name=f"ticket-{member.display_name}", overwrites=overwrites,
                reason=f"Ticket oleh {member}"
            )
            tickets[str(ticket_channel.id)] = {
                "user_id": member.id, "status": "open",
                "created_at": str(datetime.datetime.utcnow())
            }
            save_tickets(tickets)

            embed = discord.Embed(
                title="📩 Ticket Dibuat",
                description=(
                    f"Halo {member.mention}!\n\n"
                    "Jelaskan laporan atau pertanyaan kamu.\n"
                    "Admin akan segera merespons.\n\n"
                    "Klik **Tutup Ticket** jika sudah selesai."
                ),
                color=discord.Color.blue(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text="Asisten Lurah BFL • Ticket System")
            await ticket_channel.send(content=f"{member.mention}", embed=embed,
                                       view=CloseTicketView(ticket_channel.id))
            await interaction.followup.send(f"✅ Ticket: {ticket_channel.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ Bot tidak punya izin Manage Channels.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: `{e}`", ephemeral=True)

class CloseTicketView(View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="🔒 Tutup Ticket", style=discord.ButtonStyle.danger, custom_id="tutup_ticket_v2")
    async def tutup_ticket(self, interaction: discord.Interaction, button: Button):
        member  = interaction.user
        tickets = load_tickets()
        tdata   = tickets.get(str(self.channel_id))
        if not tdata:
            await interaction.response.send_message("⚠️ Data tidak ditemukan.", ephemeral=True)
            return
        if member.id != tdata["user_id"] and not is_admin(member):
            await interaction.response.send_message("❌ Hanya pembuat ticket atau admin.", ephemeral=True)
            return
        await interaction.response.defer()
        await interaction.followup.send("🔒 Menutup ticket dalam 5 detik...")
        await asyncio.sleep(5)
        tickets[str(self.channel_id)]["status"] = "closed"
        save_tickets(tickets)
        channel = bot.get_channel(self.channel_id)
        if channel:
            try:
                await channel.delete(reason="Ticket ditutup")
            except Exception:
                pass

# ═══════════════════════════════════════════════════════
#  GIVEAWAY VIEW
# ═══════════════════════════════════════════════════════
class GiveawayView(View):
    def __init__(self, giveaway_id: str):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="🎉 Ikut Giveaway", style=discord.ButtonStyle.success,
                       custom_id="join_giveaway")
    async def join_giveaway(self, interaction: discord.Interaction, button: Button):
        giveaways = load_giveaways()
        gw = giveaways.get(self.giveaway_id)
        if not gw:
            await interaction.response.send_message("❌ Giveaway tidak ditemukan.", ephemeral=True)
            return
        if gw.get("ended"):
            await interaction.response.send_message("❌ Giveaway sudah berakhir.", ephemeral=True)
            return
        uid = str(interaction.user.id)
        if uid in gw["entries"]:
            # Toggle keluar
            gw["entries"].remove(uid)
            save_giveaways(giveaways)
            await interaction.response.send_message(
                "✅ Kamu keluar dari giveaway.", ephemeral=True)
        else:
            gw["entries"].append(uid)
            save_giveaways(giveaways)
            await interaction.response.send_message(
                f"🎉 Kamu sudah terdaftar! Total peserta: **{len(gw['entries'])}**", ephemeral=True)

        # Update embed
        try:
            ch = bot.get_channel(int(gw["channel_id"]))
            msg = await ch.fetch_message(int(gw["message_id"]))
            new_embed = build_giveaway_embed(gw)
            await msg.edit(embed=new_embed)
        except Exception:
            pass

def build_giveaway_embed(gw: dict) -> discord.Embed:
    end_dt = datetime.datetime.fromisoformat(gw["end_time"])
    now    = datetime.datetime.utcnow()
    sisa   = end_dt - now
    if sisa.total_seconds() > 0:
        h, rem = divmod(int(sisa.total_seconds()), 3600)
        m, s   = divmod(rem, 60)
        sisa_str = f"{h}j {m}m {s}d"
    else:
        sisa_str = "Selesai"

    embed = discord.Embed(
        title=f"🎉 GIVEAWAY — {gw['prize']}",
        description=(
            f"Klik tombol **🎉 Ikut Giveaway** untuk ikut!\n\n"
            f"👥 **Peserta:** {len(gw['entries'])} orang\n"
            f"⏰ **Berakhir dalam:** {sisa_str}\n"
            f"🏆 **Hadiah:** {gw['prize']}"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Asisten Lurah BFL • Giveaway System")
    return embed

# ═══════════════════════════════════════════════════════
#  EVENTS
# ═══════════════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ {bot.user} online!")
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Desa BFL 🏘️")
    )
    bot.add_view(TicketView())
    tickets = load_tickets()
    for channel_id, tdata in tickets.items():
        if tdata.get("status") == "open":
            bot.add_view(CloseTicketView(int(channel_id)))
    # Register giveaway views
    giveaways = load_giveaways()
    for gid, gw in giveaways.items():
        if not gw.get("ended"):
            bot.add_view(GiveawayView(gid))
    # Register poll views
    polls = load_polls()
    for pid, pw in polls.items():
        if not pw.get("ended"):
            bot.add_view(PollView(pid, pw["options"]))

    check_tiktok.start()
    check_giveaways.start()
    daily_tax.start()
    # Start coin price auto-update
    try:
        auto_price_update.start()
    except Exception:
        pass
    # Pastikan saldo admin bank sudah ada (init 10000 jika belum)
    coins = load_coins()
    if ADMIN_BANK_ID not in coins:
        coins[ADMIN_BANK_ID] = 20000
        save_coins(coins)
        print(f"✅ Saldo admin bank diinisialisasi: 20,000 Bcash")

    # Inisialisasi harga Bcash jika belum ada
    import os as _os
    if not _os.path.exists(PRICE_FILE):
        init_price = _PRICE_FILE_DEFAULT.copy()
        save_price(init_price)
        print(f"✅ Harga Bcash diinisialisasi: Rp{_PRICE_INITIAL:,} / 100 Bcash")
    print(f"✅ Semua sistem aktif. Logged in as {bot.user}")
    # Auto backup saldo coins saat bot start/restart
    ts = save_backup()
    print(f"✅ Auto-backup coins tersimpan: {ts}")
    # Kirim backup ke DM admin saat bot online
    coins_at_start = load_coins()
    await send_backup_to_admin(ts, coins_at_start, trigger="Auto (Bot Online/Restart)")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ── Auto Mod Anti Spam ──
    await _check_automod(message)

    # ── AFK check ──
    if not isinstance(message.channel, discord.DMChannel):
        afk_data = load_afk()
        uid = str(message.author.id)
        # Hapus AFK jika yang kirim pesan sendiri
        if uid in afk_data:
            del afk_data[uid]
            save_afk(afk_data)
            await message.channel.send(
                f"👋 {message.author.mention} selamat datang kembali! Status AFK dihapus.",
                delete_after=8
            )
        # Cek mention ke user AFK
        for mentioned in message.mentions:
            mid = str(mentioned.id)
            if mid in afk_data:
                alasan = afk_data[mid].get("reason", "Tidak ada alasan")
                await message.channel.send(
                    f"💤 **{mentioned.display_name}** sedang offline — {alasan}",
                    delete_after=10
                )

    # ── DM Handler ──
    if isinstance(message.channel, discord.DMChannel):
        # Cek apakah pengirim adalah admin/owner di salah satu guild
        sender_is_admin = message.author.id == OWNER_ID
        if not sender_is_admin:
            for g in bot.guilds:
                member_obj = g.get_member(message.author.id)
                if member_obj is None:
                    try:
                        member_obj = await g.fetch_member(message.author.id)
                    except Exception:
                        continue
                if member_obj and is_admin(member_obj):
                    sender_is_admin = True
                    break

        # Jika admin/owner → langsung proses command, skip verifikasi
        if sender_is_admin:
            await bot.process_commands(message)
            return

        # Bukan admin → cek apakah kirim attachment untuk verifikasi
        if message.attachments:
            verif = load_verif()
            uid   = str(message.author.id)
            if uid in verif:
                await message.channel.send("⏳ Verifikasi sedang diproses.")
                return
            verif[uid] = {"status": "pending"}
            save_verif(verif)
            owner = await bot.fetch_user(OWNER_ID)
            embed = discord.Embed(
                title="📋 Verifikasi Masuk",
                description=(
                    f"**User:** {message.author} (`{message.author.id}`)\n"
                    f"**Name:** {message.author.display_name}\n\n"
                    "Pilih role lalu ACC/REJECT."
                ),
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            guild_id = None
            for g in bot.guilds:
                if g.get_member(message.author.id):
                    guild_id = g.id
                    break
            files = [await att.to_file() for att in message.attachments
                     if att.content_type and att.content_type.startswith("image")]
            if guild_id:
                await owner.send(embed=embed, files=files,
                                 view=VerifView(message.author.id, guild_id))
                await message.channel.send("✅ Bukti dikirim ke admin. Tunggu konfirmasi!")
            else:
                await message.channel.send("❌ Bergabung ke server terlebih dahulu.")
            return

        # Member biasa tanpa attachment → proses command (bisa !koin dll)
        await bot.process_commands(message)
        return

    # ── Welcome Bonus 15 Bcash untuk user baru di #spam ──
    if message.channel.id == SPAM_CHANNEL_ID:
        welcome_data = load_welcome_bonus()
        uid_str = str(message.author.id)
        if uid_str not in welcome_data:
            welcome_data[uid_str] = True
            save_welcome_bonus(welcome_data)
            ensure_coins(uid_str)
            # Mint Bcash baru untuk welcome bonus
            add_coins(uid_str, WELCOME_BONUS_AMOUNT)
            mint_coins(WELCOME_BONUS_AMOUNT)
            log_history(uid_str, "🎁 Welcome Bonus (pemain baru)", +WELCOME_BONUS_AMOUNT)
            embed_welcome = discord.Embed(
                title="🎉 Selamat Datang di BFL!",
                description=(
                    f"Halo {message.author.mention}! Kamu dapat **{WELCOME_BONUS_AMOUNT} Bcash** sebagai hadiah pemain baru! 🪙\n\n"
                    f"Gunakan `!koin` untuk cek saldo, `!daily` untuk reward harian, dan `!help` untuk lihat semua command."
                ),
                color=discord.Color.gold()
            )
            embed_welcome.set_thumbnail(url=message.author.display_avatar.url)
            embed_welcome.set_footer(text="Asisten Lurah BFL • Welcome Bonus")
            await message.channel.send(embed=embed_welcome)

    # ── Bcash Reward Channel ──
    reward_channels = load_bcash_reward_channels()
    ch_id_str = str(message.channel.id)
    if ch_id_str in reward_channels:
        reward_cfg = reward_channels[ch_id_str]
        reward_amt = reward_cfg.get("amount", 6)
        uid_rc = str(message.author.id)
        # Cooldown 1 menit per user per channel agar tidak spam
        cooldown_key = f"_rcooldown_{uid_rc}_{ch_id_str}"
        now_ts = datetime.datetime.utcnow().timestamp()
        last_ts = getattr(bot, cooldown_key, 0)
        if now_ts - last_ts >= 60:
            setattr(bot, cooldown_key, now_ts)
            ensure_coins(uid_rc)
            add_coins(uid_rc, reward_amt)
            mint_coins(reward_amt)
            log_history(uid_rc, f"💬 Chat reward di #{message.channel.name}", +reward_amt)

    # ── XP System ──
    data = load_data()
    uid  = str(message.author.id)
    if uid not in data:
        data[uid] = {"xp": 0, "level": 1}
    old_level        = data[uid]["level"]
    data[uid]["xp"] += XP_PER_MESSAGE
    new_level        = get_level(data[uid]["xp"])
    data[uid]["level"] = new_level
    save_data(data)
    if new_level > old_level:
        banner_data = assign_banner(message.author.id, new_level)
        embed = discord.Embed(
            title="🎉 LEVEL UP!",
            description=(
                f"{message.author.mention} naik ke **Level {new_level} — {LEVEL_CONFIG[new_level]['name']}**!\n"
                f"Banner diupgrade ke **{banner_data['rarity']}** ✦"
            ),
            color=discord.Color.from_rgb(*LEVEL_CONFIG[new_level]["color"])
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and before.channel.id in active_voice_rooms:
        if len(before.channel.members) == 0:
            try:
                await before.channel.delete(reason="Voice room kosong.")
            except Exception:
                pass
            active_voice_rooms.pop(before.channel.id, None)

# ═══════════════════════════════════════════════════════
#  TASKS — GIVEAWAY CHECKER
# ═══════════════════════════════════════════════════════
@tasks.loop(seconds=30)
async def check_giveaways():
    giveaways = load_giveaways()
    changed   = False
    for gid, gw in giveaways.items():
        if gw.get("ended"):
            continue
        end_dt = datetime.datetime.fromisoformat(gw["end_time"])
        if datetime.datetime.utcnow() >= end_dt:
            gw["ended"] = True
            changed = True
            ch = bot.get_channel(int(gw["channel_id"]))
            if not ch:
                continue
            entries = gw.get("entries", [])
            if not entries:
                await ch.send(f"🎉 Giveaway **{gw['prize']}** berakhir — tidak ada peserta.")
                continue
            winner_id = int(random.choice(entries))
            try:
                winner = await bot.fetch_user(winner_id)
            except Exception:
                winner = None
            # Update embed
            try:
                msg = await ch.fetch_message(int(gw["message_id"]))
                embed = discord.Embed(
                    title=f"🏆 GIVEAWAY SELESAI — {gw['prize']}",
                    description=(
                        f"🎊 Pemenang: {winner.mention if winner else winner_id}\n"
                        f"👥 Total peserta: {len(entries)}"
                    ),
                    color=discord.Color.green()
                )
                embed.set_footer(text="Asisten Lurah BFL • Giveaway Selesai")
                await msg.edit(embed=embed, view=None)
            except Exception:
                pass
            # Announce
            await ch.send(
                f"🎊 Selamat {winner.mention if winner else winner_id}! "
                f"Kamu menang giveaway **{gw['prize']}**!"
            )
            # DM winner
            if winner:
                try:
                    dm_embed = discord.Embed(
                        title="🏆 Kamu Menang Giveaway!",
                        description=(
                            f"Selamat! Kamu memenangkan **{gw['prize']}**!\n\n"
                            f"👥 Total peserta: **{len(entries)}** orang\n"
                            "Hubungi admin untuk mengklaim hadiahmu."
                        ),
                        color=discord.Color.gold()
                    )
                    dm_embed.set_footer(text="Asisten Lurah BFL • Giveaway")
                    await winner.send(embed=dm_embed)
                except Exception:
                    pass
    if changed:
        save_giveaways(giveaways)

@check_giveaways.before_loop
async def before_check_giveaways():
    await bot.wait_until_ready()


# ═══════════════════════════════════════════════════════
#  TASKS — TIKTOK
# ═══════════════════════════════════════════════════════
@tasks.loop(minutes=5)
async def check_tiktok():
    channel = bot.get_channel(TIKTOK_CHECK_CHANNEL_ID)
    if not channel:
        return
    try:
        last_data = load_last_tiktok()
        url       = f"https://www.tiktok.com/@{TIKTOK_USERNAME}"
        headers   = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                html = await resp.text()
        matches = re.findall(r'"id":"(\d+)"', html)
        if not matches:
            return
        latest_id = matches[0]
        if last_data.get("last_id") == latest_id:
            return
        save_last_tiktok({"last_id": latest_id})
        tiktok_url = f"https://www.tiktok.com/@{TIKTOK_USERNAME}/video/{latest_id}"
        embed = discord.Embed(
            title=f"🎵 @{TIKTOK_USERNAME} baru posting di TikTok!",
            description=f"👇\n{tiktok_url}",
            color=discord.Color.from_rgb(254, 44, 85),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Asisten Lurah BFL • TikTok Tracker")
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[TikTok] {e}")

@check_tiktok.before_loop
async def before_tiktok():
    await bot.wait_until_ready()

# ═══════════════════════════════════════════════════════
#  COMMANDS — RANK & LEADERBOARD
# ═══════════════════════════════════════════════════════
@bot.command(name="rank")
async def rank(ctx, member: discord.Member = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    member = member or ctx.author
    data   = load_data()
    uid    = str(member.id)
    if uid not in data:
        data[uid] = {"xp": 0, "level": 1}
        save_data(data)
    xp    = data[uid]["xp"]
    level = data[uid]["level"]
    try:
        avatar_bytes = requests.get(member.display_avatar.url).content
    except Exception:
        avatar_bytes = b""
    card_buf = create_rank_card(str(member.display_name), avatar_bytes, xp, level, member.id)
    await ctx.send(file=discord.File(fp=card_buf, filename="rank.png"))

@bot.command(name="leaderboard", aliases=["lb", "top"])
async def leaderboard(ctx):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    data         = load_data()
    sorted_users = sorted(data.items(), key=lambda x: x[1]["xp"], reverse=True)[:10]
    medals       = ["🥇","🥈","🥉"]
    embed = discord.Embed(title="🏆 Leaderboard XP — Asisten Lurah BFL", color=discord.Color.gold())
    for i, (uid, info) in enumerate(sorted_users):
        try:
            user = await bot.fetch_user(int(uid))
            name = user.display_name
        except Exception:
            name = f"User#{uid}"
        lvl   = info["level"]
        medal = medals[i] if i < 3 else f"#{i+1}"
        banners = load_banners()
        rarity  = banners.get(uid, {}).get("rarity", "Common")
        embed.add_field(
            name=f"{medal} {name}",
            value=f"Level {lvl} ({LEVEL_CONFIG[lvl]['name']}) · {info['xp']} XP · ✦ {rarity}",
            inline=False
        )
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════════════════
#  COMMANDS — WARN
# ═══════════════════════════════════════════════════════
@bot.command(name="warn")
async def warn(ctx, member: discord.Member = None, *, alasan="Tidak ada alasan"):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if member is None:
        return await ctx.send("❌ Format: `!warn @user [alasan]`")
    if member.id == OWNER_ID:
        await ctx.send("❌ Tidak bisa warn owner.")
        return
    warns = load_warns()
    uid   = str(member.id)
    if uid not in warns:
        warns[uid] = []
    warns[uid].append({
        "alasan": alasan,
        "oleh": str(ctx.author.id),
        "waktu": str(datetime.datetime.utcnow())
    })
    total = len(warns[uid])
    save_warns(warns)

    embed = discord.Embed(
        title="⚠️ Peringatan Diberikan",
        color=discord.Color.orange()
    )
    embed.add_field(name="Member",  value=member.mention, inline=True)
    embed.add_field(name="Warn ke", value=f"**{total}/3**",  inline=True)
    embed.add_field(name="Alasan",  value=alasan, inline=False)
    embed.set_footer(text=f"Oleh: {ctx.author}")
    await ctx.send(embed=embed)

    # DM member
    try:
        await member.send(
            f"⚠️ Kamu mendapat peringatan di **{ctx.guild.name}**.\n"
            f"Alasan: **{alasan}**\n"
            f"Total warn: **{total}/3**"
        )
    except Exception:
        pass

    if total >= 3:
        await ctx.send(
            f"🚨 {member.mention} telah mendapat **3 peringatan** dan akan dikeluarkan dari server!"
        )
        try:
            await member.send(
                f"🚨 Kamu telah mendapat **3 peringatan** di **{ctx.guild.name}** "
                f"dan telah dikeluarkan dari server."
            )
        except Exception:
            pass
        await asyncio.sleep(2)
        await member.kick(reason="3x peringatan")
        # Reset warn
        warns[uid] = []
        save_warns(warns)

@warn.error
async def warn_error(ctx, error):
    await ctx.send(f"❌ Error: {error}")

@bot.command(name="warnlist")
async def warnlist(ctx, member: discord.Member):
    warns = load_warns()
    uid   = str(member.id)
    data  = warns.get(uid, [])
    if not data:
        await ctx.send(f"✅ {member.mention} tidak punya peringatan.")
        return
    embed = discord.Embed(title=f"⚠️ Daftar Warn — {member.display_name}",
                          color=discord.Color.orange())
    for i, w in enumerate(data, 1):
        embed.add_field(name=f"Warn #{i}", value=f"**Alasan:** {w['alasan']}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="clearwarn")
async def clearwarn(ctx, member: discord.Member = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if member is None:
        return await ctx.send("❌ Format: `!clearwarn @user`")
    warns = load_warns()
    warns[str(member.id)] = []
    save_warns(warns)
    await ctx.send(f"✅ Semua warn {member.mention} telah dihapus.")

# ═══════════════════════════════════════════════════════
#  COMMANDS — AFK
# ═══════════════════════════════════════════════════════
@bot.command(name="afk")
async def afk(ctx, *, alasan="Tidak ada alasan"):
    if isinstance(ctx.channel, discord.DMChannel):
        return
    afk_data = load_afk()
    afk_data[str(ctx.author.id)] = {
        "reason": alasan,
        "since": str(datetime.datetime.utcnow())
    }
    save_afk(afk_data)
    await ctx.send(f"💤 {ctx.author.mention} sekarang **offline** — {alasan}", delete_after=10)

# ═══════════════════════════════════════════════════════
#  COMMANDS — GIVEAWAY (setup via DM)
# ═══════════════════════════════════════════════════════
@bot.command(name="setgiveaway")
async def set_giveaway(ctx, channel_id: int):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Command ini hanya via DM bot.")
        return
    if not is_admin(ctx.author) and ctx.author.id != OWNER_ID:
        await ctx.send("❌ Hanya admin yang bisa setup giveaway.")
        return
    ch = bot.get_channel(channel_id)
    if not ch:
        await ctx.send("❌ Channel tidak ditemukan.")
        return

    await ctx.send(f"✅ Channel giveaway: **#{ch.name}**\n\nBerapa lama giveaway berlangsung? (contoh: `1h`, `30m`, `2d`)")

    def check(m): return m.author.id == ctx.author.id and isinstance(m.channel, discord.DMChannel)

    try:
        dur_msg = await bot.wait_for("message", check=check, timeout=60)
        dur_str = dur_msg.content.strip().lower()
        seconds = parse_duration(dur_str)
        if not seconds:
            await ctx.send("❌ Format waktu salah. Contoh: `1h`, `30m`, `2d`")
            return

        await ctx.send("Apa hadiahnya? (ketik nama hadiah)")
        prize_msg = await bot.wait_for("message", check=check, timeout=60)
        prize = prize_msg.content.strip()

        # Buat giveaway
        end_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
        gid      = str(int(datetime.datetime.utcnow().timestamp()))
        gw_data  = {
            "channel_id": str(channel_id),
            "prize": prize,
            "end_time": end_time.isoformat(),
            "entries": [],
            "ended": False,
            "message_id": None
        }

        giveaways = load_giveaways()
        giveaways[gid] = gw_data
        save_giveaways(giveaways)

        embed = build_giveaway_embed(gw_data)
        view  = GiveawayView(gid)
        msg   = await ch.send(embed=embed, view=view)
        bot.add_view(view)

        giveaways[gid]["message_id"] = str(msg.id)
        save_giveaways(giveaways)

        await ctx.send(f"🎉 Giveaway **{prize}** berhasil dibuat di #{ch.name}!")

    except asyncio.TimeoutError:
        await ctx.send("⏰ Timeout. Ulangi command.")

def parse_duration(s: str) -> int:
    total = 0
    patterns = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    for suffix, mult in patterns:
        match = re.search(r"(\d+)" + suffix, s)
        if match:
            total += int(match.group(1)) * mult
    return total if total > 0 else None

# ═══════════════════════════════════════════════════════
#  COMMANDS — QUOTE
# ═══════════════════════════════════════════════════════
@bot.command(name="setquotechannel")
async def set_quote_channel(ctx, channel_id: int):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Hanya via DM bot.")
        return
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Hanya owner.")
        return
    ch = bot.get_channel(channel_id)
    if not ch:
        await ctx.send("❌ Channel tidak ditemukan.")
        return
    settings = load_settings()
    settings["quote_channel_id"] = str(channel_id)
    save_settings(settings)
    await ctx.send(f"✅ Channel quote diset ke **#{ch.name}**. Gunakan `!kirimquote` untuk kirim manual.")

@bot.command(name="addquote")
async def add_quote(ctx, *, quote: str):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Hanya via DM bot.")
        return
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Hanya owner.")
        return
    quotes = load_quotes()
    quotes.append(quote)
    save_json(QUOTE_FILE, quotes)
    await ctx.send(f"✅ Quote ditambahkan! Total: **{len(quotes)}** quote.")

@bot.command(name="kirimquote")
async def kirim_quote_cmd(ctx, channel_id: int = None):
    """Kirim quote manual ke channel. Hanya owner via DM."""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Hanya via DM bot.")
        return
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Hanya owner.")
        return

    # Tentukan channel tujuan
    if channel_id:
        ch = bot.get_channel(channel_id)
    else:
        settings = load_settings()
        saved_id = settings.get("quote_channel_id")
        ch = bot.get_channel(int(saved_id)) if saved_id else None

    if not ch:
        await ctx.send("❌ Channel tidak ditemukan. Set dulu dengan `!setquotechannel <id>` atau sertakan ID channel: `!kirimquote <channel_id>`")
        return

    quotes = load_quotes()
    quote  = random.choice(quotes)
    embed  = discord.Embed(
        title="💬 Quote of the Day",
        description=f"*\"{quote}\"*",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Asisten Lurah BFL • Quote of the Day")
    await ch.send(embed=embed)
    await ctx.send(f"✅ Quote berhasil dikirim ke **#{ch.name}**!")

# ═══════════════════════════════════════════════════════
#  COMMANDS — BANNER INFO
# ═══════════════════════════════════════════════════════
@bot.command(name="mybanner")
async def my_banner(ctx):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    data = load_data()
    uid  = str(ctx.author.id)
    if uid not in data:
        await ctx.send("❌ Kamu belum punya data XP. Kirim pesan dulu!")
        return
    level       = data[uid]["level"]
    banner_data = assign_banner(ctx.author.id, level)
    rarity      = banner_data["rarity"]
    theme_names = ["Sakura","Galaxy","Cyber","Ocean","Fire","Forest","Moonlight","Aurora"]
    theme_name  = theme_names[banner_data.get("theme",0) % 8]
    rarity_colors_hex = {
        "Common":"⬜","Uncommon":"🟩","Rare":"🟦","Epic":"🟪","Legendary":"🟨"
    }
    embed = discord.Embed(
        title="✦ Info Banner Kamu",
        description=(
            f"**Rarity:** {rarity_colors_hex.get(rarity,'✦')} **{rarity}**\n"
            f"**Tema:** {theme_name}\n"
            f"**Level saat ini:** {level} — {LEVEL_CONFIG[level]['name']}\n\n"
            "Gunakan `!rank` untuk melihat banner kamu!"
        ),
        color=discord.Color.from_rgb(*BANNER_RARITY[rarity]["color"])
    )
    embed.set_footer(text="Asisten Lurah BFL • Banner System")
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════════════════
#  COMMANDS — PENGUMUMAN
# ═══════════════════════════════════════════════════════
@bot.command(name="pengumuman")
async def pengumuman(ctx, channel_id: int, *, pesan: str):
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Hanya via DM bot.")
        return
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Tidak punya izin.")
        return
    channel = bot.get_channel(channel_id)
    if not channel:
        await ctx.send("❌ Channel tidak ditemukan.")
        return
    embed = discord.Embed(
        title="📢 PENGUMUMAN", description=pesan,
        color=discord.Color.blue(), timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Asisten Lurah BFL")
    await channel.send("@everyone", embed=embed)
    await ctx.send(f"✅ Dikirim ke #{channel.name}!")

# ═══════════════════════════════════════════════════════
#  COMMANDS — MODERASI
# ═══════════════════════════════════════════════════════
@bot.command(name="timeout")
async def timeout_member(ctx, member: discord.Member = None, durasi: int = None, *, alasan="Tidak ada alasan"):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if member is None or durasi is None:
        return await ctx.send("❌ Format: `!timeout @user <menit> [alasan]`")
    until = discord.utils.utcnow() + datetime.timedelta(minutes=durasi)
    await member.timeout(until, reason=alasan)
    embed = discord.Embed(title="⏱️ Member di-Timeout", color=discord.Color.orange())
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Durasi", value=f"{durasi} menit", inline=True)
    embed.add_field(name="Alasan", value=alasan, inline=False)
    embed.set_footer(text=f"Oleh: {ctx.author}")
    await ctx.send(embed=embed)

@timeout_member.error
async def timeout_error(ctx, error): await ctx.send(f"❌ Error: {error}")

@bot.command(name="ban")
async def ban_member(ctx, member: discord.Member = None, *, alasan="Tidak ada alasan"):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if member is None:
        return await ctx.send("❌ Format: `!ban @user [alasan]`")
    await member.ban(reason=alasan)
    embed = discord.Embed(title="🔨 Member di-Ban", color=discord.Color.red())
    embed.add_field(name="Member", value=f"{member} ({member.id})", inline=False)
    embed.add_field(name="Alasan", value=alasan, inline=False)
    embed.set_footer(text=f"Oleh: {ctx.author}")
    await ctx.send(embed=embed)

@ban_member.error
async def ban_error(ctx, error): await ctx.send(f"❌ Error: {error}")

@bot.command(name="unban")
async def unban_member(ctx, user_id: int = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if user_id is None:
        return await ctx.send("❌ Format: `!unban <user_id>`")
    guild = ctx.guild
    if guild is None:
        # Coba cari dari bot guilds jika dari DM
        if bot.guilds:
            guild = bot.guilds[0]
        else:
            return await ctx.send("❌ Tidak ada server yang ditemukan.")

    user = await bot.fetch_user(user_id)
    await guild.unban(user)
    await ctx.send(f"✅ **{user}** berhasil di-unban.")

@bot.command(name="addrole")
async def add_role(ctx, member: discord.Member = None, *, role_name: str = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if member is None or role_name is None:
        return await ctx.send("❌ Format: `!addrole @user <nama_role>`")
    if ctx.guild is None:
        return await ctx.send("❌ Command ini harus dijalankan di server.")
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Role **{role_name}** tidak ditemukan.")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Role **{role_name}** → {member.mention}.")

@bot.command(name="removerole")
async def remove_role(ctx, member: discord.Member = None, *, role_name: str = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if member is None or role_name is None:
        return await ctx.send("❌ Format: `!removerole @user <nama_role>`")
    if ctx.guild is None:
        return await ctx.send("❌ Command ini harus dijalankan di server.")
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Role **{role_name}** tidak ditemukan.")
        return
    await member.remove_roles(role)
    await ctx.send(f"✅ Role **{role_name}** dihapus dari {member.mention}.")

@bot.command(name="clear", aliases=["purge","hapus"])
async def clear_messages(ctx, jumlah: int = 10):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if isinstance(ctx.channel, discord.DMChannel):
        return await ctx.send("❌ Command ini hanya bisa digunakan di server.")
    await ctx.channel.purge(limit=jumlah+1)
    await ctx.send(f"✅ **{jumlah}** pesan dihapus.", delete_after=5)

@clear_messages.error
async def clear_error(ctx, error): await ctx.send(f"❌ Error: {error}")

# ═══════════════════════════════════════════════════════
#  COMMANDS — TICKET SETUP
# ═══════════════════════════════════════════════════════
@bot.command(name="setupticket")
async def setup_ticket(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send("❌ Hanya owner.", delete_after=5)
        return
    channel = bot.get_channel(TICKET_CHANNEL_ID)
    if not channel:
        await ctx.send("❌ Channel tidak ditemukan.")
        return
    embed = discord.Embed(
        title="📩 Buat Laporan / Diskusi",
        description=(
            "Klik tombol di bawah untuk membuat ticket.\n\n"
            "Channel privat akan dibuat, hanya kamu dan admin yang bisa melihatnya."
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Asisten Lurah BFL • Ticket System")
    await channel.send(embed=embed, view=TicketView())
    await ctx.send(f"✅ Ticket system dipasang di {channel.mention}!")

# ═══════════════════════════════════════════════════════
#  COMMANDS — YOUTUBE DATABASE
# ═══════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════
#  COMMANDS — VOICE ROOM
# ═══════════════════════════════════════════════════════
@bot.command(name="createroom")
async def create_room(ctx, *, nama_room: str = None):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("❌ Hanya di server.")
        return
    guild    = ctx.guild
    member   = ctx.author
    category = discord.utils.get(guild.categories, id=VOICE_CATEGORY_ID)
    if not category:
        await ctx.send("❌ Kategori Voice Zone tidak ditemukan.")
        return
    for ch_id, owner_id in list(active_voice_rooms.items()):
        if owner_id == member.id:
            ch = guild.get_channel(ch_id)
            if ch:
                await ctx.send(f"⚠️ Kamu sudah punya room: **{ch.name}**", delete_after=10)
                return
    current_rooms = [ch for ch in category.voice_channels if ch.id in active_voice_rooms]
    if len(current_rooms) >= 10:
        await ctx.send("⚠️ Maks 10 room aktif.", delete_after=10)
        return
    room_name = nama_room if nama_room else f"Room {member.display_name}"
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
        member: discord.PermissionOverwrite(connect=True, manage_channels=True,
                                            mute_members=True, move_members=True),
        guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True),
    }
    vc = await guild.create_voice_channel(
        name=room_name, category=category, overwrites=overwrites,
        user_limit=10, reason=f"Room oleh {member}"
    )
    active_voice_rooms[vc.id] = member.id
    embed = discord.Embed(
        title="🎙️ Voice Room Dibuat!",
        description=f"Room **{room_name}** aktif di **Voice Zone**.\nAuto-hapus saat kosong. Kapasitas: **10 orang**.",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Dibuat oleh {member.display_name}")
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════════════════
#  COMMANDS — HELP
# ═══════════════════════════════════════════════════════
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="📖 Asisten Lurah BFL — Command List",
        description="Prefix: `!` | Command game hanya di <#" + str(SPAM_CHANNEL_ID) + ">",
        color=discord.Color.blue()
    )
    embed.add_field(name="🏅 Level & XP (di #spam)",
        value=("`!rank [@user]` — Lihat rank card + banner kamu\n"
               "`!leaderboard` / `!lb` / `!top` — Top 10 XP server\n"
               "`!mybanner` — Info rarity & tema banner kamu\n"
               "📌 XP dapet dari chat, level naik otomatis!"), inline=False)
    embed.add_field(name="💰 Bcash System (di #spam)",
        value=("`!koin [@user]` — Cek saldo + nilai IDR Bcash kamu\n"
               "`!daily` / `!klaim` — Klaim reward harian (streak 1–7, max 7 Bcash)\n"
               "`!kirim @user <jumlah>` — Transfer Bcash ke member lain\n"
               "`!convertcoin <jumlah>` — Tukar Bcash ke IDR (min. **Rp50.000**), tarik ke DANA/OVO/ShopeePay\n"
               "`!deposit <jumlah>` — Request deposit Bcash\n"
               "`!price` — Cek harga Bcash + grafik + market sentiment\n"
               "💱 **Harga Bcash bergerak seperti crypto!** Dipengaruhi game, trading, dan sirkulasi"), inline=False)
    embed.add_field(name="🎰 Mini Games (di #spam)",
        value=("`!slot <bet>` — Mesin slot, taruhan Bcash (min. 1)\n"
               "`!coinflip <heads/tails> <bet>` — Flip koin, tebak sisi yang benar!\n"
               "`!balapan <1/2> <bet>` — 🏇 Balapan kuda! Pilih kuda & taruhan (ada animasi!)\n"
               "`!ball <bet>` — ⚽ Tendang bola ke gawang!\n"
               "`!hunt` — 🏹 Berburu di hutan! Modal **2 Bcash**, hadiah 2–15 Bcash\n"
               "`!duel @user <jumlah>` — Tantang user duel Bcash (ketik `ya` untuk terima)\n"
               "`!bonanza <bet>` — 🍬 Sweet Bonanza! Bet **1–15 Bcash**, cluster buah + Free Spin langka!\n"
               "🔥 **Kalah → Bcash di-burn otomatis** (harga naik!)\n"
               "💰 **Menang → Bcash baru di-mint** (hadiahmu!)\n"
               "🎮 **Bonus 10 Bcash** untuk pertama kali main game!"), inline=False)
    embed.add_field(name="📊 Statistik (di #spam)",
        value=("`!history [@user]` / `!riwayat` — Lihat 10 transaksi Bcash terakhir"), inline=False)
    embed.add_field(name="🛒 Market System (di #spam)",
        value=("`!market` / `!shop` / `!katalog` — Lihat semua item\n"
               "`!buy <item_id>` — Beli item (isi form pengiriman via DM)\n"
               "`!inventory` / `!inv` [@user] — Lihat barang yang dimiliki"), inline=False)
    embed.add_field(name="🎙️ Voice Room",
        value=("`!createroom [nama]` — Buat voice room pribadi\n"
               "📌 Room auto-hapus saat kosong, maks 10 orang"), inline=False)
    embed.add_field(name="💤 AFK",
        value=("`!afk [alasan]` — Set status AFK\n"
               "📌 Status hilang otomatis saat kamu kirim pesan"), inline=False)
    embed.add_field(name="✏️ Nickname",
        value=("`!nick <nickname baru>` — Ganti nickname kamu di server ini\n"
               "`!nick reset` — Reset nickname ke nama asli"), inline=False)
    embed.add_field(name="📊 Polling",
        value=("`!poll <menit> <pertanyaan> | <opsi1> | <opsi2>` — Buat poll\n"
               "Contoh: `!poll 10 Warna favorit? | Merah | Biru | Hijau`\n"
               "`!pollresult <id>` — Lihat hasil poll"), inline=False)
    embed.add_field(name="🎵 Music",
        value=("`!play <judul/URL>` — Putar musik dari YouTube (harus di voice channel)\n"
               "`!skip` — Skip lagu\n"
               "`!stop` / `!dc` — Stop & bot keluar voice\n"
               "`!pause` / `!resume` — Pause/lanjutkan\n"
               "`!queue` / `!q` — Lihat antrian lagu\n"
               "`!nowplaying` / `!np` — Lagu yang sedang diputar"), inline=False)
    embed.set_footer(text="Asisten Lurah BFL • Gunakan !helpadmin untuk command admin")
    await ctx.send(embed=embed)

@bot.command(name="helpadmin", aliases=["adminhelp"])
async def help_admin_cmd(ctx):
    # Resolve author sebagai Member (bukan User) agar guild_permissions tersedia
    author = ctx.author
    if isinstance(ctx.channel, discord.DMChannel):
        # Cari member object di salah satu guild
        for g in bot.guilds:
            m = g.get_member(author.id)
            if m is None:
                try:
                    m = await g.fetch_member(author.id)
                except Exception:
                    continue
            if m:
                author = m
                break

    if not is_admin(author):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("❌ Kamu bukan admin.")
        else:
            await ctx.send("❌ Hanya admin yang bisa melihat command ini.", delete_after=5)
        return
    embed = discord.Embed(
        title="🛡️ Admin Command List — Asisten Lurah BFL",
        description="Semua command di bawah hanya untuk Admin/Owner\n📌 Command bertanda *(DM)* bisa dipakai di DM bot",
        color=discord.Color.red()
    )
    embed.add_field(name="⚠️ Moderasi Member",
        value=("`!warn @user [alasan]` — Beri peringatan (auto-kick di warn ke-3)\n"
               "`!warnlist @user` — Lihat semua warn milik user\n"
               "`!clearwarn @user` — Hapus semua warn user\n"
               "`!timeout @user <menit> [alasan]` — Timeout member\n"
               "`!ban @user [alasan]` — Ban member dari server\n"
               "`!unban <user_id>` — Unban member via ID\n"
               "`!clear [n]` / `!purge` / `!hapus` — Hapus n pesan (default 10)"), inline=False)
    embed.add_field(name="🎭 Role Management",
        value=("`!addrole @user <nama_role>` — Tambahkan role ke member\n"
               "`!removerole @user <nama_role>` — Hapus role dari member\n"
               "`!giverole @role @user` — Beri role ke user (format baru, lebih mudah)"), inline=False)
    embed.add_field(name="💰 Bcash & Market Admin",
        value=("`!givecoin @user <jumlah>` *(DM/server)* — Tambah Bcash ke user\n"
               "`!addkoin <jumlah>` *(DM/server)* — ➕ Tambah saldo admin bank langsung\n"
               "`!checkbalance @user` — Cek saldo Bcash user\n"
               "`!setprice <harga>` — Override harga Bcash (Rp1.000–Rp15.000 per 100)\n"
               "`!burncoin <jumlah>` *(DM/server)* — 🔥 Burn Bcash → supply turun → harga naik\n"
               "`!price` — Lihat harga & market info\n"
               "`!supply` *(DM/server)* — Laporan sirkulasi: holder, mint, burn, supply\n"
               "`!setspamchannel <channel_id>` *(DM)* — Ganti spam channel\n"
               "`!additem` *(DM)* — Tambah item market baru (step-by-step)\n"
               "`!deleteitem <item_id>` — Hapus item dari market\n"
               "`!listuser` — Daftar semua user dengan saldo > 1 Bcash\n"
               "`!rain <total> [jumlah_user]` — Sebar Bcash ke user aktif\n"
               "📌 WD minimum **Rp50.000** | Kalah game → Bcash di-burn otomatis\n"
               "🏛️ **Pajak otomatis 10%** setiap hari untuk user tidak aktif bermain"), inline=False)
    embed.add_field(name="🎮 Game Settings",
        value=("`!setgame info` — Lihat semua setting game saat ini\n"
               "`!setgame winrate <game> <0.0-1.0>` — Set winrate user (contoh: `!setgame winrate slot 0.60`)\n"
               "`!setgame adminwinrate <0.0-1.0>` — Set winrate admin di semua game (default: 90%)\n"
               "`!setgame maxbet <game> <jumlah>` — Set max bet per game\n"
               "`!setgame reward <key> <multiplier>` — Set multiplier hadiah\n"
               f"📌 Game: slot, coinflip, balapan, ball, hunt, bonanza, duel"), inline=False)
    embed.add_field(name="🎉 Giveaway *(DM)*",
        value=("`!setgiveaway <channel_id>` — Buat giveaway baru\n"
               "📌 Bot tanya: durasi (`1h`, `30m`, `2d`) lalu nama hadiah\n"
               "📌 Auto undi pemenang & DM pemenang"), inline=False)
    embed.add_field(name="📢 Pengumuman & Quote *(DM)*",
        value=("`!pengumuman <channel_id> <pesan>` — Kirim pengumuman @everyone\n"
               "`!setquotechannel <channel_id>` — Set channel tujuan quote\n"
               "`!addquote <quote>` — Tambah quote baru ke database\n"
               "`!kirimquote [channel_id]` — Kirim quote random manual"), inline=False)
    embed.add_field(name="🎫 Ticket System",
        value=("`!setupticket` — Pasang panel ticket di TICKET_CHANNEL\n"
               "📌 Member klik tombol → buat ticket privat"), inline=False)
    embed.add_field(name="🎭 React to Get Role",
        value=("`!addreactrole #channel <msg_id> <emoji> @role` — Tambah react role\n"
               "`!removereactrole <msg_id> <emoji>` — Hapus react role\n"
               "`!listreactrole` — Daftar semua react role aktif"), inline=False)
    embed.add_field(name="🛡️ Auto Mod Anti Spam",
        value=("`!automod on/off` — Aktifkan/nonaktifkan auto mod\n"
               "`!automod threshold <n>` — Set batas pesan spam (default: 5)\n"
               "`!automod interval <detik>` — Set jendela waktu (default: 5 detik)\n"
               "`!automod mute <detik>` — Set durasi timeout (default: 60 detik)\n"
               "`!automod status` — Lihat pengaturan saat ini"), inline=False)
    embed.add_field(name="👋 Welcome & Leave",
        value=("`!setwelcome #channel` — Set channel welcome card\n"
               "`!setleave #channel` — Set channel leave message\n"
               "`!welcometest` — Test welcome card\n"
               "`!leavetest` — Test leave message"), inline=False)
    embed.add_field(name="✏️ Nickname & 📊 Poll",
        value=("`!setnick @user <nick>` — Atur nickname orang lain\n"
               "`!nick <nick>` / `!nick reset` — Ganti/reset nickname sendiri\n"
               "`!poll <menit> <pertanyaan> | <opsi1> | <opsi2>` — Buat poll\n"
               "`!endpoll <id>` — Akhiri poll lebih cepat\n"
               "`!pollresult <id>` — Lihat hasil poll"), inline=False)
    embed.add_field(name="👤 Info User",
        value=("`!userinfo [@user]` / `!cekuser` — Cek info lengkap user\n"
               "📌 Menampilkan: kapan join, estimasi pesan, level, XP, Bcash, warn, roles, banner"), inline=False)
    embed.add_field(name="💬 Bcash Reward Channel",
        value=("`!setrewardchannel #channel [jumlah]` — Set channel yang beri Bcash saat pesan (default 6)\n"
               "`!removerewardchannel #channel` — Hapus channel dari daftar reward\n"
               "`!listrewardchannel` — Lihat semua reward channel aktif\n"
               "📌 Cooldown 1 menit/user agar tidak disalahgunakan"), inline=False)
    embed.add_field(name="🎵 Music",
        value=("`!play <judul/URL>` — Putar musik dari YouTube\n"
               "`!skip` — Skip lagu sekarang\n"
               "`!stop` — Stop & bot keluar voice\n"
               "`!pause` / `!resume` — Pause/lanjutkan musik\n"
               "`!queue` — Lihat antrian lagu\n"
               "`!nowplaying` — Lagu yang sedang diputar\n"
               "📌 Butuh: `pip install yt-dlp` & FFmpeg (sudah aktif di pella.app)"), inline=False)
    embed.set_footer(text="Asisten Lurah BFL • Hanya terlihat oleh Admin/Owner")
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════════════════
#  COIN SYSTEM (menggantikan BFcash)
# ═══════════════════════════════════════════════════════
def load_coins():
    return load_json(COIN_FILE, default={})

def save_coins(d):
    save_json(COIN_FILE, d)

def get_coins(uid: str) -> int:
    """Selalu return int, pastikan uid string, handle format lama (int key)."""
    uid = str(uid)
    coins = load_coins()
    # Cek string key dulu, fallback ke int key (format lama)
    if uid in coins:
        return int(coins[uid])
    if int(uid) in coins:
        # Migrasi key int ke string
        val = int(coins[int(uid)])
        coins[uid] = val
        del coins[int(uid)]
        save_coins(coins)
        return val
    return 0

def add_coins(uid: str, amount: int) -> int:
    """Tambah/kurang coin, pastikan uid string, return saldo baru."""
    uid = str(uid)
    coins = load_coins()
    # Migrasi int key ke string key jika ada
    if int(uid) in coins and uid not in coins:
        coins[uid] = coins.pop(int(uid))
    current = int(coins.get(uid, 0))
    coins[uid] = max(0, current + amount)
    save_coins(coins)
    return coins[uid]

def ensure_coins(uid: str):
    uid = str(uid)
    coins = load_coins()
    # Migrasi int key ke string key jika ada
    if int(uid) in coins and uid not in coins:
        coins[uid] = coins.pop(int(uid))
        save_coins(coins)
        return
    if uid not in coins:
        coins[uid] = 0
        save_coins(coins)

def log_history(uid: str, label: str, amount: int):
    """Catat transaksi ke history.json. amount positif = masuk, negatif = keluar."""
    uid = str(uid)
    data = load_json(HISTORY_FILE, default={})
    if uid not in data:
        data[uid] = []
    entry = {
        "label":  label,
        "amount": amount,
        "time":   datetime.datetime.utcnow().strftime("%d/%m %H:%M")
    }
    data[uid].insert(0, entry)   # terbaru di atas
    data[uid] = data[uid][:30]   # simpan max 30 entri
    save_json(HISTORY_FILE, data)

# ═══════════════════════════════════════════════════════
#  BACKUP & LOAD SYSTEM
# ═══════════════════════════════════════════════════════
BACKUP_FILE = "coins_backup.json"

def save_backup():
    """Backup seluruh data coins saat ini ke coins_backup.json."""
    coins = load_coins()
    backup = {
        "timestamp": datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S UTC"),
        "data": coins
    }
    save_json(BACKUP_FILE, backup)
    return backup["timestamp"]

def load_backup():
    """Load backup coins dari coins_backup.json. Return (timestamp, data) atau (None, None)."""
    if not os.path.exists(BACKUP_FILE):
        return None, None
    b = load_json(BACKUP_FILE, default={})
    return b.get("timestamp"), b.get("data")

async def send_backup_to_admin(ts: str, coins: dict, trigger: str = "Manual"):
    """Kirim file backup JSON ke DM admin/owner."""
    try:
        owner = await bot.fetch_user(OWNER_ID)
        total_users = len([uid for uid, bal in coins.items() if str(uid) != ADMIN_BANK_ID and int(bal) > 0])
        total_bcash = sum(int(bal) for uid, bal in coins.items() if str(uid) != ADMIN_BANK_ID)
        backup_bytes = json.dumps({"timestamp": ts, "data": coins}, indent=2).encode("utf-8")
        file_obj = discord.File(
            fp=io.BytesIO(backup_bytes),
            filename=f"backup_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        )
        embed = discord.Embed(
            title="💾 BACKUP DATA BCASH",
            description=(
                f"📋 **Trigger:** {trigger}\n"
                f"📅 **Timestamp:** `{ts}`\n"
                f"👥 **Total User:** {total_users} akun\n"
                f"💰 **Total Bcash:** {total_bcash:,} Bcash\n\n"
                f"📎 File backup terlampir.\n"
                f"Restore: kirim `!load` di DM bot sambil lampirkan file JSON ini."
            ),
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Asisten Lurah BFL • Auto Backup System")
        await owner.send(embed=embed, file=file_obj)
        print(f"✅ Backup dikirim ke DM owner: {ts}")
    except discord.Forbidden:
        print(f"[BACKUP] ❌ Bot tidak bisa DM owner — pastikan owner allow DM dari bot/server.")
    except discord.HTTPException as e:
        print(f"[BACKUP] ❌ HTTP error saat kirim DM: {e}")
    except Exception as e:
        print(f"[BACKUP] ❌ Gagal kirim DM ke owner: {e}")

@bot.command(name="backup")
async def backup_cmd(ctx):
    """Admin — backup Bcash, kirim file JSON ke DM admin. Bisa di server & DM."""
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin yang bisa menjalankan backup.", delete_after=5)
        return

    ts    = save_backup()
    coins = load_coins()
    total_users = len([uid for uid, bal in coins.items() if str(uid) != ADMIN_BANK_ID and int(bal) > 0])
    total_bcash = sum(int(bal) for uid, bal in coins.items() if str(uid) != ADMIN_BANK_ID)

    embed = discord.Embed(
        title="💾 BACKUP BERHASIL",
        description=(
            f"Seluruh data saldo Bcash telah disimpan.\n\n"
            f"📅 **Timestamp:** `{ts}`\n"
            f"👥 **Total User:** {total_users} akun\n"
            f"💰 **Total Bcash:** {total_bcash:,} Bcash\n\n"
            f"📩 File backup dikirim ke **DM admin**.\n"
            f"Saat deploy ulang: kirim `!load` di DM bot + lampirkan file JSON backup."
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Asisten Lurah BFL • Backup oleh {ctx.author}")
    await ctx.send(embed=embed)
    await send_backup_to_admin(ts, coins, trigger=f"Manual oleh {ctx.author}")

@bot.command(name="load")
async def load_cmd(ctx):
    """
    Admin — muat backup Bcash.
    DM + lampiran file JSON → restore dari file tersebut.
    Server / DM tanpa lampiran → restore dari backup file lokal terakhir.
    """
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin yang bisa menjalankan load backup.", delete_after=5)
        return

    is_dm = isinstance(ctx.channel, discord.DMChannel)

    # Mode DM dengan file JSON terlampir
    if is_dm and ctx.message.attachments:
        att = ctx.message.attachments[0]
        if not att.filename.endswith(".json"):
            await ctx.send("❌ Lampirkan file **.json** backup yang valid.")
            return
        try:
            raw    = await att.read()
            parsed = json.loads(raw.decode("utf-8"))
            if "data" in parsed and isinstance(parsed["data"], dict):
                backup_data = parsed["data"]
                ts = parsed.get("timestamp", "Tidak diketahui")
            elif parsed and isinstance(parsed, dict):
                backup_data = parsed
                ts = "Dari file langsung"
            else:
                await ctx.send("❌ Format file backup tidak valid.")
                return

            total_bak = sum(int(b) for uid, b in backup_data.items() if str(uid) != ADMIN_BANK_ID)
            embed_confirm = discord.Embed(
                title="⚠️ KONFIRMASI LOAD BACKUP (via File DM)",
                description=(
                    f"**Backup dari:** `{ts}`\n\n"
                    f"📦 **Data Backup:** {total_bak:,} Bcash ({len(backup_data)} akun)\n\n"
                    f"⚠️ **Data coins sekarang akan DIGANTIKAN!**\n"
                    f"Ketik `!loadconfirm` dalam 30 detik untuk melanjutkan."
                ),
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed_confirm)

            def check_dm(m):
                return (m.author.id == ctx.author.id
                        and m.content.strip().lower() == "!loadconfirm"
                        and isinstance(m.channel, discord.DMChannel))
            try:
                await bot.wait_for("message", check=check_dm, timeout=30)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Timeout. Load backup dibatalkan.")
                return

            save_coins(backup_data)
            save_json(BACKUP_FILE, {"timestamp": ts, "data": backup_data})

            embed_done = discord.Embed(
                title="✅ LOAD BACKUP BERHASIL (dari File DM)",
                description=(
                    f"Data Bcash berhasil dipulihkan!\n\n"
                    f"📅 **Backup dari:** `{ts}`\n"
                    f"👥 **User dipulihkan:** {len(backup_data)} akun\n"
                    f"💰 **Total Bcash:** {total_bak:,} Bcash"
                ),
                color=discord.Color.green()
            )
            embed_done.set_footer(text=f"Asisten Lurah BFL • Dipulihkan via DM oleh {ctx.author}")
            await ctx.send(embed=embed_done)
            return
        except Exception as e:
            await ctx.send(f"❌ Gagal membaca file backup: `{e}`")
            return

    # DM tanpa lampiran
    if is_dm and not ctx.message.attachments:
        ts_local, bak_local = load_backup()
        if bak_local:
            total_bak = sum(int(b) for uid, b in bak_local.items() if str(uid) != ADMIN_BANK_ID)
            await ctx.send(
                f"📎 **Cara Load Backup via DM:**\n"
                f"Kirim `!load` sambil melampirkan file `.json` backup yang dikirim bot.\n\n"
                f"📦 Backup lokal: `{ts_local}` ({total_bak:,} Bcash)\n"
                f"Untuk restore dari backup lokal, jalankan `!load` di server."
            )
        else:
            await ctx.send(
                "📎 **Cara Load Backup via DM:**\n"
                "Kirim `!load` sambil melampirkan file `.json` backup.\n\n"
                "Belum ada backup lokal. Jalankan `!backup` di server/DM terlebih dahulu."
            )
        return

    # Mode Server: restore dari file lokal
    ts, backup_data = load_backup()
    if not backup_data:
        await ctx.send("❌ Tidak ada file backup ditemukan. Jalankan `!backup` terlebih dahulu.")
        return

    coins_now = load_coins()
    total_now = sum(int(b) for uid, b in coins_now.items() if str(uid) != ADMIN_BANK_ID)
    total_bak = sum(int(b) for uid, b in backup_data.items() if str(uid) != ADMIN_BANK_ID)

    embed_confirm = discord.Embed(
        title="⚠️ KONFIRMASI LOAD BACKUP",
        description=(
            f"**Backup dari:** `{ts}`\n\n"
            f"📊 **Data Sekarang:** {total_now:,} Bcash ({len(coins_now)} akun)\n"
            f"📦 **Data Backup:**   {total_bak:,} Bcash ({len(backup_data)} akun)\n\n"
            f"⚠️ **Data coins sekarang akan DIGANTIKAN dengan data backup!**\n"
            f"Ketik `!loadconfirm` dalam 30 detik untuk melanjutkan."
        ),
        color=discord.Color.orange()
    )
    embed_confirm.set_footer(text="Asisten Lurah BFL • Hanya admin")
    await ctx.send(embed_confirm)

    def check(m):
        return (m.author.id == ctx.author.id
                and m.content.strip().lower() == "!loadconfirm"
                and (isinstance(m.channel, discord.DMChannel) or m.channel.id == ctx.channel.id))

    try:
        await bot.wait_for("message", check=check, timeout=30)
    except asyncio.TimeoutError:
        await ctx.send("⏰ Timeout. Load backup dibatalkan.")
        return

    save_coins(backup_data)

    embed_done = discord.Embed(
        title="✅ LOAD BACKUP BERHASIL",
        description=(
            f"Data Bcash berhasil dipulihkan dari backup!\n\n"
            f"📅 **Backup dari:** `{ts}`\n"
            f"👥 **User dipulihkan:** {len(backup_data)} akun\n"
            f"💰 **Total Bcash dipulihkan:** {total_bak:,} Bcash"
        ),
        color=discord.Color.green()
    )
    embed_done.set_footer(text=f"Asisten Lurah BFL • Dipulihkan oleh {ctx.author}")
    await ctx.send(embed_done)

@bot.command(name="loadconfirm")
async def loadconfirm_cmd(ctx):
    """Placeholder — perintah ini hanya valid saat dipanggil dalam konteks !load."""
    # Jika dipanggil langsung tanpa konteks !load, abaikan saja
    pass

@bot.command(name="backupinfo", aliases=["cekbackup"])
async def backup_info_cmd(ctx):
    """Admin — lihat info backup terakhir tanpa melakukan apa-apa."""
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin.", delete_after=5)
        return
    ts, backup_data = load_backup()
    if not backup_data:
        await ctx.send("📭 Belum ada backup. Jalankan `!backup` dulu.")
        return
    total_bak  = sum(int(b) for uid, b in backup_data.items() if str(uid) != ADMIN_BANK_ID)
    total_user = len([uid for uid, b in backup_data.items() if str(uid) != ADMIN_BANK_ID and int(b) > 0])
    embed = discord.Embed(
        title="📦 Info Backup Terakhir",
        description=(
            f"📅 **Timestamp:** `{ts}`\n"
            f"👥 **User:** {total_user} akun\n"
            f"💰 **Total Bcash:** {total_bak:,} Bcash\n\n"
            f"Gunakan `!load` untuk restore, `!backup` untuk buat backup baru."
        ),
        color=discord.Color.blue()
    )
    embed.set_footer(text="Asisten Lurah BFL • Backup System")
    await ctx.send(embed=embed)

@bot.command(name="koin", aliases=["coins", "coin", "bcash", "wallet"])
async def coins_balance(ctx, member: discord.Member = None):
    is_dm = isinstance(ctx.channel, discord.DMChannel)
    if not is_dm and not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    if is_dm:
        member = ctx.author
    else:
        member = member or ctx.author
    uid = str(member.id)
    ensure_coins(uid)
    balance = get_coins(uid)

    price_data = load_price()
    price     = price_data["price"]
    total_idr = int((balance / 100) * price)

    # Trend singkat
    hist = price_data.get("history", [price])
    if len(hist) >= 2:
        trend = "📈" if price >= hist[-2] else "📉"
    else:
        trend = "➡️"

    embed = discord.Embed(
        title=f"💰 Dompet Bcash — {member.display_name}",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="💰 Saldo",
        value=f"**{balance:,} Bcash**",
        inline=True
    )
    embed.add_field(
        name="💵 Nilai IDR",
        value=f"**Rp{total_idr:,}**",
        inline=True
    )
    embed.add_field(
        name=f"{trend} Harga Bcash",
        value=f"**Rp{price:,}** / 100 Bcash",
        inline=False
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Asisten Lurah BFL • Bcash | !price untuk detail market")
    await ctx.send(embed=embed)

@bot.command(name="givecoin")
async def give_coin(ctx, target: str = None, amount: str = None):
    """Admin beri Bcash ke user. Bisa di server (mention) atau DM (user_id)."""
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin.", delete_after=5 if not isinstance(ctx.channel, discord.DMChannel) else None)
        return

    if not target or not amount or not amount.replace(".", "").replace(",", "").isdigit():
        await ctx.send("❌ Format: `!givecoin @user 100` atau `!givecoin <user_id> 100`")
        return

    amt = int(amount.replace(".", "").replace(",", ""))

    # Resolve member — bisa mention atau user_id (penting untuk DM)
    member = None
    # Coba parse sebagai user_id
    raw_id = target.strip("<@!>")
    if raw_id.isdigit():
        try:
            member = await bot.fetch_user(int(raw_id))
        except Exception:
            pass
    if not member:
        await ctx.send("❌ User tidak ditemukan. Gunakan mention `@user` atau ID numerik.")
        return

    uid = str(member.id)
    ensure_coins(uid)
    ensure_coins(ADMIN_BANK_ID)
    admin_bal = get_coins(ADMIN_BANK_ID)
    if admin_bal < amt:
        return await ctx.send(f"❌ Saldo admin bank tidak cukup! Saldo: **{admin_bal:,} Bcash**, butuh: **{amt:,} Bcash**.")

    add_coins(ADMIN_BANK_ID, -amt)
    new_balance = add_coins(uid, amt)
    mint_coins(amt)
    log_history(uid, "💝 Givecoin dari Admin", +amt)
    log_history(ADMIN_BANK_ID, f"💝 Givecoin → {member.display_name}", -amt)

    display = f"<@{member.id}>" if not isinstance(ctx.channel, discord.DMChannel) else f"**{member.display_name}**"
    await ctx.send(f"✅ **{amt:,} Bcash** diberikan ke {display}. Saldo sekarang: **{new_balance:,} Bcash**")

    # Notif DM ke penerima
    try:
        await member.send(f"💝 Kamu mendapat **{amt:,} Bcash** dari Admin!\nSaldo sekarang: **{new_balance:,} Bcash**")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════
#  MARKET SYSTEM
# ═══════════════════════════════════════════════════════
def load_market():
    return load_json(MARKET_FILE, default={})

def save_market(d):
    save_json(MARKET_FILE, d)

def load_inventory():
    return load_json(INVENTORY_FILE, default={})

def save_inventory(d):
    save_json(INVENTORY_FILE, d)

@bot.command(name="additem", aliases=["addmarket"])
async def add_market_item(ctx):
    """Admin setup item market via DM (nama, harga, deskripsi, foto katalog)"""
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Command ini hanya via DM bot.", delete_after=5)
        return
    if not is_admin(ctx.author) and ctx.author.id != OWNER_ID:
        await ctx.send("❌ Hanya admin yang boleh setup market.", delete_after=5)
        return

    await ctx.send("🛒 **Setup Item Market Baru**\n\n**1.** Ketik **nama item** (contoh: Kaos BFL Premium)")
    
    def check(m): 
        return m.author.id == ctx.author.id and isinstance(m.channel, discord.DMChannel)

    try:
        # Nama
        name_msg = await bot.wait_for("message", check=check, timeout=180)
        name = name_msg.content.strip()[:100]

        await ctx.send("**2.** Ketik **harga dalam Bcash** (contoh: 500)")
        price_msg = await bot.wait_for("message", check=check, timeout=60)
        if not price_msg.content.strip().isdigit():
            await ctx.send("❌ Harga harus angka!")
            return
        price = int(price_msg.content.strip())

        await ctx.send("**3.** Ketik **deskripsi item** (bisa panjang)")
        desc_msg = await bot.wait_for("message", check=check, timeout=180)
        description = desc_msg.content.strip()[:500]

        await ctx.send("**4.** Ketik **jumlah stok** (contoh: `10`), atau ketik `unlimited` jika tidak terbatas.")
        stock_msg = await bot.wait_for("message", check=check, timeout=60)
        stock_raw = stock_msg.content.strip().lower()
        if stock_raw in ["unlimited", "infinite", "tak terbatas", "-1", "∞"]:
            stock = -1
        elif stock_raw.isdigit() and int(stock_raw) > 0:
            stock = int(stock_raw)
        else:
            await ctx.send("❌ Stok harus angka positif atau `unlimited`!")
            return

        await ctx.send("**5.** Kirim **foto katalog** (satu attachment gambar) sekarang.")
        
        def check_photo(m):
            return (m.author.id == ctx.author.id and 
                    isinstance(m.channel, discord.DMChannel) and 
                    m.attachments and 
                    m.attachments[0].content_type.startswith("image"))
        
        photo_msg = await bot.wait_for("message", check=check_photo, timeout=300)
        image_url = photo_msg.attachments[0].url

        # Simpan ke market
        market = load_market()
        item_id = f"item_{int(datetime.datetime.utcnow().timestamp())}"
        market[item_id] = {
            "name": name,
            "price": price,
            "description": description,
            "image_url": image_url,
            "stock": stock,
            "added_by": str(ctx.author.id),
            "added_at": str(datetime.datetime.utcnow())
        }
        save_market(market)

        stock_str = "∞ Unlimited" if stock == -1 else str(stock)
        embed = discord.Embed(title="✅ Item Berhasil Ditambahkan!", color=discord.Color.green())
        embed.add_field(name="ID", value=f"`{item_id}`", inline=False)
        embed.add_field(name="Nama", value=name, inline=False)
        embed.add_field(name="Harga", value=f"{price} Bcash", inline=True)
        embed.add_field(name="Stok", value=stock_str, inline=True)
        embed.set_thumbnail(url=image_url)
        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        await ctx.send("⏰ Timeout. Ulangi dengan `!additem`.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

@bot.command(name="market", aliases=["shop", "katalog"])
async def show_market(ctx):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    market = load_market()
    if not market:
        await ctx.send("🛒 Market masih kosong. Admin bisa tambah dengan `!additem` via DM.")
        return

    # Bagi item ke beberapa embed (max 25 field per embed Discord)
    items_list = list(market.items())
    chunks = [items_list[i:i+8] for i in range(0, len(items_list), 8)]

    for page_num, chunk in enumerate(chunks):
        embed = discord.Embed(
            title="🛒 KATALOG MARKET BFL",
            description="Gunakan `!buy <ID>` untuk membeli item",
            color=discord.Color.gold()
        )
        if len(chunks) > 1:
            embed.title = f"🛒 KATALOG MARKET BFL (Halaman {page_num+1}/{len(chunks)})"

        for item_id, item in chunk:
            stock = item.get("stock", -1)
            if stock == -1:
                stock_str = "✅ ∞"
            elif stock > 0:
                stock_str = f"✅ {stock}"
            else:
                stock_str = "❌ Habis"

            embed.add_field(
                name=f"🛍️ {item['name']}",
                value=(
                    f"💰 **{item['price']} Bcash**\n"
                    f"📦 Stok: {stock_str}\n"
                    f"📝 {item['description'][:80]}{'...' if len(item['description']) > 80 else ''}\n"
                    f"🆔 `{item_id}`"
                ),
                inline=True
            )

        # Gunakan thumbnail item pertama di chunk sebagai preview
        first_item = chunk[0][1]
        embed.set_thumbnail(url=first_item.get("image_url", ""))
        embed.set_footer(text=f"Total {len(items_list)} item | Asisten Lurah BFL")
        await ctx.send(embed=embed)

@bot.command(name="buy")
async def buy_item(ctx, item_id: str = None):
    if not is_game_channel(ctx):
        await ctx.send(game_channel_msg(ctx), delete_after=8)
        return
    if not item_id:
        await ctx.send("❌ Gunakan `!buy <item_id>` (contoh: `!buy item_1747320000`)")
        return

    market = load_market()
    if item_id not in market:
        await ctx.send("❌ Item ID tidak ditemukan di market.")
        return

    item = market[item_id]

    # Cek stok
    stock = item.get("stock", -1)
    if stock == 0:
        await ctx.send(f"❌ **{item['name']}** sudah habis stok!")
        return

    uid = str(ctx.author.id)
    ensure_coins(uid)
    balance = get_coins(uid)

    if balance < item["price"]:
        await ctx.send(f"❌ Bcash tidak cukup! Kamu punya **{balance:,} Bcash**, butuh **{item['price']:,} Bcash**.")
        return

    # Potong coin, masuk ke admin bank sebagai pendapatan market
    add_coins(uid, -item["price"])
    add_coins(ADMIN_BANK_ID, +item["price"])
    burn_coins(item["price"])   # burn untuk pengaruhi supply/harga
    log_history(ADMIN_BANK_ID, f"🛒 Pendapatan market: {item['name']} dari {ctx.author.display_name}", +item["price"])

    # Kurangi stok jika bukan unlimited
    if stock != -1:
        market[item_id]["stock"] = stock - 1
        save_market(market)

    # Notif di channel
    embed_ok = discord.Embed(title="🎉 Pembelian Berhasil!", color=discord.Color.green())
    embed_ok.add_field(name="Item", value=item["name"], inline=False)
    embed_ok.add_field(name="Harga", value=f"-{item['price']:,} Bcash", inline=True)
    embed_ok.set_thumbnail(url=item["image_url"])
    embed_ok.set_footer(text="Cek DM kamu untuk mengisi data pengiriman!")
    await ctx.send(embed=embed_ok)

    # Buka DM untuk isi form
    try:
        dm = await ctx.author.create_dm()

        def check_dm(m):
            return m.author.id == ctx.author.id and isinstance(m.channel, discord.DMChannel)

        await dm.send(
            f"📦 **Form Pembelian — {item['name']}**\n\n"
            f"Harga: **{item['price']:,} Bcash** ✅ Sudah dibayar\n\n"
            f"Isi data pengiriman kamu:\n\n**1.** Ketik **nama lengkap** kamu:"
        )

        try:
            nama_msg = await bot.wait_for("message", check=check_dm, timeout=180)
            nama = nama_msg.content.strip()[:100]

            await dm.send("**2.** Ketik **nomor HP / WhatsApp** kamu:")
            hp_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            nomor_hp = hp_msg.content.strip()[:30]

            await dm.send("**3.** Ketik **alamat lengkap** pengiriman kamu:")
            alamat_msg = await bot.wait_for("message", check=check_dm, timeout=300)
            alamat = alamat_msg.content.strip()[:500]

            # Simpan order ke file orders
            orders = load_json("orders.json", default=[])
            order_entry = {
                "user_id": str(ctx.author.id),
                "username": ctx.author.display_name,
                "item_id": item_id,
                "item_name": item["name"],
                "price": item["price"],
                "nama": nama,
                "nomor_hp": nomor_hp,
                "alamat": alamat,
                "time": datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "status": "pending"
            }
            orders.append(order_entry)
            save_json("orders.json", orders)

            # Konfirmasi ke pembeli
            konfirm = discord.Embed(
                title="✅ Data Pengiriman Tersimpan!",
                color=discord.Color.green()
            )
            konfirm.add_field(name="🛍️ Item", value=item["name"], inline=False)
            konfirm.add_field(name="👤 Nama", value=nama, inline=True)
            konfirm.add_field(name="📱 No. HP", value=nomor_hp, inline=True)
            konfirm.add_field(name="📍 Alamat", value=alamat, inline=False)
            konfirm.set_footer(text="Admin akan menghubungi kamu segera • Asisten Lurah BFL")
            await dm.send(embed=konfirm)

            # Kirim notif ke owner / admin
            try:
                owner = await bot.fetch_user(OWNER_ID)
                notif = discord.Embed(
                    title="🔔 Order Baru Masuk!",
                    color=discord.Color.orange()
                )
                notif.add_field(name="👤 Pembeli", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=False)
                notif.add_field(name="🛍️ Item", value=f"{item['name']} (`{item_id}`)", inline=False)
                notif.add_field(name="💰 Harga", value=f"{item['price']:,} Bcash", inline=True)
                notif.add_field(name="📛 Nama", value=nama, inline=True)
                notif.add_field(name="📱 No. HP", value=nomor_hp, inline=True)
                notif.add_field(name="📍 Alamat", value=alamat, inline=False)
                notif.set_footer(text=f"Waktu: {order_entry['time']}")
                await owner.send(embed=notif)
            except Exception:
                pass

        except asyncio.TimeoutError:
            await dm.send(
                "⏰ Timeout mengisi form. Data pengirimanmu belum tersimpan.\n"
                "Hubungi admin secara manual untuk konfirmasi pembelian."
            )

    except discord.Forbidden:
        await ctx.send(
            f"⚠️ {ctx.author.mention} Pembelian berhasil tapi DM kamu tertutup!\n"
            "Buka DM bot dan hubungi admin untuk isi data pengiriman."
        )

@bot.command(name="inventory", aliases=["inv", "barang", "myitems"])
async def show_inventory(ctx, member: discord.Member = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    member = member or ctx.author
    uid = str(member.id)
    inventory = load_inventory().get(uid, [])
    if not inventory:
        await ctx.send(f"🛍️ {member.mention} belum punya barang di inventory.")
        return

    embed = discord.Embed(title=f"🛍️ Inventory — {member.display_name}", color=discord.Color.purple())
    for item in inventory[-10:]:  # tampilkan 10 terakhir
        embed.add_field(
            name=item["name"],
            value=f"ID: `{item['item_id']}` • Dibeli: {item['bought_at'][:10]}",
            inline=False
        )
    embed.set_footer(text=f"Total item: {len(inventory)}")
    await ctx.send(embed=embed)

@bot.command(name="deleteitem", aliases=["hapusitem", "removeitem"])
async def delete_market_item(ctx, item_id: str = None):
    """Admin hapus item dari market. Bisa di server maupun DM."""
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin yang bisa menghapus item.")
        return
    if not item_id:
        await ctx.send("❌ Format: `!deleteitem <item_id>`\nContoh: `!deleteitem item_1747320000`")
        return

    market = load_market()
    if item_id not in market:
        await ctx.send(f"❌ Item `{item_id}` tidak ditemukan di market.")
        return

    item_name = market[item_id]["name"]
    del market[item_id]
    save_market(market)

    embed = discord.Embed(
        title="🗑️ Item Dihapus dari Market",
        description=f"**{item_name}** (`{item_id}`) berhasil dihapus.",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Dihapus oleh {ctx.author}")
    await ctx.send(embed=embed)

@bot.command(name="listuser", aliases=["daftaruser", "richlist"])
async def list_user_coins(ctx):
    """Admin — tampilkan semua user yang punya lebih dari 1 Bcash. Bisa di server maupun DM."""
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin yang bisa melihat command ini.")
        return

    coins = load_coins()
    # Filter user dengan lebih dari 1 koin, urutkan dari terbanyak
    rich_users = [
        (uid, int(bal)) for uid, bal in coins.items()
        if str(uid) != ADMIN_BANK_ID and int(bal) > 1
    ]
    rich_users.sort(key=lambda x: x[1], reverse=True)

    if not rich_users:
        await ctx.send("📭 Tidak ada user dengan saldo lebih dari 1 Bcash.")
        return

    price_data = load_price()
    price = price_data.get("price", 10000)

    embed = discord.Embed(
        title="💰 Daftar User Bcash (> 1 Bcash)",
        description=f"Total: **{len(rich_users)} user** | Harga: Rp{price:,}/100",
        color=discord.Color.gold()
    )

    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, (uid, bal) in enumerate(rich_users[:25]):  # max 25
        medal = medals[i] if i < 3 else f"`#{i+1}`"
        idr = int((bal / 100) * price)
        try:
            user = await bot.fetch_user(int(uid))
            name = user.display_name
        except Exception:
            name = f"User#{uid}"
        lines.append(f"{medal} **{name}** — {bal:,} Bcash (≈ Rp{idr:,})")

    # Potong jika terlalu panjang
    chunk_size = 10
    for chunk_start in range(0, len(lines), chunk_size):
        chunk = lines[chunk_start:chunk_start + chunk_size]
        field_name = f"Peringkat {chunk_start+1}–{chunk_start+len(chunk)}"
        embed.add_field(name=field_name, value="\n".join(chunk), inline=False)

    embed.set_footer(text=f"Asisten Lurah BFL • Hanya terlihat admin | Total user terdaftar: {len(coins)}")
    await ctx.send(embed=embed)


@bot.command(name="supply", aliases=["supplyinfo", "sirkulasi"])
async def supply_cmd(ctx):
    """Admin — lihat info sirkulasi: total supply beredar, daftar holder, total burn. Bisa di DM."""
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin yang bisa melihat command ini.")
        return

    price_data  = load_price()
    coins_data  = load_coins()
    history_data = load_json(HISTORY_FILE, default={})

    # ── Hitung total beredar (semua user kecuali admin bank) ──
    total_beredar = 0
    holder_list   = []
    for uid, bal in coins_data.items():
        if str(uid) == ADMIN_BANK_ID:
            continue
        b = int(bal)
        if b > 0:
            total_beredar += b
            holder_list.append((str(uid), b))

    holder_list.sort(key=lambda x: x[1], reverse=True)

    # ── Hitung total coin yang pernah di-burn dari history ──
    total_burned = 0
    for uid, entries in history_data.items():
        for e in entries:
            lbl = e.get("label", "")
            # burn terjadi saat: slot kalah, buy item, lotre, convert, trade lose, duel
            if any(kw in lbl.lower() for kw in ["slot bet", "beli", "tiket lotre", "convert", "trade taruhan", "duel", "burn"]):
                if e["amount"] < 0:
                    total_burned += abs(e["amount"])

    supply_in_price = price_data.get("supply", 0)
    admin_bal       = get_coins(ADMIN_BANK_ID)
    price           = price_data.get("price", _PRICE_INITIAL)
    total_minted    = price_data.get("minted", 0)
    total_burned_stat = price_data.get("burned", 0)
    # Supply sejati = saldo admin bank + semua Bcash yg di-mint dari game
    real_supply     = admin_bal + total_minted

    # ── Embed utama ──
    embed = discord.Embed(
        title="📊 Laporan Sirkulasi Bcash",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="💰 Saldo Admin Bank",    value=f"**{admin_bal:,} Bcash**",       inline=True)
    embed.add_field(name="🏦 Total Beredar (User)",value=f"**{total_beredar:,} Bcash**",    inline=True)
    embed.add_field(name="📦 Total Supply Sistem", value=f"**{real_supply:,} Bcash**\n*(Admin Bank + Mint Game)*", inline=True)
    embed.add_field(name="🔥 Total Burn (Game)",   value=f"**{total_burned_stat:,} Bcash**", inline=True)
    embed.add_field(name="🪙 Total Mint (Game)",   value=f"**{total_minted:,} Bcash**",     inline=True)
    embed.add_field(name="👥 Total Holder Aktif",  value=f"**{len(holder_list)} user**",    inline=True)
    embed.add_field(name="💱 Harga Saat Ini",      value=f"**Rp{price:,}** / 100 Bcash",   inline=True)

    # ── Top 10 holder ──
    if holder_list:
        lines = []
        medals = ["🥇","🥈","🥉"]
        for i, (uid, bal) in enumerate(holder_list[:10]):
            medal = medals[i] if i < 3 else f"`#{i+1}`"
            idr   = int((bal / 100) * price)
            try:
                user = await bot.fetch_user(int(uid))
                nama = user.display_name
            except Exception:
                nama = f"User#{uid}"
            lines.append(f"{medal} **{nama}** — {bal:,} Bcash ≈ Rp{idr:,}")
        embed.add_field(
            name=f"🏆 Top {min(10, len(holder_list))} Holder",
            value="\n".join(lines),
            inline=False
        )

    embed.set_footer(text=f"Asisten Lurah BFL • Admin Only | Supply naik → harga ↓, burn → harga ↑")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
PRICE_FILE  = "coin_price.json"

# ══════════════════════════════════════════════════════════════════════
#  KONSTANTA MARKET
#  Hard cap: 100 Bcash = Rp15.000 (batas atas mutlak)
#  Floor   : 100 Bcash = Rp1.000  (batas bawah mutlak)
#
#  SISTEM HARGA:
#  - Harga HANYA bergerak dari aktivitas game, burn, dan mint
#  - Tidak ada random walk / pergerakan palsu otomatis
#  - Kalah game → Bcash di-burn → supply turun → harga naik
#  - Menang game → Bcash di-mint baru → supply naik → harga turun
#  - Supply = saldo admin bank + semua Bcash yang sudah di-mint dari game
# ══════════════════════════════════════════════════════════════════════
_PRICE_INITIAL = 10000   # harga awal  : 100 Bcash = Rp10.000
_PRICE_CAP     = 15000   # batas atas  : 100 Bcash = Rp15.000 (HARD CAP)
_PRICE_FLOOR   = 1000    # batas bawah : 100 Bcash = Rp1.000
_SUPPLY_INIT   = 20000   # supply awal Bcash

# ── GAME SETTINGS (bisa diubah admin via !setgame) ────
_GAME_SETTINGS_DEFAULT = {
    "winrate": {          # winrate default per game (0.0 - 1.0)
        "slot":     0.45,
        "coinflip": 0.50,
        "balapan":  0.45,
        "ball":     0.42,
        "hunt":     0.60,
        "duel":     0.50,
        "bonanza":  0.30,   # bonanza — susah, cluster jarang terbentuk
    },
    "bonanza_scatter_chance": 0.15,  # chance scatter muncul per spin setelah target (default 15%)
    "bonanza_fs_cap_chance":  0.35,  # chance free spin total dikap ×10 dari bet (default 35%)
    "admin_winrate": 0.90,  # winrate admin saat bermain game (90%)
    "max_bet": {            # max bet per game (Bcash)
        "slot":    100,
        "coinflip": 10,
        "balapan":  15,
        "ball":     15,
        "hunt":      2,   # hunt fixed cost, bukan bet
        "duel":    999,
        "bonanza":  15,  # max bet bonanza (1–15 Bcash)
    },
    "rewards": {            # multiplier reward saat menang
        "slot_x1":  1.0,
        "slot_x15": 1.5,
        "slot_x2":  2.0,
        "coinflip": 2.0,
        "balapan":  2.0,
        "ball":     2.0,
        "duel":     2.0,
        "bonanza":  2.0,
    },
    "hunt_rewards": [       # (min, max, chance_pct, label, emoji)
        (2,  5,  40, "Buruan Kecil",   "🐇"),
        (5,  7,  10, "Buruan Sedang",  "🦌"),
        (15, 15,  5, "JACKPOT BESAR",  "🐗"),
    ],
}

GAME_SETTINGS_FILE = "game_settings.json"

def load_game_settings() -> dict:
    d = load_json(GAME_SETTINGS_FILE, default={})
    # Merge default agar key baru selalu ada
    import copy
    result = copy.deepcopy(_GAME_SETTINGS_DEFAULT)
    def deep_merge(base, override):
        for k, v in override.items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                deep_merge(base[k], v)
            else:
                base[k] = v
    deep_merge(result, d)
    return result

def save_game_settings(d: dict):
    save_json(GAME_SETTINGS_FILE, d)

def get_winrate(game: str, is_admin_player: bool = False) -> float:
    """Ambil winrate untuk game tertentu. Admin dapat winrate 90%."""
    gs = load_game_settings()
    if is_admin_player:
        return gs.get("admin_winrate", 0.90)
    return gs["winrate"].get(game, 0.50)

def get_max_bet(game: str) -> int:
    gs = load_game_settings()
    return gs["max_bet"].get(game, 15)

def get_reward_multiplier(key: str) -> float:
    gs = load_game_settings()
    return gs["rewards"].get(key, 2.0)

_PRICE_FILE_DEFAULT = {
    "price":    _PRICE_INITIAL,
    "supply":   _SUPPLY_INIT,
    "history":  [],
    "pressure": 0.0,   # akumulasi tekanan dari game (positif=naik, negatif=turun)
    "minted":   0,     # total Bcash yang pernah di-mint dari game
    "burned":   0,     # total Bcash yang pernah di-burn dari game
}

def load_price():
    d = load_json(PRICE_FILE, default=_PRICE_FILE_DEFAULT.copy())
    for k, v in _PRICE_FILE_DEFAULT.items():
        d.setdefault(k, v)
    return d

def save_price(d):
    save_json(PRICE_FILE, d)

def coin_to_idr(coin_amount: int) -> int:
    return int((coin_amount / 100) * load_price()["price"])

def get_total_supply() -> int:
    """Supply = saldo admin bank + semua Bcash yg sudah di-mint dari game."""
    admin_bal = get_coins(ADMIN_BANK_ID)
    price_data = load_price()
    minted = price_data.get("minted", 0)
    return admin_bal + minted

# ── Trigger tekanan harga dari game ───────────────────
def price_trigger(pressure_delta: float, reason: str = ""):
    """
    Tambah tekanan harga dari aktivitas game.
    pressure_delta > 0 → harga naik (burn/kalah)
    pressure_delta < 0 → harga turun (mint/menang)
    Tekanan langsung diserap ke harga seketika.
    """
    data = load_price()
    current = data["price"]
    # Langsung ubah harga berdasarkan pressure (tidak ada random walk)
    move = int(pressure_delta)
    new_price = max(_PRICE_FLOOR, min(_PRICE_CAP, current + move))
    data["price"] = new_price
    hist = data.get("history", [])
    if not hist or hist[-1] != new_price:
        hist.append(new_price)
        data["history"] = hist[-288:]   # ~24 jam jika tiap 5 menit
    data["pressure"] = 0.0  # reset setelah diserap
    save_price(data)
    print(f"[MARKET] {reason} | Δ={pressure_delta:+.1f} | harga={new_price:,}")

# ── Engine harga — hanya dari game activity (tidak ada random walk) ──
def market_tick() -> int:
    """
    Tick market: hanya memproses sisa pressure yang carry-over.
    Harga TIDAK bergerak tanpa ada aktivitas game / burn / mint.
    """
    data     = load_price()
    pressure = data.get("pressure", 0.0)

    if abs(pressure) < 1:
        # Tidak ada tekanan signifikan, harga tidak bergerak
        return data["price"]

    current   = data["price"]
    move      = int(pressure * 0.8)  # serap 80% carry-over
    new_price = max(_PRICE_FLOOR, min(_PRICE_CAP, current + move))

    data["price"]    = new_price
    data["pressure"] = pressure * 0.2  # sisa 20% carry ke tick berikutnya
    hist = data.get("history", [])
    if not hist or hist[-1] != new_price:
        hist.append(new_price)
        data["history"] = hist[-288:]
    save_price(data)
    return new_price

@tasks.loop(minutes=5)
async def auto_price_update():
    """Serap sisa pressure carry-over setiap 5 menit. Tidak ada gerak acak."""
    market_tick()

def burn_coins(amount: int):
    """
    Bcash di-burn → supply turun → harga naik.
    Saat user kalah: saldo di-burn otomatis, tidak masuk ke siapa-siapa.
    Hadiah game berasal dari Bcash baru yang di-mint, bukan dari saldo admin.
    """
    data = load_price()
    data["supply"] = max(1, data.get("supply", _SUPPLY_INIT) - amount)
    data["burned"] = data.get("burned", 0) + amount
    save_price(data)
    # Supply turun → harga naik langsung
    pressure_delta = max(20, amount * 0.5)   # min Rp20 naik per burn
    price_trigger(pressure_delta, f"burn {amount} Bcash")

def mint_coins(amount: int):
    """
    Bcash baru di-mint → supply naik → harga turun.
    Hadiah menang game SELALU dari mint baru, bukan dari saldo admin.
    """
    data = load_price()
    data["supply"] = data.get("supply", _SUPPLY_INIT) + amount
    data["minted"] = data.get("minted", 0) + amount
    save_price(data)
    # Supply naik → harga turun langsung
    pressure_delta = min(-10, -amount * 0.3)
    price_trigger(pressure_delta, f"mint {amount} Bcash")

# ── Commands ──────────────────────────────────────────────
@bot.command(name="convertcoin")
async def convert_coin(ctx, amount: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    # Hitung minimum Bcash agar nilai IDR >= 50.000
    current_price = load_price()["price"]
    min_bcash = math.ceil(50000 / (current_price / 100))   # Bcash yang nilainya = Rp50.000

    if not amount:
        return await ctx.send(
            f"❌ Contoh: `!convertcoin {min_bcash}`\n"
            f"💡 Minimum WD: **Rp50.000** = **{min_bcash:,} Bcash** (harga saat ini Rp{current_price:,}/100)"
        )

    idr_preview = int((amount / 100) * current_price)
    if idr_preview < 50000:
        return await ctx.send(
            f"❌ Minimum penarikan **Rp50.000**!\n"
            f"Kamu mau convert **{amount:,} Bcash** = **Rp{idr_preview:,}** — belum cukup.\n"
            f"💡 Kamu butuh minimal **{min_bcash:,} Bcash** (≈ Rp50.000 saat ini)."
        )

    uid = str(ctx.author.id)
    ensure_coins(uid)
    bal = get_coins(uid)
    if bal < amount:
        return await ctx.send(f"❌ Coin tidak cukup! Saldo kamu: **{bal:,} Bcash**, butuh: **{amount:,} Bcash**.")

    idr = coin_to_idr(amount)

    # Potong coin, masuk ke admin bank, burn sisanya (untuk pengaruhi supply)
    add_coins(uid, -amount)
    add_coins(ADMIN_BANK_ID, +amount)   # kekalahan/convert → masuk admin bank
    burn_coins(amount)                   # tetap burn untuk pengaruhi harga
    price_trigger(+amount * 0.8, f"convert {amount} Bcash ke IDR")
    log_history(uid, f"💱 WD ke IDR (Rp{idr:,})", -amount)
    log_history(ADMIN_BANK_ID, f"💱 WD masuk dari {ctx.author.display_name}", +amount)

    await ctx.send(f"✅ Convert **{amount:,} Bcash** (≈ **Rp{idr:,}**) berhasil. Cek DM kamu untuk isi data penarikan!")

    # Buka DM untuk isi form penarikan
    try:
        dm = await ctx.author.create_dm()

        EWALLET_OPTIONS = {
            "1": "DANA",
            "2": "OVO",
            "3": "ShopeePay",
        }

        def check_dm(m):
            return m.author.id == ctx.author.id and isinstance(m.channel, discord.DMChannel)

        await dm.send(
            f"💱 **Form Penarikan Bcash**\n\n"
            f"💰 Jumlah: **{amount:,} Bcash**\n"
            f"💵 Nilai: **Rp{idr:,}**\n"
            f"📊 Harga saat convert: **Rp{current_price:,}** / 100 Bcash\n\n"
            f"Pilih **e-wallet** tujuan penarikan:\n"
            f"`1` — DANA\n"
            f"`2` — OVO\n"
            f"`3` — ShopeePay\n\n"
            f"Ketik angka pilihanmu (1/2/3):"
        )

        try:
            pilih_msg = await bot.wait_for("message", check=check_dm, timeout=60)
            pilihan = pilih_msg.content.strip()
            if pilihan not in EWALLET_OPTIONS:
                await dm.send("❌ Pilihan tidak valid. Penarikan dibatalkan. Ulangi dengan `!convertcoin`.")
                return
            ewallet = EWALLET_OPTIONS[pilihan]

            await dm.send(f"📱 Ketik **nomor {ewallet}** kamu (contoh: 0812xxxxxxxx):")
            nomor_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            nomor = nomor_msg.content.strip()[:20]

            await dm.send(f"👤 Ketik **nama pemilik akun {ewallet}** (sesuai yang terdaftar):")
            nama_msg = await bot.wait_for("message", check=check_dm, timeout=120)
            nama_akun = nama_msg.content.strip()[:100]

            # Simpan withdrawal request
            withdrawals = load_json("withdrawals.json", default=[])
            entry = {
                "user_id": str(ctx.author.id),
                "username": ctx.author.display_name,
                "amount_bcash": amount,
                "amount_idr": idr,
                "price_at_convert": current_price,
                "ewallet": ewallet,
                "nomor": nomor,
                "nama_akun": nama_akun,
                "time": datetime.datetime.utcnow().strftime("%d/%m/%Y %H:%M"),
                "status": "pending"
            }
            withdrawals.append(entry)
            save_json("withdrawals.json", withdrawals)

            # Konfirmasi ke user
            konfirm = discord.Embed(
                title="✅ Request Penarikan Diterima!",
                color=discord.Color.green()
            )
            konfirm.add_field(name="💰 Jumlah", value=f"{amount:,} Bcash", inline=True)
            konfirm.add_field(name="💵 Nilai IDR", value=f"Rp{idr:,}", inline=True)
            konfirm.add_field(name="📲 E-Wallet", value=ewallet, inline=True)
            konfirm.add_field(name="📱 Nomor", value=nomor, inline=True)
            konfirm.add_field(name="👤 Nama Akun", value=nama_akun, inline=True)
            konfirm.set_footer(text="Admin akan memproses dalam 1×24 jam • Asisten Lurah BFL")
            await dm.send(embed=konfirm)

            # Notif ke owner/admin
            try:
                owner = await bot.fetch_user(OWNER_ID)
                notif = discord.Embed(
                    title="💸 Request Penarikan Baru!",
                    color=discord.Color.orange()
                )
                notif.add_field(name="👤 User", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=False)
                notif.add_field(name="💰 Bcash", value=f"{amount:,} Bcash", inline=True)
                notif.add_field(name="💵 IDR", value=f"Rp{idr:,}", inline=True)
                notif.add_field(name="📲 E-Wallet", value=ewallet, inline=True)
                notif.add_field(name="📱 Nomor", value=nomor, inline=True)
                notif.add_field(name="👤 Nama Akun", value=nama_akun, inline=True)
                notif.set_footer(text=f"Waktu: {entry['time']} | Harga: Rp{current_price:,}/100 Bcash")
                await owner.send(embed=notif)
            except Exception:
                pass

        except asyncio.TimeoutError:
            await dm.send(
                "⏰ Timeout mengisi form penarikan.\n"
                "Bcash sudah dipotong. Hubungi admin secara manual untuk konfirmasi penarikan."
            )

    except discord.Forbidden:
        await ctx.send(
            f"⚠️ {ctx.author.mention} DM kamu tertutup! Buka DM bot dan hubungi admin "
            f"untuk konfirmasi penarikan **{amount:,} Bcash (Rp{idr:,})**."
        )

@bot.command(name="setprice")
async def setprice(ctx, new_price: int = None):
    """Admin set harga pasar langsung (override manual)."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Admin only.")
    if not new_price or new_price < _PRICE_FLOOR:
        return await ctx.send(f"❌ Contoh: `!setprice 10000` (Rp{_PRICE_FLOOR:,}–Rp{_PRICE_CAP:,})")
    data = load_price()
    new_price         = min(new_price, _PRICE_CAP)
    data["price"]     = new_price
    data["pressure"]  = 0.0
    save_price(data)
    await ctx.send(f"✅ Harga Bcash diset ke **Rp{new_price:,}** / 100 Bcash.")


# ═══════════════════════════════════════════════════════
#  SETGAME — Admin kelola winrate, hadiah, max bet game
# ═══════════════════════════════════════════════════════
@bot.command(name="setgame", aliases=["gamesetting", "gameset"])
async def setgame_cmd(ctx, action: str = None, game: str = None, value: str = None):
    """
    Admin atur winrate, maxbet, reward game.
    Bisa di server atau DM.

    Contoh:
      !setgame winrate slot 0.60       → winrate slot 60%
      !setgame winrate coinflip 0.55   → winrate coinflip 55%
      !setgame adminwinrate 0.90       → winrate admin 90% di semua game
      !setgame maxbet ball 20          → max bet ball 20 Bcash
      !setgame reward coinflip 2.5     → multiplier coinflip 2.5x
      !setgame info                    → lihat semua setting saat ini
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.")

    gs = load_game_settings()
    GAMES = list(_GAME_SETTINGS_DEFAULT["winrate"].keys())

    if not action or action.lower() == "info":
        # Tampilkan semua setting
        embed = discord.Embed(
            title="⚙️ Game Settings — Asisten Lurah BFL",
            color=discord.Color.blurple()
        )
        wr_lines = []
        for g, wr in gs["winrate"].items():
            wr_lines.append(f"`{g}`: **{wr*100:.0f}%**")
        embed.add_field(
            name="🎯 Winrate User",
            value="\n".join(wr_lines),
            inline=True
        )
        admin_wr = gs.get("admin_winrate", 0.90)
        embed.add_field(
            name="👑 Winrate Admin",
            value=f"**{admin_wr*100:.0f}%** (semua game)",
            inline=True
        )
        mb_lines = []
        for g, mb in gs["max_bet"].items():
            mb_lines.append(f"`{g}`: **{mb} Bcash**")
        embed.add_field(
            name="💰 Max Bet",
            value="\n".join(mb_lines),
            inline=False
        )
        rw_lines = []
        for k, rv in gs["rewards"].items():
            rw_lines.append(f"`{k}`: **{rv}×**")
        embed.add_field(
            name="🏆 Multiplier Reward",
            value="\n".join(rw_lines),
            inline=False
        )
        embed.set_footer(text="Gunakan !setgame winrate/maxbet/reward/adminwinrate/scatter/fscap untuk edit")
        scatter_pct = gs.get("bonanza_scatter_chance", 0.15) * 100
        fscap_pct   = gs.get("bonanza_fs_cap_chance",  0.35) * 100
        embed.add_field(
            name="🍬 Bonanza Scatter & FS Cap",
            value=(
                f"`scatter`: **{scatter_pct:.0f}%** chance scatter muncul per spin\n"
                f"`fscap`: **{fscap_pct:.0f}%** chance FS total dikap ×10 dari bet"
            ),
            inline=False
        )
        return await ctx.send(embed=embed)

    action = action.lower()

    if action == "winrate":
        if not game or not value:
            return await ctx.send(f"❌ Contoh: `!setgame winrate slot 0.60`\nGame: {', '.join(GAMES)}")
        if game not in GAMES:
            return await ctx.send(f"❌ Game tidak valid. Pilih: {', '.join(GAMES)}")
        try:
            val = float(value)
        except ValueError:
            return await ctx.send("❌ Winrate harus angka desimal (0.0 – 1.0). Contoh: `0.55`")
        val = max(0.0, min(1.0, val))
        gs["winrate"][game] = val
        save_game_settings(gs)
        await ctx.send(f"✅ Winrate **{game}** diset ke **{val*100:.0f}%**")

    elif action == "adminwinrate":
        # !setgame adminwinrate 0.90
        target_val = game or value  # fleksibel argumen
        if not target_val:
            return await ctx.send("❌ Contoh: `!setgame adminwinrate 0.90`")
        try:
            val = float(target_val)
        except ValueError:
            return await ctx.send("❌ Winrate harus angka desimal (0.0 – 1.0).")
        val = max(0.0, min(1.0, val))
        gs["admin_winrate"] = val
        save_game_settings(gs)
        await ctx.send(f"✅ Winrate **admin** diset ke **{val*100:.0f}%** (berlaku di semua game)")

    elif action == "maxbet":
        if not game or not value:
            return await ctx.send(f"❌ Contoh: `!setgame maxbet ball 20`\nGame: {', '.join(GAMES)}")
        if game not in GAMES:
            return await ctx.send(f"❌ Game tidak valid. Pilih: {', '.join(GAMES)}")
        try:
            val = int(value)
        except ValueError:
            return await ctx.send("❌ Max bet harus angka bulat.")
        if val < 1:
            return await ctx.send("❌ Max bet minimal 1 Bcash.")
        gs["max_bet"][game] = val
        save_game_settings(gs)
        await ctx.send(f"✅ Max bet **{game}** diset ke **{val} Bcash**")

    elif action == "reward":
        if not game or not value:
            reward_keys = list(_GAME_SETTINGS_DEFAULT["rewards"].keys())
            return await ctx.send(f"❌ Contoh: `!setgame reward coinflip 2.5`\nKey: {', '.join(reward_keys)}")
        reward_keys = list(gs["rewards"].keys())
        if game not in reward_keys:
            return await ctx.send(f"❌ Key reward tidak valid. Pilih: {', '.join(reward_keys)}")
        try:
            val = float(value)
        except ValueError:
            return await ctx.send("❌ Multiplier harus angka. Contoh: `2.5`")
        if val < 1.0:
            return await ctx.send("❌ Multiplier minimal 1.0×")
        gs["rewards"][game] = val
        save_game_settings(gs)
        await ctx.send(f"✅ Reward multiplier **{game}** diset ke **{val}×**")

    elif action == "scatter":
        # !setgame scatter 20  → scatter chance 20% per spin
        target_val = game or value
        if not target_val:
            return await ctx.send("❌ Contoh: `!setgame scatter 20` (dalam persen, 1–100)")
        try:
            val = float(target_val)
        except ValueError:
            return await ctx.send("❌ Nilai harus angka persen. Contoh: `!setgame scatter 20`")
        val = max(1.0, min(100.0, val))
        gs["bonanza_scatter_chance"] = round(val / 100, 4)
        save_game_settings(gs)
        await ctx.send(f"✅ Scatter chance Bonanza diset ke **{val:.0f}%** per spin setelah target")

    elif action == "fscap":
        # !setgame fscap 35  → 35% chance FS total dikap ×10 dari bet
        target_val = game or value
        if not target_val:
            return await ctx.send("❌ Contoh: `!setgame fscap 35` (dalam persen, 0–100)")
        try:
            val = float(target_val)
        except ValueError:
            return await ctx.send("❌ Nilai harus angka persen. Contoh: `!setgame fscap 35`")
        val = max(0.0, min(100.0, val))
        gs["bonanza_fs_cap_chance"] = round(val / 100, 4)
        save_game_settings(gs)
        await ctx.send(f"✅ FS cap chance Bonanza diset ke **{val:.0f}%** (kap ×10 dari bet)")

    elif action == "huntreward":
        await ctx.send(
            "⚙️ Edit hunt reward tiers tidak didukung via command singkat.\n"
            "Edit file `game_settings.json` langsung untuk mengubah tier hunt."
        )

    else:
        await ctx.send(
            "❌ Action tidak valid.\n"
            "Pilih: `winrate` | `adminwinrate` | `maxbet` | `reward` | `scatter` | `fscap` | `info`"
        )

@bot.command(name="burncoin", aliases=["burn", "burnbcash"])
async def burncoin_cmd(ctx, amount: str = None, mode: str = "bank"):
    """
    Admin burn Bcash.
    !burncoin <jumlah>          → burn dari saldo admin bank (default)
    !burncoin <jumlah> supply   → burn paksa dari supply global (tidak perlu saldo bank)
    Bisa dipakai di server maupun DM.
    """
    if not is_admin(ctx.author):
        await ctx.send("❌ Hanya admin yang bisa burn coin.")
        return

    if not amount or not amount.replace(".", "").replace(",", "").isdigit():
        await ctx.send(
            "❌ Format: `!burncoin <jumlah>` atau `!burncoin <jumlah> supply`\n"
            "Contoh: `!burncoin 500` / `!burncoin 1000 supply`\n\n"
            "🔥 **bank** — burn dari saldo admin bank\n"
            "🔥 **supply** — burn paksa dari total supply global (tanpa potong saldo)"
        )
        return

    amt = int(amount.replace(".", "").replace(",", ""))
    if amt < 1:
        return await ctx.send("❌ Jumlah burn minimal 1 Bcash.")

    price_before = load_price()["price"]
    mode = mode.lower()

    if mode == "supply":
        # Burn paksa dari supply global — tidak potong saldo admin
        burn_coins(amt)
        log_history(ADMIN_BANK_ID, f"🔥 Supply burn paksa {amt:,} Bcash", -amt)
        price_after = load_price()["price"]
        delta = price_after - price_before
        arrow = "📈" if delta >= 0 else "📉"
        embed = discord.Embed(
            title="🔥 SUPPLY BURN BERHASIL",
            description=(
                f"**{amt:,} Bcash** di-burn langsung dari supply global!\n"
                f"Saldo admin bank **tidak berubah**."
            ),
            color=discord.Color.dark_orange()
        )
        embed.add_field(name="🔥 Jumlah Dibakar",      value=f"**{amt:,} Bcash**",  inline=True)
        embed.add_field(name="📊 Harga Sebelum",        value=f"Rp{price_before:,}", inline=True)
        embed.add_field(name="📈 Harga Sekarang",       value=f"Rp{price_after:,}",  inline=True)
        embed.add_field(name=f"{arrow} Perubahan",      value=f"**{'+' if delta >= 0 else ''}{delta:,}**", inline=True)
        embed.set_footer(text=f"Supply burn oleh {ctx.author.display_name} • Asisten Lurah BFL")
        return await ctx.send(embed=embed)

    else:
        # Mode default: burn dari saldo admin bank
        ensure_coins(ADMIN_BANK_ID)
        admin_bal = get_coins(ADMIN_BANK_ID)
        if admin_bal < amt:
            return await ctx.send(
                f"❌ Saldo admin bank tidak cukup!\n"
                f"Saldo admin: **{admin_bal:,} Bcash** | Mau burn: **{amt:,} Bcash**\n"
                f"💡 Gunakan `!burncoin {amt} supply` untuk burn paksa dari supply global."
            )

        add_coins(ADMIN_BANK_ID, -amt)
        burn_coins(amt)
        log_history(ADMIN_BANK_ID, f"🔥 Admin burn {amt:,} Bcash", -amt)

        price_after = load_price()["price"]
        admin_bal_after = get_coins(ADMIN_BANK_ID)

        embed = discord.Embed(
            title="🔥 COIN BURN BERHASIL",
            description=(
                f"**{amt:,} Bcash** berhasil di-burn dari saldo admin bank!\n"
                f"Supply berkurang → harga Bcash terdorong naik."
            ),
            color=discord.Color.orange()
        )
        embed.add_field(name="🔥 Jumlah Dibakar",       value=f"**{amt:,} Bcash**",              inline=True)
        embed.add_field(name="💰 Saldo Admin Sisa",      value=f"**{admin_bal_after:,} Bcash**",  inline=True)
        embed.add_field(name="📊 Harga Sebelum",         value=f"Rp{price_before:,}",             inline=True)
        embed.add_field(name="📈 Harga Sekarang",        value=f"Rp{price_after:,}",              inline=True)
        delta = price_after - price_before
        arrow = "📈" if delta >= 0 else "📉"
        embed.add_field(name=f"{arrow} Perubahan Harga", value=f"**{'+' if delta >= 0 else ''}{delta:,}**", inline=True)
        embed.set_footer(text=f"Dibakar oleh {ctx.author.display_name} • Asisten Lurah BFL")
        await ctx.send(embed=embed)

@bot.command(name="price")
async def price_cmd(ctx):
    data  = load_price()
    price = data["price"]
    hist  = data.get("history", [price])
    if len(hist) >= 2:
        prev = hist[-2]
        if price > prev:   arrow = "📈"
        elif price < prev: arrow = "📉"
        else:              arrow = "➡️"
    else:
        arrow = "➡️"
    minted = data.get("minted", 0)
    burned = data.get("burned", 0)
    admin_bal = get_coins(ADMIN_BANK_ID)
    supply = admin_bal + minted
    embed = discord.Embed(
        title="💱 Harga Bcash",
        color=discord.Color.gold()
    )
    embed.add_field(name=f"{arrow} Harga", value=f"**Rp{price:,}** / 100 Bcash", inline=True)
    embed.add_field(name="📦 Supply", value=f"**{supply:,} Bcash**", inline=True)
    embed.add_field(name="🔥 Total Burn", value=f"**{burned:,} Bcash**", inline=True)
    embed.add_field(name="🪙 Total Mint", value=f"**{minted:,} Bcash**", inline=True)
    embed.set_footer(text="Harga bergerak dari aktivitas game & burn/mint • Asisten Lurah BFL")
    await ctx.send(embed=embed)

@bot.command(name="checkbalance")
async def checkbalance(ctx, target: str = None):
    """Admin cek saldo user. Bisa pakai @mention di server atau user_id di DM."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Admin only")
    if not target:
        return await ctx.send("Gunakan `!checkbalance @user` atau `!checkbalance <user_id>`")
    # Resolve user — support mention dan raw user_id
    raw_id = target.strip("<@!>")
    if not raw_id.isdigit():
        return await ctx.send("❌ Gunakan mention `@user` atau ID numerik.")
    try:
        user = await bot.fetch_user(int(raw_id))
    except Exception:
        return await ctx.send("❌ User tidak ditemukan.")
    bal = get_coins(str(user.id))
    price = load_price().get("price", 10000)
    idr   = int((bal / 100) * price)
    await ctx.send(
        f"💰 **{user.display_name}** (`{user.id}`)\n"
        f"Saldo: **{bal:,} Bcash** (≈ Rp{idr:,})"
    )

@bot.command(name="deposit")
async def deposit_cmd(ctx, amount:int=None):
    if not amount or amount < 100:
        return await ctx.send("❌ Minimum deposit 100 Bcash (Rp10.000)")
    price = load_price().get("price",10000)
    total = int((amount/100)*price)
    await ctx.author.send(f"📥 **Deposit Request**\nJumlah: **{amount} Bcash**\nTransfer: **Rp{total:,}**\nKirim bukti pembayaran ke admin untuk diproses.")

@bot.command(name="setspamchannel")
async def set_spam_channel(ctx, channel_id:int=None):
    global SPAM_CHANNEL_ID
    if not isinstance(ctx.channel, discord.DMChannel):
        return await ctx.send("DM only")
    if not is_admin(ctx.author):
        return await ctx.send("❌ Admin only")
    SPAM_CHANNEL_ID = channel_id
    await ctx.send(f"✅ Spam channel diubah ke {channel_id}")

@bot.command(name="slot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def slot_game(ctx, bet:int=None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    uid = str(ctx.author.id)
    is_admin_player = is_admin(ctx.author)
    max_b = get_max_bet("slot")
    if not bet or bet < 1:
        return await ctx.send(f"❌ Min bet 1 Bcash, max {max_b} Bcash. Contoh: `!slot 5`")
    if bet > max_b:
        return await ctx.send(f"❌ Max bet slot adalah **{max_b} Bcash**.")
    ensure_coins(uid)
    balance = get_coins(uid)
    if balance < bet:
        return await ctx.send(f"❌ Coin tidak cukup! Saldo: **{balance:,} Bcash**, butuh: **{bet:,} Bcash**.")

    add_coins(uid, -bet)
    # Kalah: langsung burn
    burn_coins(bet)
    log_history(uid, f"🎰 Slot bet", -bet)
    mark_activity(uid)
    bonus = give_firstplay_bonus(uid, ctx.author.display_name)
    if bonus:
        await ctx.send(f"🎮 {ctx.author.mention} Selamat datang! Kamu dapat **+{bonus} Bcash** bonus!", delete_after=10)

    winrate = get_winrate("slot", is_admin_player)
    roll = random.random()
    if roll < winrate:
        multi  = random.choice([1, 1.5, 2])
        reward = int(bet * multi)
        # Hadiah dari mint baru, bukan dari admin bank
        add_coins(uid, reward)
        mint_coins(reward)
        log_history(uid, f"🎰 Slot menang (x{multi})", +reward)
        msg = f"🎰 JACKPOT! Menang **{reward} Bcash** (x{multi})"
    else:
        # Sudah di-burn di atas
        log_history(uid, "🎰 Slot kalah", -bet)
        msg = f"💀 Kalah! **{bet} Bcash** di-burn → harga Bcash naik."
    await ctx.send(msg)

# ═══════════════════════════════════════════════════════
#  GAME — COIN FLIP (!coinflip)
# ═══════════════════════════════════════════════════════
_CF_HEADS_ART = (
    "```\n"
    "  ╭──────────╮\n"
    "  │  👑 HEADS │\n"
    "  │  D E P A N│\n"
    "  ╰──────────╯\n"
    "```"
)
_CF_TAILS_ART = (
    "```\n"
    "  ╭──────────╮\n"
    "  │  ✦ TAILS │\n"
    "  │ B E L A K │\n"
    "  ╰──────────╯\n"
    "```"
)

@bot.command(name="coinflip", aliases=["cf", "flip", "koinflip"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def coinflip_cmd(ctx, pilihan: str = None, bet: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    if not pilihan or not bet:
        embed_help = discord.Embed(
            title="🪙 Coin Flip — Cara Main",
            description=(
                "Tebak sisi koin yang keluar — **heads** (depan) atau **tails** (belakang)!\n\n"
                "**Format:** `!coinflip <heads/tails> <bet>`\n"
                "**Contoh:** `!coinflip heads 5`\n\n"
                "🏆 Menang → dapat **2× bet** (Bcash baru di-mint!)\n"
                "🔥 Kalah → bet **di-burn** (harga Bcash naik!)\n\n"
                "**Alias:** `!cf` · `!flip` · `!koinflip`"
            ),
            color=discord.Color.gold()
        )
        embed_help.set_footer(text="Asisten Lurah BFL • Coin Flip")
        return await ctx.send(embed=embed_help)

    pilihan = pilihan.lower().strip()
    alias_heads = ["heads", "head", "h", "depan", "muka"]
    alias_tails = ["tails", "tail", "t", "belakang", "ekor"]

    if pilihan not in alias_heads + alias_tails:
        return await ctx.send(
            "❌ Pilihan tidak valid!\n"
            "Ketik `heads` / `h` / `depan`  atau  `tails` / `t` / `belakang`\n"
            "Contoh: `!coinflip heads 5`"
        )
    is_admin_player = is_admin(ctx.author)
    max_b = get_max_bet("coinflip")
    if bet < 1 or bet > max_b:
        return await ctx.send(f"❌ Bet min **1 Bcash**, max **{max_b} Bcash**.")

    uid = str(ctx.author.id)
    ensure_coins(uid)
    bal = get_coins(uid)
    if bal < bet:
        return await ctx.send(
            f"❌ Bcash tidak cukup!\n"
            f"Saldo kamu: **{bal:,} Bcash** | Butuh: **{bet:,} Bcash**"
        )

    add_coins(uid, -bet)
    # Langsung burn saat bet (jika kalah, sudah ter-burn; jika menang, mint baru)
    burn_coins(bet)
    log_history(uid, "🪙 Coinflip bet", -bet)
    mark_activity(uid)
    bonus = give_firstplay_bonus(uid, ctx.author.display_name)
    if bonus:
        await ctx.send(f"🎮 {ctx.author.mention} Selamat datang! Kamu dapat **+{bonus} Bcash** bonus!", delete_after=10)

    pick_heads = pilihan in alias_heads
    pick_label = "👑 HEADS (Depan)" if pick_heads else "✦ TAILS (Belakang)"

    # ── Embed animasi ──
    spin_frames = [
        ("🟡", "Koin dilempar ke udara..."),
        ("🔄", "Koin berputar cepat..."),
        ("💫", "Terus berputar..."),
        ("🔄", "Melambat..."),
        ("⭕", "Hampir mendarat..."),
        ("🟡", "Koin mendarat! 🎯"),
    ]
    delays = [0.55, 0.45, 0.45, 0.5, 0.6, 0.75]

    embed_spin = discord.Embed(
        title="🪙 COIN FLIP",
        description=(
            f"**{ctx.author.display_name}** melempar koin!\n\n"
            f"**Pilihan:** {pick_label}\n"
            f"**Taruhan:** {bet:,} Bcash\n\n"
            f"🟡 *Siap-siap...*"
        ),
        color=discord.Color.yellow()
    )
    embed_spin.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed_spin.set_footer(text="Asisten Lurah BFL • Coin Flip | 50/50 Fair Game")
    msg = await ctx.send(embed=embed_spin)

    for (icon, label), delay in zip(spin_frames, delays):
        await asyncio.sleep(delay)
        embed_spin.description = (
            f"**{ctx.author.display_name}** melempar koin!\n\n"
            f"**Pilihan:** {pick_label}\n"
            f"**Taruhan:** {bet:,} Bcash\n\n"
            f"{icon} *{label}*"
        )
        try:
            await msg.edit(embed=embed_spin)
        except Exception:
            pass

    await asyncio.sleep(0.7)

    # ── Hasil ──
    winrate = get_winrate("coinflip", is_admin_player)
    result_heads = random.random() < 0.5
    player_wins  = (pick_heads == result_heads)
    # Override: jika winrate tidak 50%, paksa hasil
    if random.random() >= winrate:
        player_wins = False
    result_label = "👑 HEADS (Depan)" if result_heads else "✦ TAILS (Belakang)"
    result_art   = _CF_HEADS_ART if result_heads else _CF_TAILS_ART

    if player_wins:
        reward = bet * 2
        # Hadiah dari mint baru
        add_coins(uid, reward)
        mint_coins(reward)
        log_history(uid, "🪙 Coinflip WIN (×2)", +reward)

        embed_result = discord.Embed(
            title="🎉 COIN FLIP — MENANG!",
            description=(
                f"{result_art}\n"
                f"**Hasil:** {result_label}\n"
                f"**Pilihanmu:** {pick_label} ✅\n\n"
                f"💰 **+{reward:,} Bcash** masuk ke dompetmu! (Bcash baru di-mint)\n"
            ),
            color=discord.Color.green()
        )
        embed_result.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_result.set_footer(text="Asisten Lurah BFL • Coin Flip | 🏆 Selamat!")
        await msg.edit(embed=embed_result)

    else:
        # Sudah di-burn saat bet
        log_history(uid, "🪙 Coinflip LOSE", -bet)

        embed_result = discord.Embed(
            title="💀 COIN FLIP — KALAH!",
            description=(
                f"{result_art}\n"
                f"**Hasil:** {result_label}\n"
                f"**Pilihanmu:** {pick_label} ❌\n\n"
                f"🔥 **{bet:,} Bcash** di-burn → harga Bcash naik!\n"
            ),
            color=discord.Color.red()
        )
        embed_result.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed_result.set_footer(text="Asisten Lurah BFL • Coin Flip | Coba lagi!")
        await msg.edit(embed=embed_result)




# ═══════════════════════════════════════════════════════
#  ACTIVITY TRACKER — untuk sistem pajak
# ═══════════════════════════════════════════════════════
def load_activity():
    return load_json(ACTIVITY_FILE, default={})

def save_activity(d):
    save_json(ACTIVITY_FILE, d)

def mark_activity(uid: str):
    """Tandai user sudah main game hari ini (UTC)."""
    uid = str(uid)
    data = load_activity()
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    data[uid] = today
    save_activity(data)


# ═══════════════════════════════════════════════════════
#  GAME — SWEET BONANZA (!bonanza)
# ═══════════════════════════════════════════════════════

# ── Simbol & bobot kemunculan ──────────────────────────
# Bobot total ≈ 180 — lolipop hanya 1 dari 180 → ~0.55% per sel
# Rata-rata butuh ~182 sel sebelum lolipop muncul 1×
# Di grid 5×5 (25 sel), peluang ≥3 lolipop sangat kecil (~0.1%)
BONANZA_LOLIPOP  = "🍬"
BONANZA_SYMBOLS  = ["🍇", "🍊", "🍋", "🍉", "🍑", "🍒", "💎", BONANZA_LOLIPOP]
#                    anggur oranye lemon semangka persik ceri  berlian scatter
# ⬆ Bobot dinaikkan agar cluster lebih mudah terbentuk (seperti Pragmatic)
# Lolipop 4 → P(≥3 lolipop di 25 sel) ≈ 1.2% — lebih realistis
BONANZA_WEIGHTS  = [50,    46,    42,   38,     34,    28,   12,      4]
# Total bobot = 254. Lolipop = 4/254 per sel ≈ 1.57%

# ── Tabel hadiah per simbol — threshold 7 (diturunkan dari 8) ──
# Cluster minimum 7 simbol — lebih mudah menang dari sebelumnya
# Contoh: 🍇 7× di grid dengan bet 5 → 5 × 1 = 5 Bcash
BONANZA_PAYOUTS = {
    # Simbol murah — threshold 7, hadiah lebih besar
    "🍇": {7: 1,  8: 1,  10: 2,  12: 3,  15: 5,  18: 8,  22: 13, 25: 20},
    "🍊": {7: 1,  8: 1,  10: 2,  12: 4,  15: 6,  18: 10, 22: 16, 25: 25},
    "🍋": {7: 1,  8: 2,  10: 3,  12: 5,  15: 8,  18: 13, 22: 20, 25: 30},
    # Simbol sedang — threshold 7, hadiah lebih besar
    "🍉": {7: 2,  8: 2,  10: 4,  12: 7,  15: 11, 18: 17, 22: 25, 25: 40},
    "🍑": {7: 2,  8: 3,  10: 5,  12: 9,  15: 14, 18: 22, 22: 35, 25: 55},
    # Simbol mahal — threshold 7, hadiah premium
    "🍒": {7: 4,  8: 5,  10: 9,  12: 15, 15: 24, 18: 38, 22: 60, 25: 90},
    "💎": {7: 8,  8: 10, 10: 18, 12: 30, 15: 50, 18: 80, 22: 120, 25: 180},
}

# ── Tabel multiplier KHUSUS FREE SPIN — sistem balanced ──
# 30% jackpot (max ×20), 30% flat ×2 dari bet, 40% normal ×3–×8
BONANZA_FS_MULT_JACKPOT = (8.0, 20.0)   # 30% → jackpot range (max ×20)
BONANZA_FS_MULT_SMALL   = (2.0,  2.0)   # 30% → flat ×2 dari bet
BONANZA_FS_MULT_NORMAL  = (3.0,  8.0)   # 40% → normal range

# ── Jackpot progresif ──────────────────────────────────
BONANZA_JP_FILE    = "bonanza_jackpot.json"
BONANZA_JP_SEED    = 200     # jackpot awal 200 Bcash (lebih kecil, grow dari kontribusi)
BONANZA_JP_CONTRIB = 0.08   # 8% dari setiap bet masuk jackpot (naik lebih cepat)
# Jackpot triggered: 20+ 💎 di grid natural (tanpa tumble) — sangat jarang

# ── Ante Bet & Buy Free Spin ───────────────────────────
BONANZA_ANTE_MULT   = 1.25   # Ante Bet → bayar +25%, boost scatter +50%
BONANZA_BUY_FS_MULT = 100    # Buy Free Spin → bayar 100× bet

# ── Batas bet ─────────────────────────────────────────
BONANZA_MIN_BET = 1
BONANZA_MAX_BET = 15   # selaraskan dengan max_bet di settings

# ── Tracking scatter per user — scatter muncul antara spin ke-42 hingga ke-100 ──
_bz_scatter_tracker: dict = {}    # uid → target spin count untuk scatter berikutnya
_bz_active_sessions: set  = set() # uid yang sedang main bonanza (anti multi-session)

def _bz_get_scatter_target(uid: str) -> int:
    """Tentukan target spin untuk scatter berikutnya (42–100 random)."""
    target = random.randint(42, 100)
    _bz_scatter_tracker[uid] = target
    return target

def _bz_reset_scatter(uid: str):
    """Reset tracker scatter setelah scatter triggered atau game selesai."""
    _bz_scatter_tracker.pop(uid, None)

def _bz_load_jackpot() -> int:
    d = load_json(BONANZA_JP_FILE, default={"pool": BONANZA_JP_SEED})
    return max(int(d.get("pool", BONANZA_JP_SEED)), BONANZA_JP_SEED)

def _bz_save_jackpot(pool: int):
    save_json(BONANZA_JP_FILE, {"pool": max(pool, BONANZA_JP_SEED)})

def _bz_add_jackpot(bet: int):
    """Tambah kontribusi ke pool jackpot dari setiap bet."""
    pool = _bz_load_jackpot()
    pool += max(1, int(bet * BONANZA_JP_CONTRIB))
    _bz_save_jackpot(pool)

def _bz_empty_grid():
    return [["⬛"] * 5 for _ in range(5)]

def _bz_render_grid(grid):
    lines = []
    for row in grid:
        lines.append("  ".join(row))
    return "```\n" + "\n".join(lines) + "\n```"

def _bz_spin_grid(ante_mode: bool = False):
    """
    Generate grid 5×5 acak.
    ante_mode=True → bobot lolipop dinaikkan 3× (dari 1 → 3)
    karena base-nya sudah sangat kecil (1/169), ini masih langka (3/171 ≈ 1.8%)
    """
    weights = list(BONANZA_WEIGHTS)
    if ante_mode:
        weights[-1] = weights[-1] * 3   # 1 → 3, scatter ~3× lebih sering
    grid = []
    for _ in range(5):
        row = random.choices(BONANZA_SYMBOLS, weights=weights, k=5)
        grid.append(row)
    return grid

def _bz_count_symbol(grid, sym: str) -> int:
    return sum(row.count(sym) for row in grid)

def _bz_highlight_symbols(grid, syms: list):
    """Tampilkan hanya simbol di `syms`, sisanya ⬛."""
    result = []
    for row in grid:
        result.append([cell if cell in syms else "⬛" for cell in row])
    return result

def _bz_get_payout(sym: str, count: int) -> int:
    """Kembalikan nilai hadiah flat (per 1 unit bet) berdasarkan simbol dan jumlah cluster."""
    tiers = BONANZA_PAYOUTS.get(sym, {})
    payout = 0
    for threshold in sorted(tiers.keys()):
        if count >= threshold:
            payout = tiers[threshold]
    return payout

def _bz_calculate_win_normal(grid, bet: int):
    """
    Hitung kemenangan putaran normal (BUKAN free spin).
    Hadiah = flat Bcash berdasarkan tabel BONANZA_PAYOUTS × bet.
    Threshold cluster minimum: 7 (diturunkan dari 8 agar lebih sering menang).
    TIDAK ada multiplier.
    """
    total_win  = 0
    win_details = []
    for sym in BONANZA_SYMBOLS:
        if sym == BONANZA_LOLIPOP:
            continue
        count = _bz_count_symbol(grid, sym)
        if count >= 7:
            payout_rate = _bz_get_payout(sym, count)
            if payout_rate > 0:
                win = payout_rate * bet
                total_win += win
                win_details.append((sym, count, payout_rate, win, False))
    return total_win, win_details

def _bz_force_freespin_grid():
    """
    Generate grid untuk free spin.
    TIDAK dijamin ada cluster — hasil ditentukan oleh tipe spin di calculate_win.
    """
    grid = []
    for _ in range(5):
        row = random.choices(BONANZA_SYMBOLS[:-1], weights=BONANZA_WEIGHTS[:-1], k=5)
        grid.append(row)
    return grid

def _bz_calculate_win_freespin(grid, bet: int):
    """
    Hitung kemenangan free spin — sistem 3 tipe (PER SPIN, bukan per-tumble):
    - 30% jackpot : multiplier ×8–×20 dari cluster (jika tidak ada cluster → return 0, no-win)
    - 30% gagal   : tidak ada cluster, return (0, []) → loop tumble langsung break
    - 40% normal  : multiplier ×3–×8 dari cluster (jika tidak ada cluster → return 0, no-win)

    Catatan: flat ×2–×10 dari TOTAL BET SELURUH 10 SPIN dihitung di luar fungsi ini
    saat free spin selesai (lihat _bz_freespin_consolation_prize).
    """
    total_win   = 0
    win_details = []

    # Roll tipe spin
    roll = random.random()
    if roll < 0.30:
        spin_type = "jackpot"
        mult      = round(random.uniform(*BONANZA_FS_MULT_JACKPOT), 1)
        is_big    = True
    elif roll < 0.60:
        # 30% gagal — tidak ada cluster, langsung return kosong
        # loop tumble akan break karena winfo kosong
        return 0, []
    else:
        spin_type = "normal"
        mult      = round(random.uniform(*BONANZA_FS_MULT_NORMAL), 1)
        is_big    = False

    # Hitung cluster untuk jackpot dan normal
    cluster_found = False
    for sym in BONANZA_SYMBOLS:
        if sym == BONANZA_LOLIPOP:
            continue
        count = _bz_count_symbol(grid, sym)
        if count >= 7:
            payout_rate = _bz_get_payout(sym, count)
            if payout_rate > 0:
                base_win    = payout_rate * bet
                win         = int(base_win * mult)
                total_win  += win
                win_details.append((sym, count, payout_rate, mult, win, is_big))
                cluster_found = True

    # Tidak ada cluster (meski jackpot/normal roll) → return kosong, no-win spin ini
    if not cluster_found:
        return 0, []

    return total_win, win_details


def _bz_freespin_consolation_prize(bet: int, fs_total_won: int) -> int:
    """
    Hadiah konsolasi setelah 10 free spin selesai jika total kemenangan FS < 2× total bet.
    30% chance: user dapat antara ×2–×10 dari total bet seluruh 10 spin (= bet × 10).
    Ini menggantikan sistem flat ×2 lama yang menyebabkan bug tumble tak terbatas.
    Return jumlah bonus (0 jika tidak dapat atau sudah menang cukup).
    """
    total_bet_10_spin = bet * 10
    # Jika sudah menang ≥ 2× total bet, tidak perlu konsolasi
    if fs_total_won >= total_bet_10_spin * 2:
        return 0
    # 30% chance dapat konsolasi
    if random.random() < 0.30:
        mult   = random.randint(2, 10)
        return total_bet_10_spin * mult
    return 0

def _bz_tumble(grid, winning_symbols: list):
    """
    Tumble mechanic: hapus sel simbol pemenang dari grid,
    kembalikan grid baru (sel kosong = ⬛).
    """
    new_grid = []
    for row in grid:
        new_row = [("⬛" if cell in winning_symbols else cell) for cell in row]
        new_grid.append(new_row)
    return new_grid

def _bz_refill_grid(grid):
    """Isi ulang sel ⬛ dengan simbol baru (turun dari atas)."""
    for r in range(5):
        for c in range(5):
            if grid[r][c] == "⬛":
                grid[r][c] = random.choices(BONANZA_SYMBOLS, weights=BONANZA_WEIGHTS, k=1)[0]
    return grid

# ── View tombol bonanza ────────────────────────────────
class BonanzaView(View):
    def __init__(self, uid: str, bet: int, free_spins_left: int = 0, ante_mode: bool = False, gaib_unlocked: bool = False):
        super().__init__(timeout=90)
        self.uid             = uid
        self.bet             = bet
        self.free_spins_left = free_spins_left
        self.ante_mode       = ante_mode
        self.gaib_unlocked   = gaib_unlocked
        self.choice          = None   # "next" | "stop" | "ante" | "buyfs" | "auto10" | "auto30" | "auto50" | "auto100" | "autogaib"

        # Sembunyikan tombol Auto Gaib jika belum unlock (harus beli Auto 10/30/50 dulu)
        if not gaib_unlocked:
            self.autogaib_btn.disabled = True
            self.autogaib_btn.label    = "🔮 Auto Gaib 🔒"
            self.autogaib_btn.style    = discord.ButtonStyle.secondary

    @discord.ui.button(label="▶️ Next Spin", style=discord.ButtonStyle.success, row=0)
    async def next_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "next"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="⚡ Ante Bet (+25%)", style=discord.ButtonStyle.primary, row=0)
    async def ante_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "ante"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🎁 Buy FS (×100)", style=discord.ButtonStyle.secondary, row=0)
    async def buyfs_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "buyfs"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🔁 Auto 10", style=discord.ButtonStyle.secondary, row=1)
    async def auto10_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "auto10"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🔁 Auto 30", style=discord.ButtonStyle.secondary, row=1)
    async def auto30_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "auto30"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🔁 Auto 50", style=discord.ButtonStyle.secondary, row=1)
    async def auto50_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "auto50"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🔁 Auto 100", style=discord.ButtonStyle.primary, row=2)
    async def auto100_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "auto100"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="🔮 Auto Gaib", style=discord.ButtonStyle.primary, row=2)
    async def autogaib_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        if not self.gaib_unlocked:
            return await interaction.response.send_message(
                "🔒 **Auto Gaib terkunci!**\nBeli **Auto Spin 10, 30, atau 50** terlebih dahulu untuk membuka fitur ini.",
                ephemeral=True
            )
        self.choice = "autogaib"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="⏹️ Stop & Klaim", style=discord.ButtonStyle.danger, row=2)
    async def stop_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "stop"
        self.stop()
        await interaction.response.defer()


class BonanzaAutoStopView(View):
    """Tombol stop saat auto spin / gaib berjalan."""
    def __init__(self, uid: str):
        super().__init__(timeout=300)   # timeout 5 menit, bukan None (None bisa memory leak)
        self.uid         = uid
        self.stop_signal = False
        self._stop_event = asyncio.Event()  # event untuk sinyal stop yang bisa di-await

    @discord.ui.button(label="⏹️ Stop Auto Spin", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.stop_signal = True
        self._stop_event.set()   # sinyal event agar loop bisa detect segera
        self.stop()
        await interaction.response.send_message("⏹️ Menghentikan auto spin...", ephemeral=True)

    async def wait_for_stop(self, timeout: float = 0.5) -> bool:
        """Tunggu sampai stop ditekan atau timeout habis. Return True jika stop ditekan."""
        try:
            await asyncio.wait_for(self._stop_event.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return self.stop_signal


class BonanzaFSView(View):
    """View sederhana hanya Next untuk saat free spin aktif."""
    def __init__(self, uid: str, spins_left: int):
        super().__init__(timeout=90)
        self.uid        = uid
        self.spins_left = spins_left
        self.choice     = None

    @discord.ui.button(label="▶️ Lanjut Free Spin", style=discord.ButtonStyle.success)
    async def next_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "next"
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="⏹️ Stop & Klaim", style=discord.ButtonStyle.danger)
    async def stop_btn(self, interaction: discord.Interaction, button: Button):
        if str(interaction.user.id) != self.uid:
            return await interaction.response.send_message("❌ Ini bukan game kamu!", ephemeral=True)
        self.choice = "stop"
        self.stop()
        await interaction.response.defer()

# ── Command utama ──────────────────────────────────────
@bot.command(name="bonanza", aliases=["sweetbonanza", "bn"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def bonanza_cmd(ctx, bet: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    uid            = str(ctx.author.id)
    is_admin_player = is_admin(ctx.author)
    max_b          = get_max_bet("bonanza")
    jp_pool        = _bz_load_jackpot()

    if not bet or bet < BONANZA_MIN_BET:
        tabel_lines = []
        for sym, tiers in BONANZA_PAYOUTS.items():
            sorted_tiers = sorted(tiers.items())
            tier_str = " | ".join([f"{k}+:×{v}" for k, v in sorted_tiers])
            tabel_lines.append(f"{sym} → {tier_str}")
        embed = discord.Embed(
            title="🍬 Sweet Bonanza — Cara Main",
            color=discord.Color.from_rgb(255, 105, 180)
        )
        embed.add_field(
            name="📌 Info Umum",
            value=(
                f"**Format:** `!bonanza <bet>`  |  **Contoh:** `!bonanza 5`\n"
                f"**Min:** {BONANZA_MIN_BET} Bcash  |  **Max:** {max_b} Bcash\n"
                f"**🏆 Jackpot Pool:** **{jp_pool:,} Bcash**"
            ),
            inline=False
        )
        embed.add_field(
            name="🎮 Mekanik Utama",
            value=(
                "• Grid **5×5** — simbol buah turun satu per satu\n"
                "• **7+ simbol sama** di grid → cluster WIN! (threshold diturunkan ke 7)\n"
                "• Hadiah **flat per simbol** (lihat tabel) × bet kamu\n"
                "• **Tumble:** simbol menang hilang → simbol baru turun → cek cluster lagi!\n"
                "• Makin banyak cluster = makin besar hadiah, tumble bisa beruntun!\n"
                "• ⚡ **Animasi super cepat** — tidak ada waktu nunggu lama!"
            ),
            inline=False
        )
        embed.add_field(
            name="🍬 Scatter & Free Spin",
            value=(
                "• **3+ Lolipop 🍬** di grid → **10 Free Spin!**\n"
                "• Scatter bisa muncul setelah spin ke-42 hingga ke-100\n"
                "• Free Spin — tipe spin acak:\n"
                "  ▸ **30%** dapat **×8 – ×20** 🔥 JACKPOT!\n"
                "  ▸ **30%** dapat **×2** flat dari bet\n"
                "  ▸ **40%** dapat **×3 – ×8** normal\n"
                "• Free Spin **gratis**, tidak potong bet"
            ),
            inline=False
        )
        embed.add_field(
            name="⚡ Fitur Khusus",
            value=(
                "**⚡ Ante Bet** — bayar **+25% bet**, scatter 3× lebih mungkin muncul\n"
                "**🎁 Buy Free Spin** — bayar **100× bet**, langsung 10 Free Spin!\n"
                "**🏆 Jackpot Progresif** — 8% tiap bet masuk pool, pecah saat 20+ 💎 di grid"
            ),
            inline=False
        )
        embed.add_field(
            name="💎 Tabel Hadiah (per 1 Bcash bet)",
            value="\n".join(tabel_lines),
            inline=False
        )
        embed.set_footer(text="Asisten Lurah BFL • Sweet Bonanza 🍬 | Alias: !bn !sweetbonanza")
        return await ctx.send(embed=embed)

    if bet > max_b:
        return await ctx.send(
            f"❌ Bet bonanza harus **{BONANZA_MIN_BET}–{max_b} Bcash**. "
            f"Contoh: `!bonanza 5`"
        )

    ensure_coins(uid)
    balance = get_coins(uid)
    if balance < bet:
        return await ctx.send(
            f"❌ Bcash tidak cukup! Saldo: **{balance:,} Bcash**, butuh: **{bet:,} Bcash**."
        )

    mark_activity(uid)
    bonus = give_firstplay_bonus(uid, ctx.author.display_name)
    if bonus:
        await ctx.send(
            f"🎮 {ctx.author.mention} Selamat datang! Kamu dapat **+{bonus} Bcash** bonus!",
            delete_after=10
        )

    # ── Anti multi-session: cegah 1 user buka bonanza lebih dari 1 ──
    if uid in _bz_active_sessions:
        return await ctx.send(
            f"⚠️ {ctx.author.mention} Kamu sudah punya sesi Bonanza yang aktif! "
            f"Selesaikan atau hentikan dulu sebelum membuka yang baru."
        )
    _bz_active_sessions.add(uid)

    # ── State game ──
    total_won        = 0
    spin_count       = 0
    tumble_count     = 0
    free_spins_left  = 0
    free_spins_total = 0
    is_free_spin     = False
    is_fs_capped     = False   # True → total kemenangan FS dikap ×10 dari bet
    fs_won_start     = 0       # total_won saat FS dimulai, untuk hitung kemenangan FS saja
    ante_mode        = False
    game_active      = True
    auto_spins_left  = 0       # sisa spin auto (10/30/50/100); 0 = manual
    auto_gaib_mode   = False   # True = auto gaib: skip animasi, berhenti saat scatter
    gaib_unlocked    = False   # True jika user sudah beli Auto Spin 10/30/50 di sesi ini
    # Scatter target: scatter bisa muncul setelah spin ke-42 hingga ke-100
    scatter_target      = _bz_get_scatter_target(uid)
    total_spin_global   = 0

    # ── Embed awal ──
    embed_game = discord.Embed(
        title="🍬 SWEET BONANZA",
        description=_bz_render_grid(_bz_empty_grid()),
        color=discord.Color.from_rgb(255, 105, 180)
    )
    embed_game.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed_game.set_footer(text=f"Asisten Lurah BFL • Sweet Bonanza 🍬 | 🏆 Jackpot: {_bz_load_jackpot():,} Bcash")
    game_msg = await ctx.send(embed=embed_game)

    # ════════════════════════════════════════════
    #  FUNGSI LOKAL: jalankan satu putaran spin
    # ════════════════════════════════════════════
    async def _run_spin(is_fs: bool, ante: bool):
        nonlocal total_won, tumble_count, is_fs_capped, fs_won_start

        fs_num = free_spins_total - free_spins_left + 1 if is_fs else 0

        # ── Animasi gulungan turun ──
        grid_anim  = _bz_empty_grid()
        title_str  = f"🍬 FREE SPIN {fs_num}/10 ✨" if is_fs else f"🍬 SWEET BONANZA | Spin #{spin_count}"
        color_spin = discord.Color.gold() if is_fs else discord.Color.from_rgb(255, 105, 180)
        if ante and not is_fs:
            title_str += " ⚡ ANTE"

        embed_game.title       = title_str
        embed_game.color       = color_spin
        embed_game.description = _bz_render_grid(_bz_empty_grid())
        embed_game.clear_fields()
        embed_game.add_field(name="🔄 Buah-buahan turun...", value="Simbol bergulir!", inline=False)
        await game_msg.edit(embed=embed_game, view=None)
        await asyncio.sleep(0.2)  # ⚡ lebih cepat

        # Untuk free spin, gunakan grid yang dijamin ada cluster
        if is_fs:
            final_grid = _bz_force_freespin_grid()
        else:
            final_grid = _bz_spin_grid(ante_mode=ante)

        # ── Winrate gate: jika roll gagal, paksa grid "buruk" (distribusi merata) ──
        # Ini memastikan winrate setting admin berpengaruh nyata
        winrate = get_winrate("bonanza", is_admin_player)
        if not is_fs and random.random() >= winrate:
            # Regenerasi grid dengan distribusi lebih merata → susah cluster
            # Paksa setiap simbol muncul ≤3× (tidak ada yang dominan)
            pool = []
            for sym in BONANZA_SYMBOLS[:-1]:   # tanpa lolipop
                pool.extend([sym] * 3)
            random.shuffle(pool)
            bad_grid = []
            idx = 0
            for r in range(5):
                row = []
                for c in range(5):
                    row.append(pool[idx % len(pool)])
                    idx += 1
                bad_grid.append(row)
            final_grid = bad_grid

        # Animasi baris turun per baris — lebih cepat
        for r in range(5):
            grid_anim[r] = final_grid[r]
            embed_game.description = _bz_render_grid(grid_anim)
            await game_msg.edit(embed=embed_game)
            await asyncio.sleep(0.15)  # ⚡ dari 0.3 → 0.15

        await asyncio.sleep(0.2)  # ⚡ dari 0.35 → 0.2
        current_grid      = [row[:] for row in final_grid]
        spin_session_win  = 0
        tumble_idx        = 0
        all_win_details   = []

        while True:
            # Hitung cluster
            if is_fs:
                sw, winfo = _bz_calculate_win_freespin(current_grid, bet)
            else:
                sw, winfo = _bz_calculate_win_normal(current_grid, bet)

            if sw == 0 or not winfo:
                break   # tidak ada cluster → selesai tumble

            tumble_idx        += 1
            tumble_count      += 1
            spin_session_win  += sw
            all_win_details   += winfo

            # Highlight simbol menang
            winning_syms = list({wd[0] for wd in winfo})
            hl_grid      = _bz_highlight_symbols(current_grid, winning_syms)
            embed_game.description = _bz_render_grid(hl_grid)
            embed_game.clear_fields()

            if is_fs:
                detail_lines = []
                for (sym, cnt, rate, mult, w, big) in winfo:
                    tag = "🔥 BIG" if big else "✨"
                    detail_lines.append(f"{sym} ×{cnt}  base ×{rate}  {tag}×{mult} = **+{w:,} Bcash**")
            else:
                detail_lines = []
                for (sym, cnt, rate, w, _) in winfo:
                    detail_lines.append(f"{sym} ×{cnt} → tabel ×{rate} = **+{w:,} Bcash**")

            embed_game.add_field(
                name=f"💥 CLUSTER WIN!{'  (Tumble #'+str(tumble_idx)+')' if tumble_idx > 1 else ''}",
                value="\n".join(detail_lines),
                inline=False
            )
            embed_game.add_field(
                name="💰 Kemenangan Spin Ini",
                value=f"**+{spin_session_win:,} Bcash**",
                inline=True
            )
            await game_msg.edit(embed=embed_game)
            await asyncio.sleep(0.6)  # ⚡ dari 1.0 → 0.6

            # Tumble: hapus simbol menang, isi ulang
            current_grid = _bz_tumble(current_grid, set(winning_syms))
            embed_game.description = _bz_render_grid(current_grid)
            embed_game.clear_fields()
            embed_game.add_field(name="🌀 Tumble...", value="Simbol baru turun!", inline=False)
            await game_msg.edit(embed=embed_game)
            await asyncio.sleep(0.2)  # ⚡ dari 0.4 → 0.2

            current_grid = _bz_refill_grid(current_grid)
            embed_game.description = _bz_render_grid(current_grid)
            await game_msg.edit(embed=embed_game)
            await asyncio.sleep(0.2)  # ⚡ dari 0.4 → 0.2

        # ── Selesai tumble untuk spin ini ──
        if spin_session_win > 0:
            if is_fs and is_fs_capped:
                # Hitung sisa ruang sebelum cap
                cap_limit  = bet * 10
                fs_won_so_far = total_won - fs_won_start
                ruang_sisa    = max(0, cap_limit - fs_won_so_far)
                actual_win    = min(spin_session_win, ruang_sisa)
                if actual_win > 0:
                    total_won += actual_win
                    add_coins(uid, actual_win)
                    mint_coins(actual_win)
                    log_history(uid, f"🍬 Bonanza FreeSpin WIN spin#{spin_count}", +actual_win)
                # jika ruang_sisa == 0, spin ini tidak memberi koin (sudah mentok cap)
            else:
                total_won += spin_session_win
                add_coins(uid, spin_session_win)
                mint_coins(spin_session_win)
                label_type = "FreeSpin" if is_fs else "Normal"
                log_history(uid, f"🍬 Bonanza {label_type} WIN spin#{spin_count}", +spin_session_win)

        # ── Jackpot check: 20+ 💎 di grid asli ──
        diamond_count = _bz_count_symbol(final_grid, "💎")
        jackpot_won   = 0
        if diamond_count >= 20:
            jackpot_won = _bz_load_jackpot()
            _bz_save_jackpot(BONANZA_JP_SEED)
            add_coins(uid, jackpot_won)
            mint_coins(jackpot_won)
            log_history(uid, f"🍬 Bonanza JACKPOT {jackpot_won:,} Bcash", +jackpot_won)
            total_won += jackpot_won

        # ── Scatter check — hanya bisa trigger setelah mencapai spin target (42–100) ──
        nonlocal total_spin_global, scatter_target
        total_spin_global += 1
        lolipop_count = _bz_count_symbol(final_grid, BONANZA_LOLIPOP)
        scatter_triggered = False
        scatter_chance = load_game_settings().get("bonanza_scatter_chance", 0.15)
        if (lolipop_count >= 3 and not is_fs and free_spins_left == 0
                and total_spin_global >= scatter_target
                and random.random() < scatter_chance):
            hl = _bz_highlight_symbols(final_grid, [BONANZA_LOLIPOP])
            embed_game.description = _bz_render_grid(hl)
            embed_game.clear_fields()
            embed_game.add_field(
                name="🍬✨ SCATTER TRIGGERED!",
                value=f"**{lolipop_count} Lolipop** muncul!\n🎰 **10 FREE SPIN** sedang disiapkan...",
                inline=False
            )
            embed_game.color = discord.Color.gold()
            await game_msg.edit(embed=embed_game)
            await asyncio.sleep(1.2)
            scatter_triggered = True
            scatter_target = _bz_get_scatter_target(uid)  # reset untuk scatter berikutnya

        # ── Tampilkan grid akhir spin + ringkasan ──
        embed_game.description = _bz_render_grid(current_grid)
        embed_game.color       = (
            discord.Color.gold()       if is_fs else
            discord.Color.green()      if spin_session_win > 0 else
            discord.Color.from_rgb(255, 105, 180)
        )
        embed_game.clear_fields()

        if spin_session_win > 0:
            embed_game.add_field(
                name="🎉 Total Spin Ini",
                value=(
                    f"**+{spin_session_win:,} Bcash**"
                    + (f"  (+{tumble_idx} tumble!)" if tumble_idx > 1 else "")
                    + (f"\n🏆 **JACKPOT +{jackpot_won:,} Bcash!!**" if jackpot_won else "")
                ),
                inline=False
            )
        else:
            embed_game.add_field(name="💨 Tidak ada cluster", value="Tidak ada simbol cukup.", inline=False)

        embed_game.add_field(
            name="📊 Sesi",
            value=(
                f"🎯 Spin: **{spin_count}**"
                + (f" | 🌀 Tumble: **{tumble_count}**" if tumble_count > 0 else "")
                + f"\n💰 Total Menang: **{total_won:,} Bcash**"
                + f"\n💳 Saldo: **{get_coins(uid):,} Bcash**"
                + (f"\n🎁 Free Spin sisa: **{free_spins_left}**" if free_spins_left > 0 else "")
            ),
            inline=False
        )
        embed_game.set_footer(
            text=f"Asisten Lurah BFL • Sweet Bonanza 🍬 | 🏆 Jackpot: {_bz_load_jackpot():,} Bcash"
        )

        return scatter_triggered

    # ════════════════════════════════════════════
    #  MAIN GAME LOOP
    # ════════════════════════════════════════════
    while game_active:

        # ═══ MODE FREE SPIN ═══
        if is_free_spin and free_spins_left > 0:
            spin_count      += 1
            scatter_hit      = await _run_spin(is_fs=True, ante=False)
            free_spins_left -= 1

            if free_spins_left <= 0:
                is_free_spin = False
                is_fs_capped = False

                embed_game.add_field(
                    name="🏁 Free Spin Selesai!",
                    value="10 Free Spin habis. Kamu bisa lanjut spin atau berhenti.",
                    inline=False
                )
                await game_msg.edit(embed=embed_game)

                # Jika sedang auto gaib → berhenti total setelah scatter selesai
                if auto_gaib_mode:
                    auto_gaib_mode  = False
                    auto_spins_left = 0
                    embed_game.add_field(
                        name="🔮 Auto Gaib Selesai",
                        value="Scatter telah selesai. Auto Gaib berhenti otomatis.",
                        inline=False
                    )
                    await game_msg.edit(embed=embed_game)

                view = BonanzaView(uid, bet, free_spins_left=0, ante_mode=ante_mode, gaib_unlocked=gaib_unlocked)
                await game_msg.edit(embed=embed_game, view=view)
                await view.wait()
                choice = view.choice or "stop"
            else:
                # Masih ada free spin — lanjut tanpa tombol (auto) atau tampil tombol
                if auto_gaib_mode or auto_spins_left > 0:
                    await asyncio.sleep(0.15)
                    choice = "next"
                else:
                    view = BonanzaFSView(uid, free_spins_left)
                    await game_msg.edit(embed=embed_game, view=view)
                    await view.wait()
                    choice = view.choice or "stop"

            if choice == "stop":
                game_active     = False
                auto_spins_left = 0
                auto_gaib_mode  = False
            continue

        # ═══ MODE AUTO GAIB — spin tanpa animasi grid ═══
        if auto_gaib_mode:
            # Buat stop_view SEKALI untuk seluruh sesi gaib (agar interaksi tombol bisa masuk)
            gaib_stop_view = BonanzaAutoStopView(uid)

            while auto_gaib_mode and game_active:
                # Cek saldo
                bal_now = get_coins(uid)
                if bal_now < bet:
                    auto_gaib_mode = False
                    embed_game.clear_fields()
                    embed_game.add_field(name="❌ Bcash Habis", value="Auto Gaib berhenti. Saldo tidak cukup.", inline=False)
                    await game_msg.edit(embed=embed_game, view=None)
                    game_active = False
                    break

                add_coins(uid, -bet)
                burn_coins(bet)
                _bz_add_jackpot(bet)
                spin_count += 1
                log_history(uid, f"🍬 Bonanza AutoGaib spin#{spin_count}", -bet)

                # Hitung hasil spin LANGSUNG tanpa animasi grid
                # (tidak panggil _run_spin agar tidak ada animasi sama sekali)
                if is_free_spin and free_spins_left > 0:
                    final_grid = _bz_force_freespin_grid()
                else:
                    final_grid = _bz_spin_grid(ante_mode=False)

                winrate = get_winrate("bonanza", is_admin_player)
                if not is_free_spin and random.random() >= winrate:
                    pool = []
                    for sym in BONANZA_SYMBOLS[:-1]:
                        pool.extend([sym] * 3)
                    random.shuffle(pool)
                    bad_grid, idx2 = [], 0
                    for r in range(5):
                        row = []
                        for c in range(5):
                            row.append(pool[idx2 % len(pool)])
                            idx2 += 1
                        bad_grid.append(row)
                    final_grid = bad_grid

                # Hitung kemenangan
                current_grid     = [row[:] for row in final_grid]
                spin_session_win = 0
                while True:
                    sw, winfo = _bz_calculate_win_normal(current_grid, bet)
                    if sw == 0 or not winfo:
                        break
                    spin_session_win += sw
                    tumble_count     += 1
                    winning_syms      = list({wd[0] for wd in winfo})
                    current_grid      = _bz_tumble(current_grid, set(winning_syms))
                    current_grid      = _bz_refill_grid(current_grid)

                # Kasih koin jika menang
                if spin_session_win > 0:
                    total_won += spin_session_win
                    add_coins(uid, spin_session_win)
                    mint_coins(spin_session_win)
                    log_history(uid, f"🍬 Bonanza AutoGaib WIN spin#{spin_count}", +spin_session_win)

                # Jackpot check
                diamond_count = _bz_count_symbol(final_grid, "💎")
                if diamond_count >= 20:
                    jp = _bz_load_jackpot()
                    _bz_save_jackpot(BONANZA_JP_SEED)
                    add_coins(uid, jp)
                    mint_coins(jp)
                    log_history(uid, f"🍬 Bonanza AutoGaib JACKPOT {jp:,} Bcash", +jp)
                    total_won += jp

                # Scatter check
                total_spin_global += 1
                lolipop_count  = _bz_count_symbol(final_grid, BONANZA_LOLIPOP)
                scatter_triggered = False
                scatter_chance = load_game_settings().get("bonanza_scatter_chance", 0.15)
                if (lolipop_count >= 3 and free_spins_left == 0
                        and total_spin_global >= scatter_target
                        and random.random() < scatter_chance):
                    scatter_triggered = True
                    scatter_target    = _bz_get_scatter_target(uid)

                # Update embed ringkas TANPA animasi
                embed_game.title = "🔮 AUTO GAIB BERJALAN..."
                embed_game.description = (
                    f"```\n"
                    f"🎯 Spin     : {spin_count}\n"
                    f"💰 Menang   : {total_won:,} Bcash\n"
                    f"💳 Saldo    : {get_coins(uid):,} Bcash\n"
                    f"```"
                )
                embed_game.clear_fields()
                embed_game.color = discord.Color.purple()

                if spin_session_win > 0:
                    embed_game.add_field(
                        name=f"✨ Spin #{spin_count}",
                        value=f"**+{spin_session_win:,} Bcash**",
                        inline=True
                    )

                # Berhenti jika scatter
                if scatter_triggered:
                    auto_gaib_mode  = False
                    is_free_spin    = True
                    free_spins_left  = 10
                    free_spins_total = 10
                    fs_cap_chance    = load_game_settings().get("bonanza_fs_cap_chance", 0.35)
                    is_fs_capped     = random.random() < fs_cap_chance
                    fs_won_start     = total_won
                    embed_game.add_field(
                        name="🍬✨ SCATTER! Auto Gaib Berhenti",
                        value=f"Scatter muncul di spin **#{spin_count}**!\n🎰 **10 Free Spin** dimulai...",
                        inline=False
                    )
                    await game_msg.edit(embed=embed_game, view=None)
                    break

                # Tampilkan embed + tombol stop (view sama, tidak dibuat ulang)
                await game_msg.edit(embed=embed_game, view=gaib_stop_view)

                # Tunggu 0.4 detik — cek stop signal via event
                stopped = await gaib_stop_view.wait_for_stop(timeout=0.4)
                if stopped:
                    auto_gaib_mode = False
                    break

            # ── Setelah gaib berhenti (scatter atau stop) ──
            if not game_active:
                break

            if not auto_gaib_mode and not is_free_spin:
                # User tekan stop — kembali ke menu manual
                embed_game.title = "🍬 SWEET BONANZA"
                embed_game.clear_fields()
                embed_game.add_field(
                    name="⏹️ Auto Gaib Dihentikan",
                    value=f"Total sesi: **{total_won:,} Bcash** | Spin: **{spin_count}**",
                    inline=False
                )
                embed_game.add_field(
                    name="💳 Saldo",
                    value=f"**{get_coins(uid):,} Bcash**",
                    inline=False
                )
                embed_game.color = discord.Color.from_rgb(255, 105, 180)
                view = BonanzaView(uid, bet, free_spins_left=0, ante_mode=ante_mode, gaib_unlocked=gaib_unlocked)
                await game_msg.edit(embed=embed_game, view=view)
                await view.wait()
                choice = view.choice or "stop"
                if choice == "stop":
                    game_active = False
                elif choice == "auto10":  auto_spins_left = 10;  gaib_unlocked = True
                elif choice == "auto30":  auto_spins_left = 30;  gaib_unlocked = True
                elif choice == "auto50":  auto_spins_left = 50;  gaib_unlocked = True
                elif choice == "auto100": auto_spins_left = 100
                elif choice == "autogaib": auto_gaib_mode = True
            continue

        # ═══ MODE AUTO SPIN (10/30/50/100) ═══
        if auto_spins_left > 0:
            # Buat stop_view SEKALI untuk seluruh sesi auto spin
            auto_stop_view = BonanzaAutoStopView(uid)

            while auto_spins_left > 0 and game_active:
                bal_now = get_coins(uid)
                if bal_now < bet:
                    auto_spins_left = 0
                    embed_game.clear_fields()
                    embed_game.add_field(name="❌ Bcash Habis", value="Auto Spin berhenti. Saldo tidak cukup.", inline=False)
                    await game_msg.edit(embed=embed_game, view=None)
                    game_active = False
                    break

                add_coins(uid, -bet)
                burn_coins(bet)
                _bz_add_jackpot(bet)
                log_history(uid, f"🍬 Bonanza AutoSpin spin#{spin_count+1}", -bet)
                spin_count      += 1
                auto_spins_left -= 1

                # Tampil stop button (view sama, tidak dibuat ulang)
                await game_msg.edit(embed=embed_game, view=auto_stop_view)

                scatter_hit = await _run_spin(is_fs=False, ante=False)

                # Update footer auto spin sisa
                embed_game.set_footer(
                    text=f"🔁 Auto Spin sisa: {auto_spins_left} | 🏆 Jackpot: {_bz_load_jackpot():,} Bcash"
                )
                await game_msg.edit(embed=embed_game, view=auto_stop_view)

                # Cek stop signal
                if auto_stop_view.stop_signal:
                    auto_spins_left = 0

                # Berhenti auto jika scatter
                if scatter_hit:
                    auto_spins_left  = 0
                    is_free_spin     = True
                    free_spins_left  = 10
                    free_spins_total = 10
                    fs_cap_chance    = load_game_settings().get("bonanza_fs_cap_chance", 0.35)
                    is_fs_capped     = random.random() < fs_cap_chance
                    fs_won_start     = total_won
                    break

                if auto_spins_left > 0:
                    # Beri jeda kecil agar stop bisa dideteksi
                    stopped = await auto_stop_view.wait_for_stop(timeout=0.15)
                    if stopped:
                        auto_spins_left = 0

            # ── Setelah auto spin habis / dihentikan ──
            if not game_active:
                break

            if auto_spins_left <= 0 and not is_free_spin:
                # Auto habis → kembali ke manual
                embed_game.clear_fields()
                embed_game.add_field(
                    name="✅ Auto Spin Selesai",
                    value=f"Auto Spin habis. Total: **{total_won:,} Bcash**",
                    inline=False
                )
                view = BonanzaView(uid, bet, free_spins_left=0, ante_mode=ante_mode, gaib_unlocked=gaib_unlocked)
                await game_msg.edit(embed=embed_game, view=view)
                await view.wait()
                choice = view.choice or "stop"
                if choice == "stop":
                    game_active = False
                elif choice == "auto10":  auto_spins_left = 10; gaib_unlocked = True
                elif choice == "auto30":  auto_spins_left = 30; gaib_unlocked = True
                elif choice == "auto50":  auto_spins_left = 50; gaib_unlocked = True
                elif choice == "auto100": auto_spins_left = 100
                elif choice == "autogaib": auto_gaib_mode = True

        # ═══ MODE NORMAL (manual) ═══
        view = BonanzaView(uid, bet, free_spins_left, ante_mode, gaib_unlocked=gaib_unlocked)
        await game_msg.edit(embed=embed_game, view=view)
        await view.wait()
        choice = view.choice or "stop"

        if choice == "stop":
            game_active = False
            break

        # Auto spin choices
        if choice == "auto10":   auto_spins_left = 10;  gaib_unlocked = True; continue
        if choice == "auto30":   auto_spins_left = 30;  gaib_unlocked = True; continue
        if choice == "auto50":   auto_spins_left = 50;  gaib_unlocked = True; continue
        if choice == "auto100":  auto_spins_left = 100; continue
        if choice == "autogaib": auto_gaib_mode = True; continue

        # ── Ante Bet toggle ──
        if choice == "ante":
            ante_cost = int(bet * 0.25)
            bal_now   = get_coins(uid)
            if bal_now < bet + ante_cost:
                await ctx.send(
                    f"⚠️ {ctx.author.mention} Saldo tidak cukup untuk Ante Bet "
                    f"(butuh **{bet + ante_cost:,} Bcash**).",
                    delete_after=6
                )
                continue
            ante_mode = not ante_mode
            status = "✅ AKTIF" if ante_mode else "❌ NONAKTIF"
            await ctx.send(
                f"⚡ {ctx.author.mention} Ante Bet {status} — "
                f"spin berikutnya {'bayar' if ante_mode else 'normal'}.",
                delete_after=5
            )
            continue

        # ── Buy Free Spin ──
        if choice == "buyfs":
            buyfs_cost = bet * BONANZA_BUY_FS_MULT
            bal_now    = get_coins(uid)
            if bal_now < buyfs_cost:
                await ctx.send(
                    f"⚠️ {ctx.author.mention} Saldo tidak cukup untuk Buy Free Spin "
                    f"(butuh **{buyfs_cost:,} Bcash**).",
                    delete_after=6
                )
                continue
            add_coins(uid, -buyfs_cost)
            burn_coins(buyfs_cost)
            log_history(uid, f"🍬 Bonanza Buy Free Spin ×100", -buyfs_cost)
            free_spins_left  = 10
            free_spins_total = 10
            is_free_spin     = True
            fs_won_start     = total_won   # catat total_won sebelum FS mulai
            # Roll 35% cap: total kemenangan FS dikap ×10 dari bet
            fs_cap_chance = load_game_settings().get("bonanza_fs_cap_chance", 0.35)
            is_fs_capped  = random.random() < fs_cap_chance
            embed_game.clear_fields()
            embed_game.add_field(
                name="🎁 BUY FREE SPIN!",
                value=f"Kamu membeli **10 Free Spin** seharga **{buyfs_cost:,} Bcash**!\n✨ Selamat menikmati!",
                inline=False
            )
            embed_game.color = discord.Color.gold()
            await game_msg.edit(embed=embed_game, view=None)
            await asyncio.sleep(0.8)
            continue

        # ── Spin Normal (choice == "next") ──
        actual_bet = int(bet * BONANZA_ANTE_MULT) if ante_mode else bet
        bal_now    = get_coins(uid)
        if bal_now < actual_bet:
            embed_game.clear_fields()
            embed_game.add_field(
                name="❌ Bcash Habis",
                value=f"Saldo tidak cukup untuk spin berikutnya.\n💰 Total menang sesi: **{total_won:,} Bcash**",
                inline=False
            )
            embed_game.color = discord.Color.red()
            await game_msg.edit(embed=embed_game, view=None)
            break

        add_coins(uid, -actual_bet)
        burn_coins(actual_bet)
        _bz_add_jackpot(actual_bet)
        log_history(uid, f"🍬 Bonanza spin #{spin_count+1}" + (" (Ante)" if ante_mode else ""), -actual_bet)
        spin_count += 1

        scatter_hit = await _run_spin(is_fs=False, ante=ante_mode)
        ante_mode   = False   # reset ante setelah 1 spin

        # Scatter triggered → aktifkan free spin
        if scatter_hit:
            free_spins_left  = 10
            free_spins_total = 10
            is_free_spin     = True
            fs_won_start     = total_won   # catat total_won sebelum FS mulai
            # Roll 35% cap saat scatter trigger
            fs_cap_chance = load_game_settings().get("bonanza_fs_cap_chance", 0.35)
            is_fs_capped  = random.random() < fs_cap_chance

    # ── Akhiri game ──
    embed_game.clear_fields()
    embed_game.color = discord.Color.blurple()
    embed_game.add_field(
        name="🏁 GAME SELESAI",
        value=(
            f"🎯 Total Spin: **{spin_count}**\n"
            f"🌀 Total Tumble: **{tumble_count}**\n"
            f"💰 Total Kemenangan: **{total_won:,} Bcash**\n"
            f"💳 Saldo Akhir: **{get_coins(uid):,} Bcash**"
        ),
        inline=False
    )
    embed_game.set_footer(
        text=f"Asisten Lurah BFL • Sweet Bonanza 🍬 | Jackpot: {_bz_load_jackpot():,} Bcash"
    )
    await game_msg.edit(embed=embed_game, view=None)
    # ── Cleanup session ──
    _bz_active_sessions.discard(uid)
    _bz_reset_scatter(uid)

# ═══════════════════════════════════════════════════════
#  BALAPAN KUDA (!balapan)
# ═══════════════════════════════════════════════════════
_active_races: dict = {}   # channel_id → race info (agar 1 race per channel)

@bot.command(name="balapan", aliases=["race", "kuda"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def balapan_cmd(ctx, pilihan: str = None, bet: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    if not pilihan or not bet:
        embed = discord.Embed(
            title="🏇 Balapan Kuda — Cara Main",
            description=(
                "Pilih kuda dan taruhkan Bcash kamu!\n\n"
                "**Format:** `!balapan <1/2> <bet>`\n"
                "**Contoh:** `!balapan 1 10`\n\n"
                "🐴 **Kuda 1** vs 🐎 **Kuda 2**\n"
                "🎯 Menang → **×2 Bcash** (Bcash baru di-mint!)\n"
                "🔥 Kalah → bet **di-burn** (harga Bcash naik!)"
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="Asisten Lurah BFL • Balapan Kuda")
        return await ctx.send(embed=embed)

    if pilihan not in ["1", "2"]:
        return await ctx.send("❌ Pilih kuda **1** atau **2**. Contoh: `!balapan 1 10`")
    is_admin_player = is_admin(ctx.author)
    max_b = get_max_bet("balapan")
    if bet < 1 or bet > max_b:
        return await ctx.send(f"❌ Bet min **1** dan max **{max_b}** Bcash.")

    uid = str(ctx.author.id)
    ensure_coins(uid)
    balance = get_coins(uid)
    if balance < bet:
        return await ctx.send(f"❌ Bcash tidak cukup! Saldo: **{balance:,}**, butuh: **{bet:,}**.")

    add_coins(uid, -bet)
    burn_coins(bet)   # langsung burn saat bet
    log_history(uid, f"🏇 Balapan Kuda bet kuda-{pilihan}", -bet)
    mark_activity(uid)

    # ── Tentukan hasil (winrate dari settings) ──
    winrate    = get_winrate("balapan", is_admin_player)
    user_won   = random.random() < winrate
    winner_kuda = pilihan if user_won else ("2" if pilihan == "1" else "1")

    # ── Animasi balapan ──
    KUDA1, KUDA2 = "🐴", "🐎"
    FINISH = "🏁"
    TRACK  = 12   # panjang lintasan (karakter)

    pos1 = 0
    pos2 = 0

    def render(p1, p2):
        lane1 = " " * p1 + KUDA1 + "─" * (TRACK - p1)
        lane2 = " " * p2 + KUDA2 + "─" * (TRACK - p2)
        return (
            f"```\n"
            f"{FINISH} Lintasan Balapan BFL {FINISH}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f" Kuda 1 ➜ {lane1}\n"
            f" Kuda 2 ➜ {lane2}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"```"
        )

    embed_race = discord.Embed(
        title="🏇 BALAPAN DIMULAI!",
        description=render(pos1, pos2),
        color=discord.Color.orange()
    )
    embed_race.add_field(name="🎯 Pilihan Kamu", value=f"Kuda **{pilihan}**", inline=True)
    embed_race.add_field(name="💰 Taruhan", value=f"**{bet:,} Bcash**", inline=True)
    embed_race.set_footer(text="Asisten Lurah BFL • Balapan Kuda")
    msg = await ctx.send(embed=embed_race)

    # Animasi — 5 frame (kedua kuda bergerak acak, netral)
    for frame in range(5):
        await asyncio.sleep(1.2)
        pos1 = min(pos1 + random.randint(0, 3), TRACK - 1)
        pos2 = min(pos2 + random.randint(0, 3), TRACK - 1)
        embed_race.description = render(pos1, pos2)
        await msg.edit(embed=embed_race)

    # Frame terakhir — pemenang maju ke garis finish
    if winner_kuda == "1":
        pos1 = TRACK
    else:
        pos2 = TRACK

    # Frame terakhir — pemenang di garis finish
    embed_race.description = render(pos1, pos2)
    await msg.edit(embed=embed_race)
    await asyncio.sleep(0.8)

    # ── Hasil ──
    user_won = (pilihan == winner_kuda)
    kuda_icon = KUDA1 if winner_kuda == "1" else KUDA2

    if user_won:
        reward = bet * 2
        # Hadiah dari mint baru
        add_coins(uid, reward)
        mint_coins(reward)
        log_history(uid, f"🏇 Balapan WIN kuda-{winner_kuda}", +reward)
        embed_result = discord.Embed(
            title=f"🏆 {kuda_icon} KUDA {winner_kuda} MENANG!",
            description=(
                f"{ctx.author.mention} Tebakanmu **BENAR**!\n\n"
                f"💰 **+{reward:,} Bcash** di-mint untukmu!\n"
                f"🔥 Bet kamu sudah di-burn → harga naik, reward baru lebih tinggi lagi!"
            ),
            color=discord.Color.green()
        )
    else:
        # Sudah di-burn saat bet
        log_history(uid, f"🏇 Balapan LOSE kuda-{winner_kuda}", -bet)
        embed_result = discord.Embed(
            title=f"💀 {kuda_icon} KUDA {winner_kuda} MENANG!",
            description=(
                f"{ctx.author.mention} Tebakanmu **SALAH**.\n\n"
                f"🔥 **{bet:,} Bcash** di-burn → harga Bcash naik!"
            ),
            color=discord.Color.red()
        )

    embed_result.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
    embed_result.set_footer(text="Asisten Lurah BFL • Balapan Kuda")
    await ctx.send(embed=embed_result)



# ═══════════════════════════════════════════════════════
#  TRANSFER BCASH (!kirim)
# ═══════════════════════════════════════════════════════
@bot.command(name="kirim", aliases=["transfer", "send"])
async def kirim_bcash(ctx, target: discord.Member = None, amount: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    # Validasi input
    if not target or not amount:
        return await ctx.send(
            "❌ Format salah! Gunakan: `!kirim @user <jumlah>`\n"
            "Contoh: `!kirim @BFL 50`"
        )
    if target.bot:
        return await ctx.send("❌ Tidak bisa kirim Bcash ke bot.")
    if target.id == ctx.author.id:
        return await ctx.send("❌ Tidak bisa kirim Bcash ke diri sendiri.")
    if amount <= 0:
        return await ctx.send("❌ Jumlah harus lebih dari 0.")

    sender_uid = str(ctx.author.id)
    target_uid = str(target.id)

    ensure_coins(sender_uid)
    ensure_coins(target_uid)

    sender_bal = get_coins(sender_uid)
    if sender_bal < amount:
        return await ctx.send(
            f"❌ Bcash tidak cukup!\n"
            f"Saldo kamu: **{sender_bal:,} Bcash**, mau kirim: **{amount:,} Bcash**."
        )

    # Eksekusi transfer
    add_coins(sender_uid, -amount)
    add_coins(target_uid, +amount)
    log_history(sender_uid, f"💸 Kirim ke {target.display_name}", -amount)
    log_history(target_uid, f"💸 Terima dari {ctx.author.display_name}", +amount)
    sender_new = get_coins(sender_uid)
    target_new  = get_coins(target_uid)

    embed = discord.Embed(
        title="💸 Transfer Bcash Berhasil",
        color=discord.Color.green()
    )
    embed.add_field(name="Dari",   value=ctx.author.mention, inline=True)
    embed.add_field(name="Ke",     value=target.mention,     inline=True)
    embed.add_field(name="Jumlah", value=f"**{amount:,} Bcash**", inline=True)
    embed.add_field(name="Saldo kamu",       value=f"{sender_new:,} Bcash", inline=True)
    embed.add_field(name=f"Saldo {target.display_name}", value=f"{target_new:,} Bcash", inline=True)
    embed.set_footer(text="Asisten Lurah BFL • Bcash Transfer")
    await ctx.send(embed=embed)

    # Notifikasi DM ke penerima
    try:
        await target.send(
            f"💸 Kamu menerima **{amount:,} Bcash** dari **{ctx.author.display_name}**!\n"
            f"Saldo sekarang: **{target_new:,} Bcash**"
        )
    except discord.Forbidden:
        pass   # DM tertutup, skip saja


# ═══════════════════════════════════════════════════════
#  DAILY REWARD (!daily)
# ═══════════════════════════════════════════════════════
DAILY_REWARDS = {
    1: 1,   # Hari ke-1: 1 Bcash
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 7,   # Hari ke-7 (streak penuh): 7 Bcash — bonus terbesar
}
DAILY_COOLDOWN_HOURS = 24

@bot.command(name="daily", aliases=["klaim", "claimdaily"])
async def daily_cmd(ctx):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    uid = str(ctx.author.id)
    ensure_coins(uid)

    daily_data = load_json(DAILY_FILE, default={})
    now        = datetime.datetime.utcnow()
    user_data  = daily_data.get(uid, {"last_claim": None, "streak": 0})

    last_claim_str = user_data.get("last_claim")
    streak         = user_data.get("streak", 0)

    if last_claim_str:
        last_claim = datetime.datetime.fromisoformat(last_claim_str)
        delta_hours = (now - last_claim).total_seconds() / 3600

        # Belum 24 jam → cooldown
        if delta_hours < DAILY_COOLDOWN_HOURS:
            sisa_detik = int((DAILY_COOLDOWN_HOURS * 3600) - (now - last_claim).total_seconds())
            h, r = divmod(sisa_detik, 3600)
            m, s = divmod(r, 60)
            return await ctx.send(
                f"⏳ Kamu sudah klaim hari ini!\n"
                f"Cooldown: **{h}j {m}m {s}d** lagi.\n"
                f"Streak saat ini: **{streak} hari** 🔥"
            )

        # Lebih dari 48 jam → streak reset
        if delta_hours >= 48:
            streak = 0

    # Hitung streak baru (maks 7 untuk reward tertinggi, lalu reset ke 1)
    streak = (streak % 7) + 1
    reward  = DAILY_REWARDS[streak]

    # Berikan Bcash dari mint baru (bukan dari admin bank)
    add_coins(uid, reward)
    mint_coins(reward)   # daily reward → supply naik → sedikit bearish
    log_history(uid, f"🌅 Daily reward (streak {streak}/7)", +reward)
    daily_data[uid] = {
        "last_claim": now.isoformat(),
        "streak":     streak,
    }
    save_json(DAILY_FILE, daily_data)

    new_bal = get_coins(uid)

    # Buat progress bar streak (7 kotak)
    bar = ""
    for i in range(1, 8):
        if i < streak:
            bar += "🟨"   # sudah lewat
        elif i == streak:
            bar += "⭐"   # hari ini
        else:
            bar += "⬜"   # belum

    # Pesan bonus hari ke-7
    if streak == 7:
        bonus_msg = "\n🎉 **STREAK SEMPURNA!** Kamu dapat bonus tertinggi minggu ini!"
    else:
        next_reward = DAILY_REWARDS[min(streak + 1, 7)]
        bonus_msg = f"\n➡️ Besok (hari ke-{streak + 1 if streak < 7 else 1}): **{next_reward} Bcash**"

    embed = discord.Embed(
        title="🌅 Daily Reward",
        description=f"{bar}",
        color=discord.Color.orange()
    )
    embed.add_field(name="🎁 Reward",    value=f"**+{reward} Bcash**",    inline=True)
    embed.add_field(name="🔥 Streak",    value=f"**{streak} / 7 hari**", inline=True)
    embed.add_field(name="💰 Saldo",     value=f"**{new_bal:,} Bcash**", inline=True)
    embed.add_field(
        name="📅 Jadwal Reward",
        value=(
            "Hari 1: 1 • Hari 2: 1 • Hari 3: 2\n"
            "Hari 4: 3 • Hari 5: 4 • Hari 6: 5\n"
            "⭐ **Hari 7: 7 Bcash** ⭐"
        ),
        inline=False
    )
    embed.set_thumbnail(url=ctx.author.display_avatar.url)
    embed.set_footer(text=f"Klaim lagi dalam 24 jam • Asisten Lurah BFL{bonus_msg}")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  RAIN BCASH (!rain) — Admin only
# ═══════════════════════════════════════════════════════
@bot.command(name="rain")
async def rain_bcash(ctx, total: int = None, max_users: int = 5):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    if not total or total < 1:
        return await ctx.send(
            "❌ Format: `!rain <total_bcash> [jumlah_user]`\n"
            "Contoh: `!rain 100 5` → sebar 100 Bcash ke 5 user aktif di channel ini"
        )

    # Cek saldo admin bank cukup
    ensure_coins(ADMIN_BANK_ID)
    admin_bal = get_coins(ADMIN_BANK_ID)
    if admin_bal < total:
        return await ctx.send(f"❌ Saldo admin bank tidak cukup! Saldo: **{admin_bal:,} Bcash**, butuh: **{total:,} Bcash**.")

    # Scan 5 menit terakhir, hanya di channel tempat !rain diketik
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    aktif = {}
    async for msg in ctx.channel.history(limit=200, after=cutoff):
        if (not msg.author.bot
                and msg.author.id != ctx.author.id
                and msg.author.id not in aktif):
            aktif[msg.author.id] = msg.author

    if not aktif:
        return await ctx.send(
            f"❌ Tidak ada user aktif dalam 5 menit terakhir di <#{ctx.channel.id}>."
        )

    pool     = list(aktif.values())
    winners  = random.sample(pool, min(max_users, len(pool)))
    per_user = total // len(winners)
    if per_user < 1:
        return await ctx.send(
            f"❌ Total terlalu kecil untuk dibagi ke {len(winners)} user. "
            f"Min **{len(winners)} Bcash**."
        )

    total_keluar = per_user * len(winners)
    # Potong saldo admin bank
    add_coins(ADMIN_BANK_ID, -total_keluar)
    log_history(ADMIN_BANK_ID, f"🌧️ Rain ke {len(winners)} user di #{ctx.channel.name}", -total_keluar)

    mention_list = []
    for w in winners:
        wuid = str(w.id)
        ensure_coins(wuid)
        add_coins(wuid, per_user)
        log_history(wuid, f"🌧️ Rain dari admin di #{ctx.channel.name}", +per_user)
        mention_list.append(w.mention)

    embed = discord.Embed(
        title="🌧️ RAIN BCASH!",
        description=f"Admin **{ctx.author.display_name}** menyebar Bcash di <#{ctx.channel.id}>!",
        color=discord.Color.blue()
    )
    embed.add_field(name="💰 Per User",    value=f"**{per_user:,} Bcash**",              inline=True)
    embed.add_field(name="👥 Penerima",    value=f"**{len(winners)} user**",              inline=True)
    embed.add_field(name="💸 Total Sebar", value=f"**{total_keluar:,} Bcash**",           inline=True)
    embed.add_field(name="🎉 Penerima",    value=" ".join(mention_list),                  inline=False)
    embed.set_footer(text=f"Aktif di #{ctx.channel.name} dalam 5 menit untuk kebagian rain berikutnya!")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  RIWAYAT TRANSAKSI (!history)
# ═══════════════════════════════════════════════════════
@bot.command(name="history", aliases=["riwayat", "log"])
async def history_cmd(ctx, member: discord.Member = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    if member and not is_admin(ctx.author):
        member = None

    target  = member or ctx.author
    uid     = str(target.id)
    data    = load_json(HISTORY_FILE, default={})
    entries = data.get(uid, [])

    if not entries:
        return await ctx.send(f"📭 Belum ada riwayat transaksi untuk **{target.display_name}**.")

    lines = []
    for e in entries[:10]:
        sign  = "+" if e["amount"] > 0 else ""
        arrow = "🟢" if e["amount"] > 0 else "🔴"
        lines.append(f"{arrow} `{e['time']}` {e['label']} **{sign}{e['amount']:,} Bcash**")

    embed = discord.Embed(
        title=f"📊 Riwayat Transaksi — {target.display_name}",
        description="\n".join(lines),
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.set_footer(text="Menampilkan 10 transaksi terakhir • Asisten Lurah BFL")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  DUEL BCASH (!duel)
# ═══════════════════════════════════════════════════════
_active_duels = set()

@bot.command(name="duel")
@commands.cooldown(1, 10, commands.BucketType.user)
async def duel_cmd(ctx, target: discord.Member = None, amount: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)
    if not target or not amount:
        return await ctx.send("❌ Format: `!duel @user <jumlah>`\nContoh: `!duel @BFL 50`")
    if target.bot:
        return await ctx.send("❌ Tidak bisa duel dengan bot.")
    if target.id == ctx.author.id:
        return await ctx.send("❌ Tidak bisa duel dengan diri sendiri.")
    if amount < 1:
        return await ctx.send("❌ Jumlah taruhan min 1 Bcash.")

    ch_uid = str(ctx.author.id)
    tg_uid = str(target.id)

    if ch_uid in _active_duels or tg_uid in _active_duels:
        return await ctx.send("❌ Salah satu pemain sedang dalam duel aktif. Tunggu selesai.")

    ensure_coins(ch_uid); ensure_coins(tg_uid)
    ch_bal = get_coins(ch_uid)
    tg_bal = get_coins(tg_uid)

    if ch_bal < amount:
        return await ctx.send(f"❌ Bcash kamu tidak cukup! Saldo: **{ch_bal:,}**, butuh: **{amount:,}**.")
    if tg_bal < amount:
        return await ctx.send(f"❌ Bcash {target.display_name} tidak cukup! Saldo: **{tg_bal:,}**, butuh: **{amount:,}**.")

    _active_duels.add(ch_uid); _active_duels.add(tg_uid)
    await ctx.send(
        f"⚔️ {target.mention} kamu ditantang duel oleh {ctx.author.mention}!\n"
        f"Taruhan: **{amount:,} Bcash** | Ketik `ya` dalam 30 detik untuk menerima."
    )

    def check_accept(m):
        return (m.author.id == target.id and
                m.channel.id == ctx.channel.id and
                m.content.lower() in ["ya", "yes", "iya", "ok"])

    try:
        await bot.wait_for("message", check=check_accept, timeout=30)
    except asyncio.TimeoutError:
        _active_duels.discard(ch_uid); _active_duels.discard(tg_uid)
        return await ctx.send(f"⏰ {target.display_name} tidak merespons. Duel dibatalkan.")

    add_coins(ch_uid, -amount)
    add_coins(tg_uid, -amount)
    mark_activity(ch_uid)
    mark_activity(tg_uid)
    # Kedua bet langsung di-burn
    burn_coins(amount)
    burn_coins(amount)
    log_history(ch_uid, f"⚔️ Duel bet vs {target.display_name}", -amount)
    log_history(tg_uid, f"⚔️ Duel bet vs {ctx.author.display_name}", -amount)

    anim_msg = await ctx.send("🪙 Lempar koin...")
    await asyncio.sleep(1)
    await anim_msg.edit(content="🪙 ~~Lempar koin...~~ ⚡ Menentukan pemenang...")
    await asyncio.sleep(1)

    winner, loser = random.choice([(ctx.author, target), (target, ctx.author)])
    w_uid = str(winner.id)
    l_uid = str(loser.id)

    # Hadiah dari mint baru (2× bet tiap orang = total pot)
    hadiah = amount * 2
    add_coins(w_uid, hadiah)
    mint_coins(hadiah)
    log_history(w_uid, f"⚔️ Duel menang vs {loser.display_name}",  +hadiah)
    log_history(l_uid, f"⚔️ Duel kalah vs {winner.display_name}", -amount)
    _active_duels.discard(ch_uid); _active_duels.discard(tg_uid)

    embed = discord.Embed(title="⚔️ Hasil Duel!", color=discord.Color.gold())
    embed.add_field(name="🏆 Pemenang",     value=winner.mention,                inline=True)
    embed.add_field(name="💀 Kalah",        value=loser.mention,                 inline=True)
    embed.add_field(name="💰 Hadiah",       value=f"**{hadiah:,} Bcash** (baru di-mint!)", inline=True)
    embed.add_field(name="🔥 Burn",         value=f"**{amount*2:,} Bcash** → harga naik!", inline=True)
    embed.set_footer(text="Asisten Lurah BFL • Duel Bcash")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  PAJAK HARIAN — user tidak main game kena 10% per hari
# ═══════════════════════════════════════════════════════
@tasks.loop(hours=24)
async def daily_tax():
    """Jalankan setiap 24 jam. User yang tidak main game hari ini kena potongan pajak 10%."""
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    activity = load_activity()
    coins    = load_coins()
    taxed    = 0

    for uid, bal in list(coins.items()):
        if uid == ADMIN_BANK_ID:
            continue
        bal = int(bal)
        if bal <= 0:
            continue
        # Cek apakah user main game hari ini
        last_active = activity.get(str(uid))
        if last_active == today:
            continue   # sudah main → bebas pajak
        # Tidak main → potong 10%
        potongan = max(1, int(bal * 0.10))
        add_coins(str(uid), -potongan)
        add_coins(ADMIN_BANK_ID, +potongan)
        log_history(str(uid), "🏛️ Potongan pajak", -potongan)
        log_history(ADMIN_BANK_ID, f"🏛️ Pajak dari user {uid}", +potongan)
        taxed += 1

    print(f"[PAJAK] {today} — {taxed} user dikenai pajak 10%")

@daily_tax.before_loop
async def before_daily_tax():
    await bot.wait_until_ready()
    # Sinkronkan loop ke jam 00:00 UTC
    now = datetime.datetime.utcnow()
    next_midnight = (now + datetime.timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    await asyncio.sleep((next_midnight - now).total_seconds())

# ═══════════════════════════════════════════════════════
#  ADDKOIN — Admin tambah saldo admin bank
# ═══════════════════════════════════════════════════════
@bot.command(name="addkoin", aliases=["addbcash", "topupbank"])
async def addkoin_cmd(ctx, amount: str = None):
    """Admin tambah saldo admin bank langsung. Bisa di server atau DM."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.")
    if not amount or not amount.replace(".", "").replace(",", "").isdigit():
        return await ctx.send(
            "❌ Format: `!addkoin <jumlah>`\n"
            "Contoh: `!addkoin 5000`\n\n"
            "💡 Perintah ini langsung menambah saldo admin bank."
        )
    amt = int(amount.replace(".", "").replace(",", ""))
    if amt < 1:
        return await ctx.send("❌ Jumlah minimal 1 Bcash.")

    ensure_coins(ADMIN_BANK_ID)
    new_bal = add_coins(ADMIN_BANK_ID, amt)
    mint_coins(amt)
    log_history(ADMIN_BANK_ID, f"➕ Topup admin bank oleh {ctx.author.display_name}", +amt)

    embed = discord.Embed(
        title="✅ Saldo Admin Bank Ditambah",
        color=discord.Color.green()
    )
    embed.add_field(name="➕ Ditambahkan", value=f"**{amt:,} Bcash**",     inline=True)
    embed.add_field(name="💰 Saldo Baru",  value=f"**{new_bal:,} Bcash**", inline=True)
    embed.set_footer(text=f"Oleh {ctx.author.display_name} • Asisten Lurah BFL")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  GAME — TENDANG BOLA (!ball)
# ═══════════════════════════════════════════════════════

_BALL_KICK_FRAMES = [
    # Frame 1 — siap tendang
    ("```\n"
     "  ⚽         🧤[     ]\n"
     "  Bola: siap ditendang!\n"
     "```"),
    # Frame 2 — tendang!
    ("```\n"
     "  💥  ⚽→→→→ 🧤[     ]\n"
     "  Bola melayang...\n"
     "```"),
    # Frame 3 — meluncur
    ("```\n"
     "  💨       ⚽→ 🧤[     ]\n"
     "  Melesat deras!\n"
     "```"),
]

_BALL_GOAL_FRAME = (
    "```\n"
    "  🥅  💥⚽  🙆 GOLAAAAAS!\n"
    "  Kiper tidak bisa menghentikan!\n"
    "```"
)

_BALL_SAVE_FRAME = (
    "```\n"
    "  🥅  🤾✋⚽  DITANGKAP!\n"
    "  Kiper berhasil blok!\n"
    "```"
)

@bot.command(name="ball", aliases=["tendang", "goal"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def ball_game(ctx, bet: int = None):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    if not bet or bet < 1:
        embed = discord.Embed(
            title="⚽ Tendang Bola — Cara Main",
            description=(
                "Tendang bola ke gawang yang dijaga kiper!\n\n"
                "**Format:** `!ball <bet>`\n"
                "**Contoh:** `!ball 10`\n\n"
                "⚽ Kamu menendang bola ke gawang\n"
                "🧤 Kiper berusaha menghalang\n"
                "🏆 Menang → **×2 Bcash** (Bcash baru di-mint!)\n"
                "🔥 Kalah → bet **di-burn** (harga naik!)"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Asisten Lurah BFL • Ball Game")
        return await ctx.send(embed=embed)

    is_admin_player = is_admin(ctx.author)
    max_b = get_max_bet("ball")
    if bet < 1 or bet > max_b:
        return await ctx.send(f"❌ Bet min **1** dan max **{max_b}** Bcash.")

    uid = str(ctx.author.id)
    ensure_coins(uid)
    balance = get_coins(uid)
    if balance < bet:
        return await ctx.send(f"❌ Bcash tidak cukup! Saldo: **{balance:,}**, butuh: **{bet:,}**.")

    add_coins(uid, -bet)
    burn_coins(bet)   # langsung burn saat bet
    log_history(uid, f"⚽ Ball bet", -bet)
    mark_activity(uid)
    bonus = give_firstplay_bonus(uid, ctx.author.display_name)
    if bonus:
        await ctx.send(f"🎮 {ctx.author.mention} Selamat datang! Kamu dapat **+{bonus} Bcash** bonus!", delete_after=10)

    # Tentukan hasil (winrate dari settings)
    winrate  = get_winrate("ball", is_admin_player)
    user_gol = random.random() < winrate

    # Animasi tendangan
    anim_msg = await ctx.send(_BALL_KICK_FRAMES[0])
    await asyncio.sleep(0.9)
    await anim_msg.edit(content=_BALL_KICK_FRAMES[1])
    await asyncio.sleep(0.9)
    await anim_msg.edit(content=_BALL_KICK_FRAMES[2])
    await asyncio.sleep(0.8)

    if user_gol:
        await anim_msg.edit(content=_BALL_GOAL_FRAME)
        await asyncio.sleep(0.5)

        reward = bet * 2
        # Hadiah dari mint baru
        add_coins(uid, reward)
        mint_coins(reward)
        log_history(uid, "⚽ Ball GOL! (×2)", +reward)

        embed = discord.Embed(
            title="⚽ GOOOOL! Bola Masuk!",
            description=(
                f"{ctx.author.mention} berhasil menjebol gawang! Kiper tak berdaya! 🎉\n\n"
                f"💰 **+{reward:,} Bcash** baru di-mint untukmu!\n"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Asisten Lurah BFL • Ball Game | ⚽ GOL!")
    else:
        await anim_msg.edit(content=_BALL_SAVE_FRAME)
        await asyncio.sleep(0.5)

        # Sudah di-burn saat bet
        log_history(uid, "⚽ Ball ditangkap", -bet)

        embed = discord.Embed(
            title="🧤 DITANGKAP! Kiper Jago!",
            description=(
                f"{ctx.author.mention} Kiper terlalu tangguh, bola tertangkap! 😤\n\n"
                f"🔥 **{bet:,} Bcash** di-burn → harga Bcash naik!\n"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Asisten Lurah BFL • Ball Game | Coba lagi!")

    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  GAME — BERBURU (!hunt)
# ═══════════════════════════════════════════════════════

_HUNT_FRAMES = [
    "```\n🌲🌲🌲🌲🌲🌲🌲🌲\n🏹 Kamu memasuki hutan...\n🌲🌲🌲🌲🌲🌲🌲🌲\n```",
    "```\n🌲🌲🌲🌲🌲🌲🌲🌲\n🏹💨 Membidik target...\n🌲🦌🌲🐗🌲🦊🌲🌲\n```",
    "```\n🌲🌲🌲🌲🌲🌲🌲🌲\n🏹💥 TEMBAK!\n🌲🌲🌲🌲🌲🌲🌲🌲\n```",
]

_HUNT_RESULTS = [
    # (min_reward, max_reward, chance_pct, label, emoji)
    (2,  5,  40, "Buruan Kecil",   "🐇"),   # kelinci/ayam hutan
    (5,  7,  10, "Buruan Sedang",  "🦌"),   # rusa
    (15, 15,  5, "JACKPOT BESAR",  "🐗"),   # babi hutan langka
]
# Kalah: 40% — hilang modal 2 Bcash

@bot.command(name="hunt", aliases=["buru", "berburu"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def hunt_game(ctx):
    if not is_game_channel(ctx):
        return await ctx.send(game_channel_msg(ctx), delete_after=8)

    is_admin_player = is_admin(ctx.author)
    HUNT_COST = 2
    uid = str(ctx.author.id)
    ensure_coins(uid)
    balance = get_coins(uid)

    if balance < HUNT_COST:
        return await ctx.send(
            f"❌ Modal berburu kurang! Butuh **{HUNT_COST} Bcash**."
        )

    add_coins(uid, -HUNT_COST)
    burn_coins(HUNT_COST)   # langsung burn modal saat berburu
    log_history(uid, "🏹 Hunt modal", -HUNT_COST)
    mark_activity(uid)
    bonus = give_firstplay_bonus(uid, ctx.author.display_name)
    if bonus:
        await ctx.send(f"🎮 {ctx.author.mention} Selamat datang! Kamu dapat **+{bonus} Bcash** bonus!", delete_after=10)

    # Animasi masuk hutan
    anim_msg = await ctx.send(_HUNT_FRAMES[0])
    await asyncio.sleep(1.0)
    await anim_msg.edit(content=_HUNT_FRAMES[1])
    await asyncio.sleep(1.0)
    await anim_msg.edit(content=_HUNT_FRAMES[2])
    await asyncio.sleep(0.8)

    # Winrate dari settings
    winrate  = get_winrate("hunt", is_admin_player)
    gs = load_game_settings()
    hunt_rewards = gs.get("hunt_rewards", _GAME_SETTINGS_DEFAULT["hunt_rewards"])

    roll = random.random()
    won  = roll < winrate

    if won:
        # Pilih tier reward
        r2 = random.randint(1, 100)
        cumulative = 0
        reward = hunt_rewards[0][0]
        result_label = "🐇 Buruan Kecil"
        embed_color  = discord.Color.blurple()
        result_icon  = "✅"
        for (rmin, rmax, chance, label, emoji) in hunt_rewards:
            cumulative += chance
            if r2 <= cumulative:
                reward = random.randint(rmin, rmax)
                result_label = f"{emoji} {label}"
                if chance <= 5:
                    embed_color = discord.Color.gold()
                    result_icon = "🏆"
                elif chance <= 10:
                    embed_color = discord.Color.green()
                    result_icon = "🎯"
                else:
                    embed_color = discord.Color.blurple()
                    result_icon = "✅"
                break

        # Hadiah dari mint baru
        add_coins(uid, reward)
        mint_coins(reward)
        log_history(uid, f"🏹 Hunt WIN — {result_label}", +reward)

        embed = discord.Embed(
            title=f"{result_icon} Hasil Berburu!",
            description=(
                f"{result_label}\n\n"
                f"{ctx.author.mention} berhasil membawa pulang buruan!\n"
                f"💰 **+{reward:,} Bcash** baru di-mint untukmu!\n"
            ),
            color=embed_color
        )
        embed.set_footer(text="Asisten Lurah BFL • Hunt Game | Selamat Berburu!")
    else:
        # Sudah di-burn modal
        reward = 0
        result_label = "💨 Target Kabur! Kamu pulang dengan tangan kosong."
        log_history(uid, "🏹 Hunt — target kabur", -HUNT_COST)

        embed = discord.Embed(
            title="💨 Buruan Kabur!",
            description=(
                f"{result_label}\n\n"
                f"🔥 Modal **{HUNT_COST} Bcash** di-burn → harga Bcash naik!\n"
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Asisten Lurah BFL • Hunt Game | Coba lagi!")

    await ctx.send(embed=embed)





# ═══════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════
#  GLOBAL ERROR HANDLER
# ═══════════════════════════════════════════════════════
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if hasattr(ctx.command, "on_error"):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Kamu tidak punya izin untuk command ini.", delete_after=5)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Argumen `{error.param.name}` diperlukan.", delete_after=8)
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Argumen tidak valid.", delete_after=8)
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"⏳ Cooldown! Coba lagi dalam **{error.retry_after:.1f}** detik.", delete_after=5)
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ Kamu tidak memenuhi syarat untuk command ini.", delete_after=5)
    else:
        print(f"[ERROR] Command '{ctx.command}' by {ctx.author}: {error}")

# ═══════════════════════════════════════════════════════
#  FITUR BARU 1 — REACT TO GET ROLE
# ═══════════════════════════════════════════════════════
# Commands:
#   !addreactrole <#channel> <message_id> <emoji> <@role>
#   !removereactrole <message_id> <emoji>
#   !listreactrole

@bot.command(name="addreactrole", aliases=["arr"])
@commands.guild_only()
async def add_react_role(ctx, *, args: str = None):
    """Tambah react-to-get-role pada sebuah pesan.
    Format: !addreactrole #channel <message_id> <emoji> @role
    Contoh: !addreactrole #general 123456789 🎮 @Gamer
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)

    if not args:
        return await ctx.send(
            "❌ Format: `!addreactrole #channel <message_id> <emoji> @role`\n"
            "Contoh: `!addreactrole #general 123456789012345678 🎮 @Gamer`",
            delete_after=12
        )

    # Parse manual agar tidak kena BadArgument dari discord.py converter
    parts = args.split()
    if len(parts) < 4:
        return await ctx.send(
            "❌ Kurang argumen!\nFormat: `!addreactrole #channel <message_id> <emoji> @role`",
            delete_after=10
        )

    # Bagian 1: channel
    channel_raw = parts[0]
    channel = None
    # Coba parsing mention #channel atau channel_id
    ch_id_match = re.search(r"\d+", channel_raw)
    if ch_id_match:
        channel = ctx.guild.get_channel(int(ch_id_match.group()))
    if not channel:
        return await ctx.send(f"❌ Channel `{channel_raw}` tidak ditemukan. Gunakan #mention atau ID channel.", delete_after=10)

    # Bagian 2: message_id
    msg_id_str = parts[1]
    if not msg_id_str.isdigit():
        return await ctx.send(f"❌ `{msg_id_str}` bukan message ID yang valid.", delete_after=8)
    message_id = int(msg_id_str)

    # Bagian 3: emoji (bisa unicode emoji atau custom <:nama:id>)
    emoji_raw = parts[2]

    # Bagian 4+: role (bisa @mention <@&id> atau nama role dengan spasi)
    role_raw  = " ".join(parts[3:])
    role      = None
    # Coba parse mention role <@&id>
    role_id_match = re.search(r"<@&(\d+)>", role_raw)
    if role_id_match:
        role = ctx.guild.get_role(int(role_id_match.group(1)))
    # Coba parse ID langsung
    if not role and role_raw.strip().isdigit():
        role = ctx.guild.get_role(int(role_raw.strip()))
    # Coba cari by nama (case-insensitive)
    if not role:
        role = discord.utils.find(lambda r: r.name.lower() == role_raw.strip().lower(), ctx.guild.roles)
    if not role:
        return await ctx.send(f"❌ Role `{role_raw}` tidak ditemukan. Gunakan @mention, ID, atau nama role.", delete_after=10)

    # Cek hierarki role
    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Role terlalu tinggi, bot tidak bisa memberikan role ini.", delete_after=8)

    # Fetch pesan
    try:
        msg = await channel.fetch_message(message_id)
    except discord.NotFound:
        return await ctx.send(f"❌ Pesan ID `{message_id}` tidak ditemukan di {channel.mention}.", delete_after=8)
    except discord.Forbidden:
        return await ctx.send(f"❌ Bot tidak punya akses membaca {channel.mention}.", delete_after=8)
    except Exception as e:
        return await ctx.send(f"❌ Gagal fetch pesan: `{e}`", delete_after=8)

    # Tambah reaksi ke pesan
    try:
        await msg.add_reaction(emoji_raw)
    except discord.HTTPException:
        return await ctx.send(f"❌ Emoji `{emoji_raw}` tidak valid. Pastikan bot ada di server yang punya emoji custom tersebut.", delete_after=10)

    # Simpan ke file
    data = load_react_roles()
    key  = str(message_id)
    if key not in data:
        data[key] = {"channel_id": channel.id, "roles": {}}
    data[key]["roles"][emoji_raw] = role.id
    save_react_roles(data)

    embed = discord.Embed(
        title="✅ React Role Ditambahkan",
        description=(
            f"**Channel:** {channel.mention}\n"
            f"**Pesan:** [Jump ke pesan]({msg.jump_url})\n"
            f"**Emoji:** {emoji_raw}\n"
            f"**Role:** {role.mention}"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Asisten Lurah BFL • React Role")
    await ctx.send(embed=embed)


@bot.command(name="removereactrole", aliases=["rrr"])
@commands.guild_only()
async def remove_react_role(ctx, message_id: str = None, emoji: str = None):
    """Hapus react-role dari sebuah pesan.
    Format: !removereactrole <message_id> <emoji>
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    if not message_id or not emoji:
        return await ctx.send("❌ Format: `!removereactrole <message_id> <emoji>`", delete_after=8)

    data = load_react_roles()
    key  = str(message_id)
    if key not in data or emoji not in data[key].get("roles", {}):
        return await ctx.send("❌ React role tidak ditemukan.", delete_after=8)
    del data[key]["roles"][emoji]
    if not data[key]["roles"]:
        del data[key]
    save_react_roles(data)
    await ctx.send(f"✅ React role `{emoji}` dihapus dari pesan `{message_id}`.", delete_after=8)


@bot.command(name="listreactrole", aliases=["lrr"])
@commands.guild_only()
async def list_react_role(ctx):
    """Tampilkan semua react role aktif."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    data = load_react_roles()
    if not data:
        return await ctx.send("📭 Tidak ada react role aktif.", delete_after=8)
    embed = discord.Embed(title="📋 Daftar React Role Aktif", color=discord.Color.blurple())
    for msg_id, val in data.items():
        ch = bot.get_channel(val["channel_id"])
        ch_mention = ch.mention if ch else f"<#{val['channel_id']}>"
        lines = []
        for emoji, role_id in val["roles"].items():
            role = ctx.guild.get_role(role_id)
            lines.append(f"{emoji} → {role.mention if role else role_id}")
        embed.add_field(
            name=f"Pesan ID: {msg_id} (di {ch_mention})",
            value="\n".join(lines) or "—",
            inline=False
        )
    embed.set_footer(text="Asisten Lurah BFL • React Role")
    await ctx.send(embed=embed)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.member and payload.member.bot:
        return
    data = load_react_roles()
    key  = str(payload.message_id)
    if key not in data:
        return
    emoji_str = str(payload.emoji)
    role_id   = data[key]["roles"].get(emoji_str)
    if not role_id:
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    role   = guild.get_role(role_id)
    member = payload.member or guild.get_member(payload.user_id)
    if member and role and role not in member.roles:
        try:
            await member.add_roles(role, reason="React Role")
        except Exception:
            pass


@bot.event
async def on_raw_reaction_remove(payload):
    data = load_react_roles()
    key  = str(payload.message_id)
    if key not in data:
        return
    emoji_str = str(payload.emoji)
    role_id   = data[key]["roles"].get(emoji_str)
    if not role_id:
        return
    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return
    role   = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)
    if member and role and role in member.roles:
        try:
            await member.remove_roles(role, reason="React Role dicopot")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════
#  FITUR BARU 2 — AUTO MOD ANTI SPAM
# ═══════════════════════════════════════════════════════
# Commands:
#   !automod on/off
#   !automod threshold <n>   — batas pesan sebelum dianggap spam (default 5)
#   !automod interval <s>    — jendela waktu dalam detik (default 5)
#   !automod mute <s>        — durasi timeout dalam detik (default 60)
#   !automod status

_spam_tracker: dict = {}   # user_id -> [timestamps]


async def _check_automod(message):
    """Dipanggil dari on_message untuk deteksi spam."""
    if message.author.bot or not message.guild:
        return
    cfg = load_automod()
    if not cfg.get("enabled", True):
        return
    if is_admin(message.author):
        return

    threshold = cfg.get("threshold", 5)
    interval  = cfg.get("interval", 5)
    mute_dur  = cfg.get("mute_duration", 60)

    uid = message.author.id
    now = message.created_at.timestamp()

    if uid not in _spam_tracker:
        _spam_tracker[uid] = []
    _spam_tracker[uid] = [t for t in _spam_tracker[uid] if now - t < interval]
    _spam_tracker[uid].append(now)

    if len(_spam_tracker[uid]) >= threshold:
        _spam_tracker[uid] = []

        def is_spam_msg(m):
            return m.author.id == uid

        try:
            deleted = await message.channel.purge(limit=20, check=is_spam_msg)
        except Exception:
            deleted = []

        if isinstance(message.author, discord.Member):
            until = datetime.datetime.utcnow() + datetime.timedelta(seconds=mute_dur)
            try:
                await message.author.timeout(until, reason=f"Auto Mod: Spam ({threshold} pesan/{interval}s)")
            except Exception:
                pass

        menit   = mute_dur // 60
        detik   = mute_dur % 60
        dur_str = f"{menit}m {detik}s" if menit else f"{detik}s"
        embed   = discord.Embed(
            title="🚫 Anti Spam Aktif!",
            description=(
                f"{message.author.mention} terdeteksi spam!\n\n"
                f"🗑️ **{len(deleted)} pesan** dihapus\n"
                f"⏳ Timeout selama **{dur_str}**"
            ),
            color=discord.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Asisten Lurah BFL • Auto Mod")
        try:
            await message.channel.send(embed=embed, delete_after=10)
        except Exception:
            pass


@bot.command(name="automod")
@commands.has_permissions(manage_guild=True)
async def automod_cmd(ctx, subcommand: str = "status", value: str = None):
    """Kelola pengaturan Auto Mod anti spam."""
    cfg = load_automod()
    sub = subcommand.lower()

    if sub == "on":
        cfg["enabled"] = True
        save_automod(cfg)
        return await ctx.send("✅ Auto Mod **diaktifkan**.", delete_after=8)
    elif sub == "off":
        cfg["enabled"] = False
        save_automod(cfg)
        return await ctx.send("✅ Auto Mod **dinonaktifkan**.", delete_after=8)
    elif sub == "threshold":
        if not value or not value.isdigit():
            return await ctx.send("❌ Gunakan: `!automod threshold <angka>`", delete_after=8)
        cfg["threshold"] = max(2, int(value))
        save_automod(cfg)
        return await ctx.send(f"✅ Threshold spam diset ke **{cfg['threshold']} pesan**.", delete_after=8)
    elif sub == "interval":
        if not value or not value.isdigit():
            return await ctx.send("❌ Gunakan: `!automod interval <detik>`", delete_after=8)
        cfg["interval"] = max(1, int(value))
        save_automod(cfg)
        return await ctx.send(f"✅ Interval diset ke **{cfg['interval']} detik**.", delete_after=8)
    elif sub == "mute":
        if not value or not value.isdigit():
            return await ctx.send("❌ Gunakan: `!automod mute <detik>`", delete_after=8)
        cfg["mute_duration"] = max(10, int(value))
        save_automod(cfg)
        return await ctx.send(f"✅ Durasi mute diset ke **{cfg['mute_duration']} detik**.", delete_after=8)
    else:
        status = "🟢 Aktif" if cfg.get("enabled", True) else "🔴 Nonaktif"
        embed  = discord.Embed(
            title="🛡️ Auto Mod Status",
            description=(
                f"**Status:** {status}\n"
                f"**Threshold:** {cfg.get('threshold', 5)} pesan\n"
                f"**Interval:** {cfg.get('interval', 5)} detik\n"
                f"**Durasi Mute:** {cfg.get('mute_duration', 60)} detik"
            ),
            color=discord.Color.orange()
        )
        embed.set_footer(text="Asisten Lurah BFL • Auto Mod")
        await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  FITUR BARU 3 — WELCOME CARD & LEAVE CHANNEL
# ═══════════════════════════════════════════════════════
# Commands:
#   !setwelcome <#channel>
#   !setleave <#channel>
#   !welcometest
#   !leavetest

def _generate_welcome_card(member_name: str, guild_name: str, member_count: int, avatar_bytes: bytes) -> io.BytesIO:
    """Generate welcome card bergaya dengan PIL."""
    W, H = 800, 250
    img  = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background ungu-biru gelap
    for y in range(H):
        r = int(30  + (y / H) * 20)
        g = int(10  + (y / H) * 10)
        b = int(60  + (y / H) * 60)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Ornamen garis diagonal
    for i in range(0, W, 40):
        alpha_val = 15 + (i % 80)
        draw.line([(i, 0), (i - 60, H)], fill=(255, 255, 255, alpha_val), width=1)

    # Ring emas di sekeliling avatar
    av_size  = 150
    av_x, av_y = 50, (H - av_size) // 2
    ring_size = av_size + 10
    draw.ellipse([av_x - 5, av_y - 5, av_x - 5 + ring_size, av_y - 5 + ring_size],
                 outline=(255, 215, 0), width=4)

    # Avatar bulat
    try:
        av_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((av_size, av_size))
        mask   = Image.new("L", (av_size, av_size), 0)
        ImageDraw.Draw(mask).ellipse([0, 0, av_size, av_size], fill=255)
        img.paste(av_img, (av_x, av_y), mask)
    except Exception:
        pass

    # Teks
    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
        font_med = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_sml = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except Exception:
        font_big = ImageFont.load_default()
        font_med = font_big
        font_sml = font_big

    tx = av_x + av_size + 30
    ty = H // 2 - 60
    draw.text((tx, ty),        "SELAMAT DATANG!",               font=font_med, fill=(255, 215, 0))
    draw.text((tx, ty + 38),   member_name[:28],                font=font_big, fill=(255, 255, 255))
    draw.text((tx, ty + 85),   f"Member ke-{member_count}",     font=font_sml, fill=(180, 180, 210))
    draw.text((tx, ty + 108),  guild_name[:40],                 font=font_sml, fill=(150, 150, 180))

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return buf


@bot.event
async def on_member_join(member):
    # ── Simpan waktu join ke tracking ──
    jt = load_join_tracking()
    jt[str(member.id)] = member.joined_at.isoformat() if member.joined_at else datetime.datetime.utcnow().isoformat()
    save_join_tracking(jt)

    cfg   = load_welcome_cfg()
    ch_id = cfg.get("welcome_channel")
    if not ch_id:
        return
    channel = member.guild.get_channel(int(ch_id))
    if not channel:
        return

    embed = discord.Embed(
        title="👋 Member Baru Bergabung!",
        description=(
            f"Halo {member.mention}, selamat datang di **{member.guild.name}**!\n\n"
            f"📌 Kamu adalah member ke **{member.guild.member_count}**\n"
            f"📅 Akun dibuat: <t:{int(member.created_at.timestamp())}:R>"
        ),
        color=discord.Color.from_rgb(80, 60, 180),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="Asisten Lurah BFL • Welcome")

    try:
        av_bytes = await member.display_avatar.read()
        card_buf = await asyncio.get_event_loop().run_in_executor(
            None, _generate_welcome_card,
            member.display_name, member.guild.name, member.guild.member_count, av_bytes
        )
        file = discord.File(card_buf, filename="welcome.png")
        embed.set_image(url="attachment://welcome.png")
        await channel.send(file=file, embed=embed)
    except Exception:
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    cfg   = load_welcome_cfg()
    ch_id = cfg.get("leave_channel")
    if not ch_id:
        return
    channel = member.guild.get_channel(int(ch_id))
    if not channel:
        return

    embed = discord.Embed(
        title="👋 Member Keluar",
        description=(
            f"**{member.display_name}** (`{member.name}`) telah meninggalkan server.\n\n"
            f"👥 Sisa member: **{member.guild.member_count}**"
        ),
        color=discord.Color.from_rgb(180, 60, 60),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_footer(text="Asisten Lurah BFL • Leave")
    await channel.send(embed=embed)


@bot.command(name="setwelcome")
@commands.has_permissions(manage_guild=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    cfg = load_welcome_cfg()
    cfg["welcome_channel"] = channel.id
    save_welcome_cfg(cfg)
    await ctx.send(f"✅ Welcome channel diset ke {channel.mention}.", delete_after=8)


@bot.command(name="setleave")
@commands.has_permissions(manage_guild=True)
async def set_leave_channel(ctx, channel: discord.TextChannel):
    cfg = load_welcome_cfg()
    cfg["leave_channel"] = channel.id
    save_welcome_cfg(cfg)
    await ctx.send(f"✅ Leave channel diset ke {channel.mention}.", delete_after=8)


@bot.command(name="welcometest")
@commands.has_permissions(manage_guild=True)
async def welcome_test(ctx):
    """Test tampilan welcome card."""
    await on_member_join(ctx.author)
    await ctx.send("✅ Welcome card terkirim (test).", delete_after=5)


@bot.command(name="leavetest")
@commands.has_permissions(manage_guild=True)
async def leave_test(ctx):
    """Test pesan leave."""
    await on_member_remove(ctx.author)
    await ctx.send("✅ Leave message terkirim (test).", delete_after=5)


# ═══════════════════════════════════════════════════════
#  FITUR BARU 4 — CUSTOM NICKNAME
# ═══════════════════════════════════════════════════════
# Commands:
#   !nick <nickname>       — ganti nickname sendiri
#   !nick reset            — reset nickname ke nama asli
#   !setnick @user <nick>  — admin: ganti nick orang lain

@bot.command(name="nick")
@commands.guild_only()
async def change_nick(ctx, *, new_nick: str = None):
    """Ganti nickname sendiri di server ini. Gunakan 'reset' untuk hapus nickname."""
    member = ctx.author

    if new_nick is None or new_nick.lower() == "reset":
        try:
            await member.edit(nick=None, reason="Reset nickname sendiri")
            return await ctx.send(f"✅ {member.mention} Nickname direset ke nama asli.", delete_after=8)
        except discord.Forbidden:
            return await ctx.send("❌ Bot tidak punya izin mengubah nickname kamu.", delete_after=8)

    if len(new_nick) > 32:
        return await ctx.send("❌ Nickname maksimal 32 karakter.", delete_after=8)

    try:
        old_nick = member.display_name
        await member.edit(nick=new_nick, reason=f"Custom nick oleh {member}")
        embed = discord.Embed(
            title="✏️ Nickname Diubah",
            description=f"**{old_nick}** → **{new_nick}**",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Asisten Lurah BFL • Custom Nick")
        await ctx.send(embed=embed, delete_after=10)
    except discord.Forbidden:
        await ctx.send("❌ Bot tidak punya izin mengubah nickname kamu.", delete_after=8)


@bot.command(name="setnick")
@commands.has_permissions(manage_nicknames=True)
@commands.guild_only()
async def set_nick_admin(ctx, member: discord.Member, *, new_nick: str = None):
    """Admin: atur nickname orang lain. Gunakan 'reset' untuk hapus nickname."""
    if new_nick is None or new_nick.lower() == "reset":
        try:
            await member.edit(nick=None, reason=f"Nick reset oleh {ctx.author}")
            return await ctx.send(f"✅ Nickname {member.mention} direset.", delete_after=8)
        except discord.Forbidden:
            return await ctx.send("❌ Bot tidak bisa mengubah nickname member ini.", delete_after=8)

    if len(new_nick) > 32:
        return await ctx.send("❌ Nickname maksimal 32 karakter.", delete_after=8)

    try:
        await member.edit(nick=new_nick, reason=f"Set nick oleh {ctx.author}")
        await ctx.send(f"✅ Nickname {member.mention} diubah ke **{new_nick}**.", delete_after=8)
    except discord.Forbidden:
        await ctx.send("❌ Bot tidak bisa mengubah nickname member ini.", delete_after=8)


# ═══════════════════════════════════════════════════════
#  FITUR BARU 5 — POLLING SISTEM
# ═══════════════════════════════════════════════════════
# Commands:
#   !poll <menit> <pertanyaan> | <opsi1> | <opsi2> ...
#   !endpoll <poll_id>
#   !pollresult <poll_id>

_NUMBER_EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]


def _build_poll_embed(poll: dict, poll_id: str) -> discord.Embed:
    options = poll["options"]
    votes   = poll.get("votes", {})
    total   = len(votes)

    counts = [0] * len(options)
    for v in votes.values():
        if 0 <= v < len(options):
            counts[v] += 1

    lines = []
    for i, opt in enumerate(options):
        pct = (counts[i] / total * 100) if total else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        lines.append(f"{_NUMBER_EMOJIS[i]} **{opt}**\n`{bar}` {counts[i]} suara ({pct:.1f}%)")

    end_dt  = datetime.datetime.fromisoformat(poll["end_time"])
    sisa    = end_dt - datetime.datetime.utcnow()
    sisa_s  = max(0, int(sisa.total_seconds()))
    h, rem  = divmod(sisa_s, 3600)
    m, s    = divmod(rem, 60)
    sisa_str = f"{h}j {m}m {s}d" if sisa_s > 0 else "Selesai"

    ended = poll.get("ended", False)
    color = discord.Color.green() if not ended else discord.Color.greyple()

    embed = discord.Embed(
        title=f"📊 {'[SELESAI] ' if ended else ''}POLL — {poll['question']}",
        description="\n\n".join(lines),
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="⏳ Sisa Waktu", value=sisa_str, inline=True)
    embed.add_field(name="🗳️ Total Vote", value=str(total), inline=True)
    embed.add_field(name="🆔 Poll ID",    value=f"`{poll_id}`", inline=True)
    embed.set_footer(text="Asisten Lurah BFL • Polling Sistem")
    return embed


class PollView(View):
    def __init__(self, poll_id: str, options: list):
        super().__init__(timeout=None)
        self.poll_id = poll_id
        for i, opt in enumerate(options[:10]):
            btn = discord.ui.Button(
                label=f"{_NUMBER_EMOJIS[i]} {opt[:60]}",
                style=discord.ButtonStyle.primary,
                custom_id=f"poll_{poll_id}_{i}"
            )
            btn.callback = self._make_callback(i)
            self.add_item(btn)

    def _make_callback(self, option_idx: int):
        async def callback(interaction: discord.Interaction):
            polls = load_polls()
            poll  = polls.get(self.poll_id)
            if not poll:
                return await interaction.response.send_message("❌ Poll tidak ditemukan.", ephemeral=True)
            if poll.get("ended"):
                return await interaction.response.send_message("❌ Poll sudah berakhir.", ephemeral=True)

            uid   = str(interaction.user.id)
            votes = poll.setdefault("votes", {})
            prev  = votes.get(uid)

            if prev == option_idx:
                del votes[uid]
                msg = f"✅ Kamu membatalkan vote **{poll['options'][option_idx]}**."
            else:
                votes[uid] = option_idx
                msg = f"✅ Kamu memilih **{poll['options'][option_idx]}**!"

            save_polls(polls)

            try:
                ch = bot.get_channel(int(poll["channel_id"]))
                m  = await ch.fetch_message(int(poll["message_id"]))
                await m.edit(embed=_build_poll_embed(poll, self.poll_id))
            except Exception:
                pass

            await interaction.response.send_message(msg, ephemeral=True)
        return callback


async def _end_poll(poll_id: str):
    polls = load_polls()
    poll  = polls.get(poll_id)
    if not poll or poll.get("ended"):
        return
    poll["ended"] = True
    save_polls(polls)

    try:
        ch  = bot.get_channel(int(poll["channel_id"]))
        msg = await ch.fetch_message(int(poll["message_id"]))
        await msg.edit(embed=_build_poll_embed(poll, poll_id), view=None)

        votes  = poll.get("votes", {})
        counts = [0] * len(poll["options"])
        for v in votes.values():
            if 0 <= v < len(counts):
                counts[v] += 1

        if any(counts):
            winner_idx = counts.index(max(counts))
            winner_opt = poll["options"][winner_idx]
            embed_win  = discord.Embed(
                title="🏆 Hasil Akhir Poll!",
                description=(
                    f"**{poll['question']}**\n\n"
                    f"🥇 Pemenang: **{winner_opt}** dengan **{counts[winner_idx]} suara**\n"
                    f"🗳️ Total vote: **{len(votes)}**"
                ),
                color=discord.Color.gold()
            )
            embed_win.set_footer(text="Asisten Lurah BFL • Polling Sistem")
            await ch.send(embed=embed_win)
    except Exception as e:
        print(f"[Poll] End error: {e}")


async def _auto_end_poll(poll_id: str, delay_seconds: float):
    await asyncio.sleep(delay_seconds)
    await _end_poll(poll_id)


@bot.command(name="poll")
@commands.guild_only()
async def create_poll(ctx, duration: int, *, content: str):
    """Buat poll baru.
    Contoh: !poll 10 Warna favorit? | Merah | Biru | Hijau
    """
    if "|" not in content:
        return await ctx.send(
            "❌ Format salah!\nGunakan: `!poll <menit> <pertanyaan> | <opsi1> | <opsi2> ...`",
            delete_after=12
        )

    parts    = [p.strip() for p in content.split("|")]
    question = parts[0]
    options  = [p for p in parts[1:] if p]

    if len(options) < 2:
        return await ctx.send("❌ Minimal 2 pilihan.", delete_after=8)
    if len(options) > 10:
        return await ctx.send("❌ Maksimal 10 pilihan.", delete_after=8)
    if duration < 1 or duration > 1440:
        return await ctx.send("❌ Durasi 1–1440 menit.", delete_after=8)

    poll_id  = str(int(datetime.datetime.utcnow().timestamp()))
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)).isoformat()

    poll = {
        "question":   question,
        "options":    options,
        "votes":      {},
        "channel_id": ctx.channel.id,
        "message_id": None,
        "end_time":   end_time,
        "creator_id": ctx.author.id,
        "ended":      False,
    }

    view = PollView(poll_id, options)
    msg  = await ctx.send(embed=_build_poll_embed(poll, poll_id), view=view)

    poll["message_id"] = msg.id
    polls = load_polls()
    polls[poll_id] = poll
    save_polls(polls)

    try:
        await ctx.message.delete()
    except Exception:
        pass

    asyncio.get_event_loop().create_task(_auto_end_poll(poll_id, duration * 60))


@bot.command(name="endpoll")
@commands.guild_only()
async def end_poll_cmd(ctx, poll_id: str):
    """Akhiri poll lebih awal (admin atau pembuat poll)."""
    polls = load_polls()
    poll  = polls.get(poll_id)
    if not poll:
        return await ctx.send("❌ Poll tidak ditemukan.", delete_after=8)
    if poll.get("ended"):
        return await ctx.send("❌ Poll sudah berakhir.", delete_after=8)
    if ctx.author.id != poll["creator_id"] and not is_admin(ctx.author):
        return await ctx.send("❌ Hanya pembuat poll atau admin.", delete_after=8)
    await _end_poll(poll_id)
    await ctx.send(f"✅ Poll `{poll_id}` diakhiri.", delete_after=8)


@bot.command(name="pollresult")
@commands.guild_only()
async def poll_result(ctx, poll_id: str):
    """Lihat hasil poll berdasarkan ID."""
    polls = load_polls()
    poll  = polls.get(poll_id)
    if not poll:
        return await ctx.send("❌ Poll tidak ditemukan.", delete_after=8)
    await ctx.send(embed=_build_poll_embed(poll, poll_id))


# ═══════════════════════════════════════════════════════
#  FITUR BARU — USERINFO ADMIN (cek info user)
# ═══════════════════════════════════════════════════════

@bot.command(name="userinfo", aliases=["infouser", "cekuser"])
@commands.guild_only()
async def userinfo_cmd(ctx, member: discord.Member = None):
    """Admin: cek info lengkap user — kapan join, jumlah chat, level, Bcash."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)

    member = member or ctx.author
    uid    = str(member.id)

    # Data XP & Level
    xp_data = load_data()
    user_xp  = xp_data.get(uid, {})
    xp       = user_xp.get("xp", 0)
    level    = user_xp.get("level", 1)
    level_name = LEVEL_CONFIG.get(level, {}).get("name", "—")

    # Saldo Bcash
    ensure_coins(uid)
    saldo = get_coins(uid)

    # Waktu join (dari tracking file atau dari member object)
    jt_data = load_join_tracking()
    if uid in jt_data:
        try:
            join_dt = datetime.datetime.fromisoformat(jt_data[uid])
            join_str = f"<t:{int(join_dt.timestamp())}:F> (<t:{int(join_dt.timestamp())}:R>)"
        except Exception:
            join_str = "Tidak diketahui"
    elif member.joined_at:
        join_dt = member.joined_at
        join_str = f"<t:{int(join_dt.timestamp())}:F> (<t:{int(join_dt.timestamp())}:R>)"
    else:
        join_str = "Tidak diketahui"

    # Kapan akun Discord dibuat
    created_str = f"<t:{int(member.created_at.timestamp())}:F> (<t:{int(member.created_at.timestamp())}:R>)"

    # Estimasi jumlah pesan dari XP (setiap pesan = 10 XP)
    est_messages = xp // XP_PER_MESSAGE

    # Warn count
    warns = load_warns()
    warn_count = len(warns.get(uid, []))

    # Roles (kecuali @everyone)
    roles = [r.mention for r in member.roles if r.name != "@everyone"]
    roles_str = ", ".join(roles) if roles else "—"

    # Banner
    banners = load_banners()
    banner  = banners.get(uid, {})
    rarity  = banner.get("rarity", "Common")

    # Daily streak
    daily_data = load_json(DAILY_FILE, default={})
    streak = daily_data.get(uid, {}).get("streak", 0)

    embed = discord.Embed(
        title=f"👤 Info User — {member.display_name}",
        color=discord.Color.from_rgb(*LEVEL_CONFIG[level]["color"]),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🏷️ Username",       value=f"{member} (`{member.id}`)", inline=False)
    embed.add_field(name="📅 Bergabung Server",value=join_str, inline=False)
    embed.add_field(name="🗓️ Akun Dibuat",     value=created_str, inline=False)
    embed.add_field(name="💬 Estimasi Pesan",  value=f"**{est_messages:,}** pesan", inline=True)
    embed.add_field(name="⭐ Level",            value=f"**{level}** — {level_name}", inline=True)
    embed.add_field(name="🔮 XP",              value=f"**{xp:,}** XP", inline=True)
    embed.add_field(name="💰 Saldo Bcash",     value=f"**{saldo:,}** Bcash", inline=True)
    embed.add_field(name="🔥 Daily Streak",    value=f"**{streak}/7** hari", inline=True)
    embed.add_field(name="✦ Banner",           value=f"**{rarity}**", inline=True)
    embed.add_field(name="⚠️ Warn",            value=f"**{warn_count}/3**", inline=True)
    embed.add_field(name="🎭 Roles",           value=roles_str[:500], inline=False)
    embed.set_footer(text=f"Asisten Lurah BFL • Diminta oleh {ctx.author}")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  FITUR BARU — !giverole @role @user
# ═══════════════════════════════════════════════════════

@bot.command(name="giverole")
@commands.guild_only()
async def giverole_cmd(ctx, role: discord.Role = None, member: discord.Member = None):
    """Admin: beri role ke user. Format: !giverole @role @user"""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)
    if role is None or member is None:
        return await ctx.send(
            "❌ Format: `!giverole @role @user`\n"
            "Contoh: `!giverole @Moderator @Budi`",
            delete_after=10
        )
    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Role terlalu tinggi, bot tidak bisa memberikan role ini.", delete_after=8)
    if role in member.roles:
        return await ctx.send(f"⚠️ {member.mention} sudah punya role **{role.name}**.", delete_after=8)
    try:
        await member.add_roles(role, reason=f"giverole oleh {ctx.author}")
        embed = discord.Embed(
            title="✅ Role Diberikan",
            description=f"Role {role.mention} berhasil diberikan ke {member.mention}.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text=f"Oleh: {ctx.author} • Asisten Lurah BFL")
        await ctx.send(embed=embed)
        # Notif DM ke member
        try:
            await member.send(
                f"🎉 Kamu mendapat role **{role.name}** di **{ctx.guild.name}** "
                f"oleh **{ctx.author.display_name}**!"
            )
        except Exception:
            pass
    except discord.Forbidden:
        await ctx.send("❌ Bot tidak punya izin memberikan role ini.", delete_after=8)


# ═══════════════════════════════════════════════════════
#  FITUR BARU — BCASH REWARD CHANNEL (admin config)
# ═══════════════════════════════════════════════════════

@bot.command(name="setrewardchannel")
@commands.guild_only()
async def set_reward_channel_cmd(ctx, channel: discord.TextChannel = None, amount: int = 6):
    """Admin: set channel yang memberi Bcash otomatis saat user mengirim pesan.
    Format: !setrewardchannel #channel [jumlah_bcash]
    Contoh: !setrewardchannel #general 6
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    if channel is None:
        return await ctx.send(
            "❌ Format: `!setrewardchannel #channel [jumlah_bcash]`\n"
            "Contoh: `!setrewardchannel #general 6`",
            delete_after=10
        )
    if amount < 1 or amount > 50:
        return await ctx.send("❌ Jumlah Bcash harus antara 1–50.", delete_after=8)

    data = load_bcash_reward_channels()
    data[str(channel.id)] = {"amount": amount, "name": channel.name}
    save_bcash_reward_channels(data)

    embed = discord.Embed(
        title="✅ Reward Channel Diset",
        description=(
            f"Channel {channel.mention} sekarang memberikan **{amount} Bcash** "
            f"per pesan (cooldown 1 menit/user)."
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Asisten Lurah BFL • Bcash Reward Channel")
    await ctx.send(embed=embed)


@bot.command(name="removerewardchannel")
@commands.guild_only()
async def remove_reward_channel_cmd(ctx, channel: discord.TextChannel = None):
    """Admin: hapus channel dari daftar reward channel."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    if channel is None:
        return await ctx.send("❌ Format: `!removerewardchannel #channel`", delete_after=8)
    data = load_bcash_reward_channels()
    if str(channel.id) not in data:
        return await ctx.send(f"⚠️ {channel.mention} bukan reward channel.", delete_after=8)
    del data[str(channel.id)]
    save_bcash_reward_channels(data)
    await ctx.send(f"✅ {channel.mention} dihapus dari reward channel.", delete_after=8)


@bot.command(name="listrewardchannel")
@commands.guild_only()
async def list_reward_channels_cmd(ctx):
    """Admin: lihat semua reward channel aktif."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    data = load_bcash_reward_channels()
    if not data:
        return await ctx.send("📭 Belum ada reward channel.", delete_after=8)
    lines = []
    for ch_id, cfg in data.items():
        ch = bot.get_channel(int(ch_id))
        mention = ch.mention if ch else f"<#{ch_id}>"
        lines.append(f"💬 {mention} → **{cfg.get('amount', 6)} Bcash**/pesan")
    embed = discord.Embed(
        title="💰 Daftar Reward Channel",
        description="\n".join(lines),
        color=discord.Color.gold()
    )
    embed.set_footer(text="Cooldown 1 menit/user • Asisten Lurah BFL")
    await ctx.send(embed=embed)


bot.run(TOKEN)
