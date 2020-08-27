import csv
import random
import typing

from simple_slack_bot.simple_slack_bot import SimpleSlackBot

simple_slack_bot = SimpleSlackBot(debug=True)

# character's name will be the key while the value will a list of all their lines
character_lines: typing.Dict[str, typing.List[str]] = {}


@simple_slack_bot.register("message")
def office_callback(request):
    """Our callback which is called every time a new message is sent by a user
    :param request: the request object that came with the message event
    """

    if request.message is not None:
        for token in request.message.split(' '):
            if token.lower() in character_lines:
                character_name = token.lower()
                random_index = random.randint(0, len(character_lines[character_name]) - 1)
                request.write(character_name.capitalize() + ": " + character_lines[character_name][random_index])


def read_in_characters_lines():
    """Stores all characters' lines into a dictionary
    """

    with open(r"the_office_lines_scripts.csv", "r", encoding='utf-8') as csvfile:
        csv_f = csv.reader(csvfile)
        print(csv_f)

        for _, _, _, _, line_text, speaker, _ in csv_f:
            speaker = speaker.lower()
            if speaker in character_lines:
                character_lines[speaker].append(line_text)
            else:
                character_lines[speaker] = []
                character_lines[speaker].append(line_text)


def main():
    read_in_characters_lines()
    print("bot ready!")
    simple_slack_bot.start()


if __name__ == "__main__":
    main()
