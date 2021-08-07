#!/usr/bin/env python3
import os, asyncio, discord, random
from discord.ext import commands, tasks
from discord.utils import get
from dotenv import load_dotenv
import mysql.connector, time
from datetime import datetime
import traceback, logging, json


running=False
lottery_tickets= []

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
USER = os.getenv('DB_USER')
PASSWORD = os.getenv('DB_PASSWORD')
DATABASE = os.getenv('DB_DATABASE')

logging.basicConfig(filename='/NOVA/NOVA_Rep/NOVA_Rep.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logging.basicConfig(filename='NOVA_Rep.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

intents = discord.Intents().all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('rep!'), case_insensitive=True, intents=intents)

#left = '⏪'
#right = '⏩'
#stop = '⏹️'
#def predicate(message, l, r):
#    def check(reaction, user):
#        if reaction.message.id != message.id or user == bot.user:
#            return False
#        if l and reaction.emoji == left:
#            return True
#        if r and reaction.emoji == right:
#            return True
#        if reaction.emoji == stop:
#            return True
#        return False
#
#    return check


@bot.event
async def on_ready():
    global running
    try:
        if running==False:
            await asyncio.sleep (1)
            logging.info(f'{bot.user.name} {discord.__version__} has connected to Discord!')
            guild = get(bot.guilds, id=815104630433775616)
            bot_log_channel = get(guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="Info Log.", description=f"{bot.user.name} {discord.__version__} has connected to Discord!",
                                          color=0x5d4991)
            embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
            running=True
    except Exception:
        logging.error(traceback.format_exc())
        bot_log_channel = get(guild.text_channels, name='bot-logs')
        embed_bot_log = discord.Embed(title="NOVA_Rep Error Log.", description="on ready", color=discord.Color.orange())
        embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
        await bot_log_channel.send(embed=embed_bot_log)
    
@bot.command(pass_context=True)
@commands.has_any_role('Moderator')
async def Logout(ctx):
    await ctx.message.delete()
    await ctx.bot.logout()

