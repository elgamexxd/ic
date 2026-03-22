import discord
from discord.ext import commands
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
IC_ISIM_KANAL_ID = 1484188689478189200
YETKILI_ROL_ID = 1485231204830810133

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


class OnayView(discord.ui.View):
    def __init__(self, hedef_uye: discord.Member, istenen_isim: str):
        super().__init__(timeout=None)
        self.hedef_uye = hedef_uye
        self.istenen_isim = istenen_isim

    @discord.ui.button(label="Onayla", style=discord.ButtonStyle.success, emoji="✅")
    async def onayla(self, interaction: discord.Interaction, button: discord.ui.Button):
        yetkili_rol = interaction.guild.get_role(YETKILI_ROL_ID)
        if yetkili_rol not in interaction.user.roles:
            await interaction.response.send_message(
                "Bu butonu kullanma yetkin yok!", ephemeral=True
            )
            return

        try:
            await self.hedef_uye.edit(nick=self.istenen_isim)
            await interaction.response.send_message(
                f"{self.hedef_uye.mention} adı **{self.istenen_isim}** olarak guncellendi!"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "Bu kisinin adini degistirme yetkim yok!", ephemeral=True
            )

        self.stop()

    @discord.ui.button(label="Reddet", style=discord.ButtonStyle.danger, emoji="❌")
    async def reddet(self, interaction: discord.Interaction, button: discord.ui.Button):
        yetkili_rol = interaction.guild.get_role(YETKILI_ROL_ID)
        if yetkili_rol not in interaction.user.roles:
            await interaction.response.send_message(
                "Bu butonu kullanma yetkin yok!", ephemeral=True
            )
            return

        try:
            await self.hedef_uye.send(
                f"Ic isim talebiniz reddedildi!\n"
                f"Istediginiz isim: {self.istenen_isim}\n"
                f"Lutfen tekrar deneyin veya yetkili ile iletisime gecin."
            )
        except discord.Forbidden:
            pass

        await interaction.response.send_message(
            f"{self.hedef_uye.mention} Ic ismin onaylanmadi! DM kutunu kontrol et.",
            delete_after=10,
        )

        self.stop()


@bot.event
async def on_ready():
    print(f"Bot hazir: {bot.user} | {bot.user.id}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.channel.id != IC_ISIM_KANAL_ID:
        await bot.process_commands(message)
        return

    istenen_isim = message.content.strip()

    if not istenen_isim:
        return

    try:
        await message.delete()
    except discord.Forbidden:
        pass

    embed = discord.Embed(
        title="Ic Isim Talebi",
        description=(
            f"**Kisi:** {message.author.mention}\n"
            f"**Istenen Isim:** `{istenen_isim}`"
        ),
        color=discord.Color.yellow(),
    )
    embed.set_footer(text="Yetkili onayi bekleniyor...")

    view = OnayView(hedef_uye=message.author, istenen_isim=istenen_isim)
    await message.channel.send(embed=embed, view=view)

    await bot.process_commands(message)


bot.run(BOT_TOKEN)
