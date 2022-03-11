from dotenv import load_dotenv, find_dotenv
from random import randint
import requests
import disnake
import os
from disnake.ext import commands

load_dotenv(find_dotenv())

wallet = os.environ.get("WALLET")
token_rri = os.environ.get("TOKEN_RRI")
transactions = "https://mainnet.radixdlt.com/account/transactions"
balances = "https://mainnet.radixdlt.com/account/balances"
headers = {'Content-Type': 'application/json',
           'X-Radixdlt-Target-Gw-Api': '1.0.0'}

bot = commands.Bot(
    command_prefix='/',
    test_guilds=[os.environ.get("GUILD_ID")]
)


@bot.slash_command(description="Link your Discord account to your Radix wallet")
async def verify(inter, address):
    if address.startswith("rdx") and len(address) == 65:
        txs = requests.request(
            "POST", transactions, headers=headers, data=get_payload(address)).json()
        verified = False
        for tx in txs["transactions"]:
            if tx["actions"][0]["to_account"]["address"] == wallet:
                if "message" in tx["metadata"] and check_message(str(inter.author), tx["metadata"]["message"]):
                    tokens = requests.request(
                        "POST", balances, headers=headers, data=get_payload(address)).json()
                    for token in tokens["account_balances"]["liquid_balances"]:
                        if token["token_identifier"]["rri"] == token_rri:
                            verified = True
                            verified_role = 939579133476868127
                            balance = int(
                                token["value"]) // 10 ** 18
                            if balance >= 50:
                                additional_role = 939579431897432085
                                additional_channel = 946083865435463710
                            elif balance >= 5:
                                additional_role = 939580638644813895
                                additional_channel = 946084021157392424
                            else:
                                additional_role = 939579533298905088
                                additional_channel = 946084151910604830
                            dao_channel = 946084422338355320
                            await inter.author.add_roles(inter.guild.get_role(verified_role), inter.guild.get_role(additional_role))

                            emb = disnake.Embed()
                            emb.color = 0x00FF00
                            emb.title = "Address verified"
                            emb.description = f"You now have access to the <#{dao_channel}> and <#{additional_channel}> channels!"
                            await inter.response.send_message(embed=emb)

        if not verified:
            emb = disnake.Embed()
            emb.title = "Could not find transaction"
            emb.color = 0xFF0000
            emb.description = f"Make sure you send **1 XRD** to the [{os.environ.get('NAME')} wallet](https://explorer.radixdlt.com/#/accounts/{wallet}) with **{inter.author}** in the message field"
            await inter.response.send_message(embed=emb)

    else:
        emb = disnake.Embed()
        emb.description = "Invalid address"
        emb.color = 0xFF0000
        await inter.response.send_message(embed=emb)


def get_payload(address):
    return f"""
        {{
            "network_identifier": {{
                "network": "mainnet"
            }},
            "account_identifier": {{
                "address": "{address}"
            }},
            "cursor": "0",
            "limit": 5
        }}
    """


def check_message(author, msg):
    decoded_1 = bytes.fromhex(msg).decode("utf-8")

    # Fix for the old transaction model
    decoded_2 = ""
    if decoded_1.startswith("00"):
        decoded_2 = bytes.fromhex(decoded_1).decode("utf-8")

    return author in decoded_1 or author in decoded_2


bot.run(os.environ.get("BOT_KEY"))