@bot.event
async def on_message(message):
    if message.channel.id == 817845958628606002 or message.channel.id == 824756168605040680:
        try:
            messageLower = message.content.lower()
            
            if messageLower.startswith('+rep'):
                
                if len(message.mentions) == 0:
                    await message.channel.send("Please make sure you are following the +rep command structure, \n"
                                    "`+rep @username <feedback>`",delete_after=10)
                else:
                    rep_target= message.mentions[0].id
                    rep_comment = messageLower.partition("> ")[2]
                    if rep_target == message.author.id:
                        await message.delete()
                        await message.channel.send("You cannot give feeback about your self",delete_after=10)
                    else:
                        cnx = mysql.connector.connect(
                                host=HOST,
                                port=DB_PORT,
                                user=USER,
                                passwd=PASSWORD,
                                database=DATABASE
                            )
                        cursor = cnx.cursor()
                        query = "INSERT INTO reputation (member_id, rep_score, rep_source, rep_comment) VALUES (%s, %s, %s, %s)"
                        val = (rep_target,1,message.author.id,rep_comment)
                        cursor.execute(query,val)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        await message.channel.send("Reputation feedback submitted",delete_after=10)
            if messageLower.startswith('-rep'):
                if len(message.mentions) == 0:
                    await message.channel.send("Please make sure you are following the +rep command structure, \n"
                                    "`-rep @username <feedback>`")
                else:
                    rep_target= message.mentions[0].id
                    rep_comment = messageLower.partition("> ")[2]
                    if rep_target == message.author.id:
                        await message.delete()
                        await message.channel.send("You cannot give feeback about your self",delete_after=10)
                    else:
                        cnx = mysql.connector.connect(
                                host=HOST,
                                port=DB_PORT,
                                user=USER,
                                passwd=PASSWORD,
                                database=DATABASE
                            )
                        cursor = cnx.cursor()
                        query = "INSERT INTO reputation (member_id, rep_score, rep_source, rep_comment) VALUES (%s, %s, %s, %s)"
                        val = (rep_target,-1,message.author.id,rep_comment)
                        cursor.execute(query,val)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        await message.channel.send("Reputation feedback submitted",delete_after=10)
            if messageLower.startswith('repstatus'):
                
                if len(message.mentions) == 0:
                    await message.channel.send("Please make sure you are following the +rep command structure, \n"
                                    "`repStatus @username`")
                else:
                    rep_target= message.mentions[0].id
                    #rep_comment = messageLower.partition(">")[2]
                    cnx = mysql.connector.connect(
                            host=HOST,
                            port=DB_PORT,
                            user=USER,
                            passwd=PASSWORD,
                            database=DATABASE
                        )
                    
                    cursor = cnx.cursor()
                    query = "select COUNT(rep_score) from reputation where member_id = %s AND rep_score = 1"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    positive_rep_score = cursor.fetchone()[0]
                    cursor.close()
                    
                    cursor = cnx.cursor()
                    query = "select COUNT(rep_score) from reputation where member_id = %s AND rep_score = -1"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    negative_rep_score = cursor.fetchone()[0]
                    cursor.close()
                    
                    cursor = cnx.cursor()
                    query = "select rep_source, rep_comment from reputation where member_id = %s and rep_score = 1 ORDER BY rep_date DESC LIMIT 5;"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    positive_rep_comments = cursor.fetchall()
                    cursor.close()
                    
                    cursor = cnx.cursor()
                    query = "select rep_source, rep_comment from reputation where member_id = %s and rep_score = -1 ORDER BY rep_date DESC LIMIT 5;"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    negative_rep_comments = cursor.fetchall()
                    cursor.close()
                    
                    cnx.close()
                    
                    user = message.guild.get_member(rep_target)
                    rep_embed=discord.Embed(title="Reputation info", description=user.display_name, color=0x4feb1c)
                    rep_embed.set_thumbnail(url=user.avatar_url)
                    rep_embed.add_field(name="Positive Score: ", value=f"`{positive_rep_score}`", inline=True)
                    rep_embed.add_field(name="Negative Score: ", value=f"`{negative_rep_score}`", inline=True)
                    positive_str = ""
                    
                    for x in positive_rep_comments:
                        #user_in_embed = message.guild.get_member(x[0])
                        #feedback_in_embed = x[1]
                        if message.guild.get_member(x[0]) is None:
                            non_member_user = await bot.fetch_user(x[0])
                            positive_str += f"**{non_member_user.display_name}**: "
                        else:
                            positive_str += f"**{message.guild.get_member(x[0]).display_name}**: "
                        positive_str += x[1]
                        positive_str += "\n"
                    
                    negative_str = ""

                    for y in negative_rep_comments:
                        #user_in_embed = message.guild.get_member(y[0])
                        #feedback_in_embed = y[1]
                        if message.guild.get_member(y[0]) is None:
                            non_member_user = await bot.fetch_user(y[0])
                            negative_str += f"**{non_member_user.display_name}**: "
                        else:
                            negative_str += f"**{message.guild.get_member(y[0]).display_name}**: "
                        negative_str += y[1]
                        negative_str += "\n"
                    ###################################################
                    #messages_stats = []
                    #for x in positive_rep_comments:
                    #    user_in_embed = message.guild.get_member(x[0])
                    #    feedback_in_embed = x[1]
                    #    messages_stats.append((f"{user_in_embed.mention}:", f"{feedback_in_embed}"))
                    #positive_str = ""
                    #for ele in messages_stats:
                    #    positive_str += ele[0]
                    #    positive_str += ele[1]
                    #    positive_str += "\n"
                    ###########################################
                    if positive_str == None or positive_str == "":
                        positive_str = "None"
                    if negative_str == None or negative_str == "":
                        negative_str = "None"
                    rep_embed.add_field(name="Recent Positive feedback: ", value=positive_str, inline=False)
                    rep_embed.add_field(name="Recent Negative feedback: ", value=negative_str, inline=True)
                    rep_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
                    rep_msg = await message.channel.send(embed=rep_embed)
                    #####################################################################
                    #messages_stats = []
                    #for x in positive_rep_comments:
                    #    messages_stats.append((f"Reputation granted by: {message.guild.get_member(x[0]).mention}",f"Feedback: {x[1]}"))
                    #index = 0
                    #msg = None
                    #action = message.channel.send
                    #while True:
                    #    res = await action(content=f"{messages_stats[index][0]}\n{messages_stats[index][1]}")
                    #    if res is not None:
                    #        msg = res
                    #        await msg.add_reaction(left)
                    #       await msg.add_reaction(right)
                    #        await msg.add_reaction(stop)
                    #    l = index != 0
                    #    r = index != len(messages_stats) - 1
                    #    if l:
                    #        await msg.add_reaction(left) 
                    #    if r:
                    #        await msg.add_reaction(right)
                    #    react, user = await bot.wait_for('reaction_add', check=predicate(msg, l, r))
                    #    if react.emoji == left:
                    #        index -= 1
                    #        await msg.remove_reaction(left,user)
                    #        action = msg.edit
                    #    elif react.emoji == right:
                    #        index += 1
                    #        await msg.remove_reaction(right,user)
                    #        action = msg.edit
                    #    elif react.emoji == stop:
                    #        await msg.delete()
                    #####################################################################
                    
            else:
                try:
                    await bot.process_commands(message)
                except Exception:
                    logging.error(traceback.format_exc())
                    bot_log_channel = get(message.guild.text_channels, name='bot-logs')
                    embed_bot_log = discord.Embed(title="Error Log.", description="bot process commands", color=0x5d4991)
                    embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
                    embed_bot_log.add_field(name="Content", value=message.content, inline=False)
                    embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
                    await bot_log_channel.send(embed=embed_bot_log)
        except Exception:
            logging.error(traceback.format_exc())
            
    else:
        try:
            await bot.process_commands(message)
        except Exception:
            logging.error(traceback.format_exc())
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="Error Log.", description=traceback.format_exc(), color=0x5d4991)
            embed_bot_log.add_field(name="Source", value="bot process commands", inline=True)
            embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
            embed_bot_log.add_field(name="Content", value=message.content, inline=False)
            embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
    ##ADV REPUTATION##
    if message.channel.id == 873182661735219240 and not message.author.bot:
        log_channel = get(message.guild.text_channels, id=873182661735219240)
        try:
            messageLower = message.content.lower()
            
            if messageLower.startswith('+score'):
                await message.delete()
                if len(message.mentions) == 0:
                    await message.channel.send("Please make sure you are following the +score command structure, \n"
                                    "`+score @username <feedback>`",delete_after=10)
                else:
                    rep_target= message.mentions[0].id
                    rep_comment = messageLower.partition("> ")[2]
                    if rep_target == message.author.id:
                        await message.delete()
                        await message.channel.send("You cannot give feeback about your self",delete_after=10)
                    else:
                        cnx = mysql.connector.connect(
                                host=HOST,
                                port=DB_PORT,
                                user=USER,
                                passwd=PASSWORD,
                                database=DATABASE
                            )
                        cursor = cnx.cursor()
                        query = "INSERT INTO advertiser_reputation (id, member_id, rep_score, rep_source, rep_comment) VALUES (%s, %s, %s, %s, %s)"
                        val = (message.id, rep_target,1,message.author.id,rep_comment)
                        cursor.execute(query,val)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        await message.channel.send(f"Reputation feedback submitted with id: {message.id}",delete_after=10)
                        em = discord.Embed(title="Advertiser Reputation added",
                                                description=
                                                    f"Reputation feedback submitted with ID **{message.id}** "
                                                    f"{message.author.mention} gave +1 to {message.mentions[0].display_name} for {rep_comment}",
                                                color=discord.Color.orange())
                        await message.author.send(embed=em)
                        await log_channel.send(embed=em)
            if messageLower.startswith('-score'):
                await message.delete()
                if len(message.mentions) == 0:
                    await message.channel.send("Please make sure you are following the -score command structure, \n"
                                    "`-score @username <feedback>`")
                else:
                    rep_target= message.mentions[0].id
                    rep_comment = messageLower.partition("> ")[2]
                    if rep_target == message.author.id:
                        await message.delete()
                        await message.channel.send("You cannot give feeback about your self",delete_after=10)
                    else:
                        cnx = mysql.connector.connect(
                                host=HOST,
                                port=DB_PORT,
                                user=USER,
                                passwd=PASSWORD,
                                database=DATABASE
                            )
                        cursor = cnx.cursor()
                        query = "INSERT INTO advertiser_reputation (id, member_id, rep_score, rep_source, rep_comment) VALUES (%s, %s, %s, %s, %s)"
                        val = (message.id, rep_target,-1,message.author.id,rep_comment)
                        cursor.execute(query,val)
                        cnx.commit()
                        cursor.close()
                        cnx.close()
                        await message.channel.send(f"Reputation feedback submitted with id: {message.id}",delete_after=10)
                        em = discord.Embed(title="Advertiser Reputation added",
                                                description=
                                                    f"Reputation feedback submitted with ID **{message.id}** "
                                                    f"{message.author.mention} gave -1 to **{message.mentions[0].display_name}** for {rep_comment}",
                                                color=discord.Color.orange())
                        await message.author.send(embed=em)
                        await log_channel.send(embed=em)
            if messageLower.startswith('remscore'):
                await message.delete()
                cnx = mysql.connector.connect(
                        host=HOST,
                        port=DB_PORT,
                        user=USER,
                        passwd=PASSWORD,
                        database=DATABASE
                    )
                cursor = cnx.cursor()
                query = "DELETE FROM advertiser_reputation where id = %s"
                val = (message.id,)
                cursor.execute(query,val)
                cnx.commit()
                cursor.close()
                cnx.close()
                await message.channel.send(f"Reputation feedback removed with id: {message.id}",delete_after=10)
                em = discord.Embed(title="Advertiser Reputation deleted",
                                        description=
                                            f"Reputation feedback removed with ID **{message.id}** "
                                            f"by {message.author.mention}",
                                        color=discord.Color.orange())
                await message.author.send(embed=em)
                await log_channel.send(embed=em)
            if messageLower.startswith('scorestatus'):
                
                if len(message.mentions) == 0:
                    await message.channel.send("Please make sure you are following the scorestatus command structure, \n"
                                    "`score @username`")
                else:
                    rep_target= message.mentions[0].id
                    #rep_comment = messageLower.partition(">")[2]
                    cnx = mysql.connector.connect(
                            host=HOST,
                            port=DB_PORT,
                            user=USER,
                            passwd=PASSWORD,
                            database=DATABASE
                        )
                    
                    cursor = cnx.cursor()
                    query = "select COUNT(rep_score) from advertiser_reputation where member_id = %s AND rep_score = 1"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    positive_rep_score = cursor.fetchone()[0]
                    cursor.close()
                    
                    cursor = cnx.cursor()
                    query = "select COUNT(rep_score) from advertiser_reputation where member_id = %s AND rep_score = -1"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    negative_rep_score = cursor.fetchone()[0]
                    cursor.close()
                    
                    cursor = cnx.cursor()
                    query = "select rep_source, rep_comment from advertiser_reputation where member_id = %s and rep_score = 1 ORDER BY rep_date DESC LIMIT 5;"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    positive_rep_comments = cursor.fetchall()
                    cursor.close()
                    
                    cursor = cnx.cursor()
                    query = "select rep_source, rep_comment from advertiser_reputation where member_id = %s and rep_score = -1 ORDER BY rep_date DESC LIMIT 5;"
                    val = (rep_target, )
                    cursor.execute(query, val)
                    negative_rep_comments = cursor.fetchall()
                    cursor.close()
                    
                    cnx.close()
                    
                    user = message.guild.get_member(rep_target)
                    rep_embed=discord.Embed(title="Reputation info", description=user.display_name, color=0x4feb1c)
                    rep_embed.set_thumbnail(url=user.avatar_url)
                    rep_embed.add_field(name="Positive Score: ", value=f"`{positive_rep_score}`", inline=True)
                    rep_embed.add_field(name="Negative Score: ", value=f"`{negative_rep_score}`", inline=True)
                    positive_str = ""
                    
                    for x in positive_rep_comments:
                        #user_in_embed = message.guild.get_member(x[0])
                        #feedback_in_embed = x[1]
                        if message.guild.get_member(x[0]) is None:
                            non_member_user = await bot.fetch_user(x[0])
                            positive_str += f"**{non_member_user.display_name}**: "
                        else:
                            positive_str += f"**{message.guild.get_member(x[0]).display_name}**: "
                        positive_str += x[1]
                        positive_str += "\n"
                    
                    negative_str = ""

                    for y in negative_rep_comments:
                        #user_in_embed = message.guild.get_member(y[0])
                        #feedback_in_embed = y[1]
                        if message.guild.get_member(y[0]) is None:
                            non_member_user = await bot.fetch_user(y[0])
                            negative_str += f"**{non_member_user.display_name}**: "
                        else:
                            negative_str += f"**{message.guild.get_member(y[0]).display_name}**: "
                        negative_str += y[1]
                        negative_str += "\n"
                    ###################################################
                    #messages_stats = []
                    #for x in positive_rep_comments:
                    #    user_in_embed = message.guild.get_member(x[0])
                    #    feedback_in_embed = x[1]
                    #    messages_stats.append((f"{user_in_embed.mention}:", f"{feedback_in_embed}"))
                    #positive_str = ""
                    #for ele in messages_stats:
                    #    positive_str += ele[0]
                    #    positive_str += ele[1]
                    #    positive_str += "\n"
                    ###########################################
                    if positive_str == None or positive_str == "":
                        positive_str = "None"
                    if negative_str == None or negative_str == "":
                        negative_str = "None"
                    rep_embed.add_field(name="Recent Positive feedback: ", value=positive_str, inline=False)
                    rep_embed.add_field(name="Recent Negative feedback: ", value=negative_str, inline=True)
                    rep_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
                    rep_msg = await message.channel.send(embed=rep_embed)
                    #####################################################################
                    #messages_stats = []
                    #for x in positive_rep_comments:
                    #    messages_stats.append((f"Reputation granted by: {message.guild.get_member(x[0]).mention}",f"Feedback: {x[1]}"))
                    #index = 0
                    #msg = None
                    #action = message.channel.send
                    #while True:
                    #    res = await action(content=f"{messages_stats[index][0]}\n{messages_stats[index][1]}")
                    #    if res is not None:
                    #        msg = res
                    #        await msg.add_reaction(left)
                    #       await msg.add_reaction(right)
                    #        await msg.add_reaction(stop)
                    #    l = index != 0
                    #    r = index != len(messages_stats) - 1
                    #    if l:
                    #        await msg.add_reaction(left) 
                    #    if r:
                    #        await msg.add_reaction(right)
                    #    react, user = await bot.wait_for('reaction_add', check=predicate(msg, l, r))
                    #    if react.emoji == left:
                    #        index -= 1
                    #        await msg.remove_reaction(left,user)
                    #        action = msg.edit
                    #    elif react.emoji == right:
                    #        index += 1
                    #        await msg.remove_reaction(right,user)
                    #        action = msg.edit
                    #    elif react.emoji == stop:
                    #        await msg.delete()
                    #####################################################################
                    
            else:
                try:
                    await bot.process_commands(message)
                except Exception:
                    logging.error(traceback.format_exc())
                    bot_log_channel = get(message.guild.text_channels, name='bot-logs')
                    embed_bot_log = discord.Embed(title="Error Log.", description="bot process commands", color=0x5d4991)
                    embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
                    embed_bot_log.add_field(name="Content", value=message.content, inline=False)
                    embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
                    await bot_log_channel.send(embed=embed_bot_log)
        except Exception:
            logging.error(traceback.format_exc())
    if message.channel.id == 872184309484781598 and not message.author.bot:
        try:
            messageLower = message.content.lower()
            await message.delete()
            if messageLower.startswith('scorestatus'):
                rep_target= message.author.id
                #rep_comment = messageLower.partition(">")[2]
                cnx = mysql.connector.connect(
                        host=HOST,
                        port=DB_PORT,
                        user=USER,
                        passwd=PASSWORD,
                        database=DATABASE
                    )
                
                cursor = cnx.cursor()
                query = "select COUNT(rep_score) from advertiser_reputation where member_id = %s AND rep_score = 1"
                val = (rep_target, )
                cursor.execute(query, val)
                positive_rep_score = cursor.fetchone()[0]
                cursor.close()
                
                cursor = cnx.cursor()
                query = "select COUNT(rep_score) from advertiser_reputation where member_id = %s AND rep_score = -1"
                val = (rep_target, )
                cursor.execute(query, val)
                negative_rep_score = cursor.fetchone()[0]
                cursor.close()
                
                cursor = cnx.cursor()
                query = "select rep_source, rep_comment from advertiser_reputation where member_id = %s and rep_score = 1 ORDER BY rep_date DESC LIMIT 5;"
                val = (rep_target, )
                cursor.execute(query, val)
                positive_rep_comments = cursor.fetchall()
                cursor.close()
                
                cursor = cnx.cursor()
                query = "select rep_source, rep_comment from advertiser_reputation where member_id = %s and rep_score = -1 ORDER BY rep_date DESC LIMIT 5;"
                val = (rep_target, )
                cursor.execute(query, val)
                negative_rep_comments = cursor.fetchall()
                cursor.close()
                
                cnx.close()
                
                user = message.guild.get_member(rep_target)
                rep_embed=discord.Embed(title="Reputation info", description=user.display_name, color=0x4feb1c)
                rep_embed.set_thumbnail(url=user.avatar_url)
                rep_embed.add_field(name="Positive Score: ", value=f"`{positive_rep_score}`", inline=True)
                rep_embed.add_field(name="Negative Score: ", value=f"`{negative_rep_score}`", inline=True)
                positive_str = ""
                
                for x in positive_rep_comments:
                    #user_in_embed = message.guild.get_member(x[0])
                    #feedback_in_embed = x[1]
                    if message.guild.get_member(x[0]) is None:
                        non_member_user = await bot.fetch_user(x[0])
                        positive_str += f"**{non_member_user.display_name}**: "
                    else:
                        positive_str += f"**{message.guild.get_member(x[0]).display_name}**: "
                    positive_str += x[1]
                    positive_str += "\n"
                
                negative_str = ""

                for y in negative_rep_comments:
                    #user_in_embed = message.guild.get_member(y[0])
                    #feedback_in_embed = y[1]
                    if message.guild.get_member(y[0]) is None:
                        non_member_user = await bot.fetch_user(y[0])
                        negative_str += f"**{non_member_user.display_name}**: "
                    else:
                        negative_str += f"**{message.guild.get_member(y[0]).display_name}**: "
                    negative_str += y[1]
                    negative_str += "\n"
                ###################################################
                #messages_stats = []
                #for x in positive_rep_comments:
                #    user_in_embed = message.guild.get_member(x[0])
                #    feedback_in_embed = x[1]
                #    messages_stats.append((f"{user_in_embed.mention}:", f"{feedback_in_embed}"))
                #positive_str = ""
                #for ele in messages_stats:
                #    positive_str += ele[0]
                #    positive_str += ele[1]
                #    positive_str += "\n"
                ###########################################
                if positive_str == None or positive_str == "":
                    positive_str = "None"
                if negative_str == None or negative_str == "":
                    negative_str = "None"
                rep_embed.add_field(name="Recent Positive feedback: ", value=positive_str, inline=False)
                rep_embed.add_field(name="Recent Negative feedback: ", value=negative_str, inline=True)
                rep_embed.set_footer(text="Timestamp (UTC±00:00): " + datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
                await message.channel.send(f"{message.author.mention}, your score as an advertiser has been sent via DM.", 
                                delete_after=5)
                rep_msg = await message.author.send(embed=rep_embed)
                #####################################################################
                #messages_stats = []
                #for x in positive_rep_comments:
                #    messages_stats.append((f"Reputation granted by: {message.guild.get_member(x[0]).mention}",f"Feedback: {x[1]}"))
                #index = 0
                #msg = None
                #action = message.channel.send
                #while True:
                #    res = await action(content=f"{messages_stats[index][0]}\n{messages_stats[index][1]}")
                #    if res is not None:
                #        msg = res
                #        await msg.add_reaction(left)
                #       await msg.add_reaction(right)
                #        await msg.add_reaction(stop)
                #    l = index != 0
                #    r = index != len(messages_stats) - 1
                #    if l:
                #        await msg.add_reaction(left) 
                #    if r:
                #        await msg.add_reaction(right)
                #    react, user = await bot.wait_for('reaction_add', check=predicate(msg, l, r))
                #    if react.emoji == left:
                #        index -= 1
                #        await msg.remove_reaction(left,user)
                #        action = msg.edit
                #    elif react.emoji == right:
                #        index += 1
                #        await msg.remove_reaction(right,user)
                #        action = msg.edit
                #    elif react.emoji == stop:
                #        await msg.delete()
                #####################################################################
                    
            else:
                try:
                    await bot.process_commands(message)
                except Exception:
                    logging.error(traceback.format_exc())
                    bot_log_channel = get(message.guild.text_channels, name='bot-logs')
                    embed_bot_log = discord.Embed(title="Error Log.", description="bot process commands", color=0x5d4991)
                    embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
                    embed_bot_log.add_field(name="Content", value=message.content, inline=False)
                    embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
                    await bot_log_channel.send(embed=embed_bot_log)
        except Exception:
            logging.error(traceback.format_exc())        
    else:
        try:
            await bot.process_commands(message)
        except Exception:
            logging.error(traceback.format_exc())
            bot_log_channel = get(message.guild.text_channels, name='bot-logs')
            embed_bot_log = discord.Embed(title="Error Log.", description=traceback.format_exc(), color=0x5d4991)
            embed_bot_log.add_field(name="Source", value="bot process commands", inline=True)
            embed_bot_log.add_field(name="Author", value=message.author.nick, inline=True)
            embed_bot_log.add_field(name="Content", value=message.content, inline=False)
            embed_bot_log.set_footer(text=datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S"))
            await bot_log_channel.send(embed=embed_bot_log)
    
bot.run(token)