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
TIKTOK_CHECK_CHANNEL_ID = int(os.environ["TIKTOK_CHECK_CHANNEL_ID"])
TICKET_CHANNEL_ID       = int(os.environ["TICKET_CHANNEL_ID"])
VOICE_CATEGORY_ID       = int(os.environ["VOICE_CATEGORY_ID"])

WIB = pytz.timezone("Asia/Jakarta")

# ═══════════════════════════════════════════════════════
#  FILE DATABASE
# ═══════════════════════════════════════════════════════
# DATA_DIR: folder tempat semua file JSON disimpan.
# PENTING (Railway): filesystem Railway bersifat ephemeral — setiap redeploy,
# container dibuat ulang dan semua file lokal (termasuk data.json dkk) HILANG,
# kecuali folder ini di-mount sebagai Railway Volume (Settings → Volumes →
# Mount Path, misal "/data") dan env var DATA_DIR diarahkan ke path yang sama.
# Kalau DATA_DIR tidak di-set, bot tetap jalan seperti biasa (folder kerja bot),
# tapi datanya TETAP akan hilang tiap redeploy sampai Volume dipasang.
DATA_DIR = os.environ.get("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)

def _p(filename):
    return os.path.join(DATA_DIR, filename)

LAST_TIKTOK_FILE = _p("last_tiktok.json")
TICKET_FILE      = _p("tickets.json")
VERIF_FILE       = _p("verif.json")
WARN_FILE        = _p("warns.json")
GIVEAWAY_FILE    = _p("giveaways.json")
SETTINGS_FILE    = _p("settings.json")
AFK_FILE         = _p("afk.json")
CUSTOM_CMD_FILE  = _p("custom_commands.json")
REACT_ROLE_FILE  = _p("react_roles.json")
AUTOMOD_FILE     = _p("automod.json")
LOGCFG_FILE      = _p("logconfig.json")
BANWORD_FILE     = _p("banwords.json")
WELCOME_CFG_FILE = _p("welcome_config.json")
POLLS_FILE       = _p("polls.json")
JOIN_TRACKING_FILE = _p("join_tracking.json")   # tracking kapan user join server

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

MODERATOR_FILE = _p("moderators.json")

def load_moderators() -> list:
    return load_json(MODERATOR_FILE, default=[
        523513293374095361,
        924476525129125938,
        419422639300411393,
        1162980404370870302,
    ])

def save_moderators(ids: list):
    save_json(MODERATOR_FILE, ids)

def is_moderator(member) -> bool:
    """Akses terbatas: hanya untuk command moderasi member (!warn, !timeout, !ban, !unban, !clear).
    Admin/Owner otomatis lolos juga."""
    if is_admin(member):
        return True
    return member.id in load_moderators()

def load_json(path, default=None):
    if default is None:
        default = {}
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    # Atomic write: tulis ke file sementara dulu lalu rename, supaya kalau bot
    # mati/restart di tengah proses simpan, file asli tidak jadi rusak/kosong.
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)

def load_last_tiktok():  return load_json(LAST_TIKTOK_FILE)
def save_last_tiktok(d): save_json(LAST_TIKTOK_FILE, d)
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
                "created_at": str(datetime.datetime.now(datetime.timezone.utc))
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
                timestamp=datetime.datetime.now(datetime.timezone.utc)
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
    now    = datetime.datetime.now(datetime.timezone.utc)
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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
        activity=discord.Activity(type=discord.ActivityType.watching, name="Watching Server 👀")
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

    # Register tombol MCASH (clip & withdraw yang masih pending)
    try:
        mcash_register_views()
    except Exception as e:
        print(f"[MCASH] Gagal register view: {e}")

    check_tiktok_live.start()
    check_giveaways.start()
    check_setoran_reset.start()
    if not check_trial_roles.is_running():
        check_trial_roles.start()
    if BACKUP_CHANNEL_ID and not auto_backup_settings.is_running():
        auto_backup_settings.start()
    print(f"✅ Semua sistem aktif. Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ── MCASH: catat aktivitas chat (untuk !rain) ──
    _mc_track(message)

    # ── Auto Mod Anti Spam ──
    await _check_automod(message)

    # ── Ban Word (per channel) ──
    if await _check_banword(message):
        return

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
                timestamp=datetime.datetime.now(datetime.timezone.utc)
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


    # ── Auto Reply ──
    autoreply_data = load_autoreply()
    content_lower = message.content.lower()
    for trigger, jawaban in autoreply_data.items():
        if trigger in content_lower:
            await message.channel.send(jawaban)
            break

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
        if datetime.datetime.now(datetime.timezone.utc) >= end_dt:
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
# ═══════════════════════════════════════════════════════
#  TASKS — TIKTOK
# ═══════════════════════════════════════════════════════
TIKTOK_SETTINGS_FILE = _p("tiktok_settings.json")

def load_tiktok_settings() -> dict:
    """Load TikTok configuration with backward compatibility."""
    data = load_json(TIKTOK_SETTINGS_FILE, default={})
    if not isinstance(data, dict):
        data = {}

    # New format:
    # {
    #   "channel_id": "...",
    #   "usernames": {
    #       "username": {"is_live": false}
    #   }
    # }
    usernames = data.get("usernames")
    if not isinstance(usernames, dict):
        usernames = {}

        # Migrate the old single-account format automatically.
        old_username = data.get("username")
        if old_username:
            old_username = str(old_username).lstrip("@").strip()
            if old_username:
                usernames[old_username] = {
                    "is_live": bool(data.get("is_live", False))
                }

    data["usernames"] = usernames
    data.setdefault("channel_id", str(TIKTOK_CHECK_CHANNEL_ID))
    return data


def save_tiktok_settings(d: dict):
    save_json(TIKTOK_SETTINGS_FILE, d)


def get_tiktok_channel():
    """Return configured notification channel, falling back to the ENV channel."""
    settings = load_tiktok_settings()
    raw_id = settings.get("channel_id") or TIKTOK_CHECK_CHANNEL_ID
    try:
        channel = bot.get_channel(int(raw_id))
    except (TypeError, ValueError):
        channel = None
    return channel


def normalize_tiktok_username(username: str) -> str:
    username = str(username or "").strip()
    username = username.replace("https://www.tiktok.com/@", "")
    username = username.replace("https://tiktok.com/@", "")
    username = username.split("/")[0]
    return username.lstrip("@").strip()


def get_tiktok_usernames(settings=None) -> list:
    settings = settings or load_tiktok_settings()
    return list(settings.get("usernames", {}).keys())


async def fetch_tiktok_live_page(username: str) -> dict:
    """Fetch the live page and return status + best available thumbnail URL."""
    url = f"https://www.tiktok.com/@{username}/live"
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            headers=TIKTOK_LIVE_HEADERS,
            timeout=aiohttp.ClientTimeout(total=15),
            allow_redirects=True
        ) as resp:
            html = await resp.text(errors="ignore")
            status = resp.status
            final_path = resp.url.path if resp.url else ""

    matched_status2 = bool(re.search(r'"status"\s*:\s*2\b', html))
    matched_status4 = bool(re.search(r'"status"\s*:\s*4\b', html))
    redirected_away = "/live" not in final_path
    blocked = html.strip() == "" or (
        "captcha" in html.lower() and "tiktok" not in html.lower()[:2000]
    )

    if redirected_away:
        is_live = False
    elif matched_status2 and not matched_status4:
        is_live = True
    else:
        is_live = False

    # TikTok normally exposes the live/profile image through og:image.
    # Keep several fallbacks because TikTok changes its HTML frequently.
    thumbnail = None
    meta_patterns = [
        r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
        r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image["\']',
    ]
    for pattern in meta_patterns:
        match = re.search(pattern, html, flags=re.I)
        if match:
            thumbnail = match.group(1).replace("&amp;", "&")
            break

    # Additional JSON fallback for TikTok cover/profile image URLs.
    if not thumbnail:
        image_patterns = [
            r'"coverLarger"\s*:\s*"([^"]+)"',
            r'"coverMedium"\s*:\s*"([^"]+)"',
            r'"cover"\s*:\s*"([^"]+)"',
            r'"avatarLarger"\s*:\s*"([^"]+)"',
        ]
        for pattern in image_patterns:
            match = re.search(pattern, html)
            if match:
                thumbnail = (
                    match.group(1)
                    .replace(r'\/', '/')
                    .replace(r'\u0026', '&')
                    .replace("&amp;", "&")
                )
                break

    return {
        "is_live": is_live,
        "status_code": status,
        "final_path": final_path,
        "html_len": len(html),
        "matched_status2": matched_status2,
        "matched_status4": matched_status4,
        "blocked": blocked,
        "thumbnail": thumbnail,
    }


async def _detect_tiktok_live(username: str) -> dict:
    """Compatibility wrapper used by the existing manual commands."""
    return await fetch_tiktok_live_page(username)


async def send_tiktok_live_notification(channel, username: str, thumbnail: str = None):
    """Send the requested @everyone TikTok LIVE notification."""
    live_url = f"https://www.tiktok.com/@{username}/live"

    embed = discord.Embed(
        title=f"🔴 @{username} sedang LIVE di TikTok!",
        description=f"**[Username]**: @{username}\n\n👇 **Klik untuk masuk ke LIVE**\n{live_url}",
        url=live_url,
        color=discord.Color.from_rgb(254, 44, 85),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    if thumbnail:
        try:
            embed.set_image(url=thumbnail)
        except Exception:
            pass

    embed.set_footer(text="Asisten Lurah BFL • TikTok Live")

    # Discord will only actually ping @everyone if the bot has
    # Mention Everyone permission in the target channel/server.
    content = f"@everyone **@{username} Lagi live nih guys...**"
    allowed_mentions = discord.AllowedMentions(
        everyone=True,
        users=False,
        roles=False,
        replied_user=False
    )

    await channel.send(
        content=content,
        embed=embed,
        allowed_mentions=allowed_mentions
    )


@bot.command(name="settiktok")
async def set_tiktok_username(ctx, username: str = None):
    """!settiktok <username> → kompatibilitas: set akun TikTok tunggal."""
    if not is_admin(ctx.author):
        return await ctx.send(
            "❌ Hanya **Admin / Owner** yang bisa mengatur username TikTok.",
            delete_after=8
        )

    if not username:
        settings = load_tiktok_settings()
        names = get_tiktok_usernames(settings)
        channel = get_tiktok_channel()
        if names:
            listed = ", ".join(f"@{x}" for x in names)
            return await ctx.send(
                f"ℹ️ TikTok aktif: **{listed}**\n"
                f"📢 Channel notif: {channel.mention if channel else '`belum ditemukan`'}"
            )
        return await ctx.send(
            "❌ Belum ada username. Gunakan `!tiktok add <username>`.",
            delete_after=8
        )

    username = normalize_tiktok_username(username)
    settings = load_tiktok_settings()
    settings["usernames"] = {
        username: {"is_live": False}
    }
    save_tiktok_settings(settings)
    save_last_tiktok({})
    await ctx.send(
        f"✅ Sekarang hanya memantau TikTok **@{username}**.\n"
        f"Gunakan `!tiktok add <username>` untuk menambah akun lain."
    )


@bot.group(name="tiktok", invoke_without_command=True)
async def tiktok_group(ctx):
    """Menu pengaturan TikTok via Discord."""
    if ctx.invoked_subcommand is None:
        await ctx.send(
            "**📱 TikTok Notification Manager**\n"
            "`!tiktok add [user1 user2 ...]` — tambah akun (bisa banyak, satu per baris)\n"
            "`!tiktok remove <user1 user2 ...>` — hapus akun (bisa banyak)\n"
            "`!tiktok list` — lihat semua akun\n"
            "`!tiktok channel #channel` — ubah channel notif\n"
            "`!tiktok channel` — lihat channel notif sekarang\n"
            "`!tiktok test <username>` — tes notif + thumbnail\n"
            "`!tiktok sync` — sinkronkan status live\n"
            "`!tiktok check` — cek status semua akun"
        )


def _parse_tiktok_usernames(text: str):
    """Pecah input jadi daftar username (pisah: baris baru, spasi, koma, titik koma).
    Return (valid, invalid). Duplikat di input otomatis dibuang."""
    valid, invalid, seen = [], [], set()
    for raw in re.split(r"[\s,;]+", text or ""):
        if not raw.strip():
            continue
        name = normalize_tiktok_username(raw)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        if re.fullmatch(r"[A-Za-z0-9._-]{1,100}", name):
            valid.append(name)
        else:
            invalid.append(raw.strip())
    return valid, invalid


@tiktok_group.command(name="add")
async def tiktok_add(ctx, *, usernames_text: str = None):
    """!tiktok add            -> bot minta input (boleh banyak baris)
    !tiktok add a b c         -> tambah beberapa akun sekaligus
    !tiktok add <baris baru>  -> satu username per baris"""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)

    # ── Mode interaktif: tanpa argumen ──
    if not usernames_text:
        await ctx.send(
            f"{ctx.author.mention} 📝 Silahkan input username TikTok.\n"
            f"Boleh **banyak sekaligus**, satu username per baris, contoh:\n"
            f"```\nAaaaa\nKhiara\nBenii\nZoiii\n```"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            reply = await bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send(
                f"{ctx.author.mention} ⏰ Waktu habis. Ketik `!tiktok add` lagi untuk mulai ulang.",
                delete_after=10
            )
        usernames_text = reply.content

    valid, invalid = _parse_tiktok_usernames(usernames_text)
    if not valid:
        return await ctx.send(
            "❌ Tidak ada username valid. Contoh: `!tiktok add Aaaaa Khiara Benii`",
            delete_after=10
        )

    settings  = load_tiktok_settings()
    usernames = settings["usernames"]
    existing  = {k.lower() for k in usernames}

    added, skipped = [], []
    for name in valid:
        if name.lower() in existing:
            skipped.append(name)
        else:
            usernames[name] = {"is_live": False}
            existing.add(name.lower())
            added.append(name)

    if added:
        save_tiktok_settings(settings)

    lines = []
    if added:
        lines.append(f"✅ **{len(added)}** akun ditambahkan:\n" + "\n".join(f"• @{n}" for n in added))
    if skipped:
        lines.append(f"⚠️ **{len(skipped)}** sudah ada (dilewati): " + ", ".join(f"@{n}" for n in skipped))
    if invalid:
        lines.append(f"❌ **{len(invalid)}** tidak valid: " + ", ".join(f"`{n}`" for n in invalid))
    lines.append(f"👥 Total dipantau: **{len(usernames)}** akun.")
    await ctx.send("\n".join(lines))


@tiktok_group.command(name="remove", aliases=["delete", "del"])
async def tiktok_remove(ctx, *, usernames_text: str = None):
    """!tiktok remove a b c  (atau satu username per baris)"""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)
    if not usernames_text:
        return await ctx.send(
            "❌ Format: `!tiktok remove <username>` (boleh banyak, pisah spasi/baris baru)",
            delete_after=8
        )

    valid, invalid = _parse_tiktok_usernames(usernames_text)
    if not valid:
        return await ctx.send("❌ Tidak ada username valid.", delete_after=8)

    settings  = load_tiktok_settings()
    usernames = settings["usernames"]
    lower_map = {k.lower(): k for k in usernames}

    removed, not_found = [], []
    for name in valid:
        real = lower_map.get(name.lower())
        if real is None:
            not_found.append(name)
        else:
            del usernames[real]
            removed.append(real)

    if removed:
        save_tiktok_settings(settings)
        last_data = load_last_tiktok()
        videos = last_data.get("videos", {}) if isinstance(last_data, dict) else {}
        for real in removed:
            videos.pop(real, None)
        save_last_tiktok({"videos": videos})

    lines = []
    if removed:
        lines.append(f"🗑️ **{len(removed)}** akun dihapus:\n" + "\n".join(f"• @{n}" for n in removed))
    if not_found:
        lines.append(f"❌ **{len(not_found)}** tidak ada di daftar: " + ", ".join(f"@{n}" for n in not_found))
    if invalid:
        lines.append(f"❌ **{len(invalid)}** tidak valid: " + ", ".join(f"`{n}`" for n in invalid))
    lines.append(f"👥 Sisa dipantau: **{len(usernames)}** akun.")
    await ctx.send("\n".join(lines))


@tiktok_group.command(name="list", aliases=["ls"])
async def tiktok_list(ctx):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)

    settings = load_tiktok_settings()
    usernames = settings.get("usernames", {})
    channel = get_tiktok_channel()

    embed = discord.Embed(
        title="📱 Daftar TikTok yang Dipantau",
        color=discord.Color.from_rgb(254, 44, 85),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    if usernames:
        lines = []
        for i, (name, state) in enumerate(usernames.items(), 1):
            status = "🔴 LIVE" if state.get("is_live", False) else "⚫ Offline"
            lines.append(f"**{i}.** @{name} — {status}")
        embed.description = "\n".join(lines)
    else:
        embed.description = "Belum ada username TikTok."

    embed.add_field(
        name="📢 Channel Notif",
        value=channel.mention if channel else "❌ Tidak ditemukan",
        inline=False
    )
    embed.set_footer(text="Kelola dengan !tiktok add/remove/channel")
    await ctx.send(embed=embed)


@tiktok_group.command(name="channel")
async def tiktok_channel(ctx, channel: discord.TextChannel = None):
    """Set channel notif langsung dari Discord, tanpa edit source code."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)

    settings = load_tiktok_settings()

    if channel is None:
        current = get_tiktok_channel()
        return await ctx.send(
            f"📢 Channel TikTok saat ini: "
            f"{current.mention if current else '❌ belum ditemukan'}"
        )

    settings["channel_id"] = str(channel.id)
    save_tiktok_settings(settings)

    await ctx.send(
        f"✅ Channel notif TikTok diubah ke {channel.mention}.\n"
        "Mulai sekarang notif LIVE dan posting TikTok akan dikirim ke sana."
    )


@tiktok_group.command(name="test")
async def tiktok_test(ctx, username: str = None):
    """Tes notif live dan thumbnail tanpa mengubah status."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)
    if not username:
        return await ctx.send("❌ Format: `!tiktok test <username>`", delete_after=8)

    username = normalize_tiktok_username(username)
    channel = get_tiktok_channel()
    if not channel:
        return await ctx.send(
            "❌ Channel notif belum ditemukan. Set dengan `!tiktok channel #channel`."
        )

    try:
        result = await _detect_tiktok_live(username)
    except Exception as e:
        return await ctx.send(f"❌ Gagal mengambil halaman TikTok: `{e}`")

    # Test intentionally sends the notification even when offline.
    await send_tiktok_live_notification(channel, username, result.get("thumbnail"))
    thumb_status = "✅ ditemukan" if result.get("thumbnail") else "⚠️ tidak ditemukan"
    await ctx.send(
        f"🧪 Test notif **@{username}** terkirim ke {channel.mention}.\n"
        f"🖼️ Thumbnail: {thumb_status}"
    )


@tiktok_group.command(name="check")
async def tiktok_check(ctx):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)

    settings = load_tiktok_settings()
    usernames = get_tiktok_usernames(settings)
    if not usernames:
        return await ctx.send("❌ Belum ada username TikTok.")

    msg = await ctx.send(f"🔎 Mengecek **{len(usernames)}** akun TikTok...")
    results = []

    for username in usernames:
        try:
            result = await _detect_tiktok_live(username)
            results.append(
                f"**@{username}** → "
                f"{'🔴 LIVE' if result['is_live'] else '⚫ Offline'}"
                + (" · ⚠️ TikTok challenge/block" if result["blocked"] else "")
            )
        except Exception as e:
            results.append(f"**@{username}** → ❌ `{e}`")

    await msg.edit(content="\n".join(results))


