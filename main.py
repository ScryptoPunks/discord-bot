import config
import requests
import disnake
from disnake.ext import commands

transactions = "https://mainnet.radixdlt.com/account/transactions"
balances = "https://mainnet.radixdlt.com/account/balances"
headers = {'Content-Type': 'application/json',
           'X-Radixdlt-Target-Gw-Api': '1.0.0'}

bot = commands.Bot(
    command_prefix='/',
    test_guilds=[config.SERVER_ID]
)


@bot.slash_command(description="Link your Discord account to your Radix address")
async def verify(inter, address):
    if address.startswith("rdx") and len(address) == 65:
        txs = requests.request(
            "POST", transactions, headers=headers, data=get_payload(address)).json()
        verified = False
        for tx in txs["transactions"]:
            if tx["actions"][0]["to_account"]["address"] == config.VERIFICATION_ADDRESS:
                if "message" in tx["metadata"] and check_message(str(inter.author), tx["metadata"]["message"]):
                    tokens = requests.request(
                        "POST", balances, headers=headers, data=get_payload(address)).json()
                    for token in tokens["account_balances"]["liquid_balances"]:
                        if token["token_identifier"]["rri"] == config.TOKEN_RRI:
                            verified = True

                            emb = disnake.Embed()
                            emb.color = 0x00FF00
                            emb.title = "Address verified"
                            emb.description = f"You now have access to <#{config.VERFIED_CHANNEL_ID}>!"
                            await inter.response.send_message(embed=emb)

        if not verified:
            emb = disnake.Embed()
            emb.title = "Could not verify address"
            emb.color = 0xFF0000
            emb.description = f"Make sure that: \n1. you hold at least **1 SPUNKS** token \n2. you sent **1 XRD** to the [{config.VERIFICATION_ADDRESS} wallet](https://explorer.radixdlt.com/#/accounts/{config.PROJECT_NAME}) with **{inter.author}** in the message field"
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
            "limit": 5
        }}
    """


def check_message(author, msg):
    decoded_1 = bytes.fromhex(msg).decode("utf-8").replace("\x00", "")

    # Fix for old transaction model
    decoded_2 = ""
    if decoded_1.startswith("00"):
        decoded_2 = bytes.fromhex(decoded_1).decode("utf-8").replace("\x00", "")

    return author == decoded_1 or author == decoded_2


bot.run(config.BOT_KEY)
