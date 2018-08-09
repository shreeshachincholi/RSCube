from telegram.ext import Updater, MessageHandler, CommandHandler, Filters
from watson_developer_cloud import ConversationV1
from urllib2 import urlopen
import json

context = None
place_type = None
list_of_category = ['night_club', 'restaurant', 'lodging', 'shopping_mall', 'hospital', 'cafe', 'hindu_temple',
                    'movie_theater', 'bus_station', 'atm', 'hindu_temple']

def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    print('Update "%s" caused error "%s"', update, error)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start_command_handler(bot, update):
    print('Received /start command')
    update.message.reply_text('Hi!')


def help_command_handler(bot, update):
    print('Received /help command')
    update.message.reply_text('Help!')

category = None

def text_message_handler(bot, update):
    print('Received a text update')
    global context

    conversation = ConversationV1(username='19f100cf-36ad-44b9-838a-4a4e9aa0afed',  # TODO
                                  password='n40e0OFlX86s',  # TODO
                                  version='2018-02-16')

    # get response from watson
    response = conversation.message(
        workspace_id='146e3a06-ffa7-4b96-88f9-a22dd237b17c',  # TODO
        input={'text': update.message.text},
        context=context)
    print(json.dumps(response, indent=2))

    if len(response['entities']) > 0:
        # print("inside")
        if 'entity' in response['entities'][0].keys():
            # print('inside')
            if str(response['entities'][0]['entity']) == 'place_name':
                # print("inside")
                if 'value' in response['entities'][0]:
                    boolean_var = response['entities'][0]['value'].encode('ascii', 'ignore') in list_of_category
                    if boolean_var:
                        global place_type
                        place_type = response['entities'][0]['value']
                        print("place type", place_type.encode('ascii', 'ignore'))
                else:
                    print("no key named value found")

    context = response['context']

    # build response
    # if 'place_name' in response['context']:
       # place = str(response['context']['place_name'])

    # build response
    resp = ''
    for text in response['output']['text']:
        resp += text

    update.message.reply_text(resp)


def location_message_handler(bot, update):
    print('Received a location update')
    lon = update.message.location.longitude
    lat = update.message.location.latitude
    # update.message.reply_text(str(lon) + ' ' + str(lat))

    places = get_places(lat, lon, place_type)

    # build text response using places
    update.message.reply_text('Here are some options.')

    for place in places['results']:
        # result = place['name'] + '(' + place['rating'] + ' stars)'
        # result = place['name'].encode('ascii', 'ignore')
        result = place['name'].encode('ascii', 'ignore') + " \n " + str(place['vicinity'])

        # result = place['name']
        # result = 'hello'
        print(result)
        update.message.reply_text(result)
    update.message.reply_text("Want to know about something else?")

def get_places(lat, lon, place_type):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json' \
          '?location=%f,%f' \
          '&radius=5000' \
          '&type=%s' \
          '&key=AIzaSyBW-83AVjn8bsLydCtxvYgctpD4-1WiNTQ' % (lat, lon, place_type)

    print(url)
    places = json.loads(urlopen(url).read())
    print(json.dumps(places, indent=2))
    return places


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater('687661025:AAFNe21i3y5z7pF0n82DhGa7uk6-M7o5VD4')  # TODO

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start_command_handler))
    dp.add_handler(CommandHandler("help", help_command_handler))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, text_message_handler))

    # longitude and latitude
    dp.add_handler(MessageHandler(Filters.location, location_message_handler))

    dp.add_error_handler(error_handler)

    # Start the Bot
    updater.start_polling()

    print('started poling, ready to receive updates')

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
