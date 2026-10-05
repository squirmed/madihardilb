import discord
from discord import app_commands
import json
import os

# --- Configuration ---
SAVE_FILE = "/data/scores.json"

# --- Score Loading & Saving ---
def load_scores():
    """Load scores from file, or return default if file doesn't exist."""
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"hardi": 0, "madi": 0}

def save_scores(scores):
    """Save scores to file."""
    with open(SAVE_FILE, "w") as f:
        json.dump(scores, f, indent=2)

# Initialize scores
scores = load_scores()

# --- Discord Setup ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

def build_embed():
    """Build the scoreboard embed."""
    embed = discord.Embed(title="🏆 Hardi vs Madi Scoreboard", color=discord.Color.gold())
    embed.add_field(name="Hardi", value=str(scores["hardi"]), inline=True)
    embed.add_field(name="Madi", value=str(scores["madi"]), inline=True)
    return embed

# --- Button View ---
class ScoreView(discord.ui.View):
    def __init__(self):
        # timeout=None is required for buttons to keep working after a bot restart
        super().__init__(timeout=None)

    @discord.ui.button(label="Hardi Wins", style=discord.ButtonStyle.success, custom_id="scoreboard:hardi")
    async def hardi_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        scores["hardi"] += 1
        save_scores(scores)  # Save immediately after every click
        await interaction.response.edit_message(embed=build_embed())

    @discord.ui.button(label="Madi Wins", style=discord.ButtonStyle.danger, custom_id="scoreboard:madi")
    async def madi_win(self, interaction: discord.Interaction, button: discord.ui.Button):
        scores["madi"] += 1
        save_scores(scores)
        await interaction.response.edit_message(embed=build_embed())

# --- Slash Command to Spawn the Scoreboard ---
@tree.command(name="scoreboard", description="Start the Hardi vs Madi scoreboard")
async def scoreboard(interaction: discord.Interaction):
    await interaction.response.send_message(embed=build_embed(), view=ScoreView())

@tree.command(name="reset", description="Reset the Hardi vs Madi scoreboard")
async def reset(interaction: discord.Interaction):
    scores["hardi"] = 0
    scores["madi"] = 0
    save_scores(scores)
    await interaction.response.send_message("Scoreboard reset! 🧹", ephemeral=True)

# --- Bot Events ---
@client.event
async def on_ready():
    # Re-register the persistent view so buttons still work after restart
    client.add_view(ScoreView())
    await tree.sync()
    print(f"Logged in as {client.user}")

# --- Run the Bot ---
client.run(os.getenv("DISCORD_TOKEN"))