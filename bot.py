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
REACT_ROLE_FILE  = "react_roles.json"
AUTOMOD_FILE     = "automod.json"
WELCOME_CFG_FILE = "welcome_config.json"
POLLS_FILE       = "polls.json"
JOIN_TRACKING_FILE = "join_tracking.json"   # tracking kapan user join server

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
        activity=discord.Activity(type=discord.ActivityType.watching, name="WATCHING SERVER 24/7")
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
    print(f"✅ Semua sistem aktif. Logged in as {bot.user}")

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


    # ── XP System ──
    data = load_data()
    uid  = str(message.author.id)
    if uid not in data:
        data[uid] = {"xp": 0, "level": 1, "message_count": 0}
    if "message_count" not in data[uid]:
        data[uid]["message_count"] = 0
    old_level        = data[uid]["level"]
    data[uid]["xp"] += XP_PER_MESSAGE
    data[uid]["message_count"] += 1
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
@bot.command(name="givecoin")
# ═══════════════════════════════════════════════════════
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
    """Admin: cek info lengkap user — profil, aktivitas, status server."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)

    member = member or ctx.author
    uid    = str(member.id)

    # ── Data pesan tercatat (sejak bot aktif) ──
    xp_data      = load_data()
    user_data    = xp_data.get(uid, {})
    msg_count    = user_data.get("message_count", 0)

    # ── Waktu join server ──
    jt_data = load_join_tracking()
    if uid in jt_data:
        try:
            join_dt  = datetime.datetime.fromisoformat(jt_data[uid])
            join_str = f"<t:{int(join_dt.timestamp())}:F>\n╰ <t:{int(join_dt.timestamp())}:R>"
        except Exception:
            join_str = "Tidak diketahui"
    elif member.joined_at:
        join_dt  = member.joined_at
        join_str = f"<t:{int(join_dt.timestamp())}:F>\n╰ <t:{int(join_dt.timestamp())}:R>"
    else:
        join_str = "Tidak diketahui"

    # ── Akun Discord dibuat ──
    created_ts  = int(member.created_at.timestamp())
    created_str = f"<t:{created_ts}:F>\n╰ <t:{created_ts}:R>"

    # ── Status & aktivitas ──
    status_map = {
        discord.Status.online:    ("🟢", "Online"),
        discord.Status.idle:      ("🌙", "Idle"),
        discord.Status.dnd:       ("🔴", "Do Not Disturb"),
        discord.Status.offline:   ("⚫", "Offline"),
    }
    status_icon, status_text = status_map.get(member.status, ("⚫", "Offline"))

    # Aktivitas (game/streaming/custom status)
    activity_str = "—"
    if member.activities:
        for act in member.activities:
            if isinstance(act, discord.Game):
                activity_str = f"🎮 Bermain **{act.name}**"
                break
            elif isinstance(act, discord.Streaming):
                activity_str = f"📺 Streaming **{act.name}**"
                break
            elif isinstance(act, discord.CustomActivity) and act.name:
                activity_str = f"💬 {act.name}"
                break
            elif isinstance(act, discord.Activity):
                activity_str = f"🎯 {act.name}"
                break

    # ── Boost status ──
    if member.premium_since:
        boost_ts   = int(member.premium_since.timestamp())
        boost_str  = f"✅ Sejak <t:{boost_ts}:D>"
    else:
        boost_str  = "❌ Tidak"

    # ── Nickname ──
    nick_str = f"`{member.nick}`" if member.nick else "*(tidak ada)*"

    # ── Hitung lama di server ──
    if member.joined_at:
        delta     = datetime.datetime.now(datetime.timezone.utc) - member.joined_at
        days      = delta.days
        lama_str  = f"**{days:,}** hari"
    else:
        lama_str  = "—"

    # ── Warna embed: berdasarkan top role ──
    top_role_color = member.top_role.color
    embed_color    = top_role_color if top_role_color != discord.Color.default() else discord.Color.from_rgb(88, 101, 242)

    # ══════════════════════════════════════
    #  BUILD EMBED
    # ══════════════════════════════════════
    embed = discord.Embed(
        description=(
            f"### <@{member.id}>\n"
            f"**`{member}`** — {member.id}"
        ),
        color=embed_color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_author(
        name="User Information",
        icon_url=member.display_avatar.url
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    # ── Row 1: Tanggal ──
    embed.add_field(
        name="📅 Bergabung Server",
        value=join_str,
        inline=True
    )
    embed.add_field(
        name="🗓️ Akun Dibuat",
        value=created_str,
        inline=True
    )
    embed.add_field(
        name="⏳ Lama di Server",
        value=lama_str,
        inline=True
    )

    # ── Divider ──
    embed.add_field(name="", value="╌" * 32, inline=False)

    # ── Row 2: Aktivitas ──
    embed.add_field(
        name=f"{status_icon} Status",
        value=f"**{status_text}**",
        inline=True
    )
    embed.add_field(
        name="🎯 Aktivitas",
        value=activity_str,
        inline=True
    )
    embed.add_field(
        name="💬 Total Chat Tercatat",
        value=f"**{msg_count:,}** pesan",
        inline=True
    )

    # ── Divider ──
    embed.add_field(name="", value="╌" * 32, inline=False)

    # ── Row 3: Profil ──
    embed.add_field(
        name="🏷️ Nickname",
        value=nick_str,
        inline=True
    )
    embed.add_field(
        name="💎 Server Boost",
        value=boost_str,
        inline=True
    )
    embed.add_field(
        name="🤖 Bot?",
        value="✅ Ya" if member.bot else "❌ Bukan",
        inline=True
    )

    embed.set_footer(
        text=f"Diminta oleh {ctx.author.display_name}  •  ID: {member.id}",
        icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  ROLE MANAGEMENT SYSTEM
#  !giverole   — beri role ke user
#  !removerole — cabut role dari user
#  !roleinfo   — info detail sebuah role
#  !listrole   — daftar semua role di server
# ═══════════════════════════════════════════════════════

def _role_too_high(ctx, role: discord.Role) -> bool:
    """True jika role lebih tinggi atau sama dengan top role bot."""
    return role >= ctx.guild.me.top_role

def _build_role_embed(role: discord.Role, action: str, member: discord.Member,
                      actor: discord.Member) -> discord.Embed:
    """Buat embed standar untuk aksi give/remove role."""
    color  = role.color if role.color != discord.Color.default() else discord.Color.from_rgb(88, 101, 242)
    icon   = "✅" if action == "give" else "🗑️"
    title  = "Role Diberikan" if action == "give" else "Role Dicabut"
    desc   = (
        f"{icon} {role.mention} berhasil "
        f"{'diberikan ke' if action == 'give' else 'dicabut dari'} {member.mention}."
    )
    embed  = discord.Embed(title=title, description=desc, color=color,
                           timestamp=datetime.datetime.utcnow())
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="👤 Member",  value=f"{member} (`{member.id}`)", inline=True)
    embed.add_field(name="🎭 Role",    value=f"{role.mention} (`{role.id}`)", inline=True)
    embed.add_field(name="🛡️ Admin",  value=f"{actor.mention}", inline=True)
    embed.set_footer(text=f"ID Role: {role.id}  •  ID Member: {member.id}",
                     icon_url=actor.display_avatar.url)
    return embed

# ── !giverole ──────────────────────────────────────────
@bot.command(name="giverole", aliases=["addrole", "berirole"])
@commands.guild_only()
async def giverole_cmd(ctx, member: discord.Member = None, *, roles_input: str = None):
    """Admin: beri satu atau lebih role ke user.
    Format  : !giverole @user @role1 @role2 ...
    Contoh  : !giverole @Budi @Member @VIP
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)

    if member is None or roles_input is None:
        embed = discord.Embed(
            title="📖 Cara Pakai — !giverole",
            description=(
                "Beri satu atau beberapa role ke member sekaligus.\n\n"
                "**Format:**\n"
                "`!giverole @user @role1 @role2 ...`\n\n"
                "**Contoh:**\n"
                "`!giverole @Budi @Member`\n"
                "`!giverole @Budi @Member @VIP @Trusted`\n\n"
                "**Alias:** `!addrole` `!berirole`"
            ),
            color=discord.Color.blue()
        )
        return await ctx.send(embed=embed, delete_after=20)

    # Parse role mentions dari teks
    role_ids    = re.findall(r"<@&(\d+)>", roles_input)
    roles_found = [ctx.guild.get_role(int(rid)) for rid in role_ids if ctx.guild.get_role(int(rid))]

    if not roles_found:
        return await ctx.send(
            "❌ Tidak ada role valid yang ditemukan.\n"
            "Contoh: `!giverole @Budi @Member @VIP`",
            delete_after=10
        )

    success, skipped, failed = [], [], []

    for role in roles_found:
        if _role_too_high(ctx, role):
            failed.append(f"{role.mention} *(terlalu tinggi)*")
            continue
        if role in member.roles:
            skipped.append(role.mention)
            continue
        try:
            await member.add_roles(role, reason=f"giverole oleh {ctx.author}")
            success.append(role.mention)
        except discord.Forbidden:
            failed.append(f"{role.mention} *(tidak ada izin)*")

    # Buat embed hasil
    color = discord.Color.green() if success else discord.Color.orange()
    embed = discord.Embed(
        title="🎭 Hasil Pemberian Role",
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="👤 Member", value=f"{member.mention} (`{member.id}`)", inline=False)

    if success:
        embed.add_field(name=f"✅ Berhasil ({len(success)})",
                        value=" ".join(success), inline=False)
    if skipped:
        embed.add_field(name=f"⚠️ Sudah Punya ({len(skipped)})",
                        value=" ".join(skipped), inline=False)
    if failed:
        embed.add_field(name=f"❌ Gagal ({len(failed)})",
                        value="\n".join(failed), inline=False)

    embed.set_footer(text=f"Oleh: {ctx.author.display_name}",
                     icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

    # DM ke member jika ada yang berhasil
    if success:
        role_names = ", ".join([r.replace("<@&", "").replace(">", "") for r in success])
        try:
            dm_embed = discord.Embed(
                title="🎉 Kamu Mendapat Role Baru!",
                description=f"Role baru telah ditambahkan ke akunmu di **{ctx.guild.name}**.",
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow()
            )
            dm_embed.add_field(name="🎭 Role Diberikan",
                               value=" ".join(success) if len(success) <= 3
                               else f"{len(success)} role baru", inline=True)
            dm_embed.add_field(name="🛡️ Oleh", value=str(ctx.author), inline=True)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except Exception:
            pass


# ── !removerole ────────────────────────────────────────
@bot.command(name="removerole", aliases=["cabutrole", "delrole"])
@commands.guild_only()
async def removerole_cmd(ctx, member: discord.Member = None, *, roles_input: str = None):
    """Admin: cabut satu atau lebih role dari user.
    Format  : !removerole @user @role1 @role2 ...
    Contoh  : !removerole @Budi @VIP @Trusted
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)

    if member is None or roles_input is None:
        embed = discord.Embed(
            title="📖 Cara Pakai — !removerole",
            description=(
                "Cabut satu atau beberapa role dari member sekaligus.\n\n"
                "**Format:**\n"
                "`!removerole @user @role1 @role2 ...`\n\n"
                "**Contoh:**\n"
                "`!removerole @Budi @VIP`\n"
                "`!removerole @Budi @VIP @Trusted`\n\n"
                "**Alias:** `!cabutrole` `!delrole`"
            ),
            color=discord.Color.red()
        )
        return await ctx.send(embed=embed, delete_after=20)

    role_ids    = re.findall(r"<@&(\d+)>", roles_input)
    roles_found = [ctx.guild.get_role(int(rid)) for rid in role_ids if ctx.guild.get_role(int(rid))]

    if not roles_found:
        return await ctx.send(
            "❌ Tidak ada role valid yang ditemukan.\n"
            "Contoh: `!removerole @Budi @VIP`",
            delete_after=10
        )

    success, skipped, failed = [], [], []

    for role in roles_found:
        if _role_too_high(ctx, role):
            failed.append(f"{role.mention} *(terlalu tinggi)*")
            continue
        if role not in member.roles:
            skipped.append(role.mention)
            continue
        try:
            await member.remove_roles(role, reason=f"removerole oleh {ctx.author}")
            success.append(role.mention)
        except discord.Forbidden:
            failed.append(f"{role.mention} *(tidak ada izin)*")

    color = discord.Color.red() if success else discord.Color.orange()
    embed = discord.Embed(
        title="🗑️ Hasil Pencabutan Role",
        color=color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="👤 Member", value=f"{member.mention} (`{member.id}`)", inline=False)

    if success:
        embed.add_field(name=f"✅ Berhasil Dicabut ({len(success)})",
                        value=" ".join(success), inline=False)
    if skipped:
        embed.add_field(name=f"⚠️ Tidak Punya Role ({len(skipped)})",
                        value=" ".join(skipped), inline=False)
    if failed:
        embed.add_field(name=f"❌ Gagal ({len(failed)})",
                        value="\n".join(failed), inline=False)

    embed.set_footer(text=f"Oleh: {ctx.author.display_name}",
                     icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

    # DM ke member jika ada yang berhasil
    if success:
        try:
            dm_embed = discord.Embed(
                title="⚠️ Role Kamu Dicabut",
                description=f"Beberapa role telah dihapus dari akunmu di **{ctx.guild.name}**.",
                color=discord.Color.orange(),
                timestamp=datetime.datetime.utcnow()
            )
            dm_embed.add_field(name="🗑️ Role Dicabut",
                               value=" ".join(success) if len(success) <= 3
                               else f"{len(success)} role", inline=True)
            dm_embed.add_field(name="🛡️ Oleh", value=str(ctx.author), inline=True)
            dm_embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            await member.send(embed=dm_embed)
        except Exception:
            pass


# ── !roleinfo ──────────────────────────────────────────
@bot.command(name="roleinfo", aliases=["inforole", "cekrole"])
@commands.guild_only()
async def roleinfo_cmd(ctx, *, role: discord.Role = None):
    """Info detail sebuah role. Format: !roleinfo @role"""
    if role is None:
        return await ctx.send(
            "❌ Sebutkan role yang ingin dicek.\n"
            "Contoh: `!roleinfo @Member`",
            delete_after=10
        )

    created_ts  = int(role.created_at.timestamp())
    color_hex   = str(role.color) if role.color != discord.Color.default() else "#99aab5 (default)"
    perms       = role.permissions
    key_perms   = []
    if perms.administrator:     key_perms.append("👑 Administrator")
    if perms.manage_guild:      key_perms.append("⚙️ Manage Server")
    if perms.manage_roles:      key_perms.append("🎭 Manage Roles")
    if perms.manage_channels:   key_perms.append("📁 Manage Channels")
    if perms.kick_members:      key_perms.append("👢 Kick Members")
    if perms.ban_members:       key_perms.append("🔨 Ban Members")
    if perms.moderate_members:  key_perms.append("🔇 Timeout Members")
    if perms.manage_messages:   key_perms.append("🗑️ Manage Messages")
    if perms.mention_everyone:  key_perms.append("📢 Mention Everyone")
    perms_str   = "\n".join(key_perms) if key_perms else "*(tidak ada izin khusus)*"

    # Hitung member dengan role ini
    member_count = len(role.members)

    embed_color  = role.color if role.color != discord.Color.default() else discord.Color.from_rgb(88, 101, 242)
    embed = discord.Embed(
        title=f"🎭 Role Info — {role.name}",
        color=embed_color,
        timestamp=datetime.datetime.utcnow()
    )
    embed.add_field(name="🆔 ID",           value=f"`{role.id}`",           inline=True)
    embed.add_field(name="🎨 Warna",        value=f"`{color_hex}`",         inline=True)
    embed.add_field(name="📅 Dibuat",       value=f"<t:{created_ts}:D>",    inline=True)
    embed.add_field(name="👥 Jumlah Member",value=f"**{member_count:,}**",  inline=True)
    embed.add_field(name="📌 Posisi",       value=f"**#{role.position}**",  inline=True)
    embed.add_field(name="🔔 Mentionable",  value="✅ Ya" if role.mentionable else "❌ Tidak", inline=True)
    embed.add_field(name="📋 Ditampilkan Terpisah",
                    value="✅ Ya" if role.hoist else "❌ Tidak", inline=True)
    embed.add_field(name="🤖 Managed (Bot/Integration)",
                    value="✅ Ya" if role.managed else "❌ Tidak", inline=True)
    embed.add_field(name="🔑 Key Permissions",
                    value=perms_str, inline=False)
    embed.set_footer(text=f"Diminta oleh {ctx.author.display_name}",
                     icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)


# ── !listrole ──────────────────────────────────────────
@bot.command(name="listrole", aliases=["listroles", "daftarrole", "semuarole"])
@commands.guild_only()
async def listrole_cmd(ctx):
    """Tampilkan semua role di server beserta jumlah membernya."""
    roles = [r for r in reversed(ctx.guild.roles) if r.name != "@everyone"]

    if not roles:
        return await ctx.send("❌ Tidak ada role di server ini.", delete_after=8)

    # Bagi jadi chunks 20 role per embed (hindari char limit)
    chunk_size = 20
    chunks     = [roles[i:i+chunk_size] for i in range(0, len(roles), chunk_size)]
    total_page = len(chunks)

    for page, chunk in enumerate(chunks, 1):
        lines = []
        for role in chunk:
            color_dot = "🔵" if role.color != discord.Color.default() else "⚪"
            lines.append(
                f"{color_dot} {role.mention} — "
                f"**{len(role.members):,}** member "
                f"{'`[HOIST]`' if role.hoist else ''}"
                f"{'`[ADMIN]`' if role.permissions.administrator else ''}"
            )

        embed = discord.Embed(
            title=f"🎭 Daftar Role Server — {ctx.guild.name}",
            description="\n".join(lines),
            color=discord.Color.from_rgb(88, 101, 242),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(
            text=f"Total {len(roles)} role  •  Halaman {page}/{total_page}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        await ctx.send(embed=embed)



bot.run(TOKEN)
