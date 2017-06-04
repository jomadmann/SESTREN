"""
Module for listener for user's joining/leaving voice channels.

On join, adds role to grant access to voice channel.
On leave, removes access role.
"""


import discord
from discord.ext import commands
# import json
from cogs.utils import config


class VCAccess:

    def __init__(self, bot):
        self.bot = bot
        self._data = config.Config("vc_access.json")

    # @property  # I'D STARTED WORKING ON THIS WHEN I WAS SHOWN DANNY'S CONFIG.PY AND I DON'T WANT TO THROW IT AWAY
    # def _data(self):
    #     """Load JSON config to property 'data'
    #
    #     Format:
    #     {
    #         "<guild id>": {
    #             "<voice channel id>": "<role id>"
    #         }
    #     }"""
    #     try:
    #         with open('vc_access.json', 'r+') as datafile:
    #             return json.load(datafile)
    #     except IOError:
    #         print("vc_access.json not found.")
    #         self.bot.unload_extension('cogs.utils.vc_access')

    @property
    def guilds(self):
        return list(self._data)

    @property
    def channels(self):
        l = []
        for g in self.guilds:
            for c in self._data.get(g):
                l.append(c)
        return l

    # def channels(self, guild):
    #     gid = str(guild)
    #     return list(self._data.get(gid))

    async def modifyrole(self, member, voicestate, action):
        guild = str(voicestate.channel.guild.id)
        if guild in self.guilds:
            channel = str(voicestate.channel.id)
            if channel in self.channels:
                channels = self._data.get(guild)
                if channel in channels:
                    role = discord.utils.get(voicestate.channel.guild.roles, id=int(channels[channel]))
                    try:
                        if action == 'add':
                            await member.add_roles(role)
                        elif action == 'remove'
                            await member.remove_roles(role)
                    except Exception as e:
                        await self.selfchannel.send(content=str(e))

    # async def removerole(self, member, voicestate):
    #     bg = str(voicestate.channel.guild.id)
    #     if bg in self.guilds:
    #         bc = str(voicestate.channel.id)
    #         if bc in self.channels:
    #             channels = self._data.get(bg)
    #             if bc in channels:
    #                 role = discord.utils.get(voicestate.channel.guild.roles, id=int(channels[bc]))
    #                 try:
    #                     await member.remove_roles(role)
    #                 except Exception as e:
    #                     await self.selfchannel.send(content=str(e))


######################################################################################
    @property  # PERSONAL GARBAGE EXPLICIT DEFINITIONS FOR FUNCTION TESTING
    def selfguild(self):
        return self.bot.get_guild(184502171117551617)

    @property
    def selfchannel(self):
        return discord.Guild.get_channel(self.selfguild, 315232431835709441)

    @commands.command(name='test')
    async def _test(self):
        # oaurl = discord.utils.oauth_url(client_id='194568954440581120')
        # await self.selfchannel.send(content='```\n{0}\n```'.format(oaurl))
        await self.selfchannel.send(content='```\n{0}\n```'.format(self.channels))
######################################################################################


    @commands.group()
    async def vca(self):
        """Voice Channel Access command group

        Help docstr here later
        [p]vca addguild <guild id>
        [p]vca removeguild <guild id>
        [p]vca role <subcommand>"""
        pass

    @vca.command(aliases=['add'])
    async def addguild(self, ctx, gid: int):  # g = discord.Guild.id
        gstr = str(gid)
        gobj = discord.utils.get(self.bot.guilds, id=gid)
        if gobj is not None:
            if gstr in self.guilds:
                await ctx.message.channel.send(content='VCA already active on {0.name}.'.format(gobj))
            else:
                await self._data.put(gid, {})
                await ctx.message.channel.send(content='VCA now active on {0.name}'.format(gobj))
        else:
            await ctx.message.channel.send(content='Server id {0} not found. Make sure SESTREN is a member.'.format(gid))

    @vca.command(aliases=['rem'])
    async def removeguild(self, ctx, gid: int):
        gstr = str(gid)
        gobj = discord.utils.get(self.bot.guilds, id=gid)
        if gobj is not None:
            if gstr in self.guilds:
                await self._data.remove(gstr)
                await ctx.message.channel.send(content='{0.name} removed from VCA.'.format(gobj))
            else:
                await ctx.message.channel.send(content='VCA is not active on {0.name}'.format(gobj))
        else:
            await ctx.message.channel.send(content='Server id {0} not found. Make sure SESTREN is a member.'.format(gid))

    @vca.command(aliases=['list'])
    async def _list(self, ctx, *args):
        """Messages channel with list of server names VCA is active on."""
        out = '```\nVoice Channel Access control active on the following servers:\n{0}\n'.format('-'*61)
        for g in self.guilds:
            guild = discord.utils.get(self.bot.guilds, id=int(g))
            out += '{0}\n'.format(guild.name)
            channels = self._data.get(g)
            if not len(channels) == 0:
                for c in channels:
                    channel = discord.utils.get(guild.channels, id=int(c))
                    role = discord.utils.get(guild.roles, id=int(channels[c]))
                    out += '--- {0} : {1}\n'.format(channel.name, role.name)
        else:
            out += '```'
        await ctx.message.channel.send(content=out)


    @vca.group()
    async def chan(self):
        """Voice Channel Access subcommand `role` command group

        [p]vca role add <voice channel id>
        [p]vca role rem <voice channel id>"""
        pass

    @chan.command(aliases=['add'])
    async def _addchannel(self, ctx, guild: str, channel: str, role: str):
        g = discord.utils.get(self.bot.guilds, id=int(guild))
        c = discord.utils.get(g.voice_channels, id=int(channel))
        r = discord.utils.get(g.roles, id=int(role))
        if g is not None and c is not None and r is not None:
            if guild not in self.guilds:
                await self._data.put(guild, {})
                await ctx.message.channel.send(content='VCA is now active on {0.name}'.format(g))
            d = self._data.get(guild)
            print(d)
            d[channel] = role
            print(d)
            await self._data.put(guild, d)

    @chan.command(aliases=['rem'])
    async def _removechannel(self, ctx, guild: int):
        pass


    async def on_voice_state_update(self, member, before, after):
        b, a, n = before.channel, after.channel, None
        if (b, a) is not (None, None):
            if a is not n:


            # if after.channel is not None:
            #     ag = str(after.channel.guild.id)
            #     if ag in self.guilds:
            #         ac = str(after.channel.id)
            #         if ac in self.channels:
            #             channels = self._data.get(ag)
            #             if ac in channels:
            #                 role = discord.utils.get(after.channel.guild.roles, id=int(channels[ac]))
            #                 try:
            #                     await member.add_roles(role)
            #                 except Exception as e:
            #                     await self.selfchannel.send(content=str(e))
            # else:
                # bg = str(before.channel.guild.id)
                # if bg in self.guilds:
                #     bc = str(before.channel.id)
                #     if bc in self.channels:
                #         channels = self._data.get(bg)
                #         if bc in channels:
                #             role = discord.utils.get(before.channel.guild.roles, id=int(channels[bc]))
                #             try:
                #                 await member.remove_roles(role)
                #             except Exception as e:
                #                 await self.selfchannel.send(content=str(e))


def setup(bot):
    bot.add_cog(VCAccess(bot))