@tiktok_group.command(name="sync")
async def tiktok_sync(ctx):
    """Sinkronkan semua akun; kirim notif jika terdeteksi baru LIVE."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya Admin / Owner.", delete_after=8)

    settings = load_tiktok_settings()
    usernames = list(settings.get("usernames", {}).keys())
    channel = get_tiktok_channel()

    if not usernames:
        return await ctx.send("❌ Belum ada username TikTok.")
    if not channel:
        return await ctx.send("❌ Channel notif tidak ditemukan.")

    sent = 0
    for username in usernames:
        try:
            result = await _detect_tiktok_live(username)
            was_live = settings["usernames"][username].get("is_live", False)
            settings["usernames"][username]["is_live"] = result["is_live"]

            if result["is_live"] and not was_live:
                await send_tiktok_live_notification(
                    channel, username, result.get("thumbnail")
                )
                sent += 1
        except Exception as e:
            print(f"[TikTokSync] @{username}: {e}")

    save_tiktok_settings(settings)
    await ctx.send(f"✅ Sinkronisasi selesai. Notif baru dikirim: **{sent}**.")




TIKTOK_LIVE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Dest": "document",
    "Referer": "https://www.tiktok.com/",
}


@tasks.loop(minutes=5)
async def check_tiktok_live():
    settings = load_tiktok_settings()
    usernames = list(settings.get("usernames", {}).keys())
    channel = get_tiktok_channel()

    if not usernames or not channel:
        return

    for username in usernames:
        try:
            result = await _detect_tiktok_live(username)
            is_live_now = result["is_live"]
            was_live = settings["usernames"][username].get("is_live", False)

            if result["blocked"]:
                print(
                    f"[TikTokLive] Kemungkinan diblokir/di-challenge TikTok "
                    f"untuk @{username} (html_len={result['html_len']})"
                )

            if is_live_now and not was_live:
                settings["usernames"][username]["is_live"] = True
                save_tiktok_settings(settings)

                await send_tiktok_live_notification(
                    channel,
                    username,
                    result.get("thumbnail")
                )

            elif not is_live_now and was_live:
                settings["usernames"][username]["is_live"] = False
                save_tiktok_settings(settings)

        except Exception as e:
            print(f"[TikTokLive] @{username}: {e}")


@check_tiktok_live.before_loop
async def before_check_tiktok_live():
    await bot.wait_until_ready()


@bot.command(name="checklive")
async def check_live_manual(ctx, username: str = None):
    """!checklive [username] → Cek status live TikTok sekarang + diagnostik."""
    if not is_admin(ctx.author):
        return await ctx.send(
            "❌ Hanya **Admin / Owner** yang bisa pakai ini.",
            delete_after=8
        )

    settings = load_tiktok_settings()
    usernames = [normalize_tiktok_username(username)] if username else get_tiktok_usernames(settings)

    if not usernames:
        return await ctx.send(
            "❌ Belum ada username TikTok. Pakai `!tiktok add <username>`.",
            delete_after=8
        )

    lines = []
    for name in usernames:
        try:
            result = await _detect_tiktok_live(name)
            lines.append(
                f"**@{name}**\n"
                f"• HTTP: `{result['status_code']}`\n"
                f"• Final path: `{result['final_path']}`\n"
                f"• HTML: `{result['html_len']}`\n"
                f"• status:2 LIVE: `{result['matched_status2']}`\n"
                f"• status:4 OFFLINE: `{result['matched_status4']}`\n"
                f"• Challenge/block: `{result['blocked']}`\n"
                f"• Thumbnail: `{'ada' if result.get('thumbnail') else 'tidak ada'}`\n"
                f"• **Deteksi: {'🔴 LIVE' if result['is_live'] else '⚫ Tidak live'}**"
            )
        except Exception as e:
            lines.append(f"**@{name}** → ❌ `{e}`")

    await ctx.send("\n\n".join(lines))


@bot.command(name="synclive")
async def sync_live_manual(ctx, username: str = None):
    """!synclive [username] → sinkronkan status dan kirim notif bila baru live."""
    if not is_admin(ctx.author):
        return await ctx.send(
            "❌ Hanya **Admin / Owner** yang bisa pakai ini.",
            delete_after=8
        )

    settings = load_tiktok_settings()
    usernames = [normalize_tiktok_username(username)] if username else list(settings.get("usernames", {}).keys())
    channel = get_tiktok_channel()

    if not usernames:
        return await ctx.send(
            "❌ Belum ada username TikTok. Pakai `!tiktok add <username>`."
        )
    if not channel:
        return await ctx.send(
            "❌ Channel notif tidak ditemukan. Pakai `!tiktok channel #channel`."
        )

    sent = 0
    for name in usernames:
        # Add manually requested account to settings if it does not exist.
        if name not in settings["usernames"]:
            settings["usernames"][name] = {"is_live": False}

        try:
            result = await _detect_tiktok_live(name)
            was_live = settings["usernames"][name].get("is_live", False)
            settings["usernames"][name]["is_live"] = result["is_live"]

            if result["is_live"] and not was_live:
                await send_tiktok_live_notification(
                    channel, name, result.get("thumbnail")
                )
                sent += 1
        except Exception as e:
            print(f"[TikTokSync] @{name}: {e}")

    save_tiktok_settings(settings)
    await ctx.send(
        f"✅ State TikTok disinkronkan. "
        f"Notif baru dikirim: **{sent}**."
    )


# ═══════════════════════════════════════════════════════
#  COMMANDS — WARN
# ═══════════════════════════════════════════════════════
@bot.command(name="warn")
async def warn(ctx, member: discord.Member = None, *, alasan="Tidak ada alasan"):
    if not is_moderator(ctx.author):
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
        "waktu": str(datetime.datetime.now(datetime.timezone.utc))
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
    if not is_moderator(ctx.author):
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
        "since": str(datetime.datetime.now(datetime.timezone.utc))
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
        end_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)
        gid      = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
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
        color=discord.Color.blue(), timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_footer(text="Asisten Lurah BFL")
    await channel.send("@everyone", embed=embed)
    await ctx.send(f"✅ Dikirim ke #{channel.name}!")

# ═══════════════════════════════════════════════════════
#  COMMANDS — MODERASI
# ═══════════════════════════════════════════════════════
@bot.command(name="timeout")
async def timeout_member(ctx, member: discord.Member = None, durasi: int = None, *, alasan="Tidak ada alasan"):
    if not is_moderator(ctx.author):
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
    if not is_moderator(ctx.author):
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
    if not is_moderator(ctx.author):
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
    if not is_moderator(ctx.author):
        return await ctx.send("❌ Kamu tidak punya izin untuk command ini.")
    if isinstance(ctx.channel, discord.DMChannel):
        return await ctx.send("❌ Command ini hanya bisa digunakan di server.")
    await ctx.channel.purge(limit=jumlah+1)
    await ctx.send(f"✅ **{jumlah}** pesan dihapus.", delete_after=5)

@clear_messages.error
async def clear_error(ctx, error): await ctx.send(f"❌ Error: {error}")

# ═══════════════════════════════════════════════════════
#  MODERATOR ACCESS (akses terbatas: !warn, !timeout, !ban, !unban, !clear)
# ═══════════════════════════════════════════════════════
@bot.command(name="addmod")
async def add_moderator(ctx, member: discord.Member = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner** yang bisa menambah moderator.", delete_after=8)
    if member is None:
        return await ctx.send("❌ Format: `!addmod @user`", delete_after=8)
    mods = load_moderators()
    if member.id in mods:
        return await ctx.send(f"⚠️ {member.mention} sudah jadi moderator.", delete_after=8)
    mods.append(member.id)
    save_moderators(mods)
    await ctx.send(f"✅ {member.mention} sekarang punya akses moderasi (`!warn`, `!timeout`, `!ban`, `!unban`, `!clear`).")

@bot.command(name="removemod")
async def remove_moderator(ctx, member: discord.Member = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner** yang bisa menghapus moderator.", delete_after=8)
    if member is None:
        return await ctx.send("❌ Format: `!removemod @user`", delete_after=8)
    mods = load_moderators()
    if member.id not in mods:
        return await ctx.send(f"❌ {member.mention} tidak ada di daftar moderator.", delete_after=8)
    mods.remove(member.id)
    save_moderators(mods)
    await ctx.send(f"🗑️ Akses moderasi {member.mention} telah dicabut.")

@bot.command(name="modlist", aliases=["listmod"])
async def list_moderators(ctx):
    mods = load_moderators()
    if not mods:
        return await ctx.send("📋 Belum ada moderator yang ditambahkan.")
    lines = []
    for uid in mods:
        member = ctx.guild.get_member(uid) if ctx.guild else None
        lines.append(f"• {member.mention if member else f'`{uid}`'}")
    embed = discord.Embed(
        title="🛡️ Daftar Moderator",
        description="\n".join(lines),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Akses: !warn · !warnlist · !clearwarn · !timeout · !ban · !unban · !clear")
    await ctx.send(embed=embed)

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
# ═══════════════════════════════════════════════════════
#  COMMANDS — HELP (menu tombol per fitur)
# ═══════════════════════════════════════════════════════
class HelpView(View):
    """Menu help: tombol = nama fitur. Tekan tombol -> tampil command fitur itu,
    tombol 'Kembali ke Menu' -> balik ke daftar fitur."""
    PER_ROW = 3

    def __init__(self, author_id, categories, title, intro, color, footer):
        super().__init__(timeout=180)
        self.author_id  = author_id
        self.categories = categories
        self.title      = title
        self.intro      = intro
        self.color      = color
        self.footer     = footer
        self.message    = None
        self._show_menu_buttons()

    def menu_embed(self) -> discord.Embed:
        e = discord.Embed(title=self.title, description=self.intro, color=self.color)
        e.set_footer(text=self.footer)
        return e

    def _show_menu_buttons(self):
        self.clear_items()
        for i, (key, (emoji, label, _text)) in enumerate(self.categories.items()):
            btn = Button(label=label, emoji=emoji,
                         style=discord.ButtonStyle.secondary,
                         row=i // self.PER_ROW)
            btn.callback = self._make_open_callback(key)
            self.add_item(btn)

    def _make_open_callback(self, key):
        async def callback(interaction: discord.Interaction):
            emoji, label, text = self.categories[key]
            embed = discord.Embed(title=f"{emoji} {label}", description=text, color=self.color)
            embed.set_footer(text=self.footer)
            self.clear_items()
            back = Button(label="Kembali ke Menu", emoji="⬅️", style=discord.ButtonStyle.primary)
            back.callback = self._back_callback
            self.add_item(back)
            await interaction.response.edit_message(embed=embed, view=self)
        return callback

    async def _back_callback(self, interaction: discord.Interaction):
        self._show_menu_buttons()
        await interaction.response.edit_message(embed=self.menu_embed(), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Menu ini milik orang lain. Ketik `!help` sendiri ya.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.edit(view=None)
            except Exception:
                pass


# key -> (emoji, label tombol, isi command)
HELP_MEMBER = {
    "voice": ("🎙️", "Voice Room", """
`!createroom [nama]` — Buat voice room pribadi
📌 Room auto-hapus saat kosong, maks 10 orang
""".strip()),
    "afk": ("💤", "AFK", """
`!afk [alasan]` — Set status AFK
📌 Status hilang otomatis saat kamu kirim pesan
""".strip()),
    "nick": ("✏️", "Nickname", """
`!nick <nickname baru>` — Ganti nickname kamu
`!nick reset` — Reset nickname ke nama asli
""".strip()),
    "poll": ("📊", "Polling", """
`!poll <menit> <pertanyaan> | <opsi1> | <opsi2>` — Buat poll
Contoh: `!poll 10 Warna favorit? | Merah | Biru | Hijau`
`!pollresult <id>` — Lihat hasil poll
""".strip()),
    "remind": ("⏰", "Reminder", """
`!reminder <10s/5m/2h/1d> <pesan>` — Set pengingat
Alias: `!remind` / `!ingatkan`
""".strip()),
    "absen": ("📝", "Absen & Setoran", """
`!absen` — Isi absen (Nama, Reason, Berapa Lama)
`!setoran <nama> <jumlah>` — Catat setoran metalscrap
`!setoranlist [lalu]` — Rekap setoran minggu ini / lalu
`!setoranbulan [lalu/bulan]` — Total setoran sebulan
`!setoranriwayat [nama] [hal]` — Riwayat input setoran
""".strip()),
    "util": ("🔎", "Info & Utilitas", """
`!ping` — Cek latensi bot & koneksi
`!cekid [@user]` — Cek Discord ID (`!myid`/`!idku`)
`!roleinfo @role` — Info role (`!inforole`/`!cekrole`)
`!listrole` — Daftar role + jumlah member
`!serverinfo` — Info server (`!server`/`!sinfo`)
`!snipe` — Pesan terakhir yang dihapus (`!sn`)
""".strip()),
}

HELP_ADMIN = {
    "mod": ("⚠️", "Moderasi", """
`!warn @user [alasan]` — Beri peringatan (auto-kick warn ke-3)
`!warnlist @user` — Lihat semua warn user
`!clearwarn @user` — Hapus semua warn user
`!timeout @user <menit> [alasan]` — Timeout member
`!ban @user [alasan]` — Ban member
`!unban <user_id>` — Unban via ID
`!clear [n]` / `!purge` / `!hapus` — Hapus n pesan (default 10)
""".strip()),
    "role": ("🎭", "Role", """
`!giverole @role @user` — Beri role (`!berirole`)
`!cabutrole @user @role1 @role2` — Cabut banyak role (`!delrole`)
`!addrole @user <nama_role>` — Tambah role ke member
`!removerole @user <nama_role>` — Hapus role dari member
`!roleinfo @role` — Info detail role
`!listrole` — Semua role + jumlah member
""".strip()),
    "trial": ("⏳", "Trial Role", """
`!trialrole @user @role <durasi>` — Beri role sementara
Durasi: `30m`, `12h`, `3d`, `1w`, `1d12h`
`!trialrole list [@user]` — Daftar trial aktif
`!trialrole cancel @user [@role]` — Hentikan trial sekarang
📌 Role otomatis dicabut saat masa trial habis
""".strip()),
    "automod": ("🛡️", "Automod", """
`!automod on/off` — Aktif/nonaktifkan
`!automod threshold <n>` — Batas pesan spam (default 5)
`!automod interval <detik>` — Jendela waktu (default 5)
`!automod mute <detik>` — Durasi timeout (default 60)
`!automod status` — Lihat pengaturan
""".strip()),
    "banword": ("🚫", "Banword & Log", """
`!banword add #channel kata1, kata2` — Ban di channel tertentu
`!banword add all kata1, kata2` — Ban di semua channel
`!banword remove #channel kata` — Hapus kata
`!banword list #channel` — Lihat ban word
`!banword clear #channel` — Kosongkan ban word
`!setlogchannel #channel` / `off` — Log pesan terhapus
📌 Tanpa `#channel` = channel tempat command dipakai
📌 `*kata*` = cocok di dalam kata
""".strip()),
    "tiktok": ("🎵", "TikTok", """
`!tiktok add` — Bot minta input, **bisa banyak username** (satu per baris)
`!tiktok add user1 user2` — Tambah banyak akun sekaligus
`!tiktok remove user1 user2` — Hapus satu/banyak akun
`!tiktok list` — Lihat semua akun (`ls`)
`!tiktok channel [#channel]` — Set/lihat channel notif
`!tiktok test <username>` — Tes notif + thumbnail
`!tiktok check` / `!tiktok sync` — Cek / sinkron status live
`!settiktok <username>` — Set akun tunggal
`!checklive [username]` — Cek status live + diagnostik
`!synclive [username]` — Sinkron & kirim notif bila baru live
""".strip()),
    "setoran": ("💰", "Setoran", """
`!setoran hapus <nama>` — Hapus entri setoran minggu ini
`!setoran reset` — Kosongkan rekap minggu ini
📌 Total bulan & riwayat tetap tersimpan
📌 Command setoran lain: lihat `!help`
""".strip()),
    "giveaway": ("🎉", "Giveaway", """
**Giveaway** *(DM)*
`!setgiveaway <channel_id>` — Buat giveaway baru
📌 Bot tanya durasi (`1h`, `30m`, `2d`) lalu hadiah
📌 Auto undi pemenang & DM pemenang

**Pengumuman** *(DM)*
`!pengumuman <channel_id> <pesan>` — Kirim pengumuman @everyone
""".strip()),
    "ticket": ("🎫", "Ticket", """
`!setupticket` — Pasang panel ticket di TICKET_CHANNEL
📌 Member klik tombol → buat ticket privat
""".strip()),
    "reactrole": ("🏷️", "React Role", """
`!addreactrole #channel <msg_id> <emoji> @role` — Tambah react role
`!removereactrole <msg_id> <emoji>` — Hapus react role
`!listreactrole` — Daftar react role aktif
""".strip()),
    "welcome": ("👋", "Welcome & Leave", """
`!setwelcome #channel` — Set channel welcome card
`!setleave #channel` — Set channel leave message
`!welcometest` — Test welcome card
`!leavetest` — Test leave message
""".strip()),
    "pollnick": ("📊", "Poll & Nickname", """
`!poll <menit> <pertanyaan> | <opsi1> | <opsi2>` — Buat poll
`!endpoll <id>` — Akhiri poll lebih cepat
`!pollresult <id>` — Lihat hasil poll
`!setnick @user <nick>` — Atur nickname orang lain
`!nick <nick>` / `!nick reset` — Nickname sendiri
""".strip()),
    "user": ("👤", "User & Moderator", """
`!userinfo [@user]` — Info lengkap user (`!cekuser`)
📌 Kapan join, profil, warn, dan roles

**Akses Moderator**
`!addmod @user` — Beri akses command moderasi
`!removemod @user` — Cabut akses moderasi
`!modlist` / `!listmod` — Daftar moderator
""".strip()),
    "util": ("🔎", "Utilitas", """
`!ping` — Latensi bot & koneksi
`!cekid [@user]` — Cek Discord ID
`!serverinfo` — Info server
`!snipe` — Pesan terakhir yang dihapus
`!avatar [@user]` — Avatar ukuran penuh (`!av`/`!pp`/`!foto`)
`!autoreply` / `!ar` — Kelola auto reply via DM
""".strip()),
    "backup": ("💾", "Backup", """
