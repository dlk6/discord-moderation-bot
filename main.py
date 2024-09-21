import json
from datetime import datetime, timedelta, timezone
from interactions import Client, Intents, listen, slash_command, slash_option, SlashContext, GuildText, Embed
from interactions.models import Member

def load_config():
    with open("config.json") as f:
        config = json.load(f)

    config["ownerid"] = [int(uid) for uid in config["ownerid"]]
    return config

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

config = load_config()

token = config["token"]
embedcol = config["embedcol"]
footer_text = config["footer_text"]
footer_icon = config["footer_icon"]

dot_emoji = config["dot_emoji"]
success_emoji = config["success_emoji"]
loading_emoji = config["loading_emoji"]
warning_emoji = config["warning_emoji"]

def is_owner(ctx):
    config = load_config()
    return ctx.author.id in config["ownerid"]

bot = Client(intents=Intents.DEFAULT)

@listen()
async def on_ready():
    print("Bot is online!")

@slash_command(name="channel_lock", description="Locks a channel of your choice for everyone except whitelisted members.")
async def channel_lock(ctx: SlashContext):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    channel = ctx.channel
    everyone_role = ctx.guild.default_role

    await channel.set_permission(everyone_role, send_messages=False, manage_threads=False, use_public_threads=False, use_private_threads=False)

    unlock_embed = Embed(title="Channel Lock", description=f"{success_emoji} This channel has been locked down. Only whitelisted members can send messages here.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
    await ctx.send(embeds=[unlock_embed])

@slash_command("channel_unlock", description="Unlocks a channel of your choice for everyone.")
async def channel_unlock(ctx: SlashContext):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    channel = ctx.channel
    everyone_role = ctx.guild.default_role

    await channel.set_permission(everyone_role, send_messages=None, manage_threads=None, use_public_threads=None, use_private_threads=None)

    unlock_embed = Embed(title="Channel Unlock", description=f"{success_emoji} This channel has been unlocked.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
    await ctx.send(embeds=[unlock_embed])

@slash_command(name="channel_nuke", description="Clears the channel and duplicates it.")
async def channel_nuke(ctx: SlashContext):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    channel = ctx.channel
    new_channel = await channel.clone(reason="Channel nuked and replaced")
    await channel.delete()
    await new_channel.edit(position=channel.position)
    embed = Embed(title="Nuke complete", description=f"{dot_emoji} Channel {new_channel.mention} has been nuked by {ctx.author.mention}.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
    await new_channel.send(embed=embed)

@slash_command(name="user_mute", description="Mutes a member for a specified duration in minutes.")
@slash_option(name="member", description="Who will be the lucky one to get muted.", required=True, opt_type=6)
@slash_option(name="mute_duration", description="For how many minutes the user will be muted for.", required=True, opt_type=4)
async def user_mute(ctx: SlashContext, member: Member, mute_duration: int):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    if mute_duration <= 0:
        invalid_duration_embed = Embed(title="Invalid Duration", description=f"{warning_emoji} The duration must be a positive number of minutes.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[invalid_duration_embed], ephemeral=True)

    try:
        end_time = datetime.now(timezone.utc) + timedelta(minutes=mute_duration)
        await member.timeout(end_time)
        success_embed = Embed(title="Muted", description=f"{success_emoji} {member.mention} has been muted for {mute_duration} minutes.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[success_embed], ephemeral=True)
    except Exception as e:
        error_embed = Embed(title="Error", description=f"{warning_emoji} There was an error muting the member: {str(e)}!", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[error_embed], ephemeral=True)

@slash_command(name="user_unmute", description="Unmutes a previously muted member.")
@slash_option(name="member", description="The member who will be unmuted.", required=True, opt_type=6)
async def user_unmute(ctx: SlashContext, member: Member):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    try:
        await member.timeout(None)
        success_embed = Embed(title="Unmuted", description=f"{success_emoji} {member.mention} has been unmuted.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[success_embed], ephemeral=True)
    except Exception as e:
        error_embed = Embed(title="Error", description=f"{warning_emoji} There was an error unmuting the member: {str(e)}!", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[error_embed], ephemeral=True)

@slash_command(name="user_ban", description="Bans a user with a specified reason.")
@slash_option(name="member", description="The member to be banned.", required=True, opt_type=6)
@slash_option(name="reason", description="Reason for the ban.", required=True, opt_type=3)
async def user_ban(ctx: SlashContext, member: Member, reason: str):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    try:
        await member.kick(reason=reason)
        success_embed = Embed(title="Banned", description=f"{success_emoji} {member.mention} has been banned for the following reason: ```{reason}```", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[success_embed], ephemeral=True)
    except Exception as e:
        error_embed = Embed(title="Error", description=f"{warning_emoji} The bot does not have permisions to ban this member!", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[error_embed], ephemeral=True)


@slash_command(name="user_unban", description="Unbans a user by their ID.")
@slash_option(name="user_id", description="The ID of the user to be unbanned.", required=True, opt_type=3)
async def user_unban(ctx: SlashContext, user_id: str):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    try:
        ban_info = await ctx.guild.fetch_ban(user_id)

        if ban_info is None:
            not_banned_embed = Embed(title="User Not Banned", description=f"{warning_emoji} The user with ID `{user_id}` is not currently banned.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
            return await ctx.send(embeds=[not_banned_embed], ephemeral=True)

        await ctx.guild.unban(user_id)
        success_embed = Embed(title="Unbanned", description=f"{success_emoji} The user with ID `{user_id}` has been unbanned.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[success_embed], ephemeral=True)
    except Exception as e:
        error_embed = Embed(title="Error", description=f"{warning_emoji} There was an error unbanning the user: {str(e)}!", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[error_embed], ephemeral=True)

@slash_command(name="user_kick", description="Kicks a user from the guild.")
@slash_option(name="member", description="The member to be kicked.", required=True, opt_type=6)
async def user_kick(ctx: SlashContext, member: Member):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    try:
        await member.kick()
        success_embed = Embed(title="Kicked", description=f"{success_emoji} {member.mention} has been kicked from the guild.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[success_embed], ephemeral=True)
    except Exception as e:
        error_embed = Embed(title="Error", description=f"{warning_emoji} There was an error kicking the member: {str(e)}!", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        await ctx.send(embeds=[error_embed], ephemeral=True)

@slash_command(name="whitelisted_members", description="Lists all whitelisted members.")
async def whitelisted_members(ctx: SlashContext):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    config = load_config()
    whitelisted_users = [f"> {i + 1}. `{user_id}` (<@{user_id}>)" for i, user_id in enumerate(config["ownerid"])]
    users_list = "\n".join(whitelisted_users)

    list_embed = Embed(title="Whitelisted Members", description=f"{dot_emoji} Whitelisted member list:\n{users_list}", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
    await ctx.send(embeds=[list_embed], ephemeral=True)

@slash_command(name="add_whitelisted", description="Adds a user to the whitelist.")
@slash_option(name="user_id", description="The ID of the user to add to the whitelist.", required=True, opt_type=3)
async def add_whitelisted(ctx: SlashContext, user_id: str):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    try:
        user_id_int = int(user_id)
    except ValueError:
        invalid_id_embed = Embed(title="Invalid ID", description=f"{warning_emoji} The provided ID is not a valid integer.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[invalid_id_embed], ephemeral=True)

    config = load_config()
    if user_id_int in config["ownerid"]:
        already_whitelisted_embed = Embed(title="Whitelist", description=f"{warning_emoji} User `{user_id_int}` (<@{user_id_int}>) is already whitelisted.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[already_whitelisted_embed], ephemeral=True)

    config["ownerid"].append(user_id_int)
    save_config(config)

    success_embed = Embed(title="Whitelist", description=f"{success_emoji} Added user `{user_id_int}` (<@{user_id_int}>) to the whitelist.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
    await ctx.send(embeds=[success_embed], ephemeral=True)

@slash_command(name="remove_whitelisted", description="Removes a user from the whitelist.")
@slash_option(name="user_id", description="The ID of the user to remove from the whitelist.", required=True, opt_type=3)
async def remove_whitelisted(ctx: SlashContext, user_id: str):
    if not is_owner(ctx):
        no_permission_embed = Embed(title="Permission Denied", description=f"{warning_emoji} You are not authorized to use this command.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[no_permission_embed], ephemeral=True)

    try:
        user_id_int = int(user_id)
    except ValueError:
        invalid_id_embed = Embed(title="Invalid ID", description=f"{warning_emoji} The provided ID is not a valid integer.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[invalid_id_embed], ephemeral=True)

    config = load_config()
    if user_id_int not in config["ownerid"]:
        not_whitelisted_embed = Embed(title="Whitelist", description=f"{warning_emoji} User `{user_id_int}` (<@{user_id_int}>) is not whitelisted.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
        return await ctx.send(embeds=[not_whitelisted_embed], ephemeral=True)

    config["ownerid"].remove(user_id_int)
    save_config(config)

    success_embed = Embed(title="Whitelist", description=f"{success_emoji} Removed user `{user_id_int}` (<@{user_id_int}>) from the whitelist.", color=embedcol, footer={"text": footer_text, "icon_url": footer_icon})
    await ctx.send(embeds=[success_embed], ephemeral=True)

bot.start(token)