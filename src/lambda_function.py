"""
AWS Lambda functions
"""

from ask import alexa
import requests
import json


def lambda_handler(request_obj, context=None):
    '''
    This is the main function to enter to enter into this code.
    If you are hosting this code on AWS Lambda, this should be the entry point.
    Otherwise your server can hit this code as long as you remember that the
    input 'request_obj' is JSON request converted into a nested python object.
    '''

    metadata = dict()
    return alexa.route_request(request_obj, metadata)


@alexa.default_handler()
def default_handler(request):
    """ The default handler gets invoked if no handler is set for a request """
    return alexa.create_response(message="Was kann ich für dich tun?", end_session=False)


@alexa.request_handler("LaunchRequest")
def launch_request_handler(request):
    return alexa.create_response(message="Du kannst mich nach den Abfahrten an einer Haltestelle der d.v.b. fragen. Was kann ich für dich tun?", end_session=False)


@alexa.request_handler("SessionEndedRequest")
def session_ended_request_handler(request):
    return


@alexa.intent_handler("AMAZON.CancelIntent")
def session_cancel_intent(request):
    return alexa.create_response(message="Okay", end_session=True)


@alexa.intent_handler("AMAZON.StopIntent")
def session_stop_intent(request):
    return alexa.create_response(message="Okay", end_session=True)


@alexa.intent_handler('AMAZON.HelpIntent')
def get_help_intent_handler(request):
    response_text = "Frage einfach nach den Abfahrten an einer Haltestelle der d.v.b., \
wie zum Beispiel 'Nenne mir die nächsten Abfahrten am Hauptbahnhof' \
oder sage Stop um den Skill zu beenden. Was kann ich für dich tun?"
    return alexa.create_response(message=response_text, end_session=False)


@alexa.intent_handler('StationIntent')
def get_station_intent_handler(request):
    """
    You can insert arbitrary business logic code here
    """

    # Get variables like userId, slots, intent name etc from the 'Request'
    # object
    station = request.slots.get("station")

    if station is None:
        return alexa.create_response(message="Entschuldigung, du hast mir \
keine Haltestelle genannt. Kannst du bitte deine Anfrage mit Haltestelle Wiederholen?")

    stops = dvb_monitor(station)

    speech_output = "Hier sind die nächsten 4 Abfahrten für {station}.".format(
        station=station)
    card_output = ""
    for stop in stops:
        speech_output += " Linie {line} nach {direction} in {arrival}.".format(
            line=stop["line"], direction=stop["direction"], arrival="einer Minute" if int(stop["arrival"]) == 1 else "{} Minuten".format(stop["arrival"]))
        card_output += "Linie {line} nach {direction}: {arrival} Minute{n}\n".format(
            line=stop["line"], direction=stop["direction"], arrival=stop["arrival"], n="n" if int(stop["arrival"]) != 1 else "")

    card = alexa.create_card(title="Die nächsten Abfahrten für {station}".format(station=station),
                             subtitle=None, content=card_output)
    return alexa.create_response(message=speech_output, end_session=True, card_obj=card)


def dvb_monitor(stop):

    try:
        r = requests.get(
            url='http://widgets.vvo-online.de/abfahrtsmonitor/Abfahrten.do',
            params={
                'ort': 'Dresden',
                'hst': stop,
                'vz': 0,
                'lim': 4,
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content.decode('utf-8'))
        else:
            raise requests.HTTPError('HTTP Status: {}'.format(r.status_code))
    except requests.RequestException as e:
        response = None

    if response is None:
        return None
    return [
        {
            'line': line,
            'direction': direction,
            'arrival': 0 if arrival == '' else int(arrival)
        } for line, direction, arrival in response
    ]