`!savesettings` — Simpan semua setting & data ke channel backup
`!loadsettings` — Load dari backup terakhir (menimpa data sekarang)
📌 Auto-backup berkala & auto-load saat bot deploy ulang
""".strip()),
}


@bot.command(name="help")
async def help_cmd(ctx):
    view = HelpView(
        author_id=ctx.author.id,
        categories=HELP_MEMBER,
        title="📖 Asisten Lurah BFL — Help",
        intro="Tekan tombol fitur di bawah untuk melihat command-nya.\nPrefix: `!`",
        color=discord.Color.blue(),
        footer="Asisten Lurah BFL • Command admin: !helpadmin",
    )
    view.message = await ctx.send(embed=view.menu_embed(), view=view)


@bot.command(name="helpadmin", aliases=["adminhelp"])
async def help_admin_cmd(ctx):
    # Resolve author sebagai Member (bukan User) agar guild_permissions tersedia
    author = ctx.author
    if isinstance(ctx.channel, discord.DMChannel):
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

    view = HelpView(
        author_id=ctx.author.id,
        categories=HELP_ADMIN,
        title="🛡️ Admin Help — Asisten Lurah BFL",
        intro="Tekan tombol fitur di bawah untuk melihat command-nya.\n"
              "Hanya untuk Admin/Owner • *(DM)* = bisa dipakai di DM bot",
        color=discord.Color.red(),
        footer="Asisten Lurah BFL • Hanya Admin/Owner • Command member: !help",
    )
    view.message = await ctx.send(embed=view.menu_embed(), view=view)


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
            until = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=mute_dur)
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
            timestamp=datetime.datetime.now(datetime.timezone.utc)
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
    jt[str(member.id)] = member.joined_at.isoformat() if member.joined_at else datetime.datetime.now(datetime.timezone.utc).isoformat()
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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
    sisa    = end_dt - datetime.datetime.now(datetime.timezone.utc)
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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

    poll_id  = str(int(datetime.datetime.now(datetime.timezone.utc).timestamp()))
    end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=duration)).isoformat()

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

    # Join server
    jt_data = load_join_tracking()
    if uid in jt_data:
        try:
            join_dt  = datetime.datetime.fromisoformat(jt_data[uid])
            join_str = f"<t:{int(join_dt.timestamp())}:F>"
        except Exception:
            join_str = "Tidak diketahui"
    elif member.joined_at:
        join_str = f"<t:{int(member.joined_at.timestamp())}:F>"
    else:
        join_str = "Tidak diketahui"

    created_str = f"<t:{int(member.created_at.timestamp())}:F>"

    top_color   = member.top_role.color
    color       = top_color if top_color != discord.Color.default() else discord.Color.from_rgb(88, 101, 242)

    embed = discord.Embed(color=color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_author(name=str(member), icon_url=member.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID",               value=f"`{member.id}`",          inline=True)
    embed.add_field(name="\u200b",               value="\u200b",                  inline=True)
    embed.add_field(name="📅 Bergabung Server",  value=join_str,                  inline=True)
    embed.add_field(name="🗓️ Akun Dibuat",       value=created_str,               inline=True)
    embed.add_field(name="\u200b",               value="\u200b",                  inline=True)
    embed.set_footer(text=f"Diminta oleh {ctx.author.display_name}",
                     icon_url=ctx.author.display_avatar.url)
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
                           timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="👤 Member",  value=f"{member} (`{member.id}`)", inline=True)
    embed.add_field(name="🎭 Role",    value=f"{role.mention} (`{role.id}`)", inline=True)
    embed.add_field(name="🛡️ Admin",  value=f"{actor.mention}", inline=True)
    embed.set_footer(text=f"ID Role: {role.id}  •  ID Member: {member.id}",
                     icon_url=actor.display_avatar.url)
    return embed

# ── !giverole ──────────────────────────────────────────
@bot.command(name="giverole", aliases=["berirole"])
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
                "**Alias:** `!berirole`"
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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
                timestamp=datetime.datetime.now(datetime.timezone.utc)
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
@bot.command(name="cabutrole", aliases=["delrole"])
@commands.guild_only()
async def cabutrole_cmd(ctx, member: discord.Member = None, *, roles_input: str = None):
    """Admin: cabut satu atau lebih role dari user.
    Format  : !cabutrole @user @role1 @role2 ...
    Contoh  : !cabutrole @Budi @VIP @Trusted
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan command ini.", delete_after=5)

    if member is None or roles_input is None:
        embed = discord.Embed(
            title="📖 Cara Pakai — !cabutrole",
            description=(
                "Cabut satu atau beberapa role dari member sekaligus.\n\n"
                "**Format:**\n"
                "`!cabutrole @user @role1 @role2 ...`\n\n"
                "**Contoh:**\n"
                "`!cabutrole @Budi @VIP`\n"
                "`!cabutrole @Budi @VIP @Trusted`\n\n"
                "**Alias:** `!delrole`"
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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
                timestamp=datetime.datetime.now(datetime.timezone.utc)
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
        timestamp=datetime.datetime.now(datetime.timezone.utc)
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
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(
            text=f"Total {len(roles)} role  •  Halaman {page}/{total_page}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )
        await ctx.send(embed=embed)



# ═══════════════════════════════════════════════════════
#  !CEKID
# ═══════════════════════════════════════════════════════
@bot.command(name="cekid", aliases=["myid", "idku"])
async def cekid_cmd(ctx, member: discord.Member = None):
    """Cek Discord ID dan username. Format: !cekid atau !cekid @user"""
    target = member or ctx.author

    embed = discord.Embed(
        title="🆔 Discord ID",
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.add_field(name="👤 Username", value=f"`{target}`",    inline=True)
    embed.add_field(name="🆔 ID",       value=f"`{target.id}`", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  !ABSEN
# ═══════════════════════════════════════════════════════
@bot.command(name="absen")
async def absen_cmd(ctx):
    """Absen dengan mengisi Nama, Reason, dan Berapa Lama."""

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    messages_to_delete = [ctx.message]

    try:
        q1 = await ctx.send(f"{ctx.author.mention} Siapa **nama** kamu?")
        messages_to_delete.append(q1)

        jawaban_nama = await bot.wait_for("message", check=check, timeout=60)
        messages_to_delete.append(jawaban_nama)
        nama = jawaban_nama.content

        q2 = await ctx.send(f"{ctx.author.mention} Apa **alasan** absenmu?")
        messages_to_delete.append(q2)

        jawaban_reason = await bot.wait_for("message", check=check, timeout=60)
        messages_to_delete.append(jawaban_reason)
        reason = jawaban_reason.content

        q3 = await ctx.send(f"{ctx.author.mention} **Berapa lama** kamu akan absen?")
        messages_to_delete.append(q3)

        jawaban_lama = await bot.wait_for("message", check=check, timeout=60)
        messages_to_delete.append(jawaban_lama)
        berapa_lama = jawaban_lama.content

        # Hapus semua pesan satu per satu
        for msg in messages_to_delete:
            try:
                await msg.delete()
                await asyncio.sleep(0.3)
            except Exception:
                pass

        embed = discord.Embed(
            title="📋 Form Absen",
            color=discord.Color.orange(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        embed.add_field(name="Nama",        value=nama,        inline=False)
        embed.add_field(name="Reason",      value=reason,      inline=False)
        embed.add_field(name="Berapa Lama", value=berapa_lama, inline=False)
        embed.set_footer(
            text=f"{ctx.author.display_name} • {ctx.author.id}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

    except asyncio.TimeoutError:
        for msg in messages_to_delete:
            try:
                await msg.delete()
                await asyncio.sleep(0.3)
            except Exception:
                pass
        await ctx.send(
            f"{ctx.author.mention} ⏰ Waktu habis! Silakan ketik `!absen` lagi.",
            delete_after=10
        )


# ═══════════════════════════════════════════════════════
#  AUTO REPLY SYSTEM
# ═══════════════════════════════════════════════════════
AUTOREPLY_FILE = _p("autoreply.json")

def load_autoreply():
    if not os.path.exists(AUTOREPLY_FILE):
        return {}
    with open(AUTOREPLY_FILE, "r") as f:
        return json.load(f)

def save_autoreply(data):
    with open(AUTOREPLY_FILE, "w") as f:
        json.dump(data, f, indent=2)


@bot.command(name="autoreply", aliases=["ar"])
async def autoreply_cmd(ctx):
    """Kelola auto reply via DM. Hanya admin/owner."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa menggunakan perintah ini.", delete_after=5)

    def dm_check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

    # Kirim menu ke DM jika dari server
    if not isinstance(ctx.channel, discord.DMChannel):
        try:
            await ctx.message.delete()
        except Exception:
            pass
        await ctx.send("📩 Cek DM kamu ya!", delete_after=5)

    menu_text = (
        "📋 **Menu Auto Reply**\n\n"
        "Ketik salah satu:\n"
        "`tambah` — Tambah trigger baru\n"
        "`hapus`  — Hapus trigger\n"
        "`list`   — Lihat semua trigger\n"
        "`batal`  — Keluar"
    )
    await ctx.author.send(menu_text)

    try:
        pilihan = await bot.wait_for("message", check=dm_check, timeout=60)
        pilihan = pilihan.content.strip().lower()
        data = load_autoreply()

        if pilihan == "tambah":
            await ctx.author.send("✏️ Ketik **trigger** (kata/kalimat pemicu):")
            msg_trigger = await bot.wait_for("message", check=dm_check, timeout=60)
            trigger = msg_trigger.content.strip().lower()

            await ctx.author.send(f"✅ Trigger: `{trigger}`\n\n✏️ Sekarang ketik **jawaban** botnya:")
            msg_jawaban = await bot.wait_for("message", check=dm_check, timeout=120)
            jawaban = msg_jawaban.content.strip()

            data[trigger] = jawaban
            save_autoreply(data)
            await ctx.author.send(f"✅ Berhasil ditambahkan!\n\n**Trigger:** `{trigger}`\n**Jawaban:** {jawaban}")

        elif pilihan == "hapus":
            if not data:
                return await ctx.author.send("❌ Belum ada trigger yang tersimpan.")
            list_trigger = "\n".join([f"`{k}`" for k in data.keys()])
            await ctx.author.send(f"🗑️ Trigger yang ada:\n{list_trigger}\n\nKetik trigger yang ingin dihapus:")
            msg_hapus = await bot.wait_for("message", check=dm_check, timeout=60)
            hapus_key = msg_hapus.content.strip().lower()
            if hapus_key in data:
                del data[hapus_key]
                save_autoreply(data)
                await ctx.author.send(f"✅ Trigger `{hapus_key}` berhasil dihapus!")
            else:
                await ctx.author.send(f"❌ Trigger `{hapus_key}` tidak ditemukan.")

        elif pilihan == "list":
            if not data:
                return await ctx.author.send("❌ Belum ada trigger yang tersimpan.")
            lines = []
            for i, (k, v) in enumerate(data.items(), 1):
                preview = v[:50] + "..." if len(v) > 50 else v
                lines.append(f"**{i}.** `{k}` → {preview}")
            await ctx.author.send("📋 **Daftar Auto Reply:**\n\n" + "\n".join(lines))

        elif pilihan == "batal":
            await ctx.author.send("❎ Dibatalkan.")

        else:
            await ctx.author.send("❌ Pilihan tidak valid.")

    except asyncio.TimeoutError:
        await ctx.author.send("⏰ Waktu habis. Ketik `!autoreply` lagi untuk memulai.")



# ═══════════════════════════════════════════════════════
#  !PING — CEK LATENCY, PING, DAN KECEPATAN INTERNET
# ═══════════════════════════════════════════════════════
@bot.command(name="ping", aliases=["latency", "speed"])
async def ping_cmd(ctx):
    """Cek latency Discord + ping HTTP + download/upload speed internet server."""
    import time, urllib.request, urllib.error, os

    msg = await ctx.send("🏓 Mengukur koneksi...")

    ws_latency_ms = round(bot.latency * 1000, 2)

    def _speed_test():
        """Tes koneksi nyata dari server menggunakan endpoint Cloudflare Speed Test."""
        result = {
            "http_ping": None,
            "download_mbps": None,
            "upload_mbps": None,
            "download_bytes": 0,
            "upload_bytes": 0,
            "error": None,
        }
        errors = []

        # PENTING: Cloudflare memblokir User-Agent bawaan urllib ("Python-urllib/3.x")
        # dengan HTTP 403 -> semua tes gagal. Wajib kirim header browser.
        HEADERS = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
            "Accept": "*/*",
            "Origin": "https://speed.cloudflare.com",
            "Referer": "https://speed.cloudflare.com/",
        }

        def _err(label, e):
            code = getattr(e, "code", None)
            errors.append(f"{label}: {type(e).__name__}" + (f" {code}" if code else ""))

        # 1) HTTP latency — koneksi internet, bukan Discord WebSocket.
        try:
            ping_times = []
            for _ in range(3):
                req = urllib.request.Request(
                    "https://speed.cloudflare.com/__down?bytes=1", headers=HEADERS
                )
                t0 = time.perf_counter()
                with urllib.request.urlopen(req, timeout=10) as response:
                    response.read(1)
                ping_times.append((time.perf_counter() - t0) * 1000)
            result["http_ping"] = round(sum(ping_times) / len(ping_times), 2)
        except Exception as e:
            _err("HTTP ping", e)

        # 2) Download test — 5 MB supaya hasil tidak bias karena file terlalu kecil.
        try:
            req = urllib.request.Request(
                "https://speed.cloudflare.com/__down?bytes=5242880", headers=HEADERS
            )
            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
            elapsed = max(time.perf_counter() - t0, 0.001)
            result["download_bytes"] = len(data)
            result["download_mbps"] = round((len(data) * 8) / elapsed / 1_000_000, 2)
        except Exception as e:
            _err("Download", e)

        # 3) Upload test — kirim 2 MB ke endpoint upload Cloudflare.
        try:
            upload_data = os.urandom(2 * 1024 * 1024)
            req = urllib.request.Request(
                "https://speed.cloudflare.com/__up",
                data=upload_data,
                method="POST",
                headers={
                    **HEADERS,
                    "Content-Type": "text/plain;charset=UTF-8",
                    "Content-Length": str(len(upload_data)),
                },
            )
            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=30) as response:
                response.read()
            elapsed = max(time.perf_counter() - t0, 0.001)
            result["upload_bytes"] = len(upload_data)
            result["upload_mbps"] = round((len(upload_data) * 8) / elapsed / 1_000_000, 2)
        except Exception as e:
            _err("Upload", e)

        if errors:
            result["error"] = " | ".join(errors)
        return result

    try:
        # Jalankan tes blocking di thread agar event loop Discord tidak freeze.
        speed = await asyncio.to_thread(_speed_test)
    except Exception as e:
        speed = {"http_ping": None, "download_mbps": None, "upload_mbps": None, "error": str(e)}

    http_ping = speed.get("http_ping")
    download_mbps = speed.get("download_mbps")
    upload_mbps = speed.get("upload_mbps")

    def speed_quality(mbps):
        if mbps is None:
            return "⚠️ Gagal"
        if mbps >= 50:
            return "🟢 Cepat"
        if mbps >= 20:
            return "🟡 Cukup"
        if mbps >= 5:
            return "🟠 Sedang"
        return "🔴 Lambat"

    # Status keseluruhan
    if download_mbps is None and http_ping is None:
        status_text, color = "🔴 **Koneksi gagal diukur**", discord.Color.red()
    elif (download_mbps or 0) >= 20 and (http_ping or 0) < 200:
        status_text, color = "🟢 **Koneksi Stabil**", discord.Color.green()
    else:
        status_text, color = "🟠 **Koneksi Kurang Optimal**", discord.Color.orange()

    def _fmt(value, unit):
        return f"`{value} {unit}`" if value is not None else "`—`"

    embed = discord.Embed(
        title="🏓 Status Koneksi",
        description=status_text,
        color=color,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    # 3 kolom sejajar (kiri-tengah-kanan), tidak turun ke bawah
    embed.add_field(
        name="Latency",
        value=f"{_fmt(round(ws_latency_ms), 'ms')} Discord\n{_fmt(round(http_ping) if http_ping is not None else None, 'ms')} HTTP",
        inline=True
    )
    embed.add_field(
        name="Download",
        value=f"{_fmt(download_mbps, 'Mbps')}\n{speed_quality(download_mbps)}",
        inline=True
    )
    embed.add_field(
        name="Upload",
        value=f"{_fmt(upload_mbps, 'Mbps')}\n{speed_quality(upload_mbps)}",
        inline=True
    )
    if speed.get("error"):
        embed.add_field(name="Catatan", value=f"`{speed['error'][:200]}`", inline=False)
    embed.set_footer(text="Asisten Lurah BFL")
    await msg.edit(content=None, embed=embed)


# ═══════════════════════════════════════════════════════
#  FITUR TAMBAHAN 1 — !SERVERINFO
#  Tampilkan info lengkap server
# ═══════════════════════════════════════════════════════
@bot.command(name="serverinfo", aliases=["server", "sinfo"])
@commands.guild_only()
async def serverinfo_cmd(ctx):
    """Tampilkan informasi lengkap tentang server ini."""
    guild = ctx.guild

    # Hitung statistik member
    total       = guild.member_count
    bots        = sum(1 for m in guild.members if m.bot)
    humans      = total - bots
    online      = sum(1 for m in guild.members if m.status != discord.Status.offline and not m.bot)

    # Hitung channel
    text_ch  = len(guild.text_channels)
    voice_ch = len(guild.voice_channels)
    cat_ch   = len(guild.categories)

    created_ts = int(guild.created_at.timestamp())

    boost_level = guild.premium_tier
    boosts      = guild.premium_subscription_count or 0

    embed = discord.Embed(
        title=f"🏰 {guild.name}",
        description=guild.description or "Tidak ada deskripsi.",
        color=discord.Color.from_rgb(88, 101, 242),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.url)

    embed.add_field(name="🆔 Server ID",      value=f"`{guild.id}`",              inline=True)
    embed.add_field(name="👑 Owner",           value=f"{guild.owner.mention}",     inline=True)
    embed.add_field(name="📅 Dibuat",          value=f"<t:{created_ts}:F>",        inline=True)
    embed.add_field(name="👥 Total Member",    value=f"**{humans}** orang + **{bots}** bot", inline=True)
    embed.add_field(name="🟢 Online Sekarang", value=f"**{online}** orang",        inline=True)
    embed.add_field(name="🎭 Total Role",      value=f"**{len(guild.roles)-1}** role", inline=True)
    embed.add_field(name="💬 Channel Teks",    value=str(text_ch),                 inline=True)
    embed.add_field(name="🔊 Channel Voice",   value=str(voice_ch),                inline=True)
    embed.add_field(name="📁 Kategori",        value=str(cat_ch),                  inline=True)
    embed.add_field(
        name="🚀 Boost Server",
        value=f"Level **{boost_level}** · **{boosts}** boost",
        inline=True
    )
    embed.add_field(
        name="🌍 Region / Verifikasi",
        value=f"`{str(guild.verification_level).title()}`",
        inline=True
    )
    embed.set_footer(
        text=f"Diminta oleh {ctx.author.display_name} • Asisten Lurah BFL",
        icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  FITUR TAMBAHAN 2 — !AVATAR
#  Tampilkan avatar user dalam ukuran besar
# ═══════════════════════════════════════════════════════
@bot.command(name="avatar", aliases=["av", "pp", "foto"])
async def avatar_cmd(ctx, member: discord.Member = None):
    """Tampilkan avatar user dalam ukuran penuh. (Admin only)
    Gunakan: !avatar atau !avatar @user
    """
    if not is_admin(ctx.author):
        return await ctx.send("❌ Command ini hanya untuk **Admin / Owner**.", delete_after=8)
    target = member or ctx.author
    formats = []
    base_url = str(target.display_avatar.url)

    # Buat link berbagai format
    for fmt in ["png", "jpg", "webp"]:
        url = target.display_avatar.with_format(fmt).with_size(1024).url
        formats.append(f"[{fmt.upper()}]({url})")
    if target.display_avatar.is_animated():
        gif_url = target.display_avatar.with_format("gif").with_size(1024).url
        formats.append(f"[GIF]({gif_url})")

    embed = discord.Embed(
        title=f"🖼️ Avatar — {target.display_name}",
        description=" • ".join(formats),
        color=discord.Color.blurple(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_image(url=target.display_avatar.with_size(1024).url)
    embed.set_footer(
        text=f"Diminta oleh {ctx.author.display_name} • Asisten Lurah BFL",
        icon_url=ctx.author.display_avatar.url
    )
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  FITUR TAMBAHAN 3 — !SNIPE
#  Tampilkan pesan terakhir yang dihapus di channel
# ═══════════════════════════════════════════════════════
_snipe_cache: dict = {}  # channel_id -> {"content", "author", "created_at"}

_bot_deleted_ids: dict = {}  # message_id -> alasan (pesan yang dihapus oleh bot sendiri)

def load_logcfg():   return load_json(LOGCFG_FILE, default={"delete_log_channel": 0})
def save_logcfg(d):  save_json(LOGCFG_FILE, d)

@bot.event
async def on_message_delete(message):
    """Cache pesan terhapus untuk !snipe + kirim log ke channel log (kalau sudah di-set)."""
    if message.guild is None or message.author.bot:
        return
    if message.content:
        _snipe_cache[message.channel.id] = {
            "content":    message.content,
            "author":     message.author,
            "created_at": message.created_at,
            "avatar_url": message.author.display_avatar.url,
        }

    reason = _bot_deleted_ids.pop(message.id, None)
    log_id = int(load_logcfg().get("delete_log_channel", 0) or 0)
    if not log_id or message.channel.id == log_id:
        return
    try:
        log_ch = bot.get_channel(log_id) or await bot.fetch_channel(log_id)
    except Exception:
        return

    # Best-effort: cari siapa yang menghapus lewat audit log (butuh izin View Audit Log)
    deleter = None
    if reason is None:
        try:
            async for entry in message.guild.audit_logs(limit=5, action=discord.AuditLogAction.message_delete):
                age = (datetime.datetime.now(datetime.timezone.utc) - entry.created_at).total_seconds()
                if entry.target.id == message.author.id and age < 10:
                    deleter = entry.user
                    break
        except Exception:
            pass

    embed = discord.Embed(
        title="🗑️ Pesan Dihapus",
        description=(message.content or "*(tanpa teks)*")[:4000],
        color=discord.Color.orange() if reason else discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_author(name=f"{message.author} ({message.author.id})",
                     icon_url=message.author.display_avatar.url)
    embed.add_field(name="Channel", value=message.channel.mention, inline=True)
    embed.add_field(name="Dikirim", value=f"<t:{int(message.created_at.timestamp())}:R>", inline=True)
    if reason:
        embed.add_field(name="Dihapus oleh", value=f"Bot — {reason}", inline=False)
    elif deleter:
        embed.add_field(name="Dihapus oleh", value=f"{deleter.mention} ({deleter})", inline=False)
    if message.attachments:
        embed.add_field(
            name="Lampiran",
            value="\n".join(f"[{a.filename}]({a.url})" for a in message.attachments)[:1000],
            inline=False)
    embed.set_footer(text=f"Message ID: {message.id}")
    try:
        await log_ch.send(embed=embed)
    except Exception as e:
        print(f"[Log] Gagal kirim log hapus pesan: {e}")

@bot.command(name="setlogchannel", aliases=["setlog"])
@commands.guild_only()
async def setlogchannel_cmd(ctx, channel: discord.TextChannel = None):
    """Admin: set channel log pesan terhapus. `!setlogchannel #channel` / `!setlogchannel off` / tanpa argumen = lihat."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa pakai command ini.", delete_after=5)
    cfg = load_logcfg()
    raw = ctx.message.content.split(maxsplit=1)
    if len(raw) > 1 and raw[1].strip().lower() in ("off", "mati", "reset", "hapus"):
        cfg["delete_log_channel"] = 0
        save_logcfg(cfg)
        return await ctx.send("✅ Log pesan terhapus **dimatikan**.")
    if channel is None:
        cur = int(cfg.get("delete_log_channel", 0) or 0)
        return await ctx.send(
            f"📋 Channel log sekarang: {f'<#{cur}>' if cur else '**belum di-set**'}\n"
            "Set: `!setlogchannel #channel` • Matikan: `!setlogchannel off`")
    cfg["delete_log_channel"] = channel.id
    save_logcfg(cfg)
    await ctx.send(f"✅ Pesan yang dihapus sekarang dilog ke {channel.mention}.")

# ═══════════════════════════════════════════════════════
#  BAN WORD — kata terlarang per channel (bisa di-setting)
#  !banword add [#channel|all] kata1, kata2
#  !banword remove [#channel|all] kata
#  !banword list [#channel|all]
#  !banword clear [#channel|all]
#  Wildcard: *kata* = cocok di dalam kata lain (tanpa * = harus kata utuh)
# ═══════════════════════════════════════════════════════
import re as _re
_banword_cache = {"data": None, "rx": {}}

def load_banwords() -> dict:
    d = load_json(BANWORD_FILE, default={})
    d.setdefault("channels", {})   # channel_id(str) -> [kata]
    d.setdefault("all", [])        # berlaku di semua channel
    return d

def save_banwords(d: dict):
    save_json(BANWORD_FILE, d)
    _banword_cache["data"] = None
    _banword_cache["rx"] = {}

def _bw_norm(text: str) -> str:
    text = _re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", text)
    return text.casefold()

def _bw_compile(word: str):
    w = _bw_norm(word.strip())
    left  = not w.startswith("*")
    right = not w.endswith("*")
    w = w.strip("*")
    if not w:
        return None
    body = r"\s+".join(_re.escape(p) for p in w.split())
    return _re.compile((r"(?<!\w)" if left else "") + body + (r"(?!\w)" if right else ""))

def _bw_patterns(channel_id: int) -> list:
    d = _banword_cache["data"]
    if d is None:
        d = _banword_cache["data"] = load_banwords()
    key = str(channel_id)
    if key not in _banword_cache["rx"]:
        words = list(d.get("all", [])) + list(d["channels"].get(key, []))
        _banword_cache["rx"][key] = [(w, rx) for w in words if (rx := _bw_compile(w))]
    return _banword_cache["rx"][key]

async def _check_banword(message) -> bool:
    """True kalau pesan mengandung kata terlarang & sudah dihapus."""
    if message.guild is None or not message.content or message.author.bot:
        return False
    try:
        if is_moderator(message.author):
            return False
    except Exception:
        pass
    text = _bw_norm(message.content)
    for word, rx in _bw_patterns(message.channel.id):
        if rx.search(text):
            _bot_deleted_ids[message.id] = f"Ban word (`{word}`)"
            try:
                await message.delete()
            except Exception:
                _bot_deleted_ids.pop(message.id, None)
                return False
            try:
                await message.channel.send(
                    f"🚫 {message.author.mention} pesanmu dihapus karena mengandung kata terlarang.",
                    delete_after=6)
            except Exception:
                pass
            return True
    return False

@bot.event
async def on_message_edit(before, after):
    """Pesan yang diedit juga dicek ban word."""
    if after.content != before.content:
        await _check_banword(after)

def _bw_parse(ctx, args: str):
    """Return (scope, words). scope: 'all' atau channel_id(int). Default = channel tempat command dipakai."""
    args = (args or "").strip()
    scope = ctx.channel.id
    if args:
        first, _, rest = args.partition(" ")
        m = _re.fullmatch(r"<#(\d+)>", first)
        if m:
            scope, args = int(m.group(1)), rest.strip()
        elif first.lower() in ("all", "semua"):
            scope, args = "all", rest.strip()
    words = [w.strip() for w in _re.split(r"[,\n]", args) if w.strip()]
    return scope, words

def _bw_scope_label(scope) -> str:
    return "**semua channel**" if scope == "all" else f"<#{scope}>"

@bot.group(name="banword", aliases=["bw", "katalarang"], invoke_without_command=True)
@commands.guild_only()
async def banword_group(ctx):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin yang bisa pakai command ini.", delete_after=5)
    await ctx.send(embed=discord.Embed(
        title="🚫 Ban Word — Cara Pakai",
        description=(
            "`!banword add [#channel|all] kata1, kata2` — Tambah kata terlarang\n"
            "`!banword remove [#channel|all] kata` — Hapus kata\n"
            "`!banword list [#channel|all]` — Lihat daftar kata\n"
            "`!banword clear [#channel|all]` — Kosongkan daftar\n\n"
            "📌 Tanpa `#channel` = channel tempat command dipakai. `all` = semua channel.\n"
            "📌 Pisahkan banyak kata dengan koma. Frasa (dengan spasi) juga bisa.\n"
            "📌 Cocok kata utuh, tidak peka huruf besar/kecil. Pakai `*kata*` agar cocok di dalam kata lain.\n"
            "📌 Admin & moderator tidak terkena filter."),
        color=discord.Color.red()))

@banword_group.command(name="add", aliases=["tambah"])
async def banword_add(ctx, *, args: str = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    scope, words = _bw_parse(ctx, args)
    if not words:
        return await ctx.send("❌ Format: `!banword add [#channel|all] kata1, kata2`", delete_after=8)
    d = load_banwords()
    lst = d["all"] if scope == "all" else d["channels"].setdefault(str(scope), [])
    existing = {_bw_norm(w) for w in lst}
    added = []
    for w in words:
        if _bw_norm(w) not in existing:
            lst.append(w); existing.add(_bw_norm(w)); added.append(w)
    save_banwords(d)
    if not added:
        return await ctx.send("ℹ️ Semua kata itu sudah ada di daftar.")
    await ctx.send(f"✅ Ditambah ke {_bw_scope_label(scope)}: " + ", ".join(f"`{w}`" for w in added))

@banword_group.command(name="remove", aliases=["hapus", "del", "delete"])
async def banword_remove(ctx, *, args: str = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    scope, words = _bw_parse(ctx, args)
    if not words:
        return await ctx.send("❌ Format: `!banword remove [#channel|all] kata`", delete_after=8)
    d = load_banwords()
    lst = d["all"] if scope == "all" else d["channels"].get(str(scope), [])
    targets = {_bw_norm(w) for w in words}
    kept = [w for w in lst if _bw_norm(w) not in targets]
    removed = len(lst) - len(kept)
    if scope == "all":
        d["all"] = kept
    elif kept:
        d["channels"][str(scope)] = kept
    else:
        d["channels"].pop(str(scope), None)
    save_banwords(d)
    await ctx.send(f"✅ {removed} kata dihapus dari {_bw_scope_label(scope)}." if removed
                   else "ℹ️ Kata tidak ditemukan di daftar.")

@banword_group.command(name="list", aliases=["daftar", "ls"])
async def banword_list(ctx, *, args: str = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    d = load_banwords()
    if not (args or "").strip():
        # Tanpa argumen: tampilkan ringkasan semua channel
        embed = discord.Embed(title="🚫 Daftar Ban Word", color=discord.Color.red())
        embed.add_field(name="🌐 Semua channel",
                        value=", ".join(f"`{w}`" for w in d["all"])[:1000] or "*kosong*", inline=False)
        for cid, words in list(d["channels"].items())[:20]:
            embed.add_field(name=f"#{cid}" if not ctx.guild.get_channel(int(cid)) else ctx.guild.get_channel(int(cid)).name,
                            value=", ".join(f"`{w}`" for w in words)[:1000], inline=False)
        if not d["all"] and not d["channels"]:
            embed.description = "Belum ada kata terlarang. Tambah dengan `!banword add`."
        return await ctx.send(embed=embed)
    scope, _ = _bw_parse(ctx, args)
    lst = d["all"] if scope == "all" else d["channels"].get(str(scope), [])
    await ctx.send(f"🚫 Ban word {_bw_scope_label(scope)}:\n" +
                   (", ".join(f"`{w}`" for w in lst)[:1800] if lst else "*kosong*"))

@banword_group.command(name="clear", aliases=["reset"])
async def banword_clear(ctx, *, args: str = None):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya admin.", delete_after=5)
    scope, _ = _bw_parse(ctx, args)
    d = load_banwords()
    if scope == "all":
        d["all"] = []
    else:
        d["channels"].pop(str(scope), None)
    save_banwords(d)
    await ctx.send(f"✅ Daftar ban word {_bw_scope_label(scope)} dikosongkan.")

@bot.command(name="snipe", aliases=["sn"])
@commands.guild_only()
async def snipe_cmd(ctx):
    """Tampilkan pesan terakhir yang dihapus di channel ini."""
    data = _snipe_cache.get(ctx.channel.id)
    if not data:
        return await ctx.send("🕵️ Tidak ada pesan terhapus yang tercache di channel ini.", delete_after=8)

    deleted_ts = int(data["created_at"].timestamp())
    embed = discord.Embed(
        description=data["content"][:4096],
        color=discord.Color.red(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_author(
        name=f"{data['author'].display_name} ({data['author']})",
        icon_url=data["avatar_url"]
    )
    embed.set_footer(text=f"Dikirim <t:{deleted_ts}:R> • Asisten Lurah BFL | !snipe")
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  FITUR TAMBAHAN 5 — !REMINDER
#  Set reminder pribadi dengan waktu custom
# ═══════════════════════════════════════════════════════
@bot.command(name="reminder", aliases=["remind", "ingatkan"])
async def reminder_cmd(ctx, waktu: str = None, *, pesan: str = "Waktunya!"):
    """Set reminder untuk dirimu sendiri.
    Format waktu: 10s, 5m, 2h, 1d
    Contoh: !reminder 30m Makan siang
            !reminder 2h Meeting BFL
    """
    if waktu is None:
        embed = discord.Embed(
            title="⏰ Cara Pakai !reminder",
            description=(
                "**Format:** `!reminder <waktu> <pesan>`\n\n"
                "**Contoh:**\n"
                "`!reminder 30m Makan siang`\n"
                "`!reminder 2h Meeting BFL`\n"
                "`!reminder 1d Bayar iuran`\n\n"
                "**Satuan waktu:**\n"
                "`s` = detik | `m` = menit | `h` = jam | `d` = hari\n"
                "⏳ Maksimal: **7 hari**"
            ),
            color=discord.Color.blue()
        )
        return await ctx.send(embed=embed, delete_after=20)

    # Parse durasi
    total_seconds = 0
    patterns = [("d", 86400), ("h", 3600), ("m", 60), ("s", 1)]
    for suffix, mult in patterns:
        match = re.search(r"(\d+)" + suffix, waktu.lower())
        if match:
            total_seconds += int(match.group(1)) * mult

    if total_seconds <= 0:
        return await ctx.send("❌ Format waktu salah. Contoh: `30m`, `2h`, `1d`", delete_after=8)

    MAX_SECONDS = 7 * 86400
    if total_seconds > MAX_SECONDS:
        return await ctx.send("❌ Maksimal reminder adalah **7 hari**.", delete_after=8)

    # Format waktu display
    days, rem  = divmod(total_seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days:  parts.append(f"{days}h")
    if hours: parts.append(f"{hours}j")
    if mins:  parts.append(f"{mins}m")
    if secs:  parts.append(f"{secs}d")
    dur_str = " ".join(parts)

    fire_ts = int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=total_seconds)).timestamp())

    confirm_embed = discord.Embed(
        title="⏰ Reminder Diset!",
        description=(
            f"✅ Kamu akan diingatkan dalam **{dur_str}**\n"
            f"📌 Pesan: **{pesan}**\n"
            f"🕐 Waktunya: <t:{fire_ts}:F> (<t:{fire_ts}:R>)"
        ),
        color=discord.Color.green()
    )
    confirm_embed.set_footer(text=f"{ctx.author.display_name} • Asisten Lurah BFL")
    await ctx.send(embed=confirm_embed)

    # Tunggu lalu kirim DM
    await asyncio.sleep(total_seconds)

    try:
        remind_embed = discord.Embed(
            title="⏰ REMINDER!",
            description=(
                f"Hei {ctx.author.mention}, ini pengingatmu!\n\n"
                f"📌 **{pesan}**"
            ),
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        remind_embed.set_footer(text="Asisten Lurah BFL • Reminder System")
        await ctx.author.send(embed=remind_embed)

        # Juga kirim di channel asal jika masih bisa
        try:
            await ctx.send(f"⏰ {ctx.author.mention} **Reminder:** {pesan}", delete_after=30)
        except Exception:
            pass
    except Exception:
        pass


# ═══════════════════════════════════════════════════════
#  SETORAN METALSCRAP
#  - Rekap MINGGUAN reset otomatis tiap Senin 00.00 WIB
#  - Semua input dicatat PERMANEN di "log" → total BULANAN & riwayat tidak ikut hilang
# ═══════════════════════════════════════════════════════
SETORAN_FILE = _p("setoran_metalscrap.json")

BULAN_ID = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
            "Agustus", "September", "Oktober", "November", "Desember"]

def _week_start_str(dt: datetime.datetime) -> str:
    """Tanggal Senin (ISO date) dari minggu yang memuat dt, dalam WIB."""
    monday = dt.date() - datetime.timedelta(days=dt.weekday())
    return monday.isoformat()

def _week_label(week_start: str) -> str:
    try:
        a = datetime.date.fromisoformat(week_start)
        b = a + datetime.timedelta(days=6)
        return f"{a:%d/%m} – {b:%d/%m/%Y}"
    except Exception:
        return str(week_start)

def _ts_to_wib(ts: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ts, WIB)

def _migrate_setoran_log(data: dict) -> bool:
    """Data lama (tanpa log) → buat log dari entries minggu ini & minggu lalu. True kalau ada perubahan."""
    if isinstance(data.get("log"), list):
        data.setdefault("next_id", len(data["log"]) + 1)
        return False
    log, nid = [], 1

    def _add(entries, week):
        nonlocal nid
        for key, e in (entries or {}).items():
            ts = e.get("terakhir_ts")
            if not ts:
                try:
                    d = datetime.date.fromisoformat(week)
                    ts = int(WIB.localize(datetime.datetime(d.year, d.month, d.day, 12)).timestamp())
                except Exception:
                    ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            log.append({
                "id": nid, "key": key, "nama": e.get("nama", key),
                "jumlah": float(e.get("jumlah", 0)), "oleh": e.get("terakhir_oleh", "-"),
                "ts": int(ts), "week": week, "deleted": False, "cleared": False, "migrasi": True,
            })
            nid += 1

    _add(data.get("previous_entries"), data.get("previous_week_start"))
    _add(data.get("entries"), data.get("week_start"))
    data["log"], data["next_id"] = log, nid
    return True

def load_setoran() -> dict:
    data = load_json(SETORAN_FILE, default={})
    data.setdefault("week_start", None)
    data.setdefault("entries", {})
    changed = _migrate_setoran_log(data)
    current_week = _week_start_str(datetime.datetime.now(WIB))
    if data.get("week_start") != current_week:
        # Minggu baru → rekap mingguan di-reset. Log (riwayat & total bulanan) TIDAK disentuh.
        if data.get("week_start") and data.get("entries"):
            data["previous_week_start"] = data["week_start"]
            data["previous_entries"] = data["entries"]
        data["week_start"] = current_week
        data["entries"] = {}
        changed = True
    if changed:
        save_json(SETORAN_FILE, data)
    return data

def save_setoran(d: dict):
    save_json(SETORAN_FILE, d)

def _parse_jumlah(raw: str):
    raw = raw.strip().lower().replace("kg", "").replace(",", ".").strip()
    try:
        val = float(raw)
        if val <= 0:
            return None
        return val
    except ValueError:
        return None

def _parse_setoran_lines(text: str):
    """Parse blok teks multi-baris, tiap baris format: <nama> <jumlah>.
    Return (entries, errors) — entries = list[(nama, jumlah)], errors = list baris yang gagal diparse."""
    entries = []
    errors  = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            errors.append(line)
            continue
        jumlah_raw = parts[-1]
        nama_raw   = " ".join(parts[:-1]).rstrip("-").strip()
        jumlah     = _parse_jumlah(jumlah_raw)
        if not nama_raw or jumlah is None:
            errors.append(line)
            continue
        entries.append((nama_raw, jumlah))
    return entries, errors

def _apply_setoran_entries(entries, oleh: str) -> dict:
    """Terapkan list (nama, jumlah) ke data setoran minggu ini (akumulatif) + catat ke log permanen."""
    data   = load_setoran()
    now_ts = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
    for nama_raw, jumlah in entries:
        key = nama_raw.lower()
        existing = data["entries"].get(key, {"nama": nama_raw, "jumlah": 0.0})
        existing["nama"]          = nama_raw
        existing["jumlah"]        = existing.get("jumlah", 0.0) + jumlah
        existing["terakhir_oleh"] = oleh
        existing["terakhir_ts"]   = now_ts
        data["entries"][key] = existing

        data["log"].append({
            "id": data["next_id"], "key": key, "nama": nama_raw, "jumlah": jumlah,
            "oleh": oleh, "ts": now_ts, "week": data["week_start"],
            "deleted": False, "cleared": False,
        })
        data["next_id"] += 1
    save_setoran(data)
    return data

# ── Helper agregasi dari log ─────────────────────────
def _log_active(data: dict):
    return [e for e in data.get("log", []) if not e.get("deleted")]

def _aggregate_log(items) -> dict:
    """list entri log → {key: {"nama", "jumlah"}}"""
    out = {}
    for e in sorted(items, key=lambda x: x["ts"]):
        row = out.setdefault(e["key"], {"nama": e["nama"], "jumlah": 0.0})
        row["nama"] = e["nama"]
        row["jumlah"] += e["jumlah"]
    return out

def _month_items(data: dict, year: int, month: int):
    res = []
    for e in _log_active(data):
        d = _ts_to_wib(e["ts"])
        if d.year == year and d.month == month:
            res.append(e)
    return res

def _month_total(data: dict, year: int, month: int) -> float:
    return sum(e["jumlah"] for e in _month_items(data, year, month))

def _table_block(rows) -> tuple:
    """rows = list[{"nama","jumlah"}] → (code block, total). Dipotong aman bila terlalu panjang."""
    NAME_WIDTH = 18
    rows = sorted(rows, key=lambda e: e["jumlah"], reverse=True)
    total = sum(r["jumlah"] for r in rows)
    lines = []
    for i, e in enumerate(rows, start=1):
        nama = e["nama"]
        if len(nama) > NAME_WIDTH:
            nama = nama[:NAME_WIDTH - 1] + "…"
        lines.append(f"{i:>2}. {nama:<{NAME_WIDTH}} {e['jumlah']:>8.0f}")
    header  = f"    {'Nama':<{NAME_WIDTH}} {'Jumlah':>8}   "
    divider = "-" * len(header)
    footer  = f"\n{divider}\n    {'Total':<{NAME_WIDTH}} {total:>8.0f} kg\n```"
    head    = "```\n" + header + "\n" + divider + "\n"
    body, used = [], len(head) + len(footer) + 40
    for ln in lines:
        if used + len(ln) + 1 > 3900:
            body.append(f"... +{len(lines) - len(body)} baris lagi")
            break
        body.append(ln)
        used += len(ln) + 1
    return head + "\n".join(body) + footer, total

def _setoran_list_embed(data: dict, footer: str, title: str = "♻️ Daftar Setoran Metalscrap",
                        entries: dict = None, empty_text: str = "_Belum ada setoran minggu ini._",
                        bulan_total: tuple = None) -> discord.Embed:
    """entries=None → pakai rekap minggu ini. bulan_total=(label, total) → tampilkan total bulan."""
    src = data["entries"] if entries is None else entries
    sorted_entries = sorted(src.values(), key=lambda e: e["jumlah"], reverse=True)

    embed = discord.Embed(
        title=title,
        color=discord.Color.from_rgb(120, 170, 80),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    if not sorted_entries:
        embed.description = empty_text
    else:
        table, total = _table_block(sorted_entries)
        embed.description = table
        embed.add_field(name="Total Penyetor", value=str(len(sorted_entries)), inline=True)
        embed.add_field(name="Total Metalscrap", value=f"{total:g} kg", inline=True)
    if bulan_total:
        embed.add_field(name=f"📅 Total {bulan_total[0]}", value=f"{bulan_total[1]:g} kg", inline=True)
    embed.set_footer(text=footer)
    return embed

@tasks.loop(minutes=5)
async def check_setoran_reset():
    # Memuat data otomatis melakukan reset mingguan jika minggu sudah berganti (log tetap aman)
    load_setoran()

@check_setoran_reset.before_loop
async def before_check_setoran_reset():
    await bot.wait_until_ready()

_SETORAN_FOOTER = "Reset mingguan tiap Senin 00.00 WIB • Asisten Lurah BFL"

@bot.command(name="setoran")
async def setoran_cmd(ctx, *, args: str = None):
    """
    !setoran                     → Bot minta input, bisa banyak baris sekaligus
    !setoran <nama> <jumlah>     → Catat langsung (bisa multi-baris juga)
    !setoran hapus <nama>        → Hapus entri setoran minggu ini (admin)
    !setoran reset               → Kosongkan rekap minggu ini (admin) — total bulan & riwayat tetap ada

    Rekap mingguan otomatis di-reset tiap Senin 00.00 WIB. Total bulanan: !setoranbulan, riwayat: !setoranriwayat
    """
    def _embed_after_input(data, footer):
        now = datetime.datetime.now(WIB)
        return _setoran_list_embed(
            data, footer,
            bulan_total=(f"{BULAN_ID[now.month - 1]} {now.year}", _month_total(data, now.year, now.month))
        )

    # ── TANPA ARGUMEN: mode interaktif ───────────────
    if not args:
        await ctx.send(f"{ctx.author.mention} 📝 Silahkan input setoran")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            reply = await bot.wait_for("message", check=check, timeout=120)
        except asyncio.TimeoutError:
            return await ctx.send(
                f"{ctx.author.mention} ⏰ Waktu habis. Ketik `!setoran` lagi untuk mulai ulang.",
                delete_after=10
            )

        entries, errors = _parse_setoran_lines(reply.content)
        if not entries:
            return await ctx.send(
                "❌ Tidak ada input valid. Format tiap baris: `nama jumlah`",
                delete_after=10
            )

        data = _apply_setoran_entries(entries, ctx.author.display_name)
        footer = f"Dicatat oleh {ctx.author.display_name} • Asisten Lurah BFL"
        if errors:
            footer += f" • {len(errors)} baris dilewati (format salah)"
        return await ctx.send(embed=_embed_after_input(data, footer))

    parts = args.strip().split()

    # ── SUBCOMMAND: reset (admin) ────────────────────
    if parts[0].lower() == "reset":
        if not is_admin(ctx.author):
            return await ctx.send("❌ Hanya **Admin / Owner** yang bisa reset setoran.", delete_after=8)
        old = load_setoran()
        if old["entries"]:
            old["previous_week_start"] = old.get("week_start")
            old["previous_entries"] = old["entries"]
        old["entries"] = {}
        for e in old["log"]:
            if e.get("week") == old["week_start"]:
                e["cleared"] = True
        save_setoran(old)
        return await ctx.send(
            "🔄 Rekap setoran **minggu ini** di-reset.\n"
            "📅 Total bulanan & riwayat input tetap tersimpan (`!setoranbulan`, `!setoranriwayat`)."
        )

    # ── SUBCOMMAND: hapus <nama> (admin) ─────────────
    if parts[0].lower() == "hapus" and len(parts) > 1:
        if not is_admin(ctx.author):
            return await ctx.send("❌ Hanya **Admin / Owner** yang bisa menghapus entri.", delete_after=8)
        nama_target = " ".join(parts[1:]).strip()
        data = load_setoran()
        key = nama_target.lower()
        if key not in data["entries"]:
            return await ctx.send(f"❌ Entri **{nama_target}** tidak ditemukan di setoran minggu ini.", delete_after=8)
        removed = data["entries"].pop(key)
        # Hapus juga dari log supaya total bulanan ikut terkoreksi
        for e in data["log"]:
            if e["key"] == key and e.get("week") == data["week_start"] and not e.get("cleared"):
                e["deleted"] = True
        save_setoran(data)
        return await ctx.send(
            f"🗑️ Entri **{removed['nama']}** ({removed['jumlah']:g}) berhasil dihapus dari setoran "
            f"(total bulanan ikut terkoreksi)."
        )

    # ── INPUT LANGSUNG: bisa satu atau banyak baris ──
    entries, errors = _parse_setoran_lines(args)
    if not entries:
        return await ctx.send(
            "❌ Format salah. Contoh: `!setoran masjack 200`\n"
            "Bisa juga banyak baris sekaligus, satu baris satu `nama jumlah`.",
            delete_after=12
        )

    data = _apply_setoran_entries(entries, ctx.author.display_name)
    footer = f"Dicatat oleh {ctx.author.display_name} • Asisten Lurah BFL"
    if errors:
        footer += f" • {len(errors)} baris dilewati (format salah)"
    await ctx.send(embed=_embed_after_input(data, footer))

def _parse_week_arg(arg: str):
    """'lalu' → Senin minggu lalu; 'YYYY-MM-DD' / 'DD-MM-YYYY' → Senin minggu yang memuat tanggal itu."""
    arg = arg.strip().lower()
    today = datetime.datetime.now(WIB)
    if arg in ("lalu", "kemarin", "last", "prev"):
        return _week_start_str(today - datetime.timedelta(days=7))
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            d = datetime.datetime.strptime(arg, fmt)
            return _week_start_str(d)
        except ValueError:
            pass
    return None

@bot.command(name="setoranlist", aliases=["setoranlst", "listsetoran"])
async def setoranlist_cmd(ctx, *, minggu: str = None):
    """Rekap setoran mingguan. `!setoranlist` = minggu ini, `!setoranlist lalu`, atau `!setoranlist 2026-09-21`."""
    data = load_setoran()
    now = datetime.datetime.now(WIB)

    if minggu:
        ws = _parse_week_arg(minggu)
        if not ws:
            return await ctx.send(
                "❌ Format salah. Contoh: `!setoranlist lalu` atau `!setoranlist 2026-09-21` (tanggal apa pun di minggu itu).",
                delete_after=12
            )
        if ws != data["week_start"]:
            items = [e for e in _log_active(data) if e.get("week") == ws]
            return await ctx.send(embed=_setoran_list_embed(
                data, _SETORAN_FOOTER,
                title=f"♻️ Setoran Minggu {_week_label(ws)}",
                entries=_aggregate_log(items),
                empty_text="_Tidak ada data setoran di minggu itu._"
            ))

    bt = (f"{BULAN_ID[now.month - 1]} {now.year}", _month_total(data, now.year, now.month))
    if not data.get("entries"):
        return await ctx.send(
            "📋 Belum ada setoran metalscrap minggu ini. Catat dengan `!setoran`\n"
            f"📅 Total {bt[0]} sejauh ini: **{bt[1]:g} kg** (`!setoranbulan` untuk detail)"
        )
    await ctx.send(embed=_setoran_list_embed(
        data, _SETORAN_FOOTER,
        title=f"♻️ Setoran Minggu Ini ({_week_label(data['week_start'])})",
        bulan_total=bt
    ))

def _parse_month_arg(arg: str):
    """Return (year, month) atau None. Mendukung: kosong, 'lalu', '10', '10-2026', '2026-10', 'oktober', 'oktober 2026'."""
    now = datetime.datetime.now(WIB)
    if not arg:
        return now.year, now.month
    a = arg.strip().lower()
    if a in ("lalu", "kemarin", "last", "prev"):
        y, m = (now.year, now.month - 1) if now.month > 1 else (now.year - 1, 12)
        return y, m
    toks = re.split(r"[\s/\-]+", a)
    year, month = now.year, None
    for t in toks:
        if not t:
            continue
        if t.isdigit():
            n = int(t)
            if n >= 1000:
                year = n
            elif 1 <= n <= 12 and month is None:
                month = n
            else:
                return None
        else:
            for i, nm in enumerate(BULAN_ID, start=1):
                if len(t) >= 3 and nm.lower().startswith(t):
                    month = i
                    break
            else:
                return None
    if month is None:
        return None
    return year, month

@bot.command(name="setoranbulan", aliases=["setoranbulanan", "bulansetoran", "totalsetoran"])
async def setoranbulan_cmd(ctx, *, bulan: str = None):
    """Total setoran sebulan penuh. Contoh: !setoranbulan | !setoranbulan lalu | !setoranbulan 9 | !setoranbulan oktober 2026"""
    ym = _parse_month_arg(bulan)
    if not ym:
        return await ctx.send(
            "❌ Format salah. Contoh: `!setoranbulan`, `!setoranbulan lalu`, `!setoranbulan 9`, `!setoranbulan oktober 2026`",
            delete_after=12
        )
    year, month = ym
    data  = load_setoran()
    items = _month_items(data, year, month)
    label = f"{BULAN_ID[month - 1]} {year}"

    embed = discord.Embed(
        title=f"📅 Rekap Setoran Bulan {label}",
        color=discord.Color.from_rgb(80, 150, 200),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    if not items:
        embed.description = f"_Belum ada data setoran di bulan {label}._"
        embed.set_footer(text="Asisten Lurah BFL")
        return await ctx.send(embed=embed)

    table, total = _table_block(list(_aggregate_log(items).values()))
    embed.description = table

    # Rincian per minggu
    per_week = {}
    for e in items:
        per_week[e.get("week") or "?"] = per_week.get(e.get("week") or "?", 0.0) + e["jumlah"]
    wk_lines = [f"• {_week_label(w)}: **{v:g} kg**" for w, v in sorted(per_week.items())]
    embed.add_field(name="🗓️ Rincian per Minggu", value="\n".join(wk_lines)[:1024], inline=False)
    embed.add_field(name="Total Penyetor", value=str(len({e['key'] for e in items})), inline=True)
    embed.add_field(name="Total Bulan Ini", value=f"{total:g} kg", inline=True)
    embed.add_field(name="Jumlah Input", value=str(len(items)), inline=True)
    embed.set_footer(text="Data bulanan tidak ikut ter-reset • Asisten Lurah BFL")
    await ctx.send(embed=embed)

@bot.command(name="setoranriwayat", aliases=["riwayatsetoran", "setoranlog", "setoranhistory"])
async def setoranriwayat_cmd(ctx, *, args: str = None):
    """Riwayat semua input setoran. Contoh: !setoranriwayat | !setoranriwayat masjack | !setoranriwayat 2 | !setoranriwayat masjack 2"""
    PER_PAGE = 15
    page, nama_filter = 1, None
    if args:
        toks = args.strip().split()
        if toks[-1].isdigit() and len(toks) > 1:
            page = max(1, int(toks.pop()))
            nama_filter = " ".join(toks)
        elif toks[-1].isdigit() and len(toks) == 1:
            page = max(1, int(toks[0]))
        else:
            nama_filter = " ".join(toks)

    data  = load_setoran()
    items = _log_active(data)
    if nama_filter:
        nf = nama_filter.lower()
        items = [e for e in items if nf in e["key"]]
    items.sort(key=lambda e: (e["ts"], e["id"]), reverse=True)

    if not items:
        return await ctx.send(
            f"📋 Tidak ada riwayat setoran{f' untuk **{nama_filter}**' if nama_filter else ''}.", delete_after=10
        )

    pages = max(1, math.ceil(len(items) / PER_PAGE))
    page  = min(page, pages)
    chunk = items[(page - 1) * PER_PAGE: page * PER_PAGE]

    lines = []
    for e in chunk:
        d = _ts_to_wib(e["ts"])
        nama = e["nama"] if len(e["nama"]) <= 14 else e["nama"][:13] + "…"
        oleh = e.get("oleh", "-")
        oleh = oleh if len(oleh) <= 12 else oleh[:11] + "…"
        mig  = "*" if e.get("migrasi") else " "
        lines.append(f"#{e['id']:<4}{d:%d/%m %H:%M} {nama:<14} {e['jumlah']:>7.0f}{mig} {oleh}")
    total_filter = sum(e["jumlah"] for e in items)

    embed = discord.Embed(
        title="🧾 Riwayat Setoran" + (f" — {nama_filter}" if nama_filter else ""),
        description="```\n" + "\n".join(lines) + "\n```",
        color=discord.Color.from_rgb(150, 120, 200),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.add_field(name="Total Input", value=str(len(items)), inline=True)
    embed.add_field(name="Total Jumlah", value=f"{total_filter:g} kg", inline=True)
    foot = f"Halaman {page}/{pages}"
    if pages > 1:
        foot += f" • !setoranriwayat {nama_filter + ' ' if nama_filter else ''}{min(page + 1, pages)} untuk berikutnya"
    if any(e.get("migrasi") for e in chunk):
        foot += " • * = data lama (sudah digabung per nama)"
    embed.set_footer(text=foot)
    await ctx.send(embed=embed)


# ═══════════════════════════════════════════════════════
#  TRIAL ROLE — beri role sementara, otomatis dicabut saat habis
# ═══════════════════════════════════════════════════════
import time as _time, zipfile, hashlib

TRIAL_ROLE_FILE = _p("trial_roles.json")
TRIAL_MAX_SECONDS = 365 * 86400

def load_trials():    return load_json(TRIAL_ROLE_FILE, default={})
def save_trials(d):   save_json(TRIAL_ROLE_FILE, d)

def _parse_trial_duration(s: str):
    """'30m', '12h', '3d', '1w', '1d12h' -> detik. None kalau format salah."""
    if not s:
        return None
    s = s.lower().replace(" ", "")
    if not re.fullmatch(r"(\d+[wdhm])+", s):
        return None
    mult = {"w": 604800, "d": 86400, "h": 3600, "m": 60}
    total = sum(int(n) * mult[u] for n, u in re.findall(r"(\d+)([wdhm])", s))
    return total if total > 0 else None

def _fmt_duration(seconds: int) -> str:
    seconds = int(seconds)
    parts = []
    for label, size in (("hari", 86400), ("jam", 3600), ("menit", 60)):
        if seconds >= size:
            parts.append(f"{seconds // size} {label}")
            seconds %= size
    return " ".join(parts) if parts else "kurang dari 1 menit"

def _trial_key(guild_id, user_id, role_id) -> str:
    return f"{guild_id}:{user_id}:{role_id}"

@bot.group(name="trialrole", aliases=["trial"], invoke_without_command=True)
async def trialrole_cmd(ctx, member: discord.Member = None, role: discord.Role = None, *, durasi: str = None):
    """!trialrole @user @role <durasi>  — contoh: !trialrole @Budi @VIP 3d"""
    if not ctx.guild:
        return await ctx.send("⚠️ Command ini hanya bisa dipakai di server.")
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner** yang bisa memberi trial role.", delete_after=8)

    if member is None or role is None or durasi is None:
        embed = discord.Embed(
            title="⏳ Cara Pakai !trialrole",
            description=(
                "`!trialrole @user @role <durasi>` — Beri role sementara\n"
                "`!trialrole list [@user]` — Lihat trial yang aktif\n"
                "`!trialrole cancel @user [@role]` — Hentikan trial sekarang\n\n"
                "**Contoh durasi:** `30m`, `12h`, `3d`, `1w`, `1d12h`\n"
                "`m` = menit | `h` = jam | `d` = hari | `w` = minggu\n"
                "⏳ Maksimal: **365 hari**"
            ),
            color=discord.Color.blue()
        )
        return await ctx.send(embed=embed, delete_after=30)

    secs = _parse_trial_duration(durasi)
    if not secs:
        return await ctx.send("❌ Format durasi salah. Contoh: `30m`, `12h`, `3d`, `1w`, `1d12h`", delete_after=10)
    if secs > TRIAL_MAX_SECONDS:
        return await ctx.send("❌ Durasi maksimal **365 hari**.", delete_after=10)

    if role.is_default() or role.managed:
        return await ctx.send("❌ Role itu tidak bisa diberikan (default/managed oleh bot atau integrasi).", delete_after=10)
    if role >= ctx.guild.me.top_role:
        return await ctx.send("❌ Role itu lebih tinggi/sama dengan role tertinggi bot. Naikkan role bot di pengaturan server.", delete_after=12)
    if ctx.author.id != OWNER_ID and ctx.author != ctx.guild.owner and role >= ctx.author.top_role:
        return await ctx.send("❌ Kamu tidak bisa memberi role yang lebih tinggi/sama dengan role tertinggimu.", delete_after=10)

    key = _trial_key(ctx.guild.id, member.id, role.id)
    trials = load_trials()
    existing = trials.get(key)
    has_role = role in member.roles

    if has_role and not existing:
        return await ctx.send(
            f"❌ {member.mention} sudah punya role **{role.name}** secara permanen. Trial dibatalkan supaya rolenya tidak ikut tercabut.",
            delete_after=12
        )

    if not has_role:
        try:
            await member.add_roles(role, reason=f"Trial role {durasi} oleh {ctx.author}")
        except discord.Forbidden:
            return await ctx.send("❌ Bot tidak punya izin untuk memberi role itu.", delete_after=10)
        except discord.HTTPException as e:
            return await ctx.send(f"❌ Gagal memberi role: {e}", delete_after=10)

    expires_at = int(_time.time()) + secs
    trials[key] = {
        "guild_id": ctx.guild.id,
        "user_id": member.id,
        "role_id": role.id,
        "expires_at": expires_at,
        "given_by": ctx.author.id,
        "channel_id": ctx.channel.id,
    }
    save_trials(trials)

    embed = discord.Embed(
        title="⏳ Trial Role " + ("Diperbarui" if existing else "Diberikan"),
        color=discord.Color.green()
    )
    embed.add_field(name="Member", value=member.mention, inline=True)
    embed.add_field(name="Role", value=role.mention, inline=True)
    embed.add_field(name="Durasi", value=_fmt_duration(secs), inline=True)
    embed.add_field(name="Berakhir", value=f"<t:{expires_at}:F> (<t:{expires_at}:R>)", inline=False)
    embed.set_footer(text="Asisten Lurah BFL • Role otomatis dicabut saat habis")
    await ctx.send(embed=embed)

@trialrole_cmd.command(name="list", aliases=["daftar"])
async def trialrole_list(ctx, member: discord.Member = None):
    if not ctx.guild:
        return await ctx.send("⚠️ Command ini hanya bisa dipakai di server.")
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    rows = [t for t in load_trials().values()
            if int(t["guild_id"]) == ctx.guild.id and (member is None or int(t["user_id"]) == member.id)]
    if not rows:
        return await ctx.send("📋 Tidak ada trial role yang aktif.")
    rows.sort(key=lambda t: t["expires_at"])
    lines = [f"<@{t['user_id']}> — <@&{t['role_id']}> — habis <t:{t['expires_at']}:R>" for t in rows[:25]]
    if len(rows) > 25:
        lines.append(f"... dan {len(rows) - 25} lainnya")
    embed = discord.Embed(title=f"⏳ Trial Role Aktif ({len(rows)})", description="\n".join(lines), color=discord.Color.blurple())
    await ctx.send(embed=embed, allowed_mentions=discord.AllowedMentions.none())

@trialrole_cmd.command(name="cancel", aliases=["batal", "stop", "hapus"])
async def trialrole_cancel(ctx, member: discord.Member, role: discord.Role = None):
    if not ctx.guild:
        return await ctx.send("⚠️ Command ini hanya bisa dipakai di server.")
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    trials = load_trials()
    keys = [k for k, t in trials.items()
            if int(t["guild_id"]) == ctx.guild.id and int(t["user_id"]) == member.id
            and (role is None or int(t["role_id"]) == role.id)]
    if not keys:
        return await ctx.send("❌ Tidak ada trial aktif yang cocok.", delete_after=8)
    names = []
    for k in keys:
        r = ctx.guild.get_role(int(trials[k]["role_id"]))
        if r and r in member.roles:
            try:
                await member.remove_roles(r, reason=f"Trial role dibatalkan oleh {ctx.author}")
            except discord.HTTPException as e:
                await ctx.send(f"⚠️ Gagal mencabut **{r.name}**: {e}", delete_after=10)
                continue
        names.append(r.name if r else f"ID {trials[k]['role_id']}")
        trials.pop(k, None)
    save_trials(trials)
    if names:
        await ctx.send(f"🛑 Trial dihentikan untuk {member.mention}: **{', '.join(names)}**", allowed_mentions=discord.AllowedMentions.none())

@tasks.loop(seconds=60)
async def check_trial_roles():
    trials = load_trials()
    if not trials:
        return
    now = int(_time.time())
    changed = False
    for key, t in list(trials.items()):
        if t["expires_at"] > now:
            continue
        guild = bot.get_guild(int(t["guild_id"]))
        if guild is None:
            continue  # guild belum ter-cache / bot sudah keluar; coba lagi nanti
        role = guild.get_role(int(t["role_id"]))
        if role is None:
            trials.pop(key, None); changed = True
            continue
        member = guild.get_member(int(t["user_id"]))
        if member is None:
            try:
                member = await guild.fetch_member(int(t["user_id"]))
            except discord.NotFound:
                trials.pop(key, None); changed = True  # member sudah keluar
                continue
            except discord.HTTPException:
                continue
        if role in member.roles:
            try:
                await member.remove_roles(role, reason="Masa trial role habis")
            except discord.Forbidden:
                print(f"[Trial] Tidak punya izin mencabut {role.name} dari {member}. Entri dihapus.")
                trials.pop(key, None); changed = True
                continue
            except discord.HTTPException as e:
                print(f"[Trial] Gagal mencabut role (akan dicoba lagi): {e}")
                continue
        trials.pop(key, None); changed = True

        try:
            await member.send(f"⏰ Masa trial role **{role.name}** kamu di **{guild.name}** sudah habis.")
        except Exception:
            pass
        ch = guild.get_channel(int(t.get("channel_id", 0) or 0))
        if ch:
            try:
                await ch.send(
                    f"⏰ Trial role **{role.name}** untuk {member.mention} sudah habis dan rolenya dicabut.",
                    allowed_mentions=discord.AllowedMentions.none()
                )
            except Exception:
                pass
    if changed:
        save_trials(trials)

@check_trial_roles.before_loop
async def before_check_trial_roles():
    await bot.wait_until_ready()


# ═══════════════════════════════════════════════════════
#  SAVE / LOAD SETTING — backup ke channel Discord, auto-load saat deploy
# ═══════════════════════════════════════════════════════
# Cara kerja:
#  - Semua file JSON di-zip lalu di-upload ke channel privat (BACKUP_CHANNEL_ID).
#  - Saat bot start, file yang HILANG di disk otomatis di-load dari backup terbaru.
#    File yang sudah ada (misal dari Railway Volume) TIDAK ditimpa.
#  - Auto-backup berkala (BACKUP_INTERVAL_MIN, default 1 hari / 1440 menit) hanya kalau ada perubahan.
BACKUP_CHANNEL_ID   = int(os.environ.get("BACKUP_CHANNEL_ID", "0") or 0)
BACKUP_INTERVAL_MIN = max(5, int(os.environ.get("BACKUP_INTERVAL_MIN", "1440") or 1440))
BACKUP_KEEP         = 5
BACKUP_PREFIX       = "YAHAHA_BACKUP"
BACKUP_MAX_BYTES    = 25 * 1024 * 1024

_backup_ready = False       # True setelah pengecekan restore saat startup selesai tanpa error
_last_backup_hash = None

def _backup_paths() -> list:
    return [
        LAST_TIKTOK_FILE, TICKET_FILE, VERIF_FILE, WARN_FILE,
        GIVEAWAY_FILE, SETTINGS_FILE, AFK_FILE, CUSTOM_CMD_FILE,
        REACT_ROLE_FILE, AUTOMOD_FILE, WELCOME_CFG_FILE, POLLS_FILE, JOIN_TRACKING_FILE,
        MODERATOR_FILE, TIKTOK_SETTINGS_FILE, AUTOREPLY_FILE, SETORAN_FILE,
        TRIAL_ROLE_FILE, LOGCFG_FILE, BANWORD_FILE, MCASH_FILE,
    ]

def _snapshot() -> dict:
    snap = {}
    for path in _backup_paths():
        if os.path.exists(path):
            with open(path, "rb") as f:
                snap[os.path.basename(path)] = f.read()
    return snap

def _snapshot_hash(snap: dict) -> str:
    h = hashlib.sha256()
    for name in sorted(snap):
        h.update(name.encode()); h.update(b"\0"); h.update(snap[name]); h.update(b"\0")
    return h.hexdigest()

def _build_zip(snap: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in snap.items():
            zf.writestr(name, content)
    return buf.getvalue()

def _restore_from_zip(data: bytes, overwrite: bool):
    """Return (restored, skipped). Hanya file JSON yang dikenal & valid yang dipulihkan."""
    allowed = {os.path.basename(p): p for p in _backup_paths()}
    restored, skipped = [], []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            base = os.path.basename(info.filename)
            if base not in allowed or info.file_size > BACKUP_MAX_BYTES:
                continue
            dest = allowed[base]
            if os.path.exists(dest) and not overwrite:
                skipped.append(base)
                continue
            content = zf.read(info)
            try:
                json.loads(content.decode("utf-8"))
            except Exception:
                skipped.append(base)
                continue
            tmp = f"{dest}.tmp"
            with open(tmp, "wb") as f:
                f.write(content)
            os.replace(tmp, dest)
            restored.append(base)
    return restored, skipped

async def _get_backup_channel():
    return bot.get_channel(BACKUP_CHANNEL_ID) or await bot.fetch_channel(BACKUP_CHANNEL_ID)

async def _find_latest_backup(channel):
    async for m in channel.history(limit=100):
        if (m.author.id == bot.user.id and m.content.startswith(BACKUP_PREFIX)
                and any(a.filename.endswith(".zip") for a in m.attachments)):
            return m
    return None

async def _try_restore_missing() -> bool:
    """Load file yang hilang dari backup terbaru. True kalau pengecekan sukses."""
    global _backup_ready, _last_backup_hash
    try:
        ch = await _get_backup_channel()
        msg = await _find_latest_backup(ch)
        if msg:
            att = next(a for a in msg.attachments if a.filename.endswith(".zip"))
            restored, _ = _restore_from_zip(await att.read(), overwrite=False)
            print(f"[Backup] Setting di-load dari backup: {len(restored)} file ({', '.join(restored) or '-'})")
        else:
            print("[Backup] Belum ada backup di channel — mulai dari kosong.")
        _last_backup_hash = _snapshot_hash(_snapshot())
        _backup_ready = True
        return True
    except Exception as e:
        print(f"[Backup] Gagal load backup: {e}")
        return False

async def _do_backup(force: bool = False) -> str:
    """Return: ok | unchanged | empty | disabled | not_ready"""
    global _last_backup_hash
    if not BACKUP_CHANNEL_ID:
        return "disabled"
    if not _backup_ready:
        return "not_ready"  # jangan sampai backup kosong menimpa backup bagus
    snap = _snapshot()
    if not snap:
        return "empty"
    h = _snapshot_hash(snap)
    if not force and h == _last_backup_hash:
        return "unchanged"
    ch = await _get_backup_channel()
    now = datetime.datetime.now(WIB)
    file = discord.File(io.BytesIO(_build_zip(snap)), filename=f"yahaha_backup_{now:%Y%m%d_%H%M%S}.zip")
    await ch.send(
        content=f"{BACKUP_PREFIX} | {len(snap)} file | {now:%d-%m-%Y %H:%M} WIB",
        file=file
    )
    _last_backup_hash = h
    old = [m async for m in ch.history(limit=100)
           if m.author.id == bot.user.id and m.content.startswith(BACKUP_PREFIX) and m.attachments]
    for m in old[BACKUP_KEEP:]:
        try:
            await m.delete()
        except Exception:
            pass
    return "ok"

@bot.event
async def setup_hook():
    # Jalan SEBELUM bot online -> data sudah ter-load sebelum event/command pertama.
    if not BACKUP_CHANNEL_ID:
        print("[Backup] BACKUP_CHANNEL_ID belum di-set — auto save/load setting nonaktif.")
        return
    await _try_restore_missing()

@tasks.loop(minutes=BACKUP_INTERVAL_MIN)
async def auto_backup_settings():
    try:
        if not _backup_ready and not await _try_restore_missing():
            return
        await _do_backup()
    except Exception as e:
        print(f"[Backup] Auto-backup gagal: {e}")

@auto_backup_settings.before_loop
async def before_auto_backup_settings():
    await bot.wait_until_ready()

@bot.command(name="savesettings", aliases=["savesetting", "backup", "simpansetting"])
async def savesettings_cmd(ctx):
    """Simpan semua setting & data ke channel backup sekarang juga."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    if not BACKUP_CHANNEL_ID:
        return await ctx.send("⚠️ `BACKUP_CHANNEL_ID` belum di-set di environment variable.")
    try:
        if not _backup_ready and not await _try_restore_missing():
            return await ctx.send("❌ Bot belum bisa mengakses channel backup. Cek izin bot & ID channel.")
        status = await _do_backup(force=True)
    except Exception as e:
        return await ctx.send(f"❌ Backup gagal: {e}")
    if status == "ok":
        await ctx.send("💾 Semua setting & data berhasil disimpan ke channel backup.")
    elif status == "empty":
        await ctx.send("⚠️ Belum ada data untuk di-backup.")
    else:
        await ctx.send(f"⚠️ Backup tidak dijalankan ({status}).")

@bot.command(name="loadsettings", aliases=["loadsetting", "restore"])
async def loadsettings_cmd(ctx, konfirmasi: str = None):
    """Load setting dari backup terakhir. Menimpa data yang sekarang!"""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    if not BACKUP_CHANNEL_ID:
        return await ctx.send("⚠️ `BACKUP_CHANNEL_ID` belum di-set di environment variable.")
    try:
        ch = await _get_backup_channel()
        msg = await _find_latest_backup(ch)
    except Exception as e:
        return await ctx.send(f"❌ Gagal mengakses channel backup: {e}")
    if not msg:
        return await ctx.send("❌ Belum ada backup di channel backup.")

    ts = int(msg.created_at.timestamp())
    if (konfirmasi or "").lower() not in ("ya", "yes", "confirm"):
        return await ctx.send(
            f"⚠️ Backup terakhir dibuat <t:{ts}:F> (<t:{ts}:R>).\n"
            f"Load akan **menimpa** semua setting & data saat ini.\n"
            f"Ketik `!loadsettings ya` untuk lanjut."
        )
    try:
        att = next(a for a in msg.attachments if a.filename.endswith(".zip"))
        restored, skipped = _restore_from_zip(await att.read(), overwrite=True)
    except Exception as e:
        return await ctx.send(f"❌ Gagal load backup: {e}")
    global _last_backup_hash
    _last_backup_hash = _snapshot_hash(_snapshot())
    # Cache banword ada di memori -> wajib di-reset supaya data hasil load langsung dipakai
    _banword_cache["data"] = None
    _banword_cache["rx"] = {}
    await ctx.send(
        f"✅ **{len(restored)} file** berhasil di-load dari backup <t:{ts}:R>."
        + (f"\n⚠️ {len(skipped)} file dilewati (tidak valid)." if skipped else "")
        + "\n📌 Kalau ada panel ticket/giveaway/poll yang tombolnya belum jalan, restart bot sekali."
    )

# ═══════════════════════════════════════════════════════
#  MCASH — SISTEM COIN
#  1000 MCASH = Rp1.000  (1 MCASH = Rp1)
#
#  User   : !createwallet  !mcash  !withdraw  !submitclip  !rain
#  Admin  : !gift  !takecoin  !setclipchannel  !setwdchannel  !mcashconfig
#  Alur   : Submit clip → masuk channel clip → Admin ACC + input coin → saldo user
#           Withdraw (DANA/ShopeePay/OVO) → notif admin → Admin transfer / tolak (refund)
#
#  ATURAN: jangan ada `await` di antara _mc_load() dan _mc_save(), supaya saldo
#  tidak bisa saling menimpa saat banyak command jalan bersamaan.
# ═══════════════════════════════════════════════════════
import time as _mc_time

MCASH_FILE              = _p("mcash.json")
MCASH_MIN_WD            = int(os.environ.get("MCASH_MIN_WD", "10000") or 10000)  # minimal withdraw (MCASH)
MCASH_RAIN_WINDOW       = 10 * 60   # user dianggap aktif jika chat dalam 10 menit terakhir
MCASH_MAX_PENDING_CLIPS = 5         # maks clip menunggu review per user
MCASH_EWALLETS = {
    "DANA":      ("DANA",      "💙"),
    "SHOPEEPAY": ("ShopeePay", "🧡"),
    "OVO":       ("OVO",       "💜"),
}

_mcash_activity: dict = {}   # {channel_id: {user_id: last_message_epoch}}


# ── Helpers ─────────────────────────────────────────────
def _mc_fmt(n) -> str:
    return f"{int(n):,}".replace(",", ".")

def _mc_idr(n) -> str:
    return "Rp" + _mc_fmt(n)

def _mc_now() -> int:
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())

def _mc_parse(raw):
    """'5000' / '5.000' / '5k' → int. None kalau tidak valid / <= 0."""
    if raw is None:
        return None
    s = str(raw).strip().lower().replace(" ", "")
    mult = 1
    if s.endswith("k"):
        mult, s = 1000, s[:-1]
    s = s.replace(".", "").replace(",", "")
    if not s.isdigit():
        return None
    v = int(s) * mult
    return v if v > 0 else None

def _mc_load() -> dict:
    d = load_json(MCASH_FILE, default={})
    d.setdefault("wallets", {})
    d.setdefault("clips", {})
    d.setdefault("withdraws", {})
    d.setdefault("config", {})
    d.setdefault("tx", [])
    d.setdefault("next_clip_id", 1)
    d.setdefault("next_wd_id", 1)
    return d

def _mc_save(d: dict):
    d["tx"] = d["tx"][-2000:]
    save_json(MCASH_FILE, d)

def _mc_wallet(d: dict, uid, create: bool = False):
    k = str(uid)
    w = d["wallets"].get(k)
    if w is None and create:
        w = {"balance": 0, "earned": 0, "withdrawn": 0, "created": _mc_now()}
        d["wallets"][k] = w
    return w

def _mc_add(d: dict, uid, amount: int, kind: str, note: str = ""):
    """Tambah/kurangi saldo + catat mutasi. Wallet dibuat otomatis kalau belum ada."""
    w = _mc_wallet(d, uid, create=True)
    w["balance"] += amount
    if amount > 0 and kind != "refund":
        w["earned"] += amount
    d["tx"].append({"uid": str(uid), "amt": amount, "type": kind,
                    "note": note[:120], "ts": _mc_now(), "bal": w["balance"]})

async def _mc_get_channel(cid):
    return bot.get_channel(int(cid)) or await bot.fetch_channel(int(cid))

async def _mc_dm(uid, embed):
    try:
        u = bot.get_user(int(uid)) or await bot.fetch_user(int(uid))
        await u.send(embed=embed)
    except Exception:
        pass

def _mc_track(message):
    """Catat aktivitas chat untuk sistem Rain."""
    if message.guild is None or message.author.bot:
        return
    ch = _mcash_activity.setdefault(message.channel.id, {})
    now = _mc_time.time()
    ch[message.author.id] = now
    if len(ch) > 500:  # buang yang sudah kadaluarsa
        for uid in [u for u, t in ch.items() if now - t > MCASH_RAIN_WINDOW]:
            del ch[uid]

def _mc_wallet_embed(member, d: dict) -> discord.Embed:
    w = d["wallets"][str(member.id)]
    e = discord.Embed(title="💰 MCASH Wallet", color=discord.Color.gold(),
                      timestamp=datetime.datetime.now(datetime.timezone.utc))
    e.set_author(name=member.display_name, icon_url=member.display_avatar.url)
    e.description = f"# {_mc_fmt(w['balance'])} MCASH\n≈ **{_mc_idr(w['balance'])}**"
    e.add_field(name="Total Didapat",   value=f"{_mc_fmt(w['earned'])} MCASH",    inline=True)
    e.add_field(name="Total Withdraw",  value=f"{_mc_fmt(w['withdrawn'])} MCASH", inline=True)
    recent = [t for t in d["tx"] if t["uid"] == str(member.id)][-5:][::-1]
    if recent:
        lines = [f"`{'+' if t['amt'] > 0 else ''}{_mc_fmt(t['amt'])}` • {t['note'] or t['type']}" for t in recent]
        e.add_field(name="Mutasi Terakhir", value="\n".join(lines), inline=False)
    e.set_footer(text=f"1000 MCASH = Rp1.000 • Minimal withdraw {_mc_fmt(MCASH_MIN_WD)} MCASH")
    return e

def _mc_clip_embed(clip: dict, status: str = "pending", reward=None, by=None, reason=None) -> discord.Embed:
    color = {"pending": discord.Color.orange(), "accepted": discord.Color.green(),
             "rejected": discord.Color.red()}[status]
    title = {"pending": "🎬 Clip Baru — Menunggu Review",
             "accepted": "✅ Clip di-ACC", "rejected": "❌ Clip di-Reject"}[status]
    e = discord.Embed(title=title, color=color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    e.add_field(name="Pengirim", value=f"<@{clip['uid']}>", inline=True)
    e.add_field(name="Clip ID",  value=f"#{clip['id']}",    inline=True)
    e.add_field(name="Clip", value=(clip["link"][:1000] if clip.get("link") else "📎 Video terlampir"), inline=False)
    if clip.get("note"):
        e.add_field(name="Catatan", value=clip["note"][:500], inline=False)
    if status == "accepted":
        e.add_field(name="Reward", value=f"**+{_mc_fmt(reward)} MCASH** (≈ {_mc_idr(reward)})", inline=True)
    if by:
        e.add_field(name="Direview oleh", value=f"<@{by}>", inline=True)
    if status == "rejected" and reason:
        e.add_field(name="Alasan", value=reason[:500], inline=False)
    e.set_footer(text=f"Clip #{clip['id']}")
    return e

async def _mc_edit_review(rec: dict, embed: discord.Embed):
    """Update pesan review (clip / withdraw) → embed baru, tombol dihapus."""
    if not rec.get("message_id"):
        return
    try:
        ch = await _mc_get_channel(rec["channel_id"])
        msg = await ch.fetch_message(rec["message_id"])
        await msg.edit(embed=embed, view=None)
    except Exception:
        pass


# ═══════════════════════════════════════════════════════
#  CLIP — submit → review admin
# ═══════════════════════════════════════════════════════
async def _mc_submit_clip(user, link, note, attachment=None):
    """Return (ok: bool, pesan: str)."""
    cfg_ch = _mc_load()["config"].get("clip_channel")
    if not cfg_ch:
        return False, "⚠️ Channel clip belum diatur. Minta admin ketik `!setclipchannel #channel`."
    try:
        ch = await _mc_get_channel(cfg_ch)
    except Exception:
        return False, "⚠️ Channel clip tidak ditemukan / bot tidak punya akses."

    # — bagian sync: validasi + simpan record (tanpa await) —
    d = _mc_load()
    if not _mc_wallet(d, user.id):
        return False, "❌ Kamu belum punya wallet. Ketik `!createwallet` dulu."
    pending = sum(1 for c in d["clips"].values() if c["uid"] == user.id and c["status"] == "pending")
    if pending >= MCASH_MAX_PENDING_CLIPS:
        return False, f"⏳ Kamu masih punya {pending} clip yang menunggu review. Tunggu admin memprosesnya dulu."
    cid = d["next_clip_id"]
    d["next_clip_id"] += 1
    clip = {"id": cid, "uid": user.id, "link": link, "note": note, "status": "pending",
            "ts": _mc_now(), "channel_id": ch.id, "message_id": None}
    d["clips"][str(cid)] = clip
    _mc_save(d)

    # — kirim ke channel clip —
    try:
        file = await attachment.to_file() if attachment else None
        msg = await ch.send(content=link or None, embed=_mc_clip_embed(clip), file=file,
                            view=ClipReviewView(cid))
    except Exception as e:
        d = _mc_load()
        d["clips"].pop(str(cid), None)
        _mc_save(d)
        return False, f"❌ Gagal mengirim clip ke channel: {e}"

    d = _mc_load()
    if str(cid) in d["clips"]:
        d["clips"][str(cid)]["message_id"] = msg.id
        _mc_save(d)
    return True, f"✅ Clip **#{cid}** terkirim! Tunggu admin me-review ya."


class ClipSubmitModal(discord.ui.Modal, title="Submit Clip"):
    def __init__(self):
        super().__init__()
        self.link = discord.ui.TextInput(label="Link Clip", placeholder="https://...", max_length=500)
        self.note = discord.ui.TextInput(label="Catatan (opsional)", required=False,
                                         style=discord.TextStyle.paragraph, max_length=300)
        self.add_item(self.link)
        self.add_item(self.note)

    async def on_submit(self, interaction: discord.Interaction):
        link = self.link.value.strip()
        if not re.match(r"^https?://\S+$", link):
            return await interaction.response.send_message("❌ Link tidak valid (harus diawali http/https).", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        ok, msg = await _mc_submit_clip(interaction.user, link, self.note.value.strip())
        await interaction.followup.send(msg, ephemeral=True)


class ClipAccModal(discord.ui.Modal, title="ACC Clip"):
    def __init__(self, clip_id):
        super().__init__()
        self.clip_id = str(clip_id)
        self.coin = discord.ui.TextInput(label="Jumlah MCASH untuk user", placeholder="contoh: 5000", max_length=12)
        self.add_item(self.coin)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Hanya admin.", ephemeral=True)
        amt = _mc_parse(self.coin.value)
        if not amt:
            return await interaction.response.send_message("❌ Jumlah tidak valid.", ephemeral=True)
        d = _mc_load()
        clip = d["clips"].get(self.clip_id)
        if not clip or clip["status"] != "pending":
            return await interaction.response.send_message("⚠️ Clip ini sudah diproses.", ephemeral=True)
        clip.update(status="accepted", reward=amt, by=interaction.user.id, decided=_mc_now())
        _mc_add(d, clip["uid"], amt, "clip", f"Reward clip #{clip['id']}")
        _mc_save(d)
        bal = d["wallets"][str(clip["uid"])]["balance"]
        embed = _mc_clip_embed(clip, "accepted", reward=amt, by=interaction.user.id)
        await interaction.response.send_message(
            f"✅ Clip #{clip['id']} di-ACC. <@{clip['uid']}> menerima **{_mc_fmt(amt)} MCASH**.", ephemeral=True)
        await _mc_edit_review(clip, embed)
        dm = discord.Embed(title="🎉 Clip kamu di-ACC!", color=discord.Color.green(),
                           description=f"Clip **#{clip['id']}** diterima.\n**+{_mc_fmt(amt)} MCASH** masuk ke wallet kamu.\n"
                                       f"Saldo sekarang: **{_mc_fmt(bal)} MCASH** (≈ {_mc_idr(bal)})")
        await _mc_dm(clip["uid"], dm)


class ClipRejectModal(discord.ui.Modal, title="Reject Clip"):
    def __init__(self, clip_id):
        super().__init__()
        self.clip_id = str(clip_id)
        self.reason = discord.ui.TextInput(label="Alasan (opsional)", required=False,
                                           style=discord.TextStyle.paragraph, max_length=300)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Hanya admin.", ephemeral=True)
        d = _mc_load()
        clip = d["clips"].get(self.clip_id)
        if not clip or clip["status"] != "pending":
            return await interaction.response.send_message("⚠️ Clip ini sudah diproses.", ephemeral=True)
        reason = self.reason.value.strip() or "Tidak ada alasan."
        clip.update(status="rejected", reason=reason, by=interaction.user.id, decided=_mc_now())
        _mc_save(d)
        embed = _mc_clip_embed(clip, "rejected", by=interaction.user.id, reason=reason)
        await interaction.response.send_message(f"❌ Clip #{clip['id']} di-reject.", ephemeral=True)
        await _mc_edit_review(clip, embed)
        await _mc_dm(clip["uid"], discord.Embed(
            title="❌ Clip kamu ditolak", color=discord.Color.red(),
            description=f"Clip **#{clip['id']}** tidak diterima.\n**Alasan:** {reason}"))


class ClipReviewView(View):
    """Tombol review clip (persistent — tetap jalan setelah bot restart)."""
    def __init__(self, clip_id):
        super().__init__(timeout=None)
        self.clip_id = str(clip_id)
        acc = Button(label="ACC + Input Coin", emoji="✅", style=discord.ButtonStyle.success,
                     custom_id=f"mcash_clipacc:{clip_id}")
        rej = Button(label="Reject", emoji="❌", style=discord.ButtonStyle.danger,
                     custom_id=f"mcash_cliprej:{clip_id}")
        acc.callback = self._acc
        rej.callback = self._rej
        self.add_item(acc)
        self.add_item(rej)

    async def _guard(self, interaction) -> bool:
        if not is_admin(interaction.user):
            await interaction.response.send_message("❌ Hanya admin.", ephemeral=True)
            return False
        clip = _mc_load()["clips"].get(self.clip_id)
        if not clip or clip["status"] != "pending":
            await interaction.response.send_message("⚠️ Clip ini sudah diproses.", ephemeral=True)
            return False
        return True

    async def _acc(self, interaction: discord.Interaction):
        if await self._guard(interaction):
            await interaction.response.send_modal(ClipAccModal(self.clip_id))

    async def _rej(self, interaction: discord.Interaction):
        if await self._guard(interaction):
            await interaction.response.send_modal(ClipRejectModal(self.clip_id))


# ═══════════════════════════════════════════════════════
#  WITHDRAW — DANA / ShopeePay / OVO
# ═══════════════════════════════════════════════════════
async def _mc_notify_wd(rec: dict, user) -> bool:
    """Kirim notif withdraw ke admin (channel WD kalau di-set, kalau tidak DM owner)."""
    label, emoji = MCASH_EWALLETS[rec["method"]]
    e = discord.Embed(title="💸 Permintaan Withdraw", color=discord.Color.orange(),
                      timestamp=datetime.datetime.now(datetime.timezone.utc))
    e.add_field(name="User",     value=f"{user.mention} (`{user.id}`)", inline=False)
    e.add_field(name="E-Wallet", value=f"{emoji} **{label}**",           inline=True)
    e.add_field(name="Nomor",    value=f"`{rec['number']}`",             inline=True)
    e.add_field(name="Atas Nama", value=rec["name"] or "-",              inline=True)
    e.add_field(name="Jumlah",   value=f"**{_mc_fmt(rec['amount'])} MCASH** → transfer **{_mc_idr(rec['amount'])}**", inline=False)
    e.set_footer(text=f"Withdraw #{rec['id']}")
    try:
        wd_ch = _mc_load()["config"].get("wd_channel")
        target = None
        if wd_ch:
            try:
                target = await _mc_get_channel(wd_ch)
            except Exception:
                target = None
        if target is None:
            target = bot.get_user(OWNER_ID) or await bot.fetch_user(OWNER_ID)
        msg = await target.send(embed=e, view=WithdrawAdminView(rec["id"]))
    except Exception as ex:
        print(f"[MCASH] Gagal kirim notif withdraw #{rec['id']}: {ex}")
        return False
    d = _mc_load()
    r = d["withdraws"].get(str(rec["id"]))
    if r:
        r["message_id"], r["channel_id"] = msg.id, msg.channel.id
        _mc_save(d)
    return True


def _mc_wd_embed(rec: dict, status: str, by=None, reason=None) -> discord.Embed:
    label, emoji = MCASH_EWALLETS[rec["method"]]
    color = discord.Color.green() if status == "paid" else discord.Color.red()
    e = discord.Embed(title="✅ Withdraw Selesai (Sudah Ditransfer)" if status == "paid" else "❌ Withdraw Ditolak (Saldo Dikembalikan)",
                      color=color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    e.add_field(name="User",      value=f"<@{rec['uid']}>", inline=True)
    e.add_field(name="E-Wallet",  value=f"{emoji} {label} • `{rec['number']}`", inline=True)
    e.add_field(name="Atas Nama", value=rec["name"] or "-", inline=True)
    e.add_field(name="Jumlah",    value=f"{_mc_fmt(rec['amount'])} MCASH ({_mc_idr(rec['amount'])})", inline=False)
    if by:
        e.add_field(name="Diproses oleh", value=f"<@{by}>", inline=True)
    if reason:
        e.add_field(name="Alasan", value=reason[:500], inline=False)
    e.set_footer(text=f"Withdraw #{rec['id']}")
    return e


class WithdrawModal(discord.ui.Modal, title="Withdraw MCASH"):
    def __init__(self, method: str):
        super().__init__()
        self.method = method
        label = MCASH_EWALLETS[method][0]
        self.number = discord.ui.TextInput(label=f"Nomor {label}", placeholder="08xxxxxxxxxx", min_length=8, max_length=16)
        self.name   = discord.ui.TextInput(label="Atas Nama", placeholder="Nama sesuai akun e-wallet", max_length=50)
        self.amount = discord.ui.TextInput(label="Jumlah MCASH", placeholder=f"minimal {_mc_fmt(MCASH_MIN_WD)}", max_length=12)
        for i in (self.number, self.name, self.amount):
            self.add_item(i)

    async def on_submit(self, interaction: discord.Interaction):
        number = re.sub(r"[\s\-]", "", self.number.value)
        if not number.isdigit() or not 8 <= len(number) <= 15:
            return await interaction.response.send_message("❌ Nomor e-wallet tidak valid (angka saja, 8–15 digit).", ephemeral=True)
        amt = _mc_parse(self.amount.value)
        if not amt:
            return await interaction.response.send_message("❌ Jumlah tidak valid.", ephemeral=True)
        if amt < MCASH_MIN_WD:
            return await interaction.response.send_message(f"❌ Minimal withdraw **{_mc_fmt(MCASH_MIN_WD)} MCASH**.", ephemeral=True)

        # — sync: cek saldo, tahan saldo, simpan record —
        d = _mc_load()
        w = _mc_wallet(d, interaction.user.id)
        if not w:
            return await interaction.response.send_message("❌ Kamu belum punya wallet. Ketik `!createwallet`.", ephemeral=True)
        if w["balance"] < amt:
            return await interaction.response.send_message(
                f"❌ Saldo tidak cukup. Saldo kamu **{_mc_fmt(w['balance'])} MCASH**.", ephemeral=True)
        wid = d["next_wd_id"]
        d["next_wd_id"] += 1
        label = MCASH_EWALLETS[self.method][0]
        _mc_add(d, interaction.user.id, -amt, "wd", f"Withdraw #{wid} → {label}")
        rec = {"id": wid, "uid": interaction.user.id, "method": self.method, "number": number,
               "name": self.name.value.strip(), "amount": amt, "status": "pending",
               "ts": _mc_now(), "message_id": None, "channel_id": None}
        d["withdraws"][str(wid)] = rec
        _mc_save(d)

        await interaction.response.defer(ephemeral=True)
        if await _mc_notify_wd(rec, interaction.user):
            await interaction.followup.send(
                f"✅ Permintaan withdraw **#{wid}** terkirim ke admin.\n"
                f"**{_mc_fmt(amt)} MCASH** → {label} `{number}` ({_mc_idr(amt)}).\n"
                f"Saldo ditahan sampai admin memproses. Kamu akan dapat DM saat selesai.", ephemeral=True)
        else:  # admin tidak bisa dihubungi → kembalikan saldo
            d = _mc_load()
            r = d["withdraws"].get(str(wid))
            if r and r["status"] == "pending":
                r["status"] = "failed"
                _mc_add(d, interaction.user.id, amt, "refund", f"Withdraw #{wid} gagal dikirim")
                _mc_save(d)
            await interaction.followup.send(
                "❌ Gagal menghubungi admin. Saldo kamu sudah dikembalikan, coba lagi nanti.", ephemeral=True)


class WithdrawSelectView(View):
    def __init__(self, uid: int):
        super().__init__(timeout=300)
        self.uid = uid
        self.sel = Select(placeholder="Pilih E-Wallet tujuan...", options=[
            discord.SelectOption(label=lbl, value=key, emoji=emo) for key, (lbl, emo) in MCASH_EWALLETS.items()
        ])
        self.sel.callback = self._pick
        self.add_item(self.sel)

    async def _pick(self, interaction: discord.Interaction):
        if interaction.user.id != self.uid:
            return await interaction.response.send_message("❌ Ini bukan menu kamu.", ephemeral=True)
        await interaction.response.send_modal(WithdrawModal(self.sel.values[0]))


class WithdrawRejectModal(discord.ui.Modal, title="Tolak Withdraw"):
    def __init__(self, wid):
        super().__init__()
        self.wid = str(wid)
        self.reason = discord.ui.TextInput(label="Alasan (opsional)", required=False,
                                           style=discord.TextStyle.paragraph, max_length=300)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Hanya admin.", ephemeral=True)
        d = _mc_load()
        rec = d["withdraws"].get(self.wid)
        if not rec or rec["status"] != "pending":
            return await interaction.response.send_message("⚠️ Withdraw ini sudah diproses.", ephemeral=True)
        reason = self.reason.value.strip() or "Tidak ada alasan."
        rec.update(status="rejected", reason=reason, by=interaction.user.id, decided=_mc_now())
        _mc_add(d, rec["uid"], rec["amount"], "refund", f"Withdraw #{rec['id']} ditolak")
        _mc_save(d)
        await interaction.response.send_message(
            f"❌ Withdraw #{rec['id']} ditolak, **{_mc_fmt(rec['amount'])} MCASH** dikembalikan ke <@{rec['uid']}>.", ephemeral=True)
        await _mc_edit_review(rec, _mc_wd_embed(rec, "rejected", by=interaction.user.id, reason=reason))
        await _mc_dm(rec["uid"], discord.Embed(
            title="❌ Withdraw ditolak", color=discord.Color.red(),
            description=f"Withdraw **#{rec['id']}** ditolak.\n**Alasan:** {reason}\n"
                        f"**{_mc_fmt(rec['amount'])} MCASH** sudah dikembalikan ke wallet kamu."))


class WithdrawAdminView(View):
    """Tombol admin untuk withdraw (persistent)."""
    def __init__(self, wid):
        super().__init__(timeout=None)
        self.wid = str(wid)
        pay = Button(label="Sudah Ditransfer", emoji="✅", style=discord.ButtonStyle.success,
                     custom_id=f"mcash_wdpay:{wid}")
        rej = Button(label="Tolak & Refund", emoji="❌", style=discord.ButtonStyle.danger,
                     custom_id=f"mcash_wdrej:{wid}")
        pay.callback = self._pay
        rej.callback = self._rej
        self.add_item(pay)
        self.add_item(rej)

    async def _pay(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Hanya admin.", ephemeral=True)
        d = _mc_load()
        rec = d["withdraws"].get(self.wid)
        if not rec or rec["status"] != "pending":
            return await interaction.response.send_message("⚠️ Withdraw ini sudah diproses.", ephemeral=True)
        rec.update(status="paid", by=interaction.user.id, decided=_mc_now())
        w = _mc_wallet(d, rec["uid"], create=True)
        w["withdrawn"] += rec["amount"]
        _mc_save(d)
        await interaction.response.send_message(f"✅ Withdraw #{rec['id']} ditandai selesai.", ephemeral=True)
        await _mc_edit_review(rec, _mc_wd_embed(rec, "paid", by=interaction.user.id))
        label = MCASH_EWALLETS[rec["method"]][0]
        await _mc_dm(rec["uid"], discord.Embed(
            title="✅ Withdraw berhasil", color=discord.Color.green(),
            description=f"Withdraw **#{rec['id']}** sebesar **{_mc_idr(rec['amount'])}** sudah ditransfer ke {label} `{rec['number']}`."))

    async def _rej(self, interaction: discord.Interaction):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("❌ Hanya admin.", ephemeral=True)
        rec = _mc_load()["withdraws"].get(self.wid)
        if not rec or rec["status"] != "pending":
            return await interaction.response.send_message("⚠️ Withdraw ini sudah diproses.", ephemeral=True)
        await interaction.response.send_modal(WithdrawRejectModal(self.wid))


# ═══════════════════════════════════════════════════════
#  PANEL WALLET (muncul setelah !createwallet)
# ═══════════════════════════════════════════════════════
async def _mc_withdraw_menu(send, user) -> None:
    d = _mc_load()
    w = _mc_wallet(d, user.id)
    if not w:
        return await send("❌ Kamu belum punya wallet. Ketik `!createwallet`.")
    if w["balance"] < MCASH_MIN_WD:
        return await send(f"❌ Saldo belum cukup. Minimal withdraw **{_mc_fmt(MCASH_MIN_WD)} MCASH**, "
                          f"saldo kamu **{_mc_fmt(w['balance'])} MCASH**.")
    await send("💸 **Withdraw MCASH** — pilih e-wallet tujuan:", view=WithdrawSelectView(user.id))


class WalletPanelView(View):
    def __init__(self, uid: int):
        super().__init__(timeout=600)
        self.uid = uid

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.uid:
            await interaction.response.send_message("❌ Ini bukan wallet kamu. Ketik `!createwallet` untuk punya sendiri.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Saldo", emoji="💰", style=discord.ButtonStyle.primary)
    async def saldo_btn(self, interaction: discord.Interaction, button: Button):
        d = _mc_load()
        if not _mc_wallet(d, interaction.user.id):
            return await interaction.response.send_message("❌ Wallet tidak ditemukan.", ephemeral=True)
        await interaction.response.send_message(embed=_mc_wallet_embed(interaction.user, d), ephemeral=True)

    @discord.ui.button(label="Withdraw", emoji="💸", style=discord.ButtonStyle.success)
    async def wd_btn(self, interaction: discord.Interaction, button: Button):
        async def _send(*a, **kw):
            await interaction.response.send_message(*a, ephemeral=True, **kw)
        await _mc_withdraw_menu(_send, interaction.user)

    @discord.ui.button(label="Submit Clip", emoji="🎬", style=discord.ButtonStyle.secondary)
    async def clip_btn(self, interaction: discord.Interaction, button: Button):
        if not _mc_wallet(_mc_load(), interaction.user.id):
            return await interaction.response.send_message("❌ Wallet tidak ditemukan.", ephemeral=True)
        await interaction.response.send_modal(ClipSubmitModal())


def mcash_register_views():
    """Dipanggil di on_ready: aktifkan lagi tombol review yang masih pending setelah restart."""
    d = _mc_load()
    for cid, c in d["clips"].items():
        if c["status"] == "pending" and c.get("message_id"):
            bot.add_view(ClipReviewView(cid))
    for wid, r in d["withdraws"].items():
        if r["status"] == "pending" and r.get("message_id"):
            bot.add_view(WithdrawAdminView(wid))


# ═══════════════════════════════════════════════════════
#  COMMANDS — USER
# ═══════════════════════════════════════════════════════
@bot.command(name="createwallet", aliases=["buatwallet", "daftarwallet"])
async def createwallet_cmd(ctx):
    """Buat wallet MCASH (semua user). Menampilkan panel Saldo / Withdraw / Submit Clip."""
    d = _mc_load()
    new = _mc_wallet(d, ctx.author.id) is None
    if new:
        _mc_wallet(d, ctx.author.id, create=True)
        _mc_save(d)
    d = _mc_load()
    head = "🎉 Wallet **MCASH** kamu berhasil dibuat!" if new else "✅ Kamu sudah punya wallet MCASH."
    await ctx.send(head, embed=_mc_wallet_embed(ctx.author, d), view=WalletPanelView(ctx.author.id))


@bot.command(name="mcash", aliases=["saldo", "balance", "wallet", "bal"])
async def mcash_cmd(ctx, member: discord.Member = None):
    """Cek saldo. Admin bisa cek saldo user lain."""
    target = ctx.author
    if member and member.id != ctx.author.id:
        if not is_admin(ctx.author):
            return await ctx.send("❌ Kamu hanya bisa cek saldo sendiri.", delete_after=8)
        target = member
    d = _mc_load()
    if not _mc_wallet(d, target.id):
        who = "Kamu" if target.id == ctx.author.id else target.display_name
        return await ctx.send(f"❌ {who} belum punya wallet. Ketik `!createwallet`.")
    await ctx.send(embed=_mc_wallet_embed(target, d))


@bot.command(name="withdraw", aliases=["wd", "tarik"])
async def withdraw_cmd(ctx):
    """Tarik MCASH ke DANA / ShopeePay / OVO."""
    await _mc_withdraw_menu(ctx.send, ctx.author)


@bot.command(name="submitclip", aliases=["clip", "kirimclip"])
async def submitclip_cmd(ctx, link: str = None, *, catatan: str = ""):
    """!submitclip <link> [catatan]  — atau lampirkan file video."""
    att = ctx.message.attachments[0] if ctx.message.attachments else None
    if not att and not (link and re.match(r"^https?://\S+$", link)):
        return await ctx.send("❌ Format: `!submitclip <link clip> [catatan]` atau lampirkan file video.", delete_after=10)
    if att and link and not re.match(r"^https?://\S+$", link):  # teks biasa → jadikan catatan
        catatan, link = f"{link} {catatan}".strip(), None
    ok, msg = await _mc_submit_clip(ctx.author, link if (link and re.match(r"^https?://\S+$", link)) else None,
                                    catatan.strip(), att)
    await ctx.send(msg, delete_after=15 if ok else 12)
    if ok and ctx.guild:
        try:
            await ctx.message.delete()
        except Exception:
            pass


@bot.command(name="rain")
async def rain_cmd(ctx, jumlah: str = None, max_penerima: str = None):
    """!rain <total MCASH> [maks penerima] — bagi rata ke user yang aktif chat di channel ini (10 menit terakhir)."""
    if ctx.guild is None:
        return await ctx.send("❌ Rain hanya bisa di server.")
    total = _mc_parse(jumlah)
    limit = _mc_parse(max_penerima) if max_penerima else None
    if not total or (max_penerima and not limit):
        return await ctx.send("❌ Format: `!rain <total MCASH> [maks penerima]`  contoh: `!rain 5000` atau `!rain 5000 10`")

    now = _mc_time.time()
    act = _mcash_activity.get(ctx.channel.id, {})
    members = [m for m in (ctx.guild.get_member(u) for u, t in act.items()
                           if now - t <= MCASH_RAIN_WINDOW and u != ctx.author.id) if m and not m.bot]
    if not members:
        return await ctx.send("🌵 Tidak ada user lain yang aktif di channel ini dalam 10 menit terakhir.")
    if limit and len(members) > limit:
        members = random.sample(members, limit)
    per = total // len(members)
    if per < 1:
        return await ctx.send(f"❌ **{_mc_fmt(total)} MCASH** terlalu kecil untuk **{len(members)}** user aktif (minimal 1 MCASH/orang).")
    spent = per * len(members)

    d = _mc_load()
    admin = is_admin(ctx.author)
    if not admin:  # user biasa → pakai saldo sendiri. Admin → gratis (dari admin).
        w = _mc_wallet(d, ctx.author.id)
        if not w:
            return await ctx.send("❌ Kamu belum punya wallet. Ketik `!createwallet`.")
        if w["balance"] < spent:
            return await ctx.send(f"❌ Saldo tidak cukup. Butuh **{_mc_fmt(spent)} MCASH**, saldo kamu **{_mc_fmt(w['balance'])} MCASH**.")
        _mc_add(d, ctx.author.id, -spent, "rain_out", f"Rain ke {len(members)} user")
    for m in members:
        _mc_add(d, m.id, per, "rain_in", f"Rain dari {ctx.author.display_name}")
    _mc_save(d)

    names = " ".join(m.mention for m in members)
    if len(names) > 1500:
        shown = ""
        for m in members:
            if len(shown) + len(m.mention) > 1400:
                break
            shown += m.mention + " "
        names = shown + f"…dan {len(members) - shown.count('<@')} lainnya"
    e = discord.Embed(
        title="🌧️ MCASH RAIN!",
        description=(f"{ctx.author.mention} menghujani **{len(members)}** user aktif!\n\n"
                     f"💰 Tiap orang dapat **{_mc_fmt(per)} MCASH** (≈ {_mc_idr(per)})\n"
                     f"📦 Total dibagikan: **{_mc_fmt(spent)} MCASH**\n\n{names}"),
        color=discord.Color.blue(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    e.set_footer(text="Cek saldo dengan !mcash" + (" • Rain dari admin" if admin else ""))
    await ctx.send(embed=e)


# ═══════════════════════════════════════════════════════
#  COMMANDS — ADMIN
# ═══════════════════════════════════════════════════════
@bot.command(name="gift", aliases=["giftcoin", "givecoin"])
async def gift_cmd(ctx, member: discord.Member = None, jumlah: str = None, *, alasan: str = "Gift dari admin"):
    """!gift @user <jumlah> [alasan]"""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    amt = _mc_parse(jumlah)
    if not member or not amt or member.bot:
        return await ctx.send("❌ Format: `!gift @user <jumlah> [alasan]`  contoh: `!gift @budi 5000 hadiah event`")
    d = _mc_load()
    _mc_add(d, member.id, amt, "gift", alasan)
    _mc_save(d)
    bal = d["wallets"][str(member.id)]["balance"]
    await ctx.send(embed=discord.Embed(
        title="🎁 Gift MCASH",
        description=(f"{member.mention} menerima **{_mc_fmt(amt)} MCASH** (≈ {_mc_idr(amt)}) dari {ctx.author.mention}\n"
                     f"📝 {alasan}\n💰 Saldo sekarang: **{_mc_fmt(bal)} MCASH**"),
        color=discord.Color.magenta()))


@bot.command(name="takecoin", aliases=["removecoin"])
async def takecoin_cmd(ctx, member: discord.Member = None, jumlah: str = None, *, alasan: str = "Dikurangi admin"):
    """!takecoin @user <jumlah> [alasan] — koreksi saldo."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    amt = _mc_parse(jumlah)
    if not member or not amt:
        return await ctx.send("❌ Format: `!takecoin @user <jumlah> [alasan]`")
    d = _mc_load()
    w = _mc_wallet(d, member.id)
    if not w:
        return await ctx.send("❌ User itu belum punya wallet.")
    amt = min(amt, w["balance"])
    _mc_add(d, member.id, -amt, "takecoin", alasan)
    _mc_save(d)
    await ctx.send(f"✅ **{_mc_fmt(amt)} MCASH** dikurangi dari {member.mention}. Saldo sekarang **{_mc_fmt(w['balance'])} MCASH**.")


@bot.command(name="setclipchannel")
async def setclipchannel_cmd(ctx, channel: discord.TextChannel = None):
    """!setclipchannel #channel — channel tempat clip masuk untuk di-review."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    if not channel:
        return await ctx.send("❌ Format: `!setclipchannel #channel`")
    d = _mc_load()
    d["config"]["clip_channel"] = channel.id
    _mc_save(d)
    await ctx.send(f"✅ Clip yang di-submit akan masuk ke {channel.mention}.")


@bot.command(name="setwdchannel")
async def setwdchannel_cmd(ctx, channel: discord.TextChannel = None):
    """!setwdchannel #channel — channel notif withdraw (kosong = DM owner)."""
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    d = _mc_load()
    if channel:
        d["config"]["wd_channel"] = channel.id
        _mc_save(d)
        return await ctx.send(f"✅ Notif withdraw akan dikirim ke {channel.mention}.")
    d["config"].pop("wd_channel", None)
    _mc_save(d)
    await ctx.send("✅ Channel withdraw dihapus — notif withdraw dikirim lewat **DM owner**.")


@bot.command(name="mcashconfig", aliases=["mcashsetting"])
async def mcashconfig_cmd(ctx):
    if not is_admin(ctx.author):
        return await ctx.send("❌ Hanya **Admin / Owner**.", delete_after=8)
    d = _mc_load()
    c = d["config"]
    pend_clip = sum(1 for x in d["clips"].values() if x["status"] == "pending")
    pend_wd   = sum(1 for x in d["withdraws"].values() if x["status"] == "pending")
    total     = sum(w["balance"] for w in d["wallets"].values())
    e = discord.Embed(title="⚙️ MCASH Config", color=discord.Color.blurple())
    e.add_field(name="Channel Clip",     value=f"<#{c['clip_channel']}>" if c.get("clip_channel") else "❌ belum diatur (`!setclipchannel`)", inline=False)
    e.add_field(name="Channel Withdraw", value=f"<#{c['wd_channel']}>" if c.get("wd_channel") else "DM owner (`!setwdchannel`)", inline=False)
    e.add_field(name="Wallet", value=str(len(d["wallets"])), inline=True)
    e.add_field(name="Total Saldo Beredar", value=f"{_mc_fmt(total)} MCASH", inline=True)
    e.add_field(name="Clip Pending", value=str(pend_clip), inline=True)
    e.add_field(name="WD Pending", value=str(pend_wd), inline=True)
    e.add_field(name="Min. Withdraw", value=f"{_mc_fmt(MCASH_MIN_WD)} MCASH", inline=True)
    await ctx.send(embed=e)


@bot.command(name="mcashhelp", aliases=["helpmcash"])
async def mcashhelp_cmd(ctx):
    e = discord.Embed(title="💰 MCASH — Bantuan", color=discord.Color.gold(),
                      description="**1000 MCASH = Rp1.000**")
    e.add_field(name="👤 User", inline=False, value=(
        "`!createwallet` — buat wallet & buka panel\n"
        "`!mcash` — cek saldo\n"
        "`!submitclip <link>` — kirim clip (atau lampirkan video)\n"
        f"`!withdraw` — tarik ke DANA / ShopeePay / OVO (min {_mc_fmt(MCASH_MIN_WD)})\n"
        "`!rain <total> [maks penerima]` — bagi MCASH ke user aktif 10 menit terakhir"))
    if is_admin(ctx.author):
        e.add_field(name="🛡️ Admin", inline=False, value=(
            "`!gift @user <jumlah> [alasan]`\n"
            "`!takecoin @user <jumlah> [alasan]`\n"
            "`!setclipchannel #channel`\n"
            "`!setwdchannel #channel` (kosong = DM owner)\n"
            "`!mcashconfig`\n"
            "ACC / Reject clip & proses withdraw lewat tombol di pesan."))
    await ctx.send(embed=e)


bot.run(TOKEN)
