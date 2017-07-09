"""
AWS Lambda functions
"""

from ask import alexa
import dvb


def lambda_handler(request_obj, context=None):
    '''
    This is the main function to enter to enter into this code.
    If you are hosting this code on AWS Lambda, this should be the entry point.
    Otherwise your server can hit this code as long as you remember that the
    input 'request_obj' is JSON request converted into a nested python object.
    '''

    metadata = {}  # add your own metadata to the request using key value pairs
    return alexa.route_request(request_obj, metadata)


@alexa.default_handler()
def default_handler(request):
    """ The default handler gets invoked if no handler is set for a request """
    return alexa.create_response(message="Was kann ich für dich tun?")


@alexa.request_handler("LaunchRequest")
def launch_request_handler(request):
    return default_handler(request)


@alexa.request_handler("SessionEndedRequest")
def session_ended_request_handler(request):
    return


@alexa.intent_handler('StationIntent')
def get_recipe_intent_handler(request):
    """
    You can insert arbitrary business logic code here
    """

    # Get variables like userId, slots, intent name etc from the 'Request'
    # object
    station = request.slots.get("station")

    if station is None:
        return alexa.create_response(message="Entschuldigung, aber du hast \
mir keine Haltestelle genannt.")

    stops = dvb.monitor(station, 0, 4)

    speech_output = "Hier sind die nächten 4 Abfahrten für {station}.".format(
        station=station)
    card_output = ""
    for stop in stops:
        speech_output += " Linie {line} nach {direction} in {arrival} Minuten.".format(
            line=stop["line"], direction=stop["direction"], arrival=stop["arrival"])
        card_output += "Linie {line} nach {direction}: {arrival} Minuten\n".format(
            line=stop["line"], direction=stop["direction"], arrival=stop["arrival"])
    
    card = alexa.create_card(title="Die nächsten Abfahrten für {station}".format(station=station),
                             subtitle=None, content=card_output)
    return alexa.create_response(message= speech_output, card_obj=card)
