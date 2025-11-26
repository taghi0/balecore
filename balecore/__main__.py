import sys
import argparse
from balecore import __version__

def main():
    parser = argparse.ArgumentParser(description="Balecore CLI - A tool for managing Bale bots.")
    
    parser.add_argument('-n', '--new', action='store_true', help='Create a new bot starter file in the current directory.')
    parser.add_argument('-f', '--github', action='store_true', help='Display the GitHub repository link.')
    parser.add_argument('-v', '--version', action='store_true', help='Display the library version.')

    args = parser.parse_args()

    if args.new:
        file_content = """from balecore import Bot
from balecore.updates import Message
from balecore.filters import Filters

bot: Bot = Bot(token="YOUR_TOKEN")

filters: Filters = Filters(bot=bot)

@bot.Message(filters.command("start") & filters.text & filters.private)
async def start_command(bot: Bot, message: Message):
    await message.reply_text(message.text)

bot.start
"""
        try:
            with open('bot.py', 'w') as f:
                f.write(file_content)
            print("New bot starter file created: bot.py")
        except Exception as e:
            print(f"Error creating file: {e}")
            sys.exit(1)
    
    elif args.github:
        print("GitHub repository: https://github.com/taghi0/balecore/")
    
    elif args.version:
        print(f"Balecore version: {__version__}")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()