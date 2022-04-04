# -*- coding: utf-8 -*-
"""Simple fact sample app."""

import logging
import requests

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response


# =========================================================================================================================================
# TODO: The items below this comment need your attention.
# =========================================================================================================================================
SKILL_NAME = "Golf Infos"
WELCOME_MESSAGE = "Bienvenue chez Golf Infos : toutes les dernières infos de la planète golf ! Vous pouvez me demander les derniers résultats ou les résultats d'un tour en particulier."
HELP_MESSAGE = "Golf Infos vous informe sur les derniers résultats des tours professionnels de golf : PGA Tour, Tour Européen, Sunshine Tour. Pour connaître les derniers résultats de l'ensemble des tours, dites \"Alexa, demande à Golf Infos les derniers résultats\". Pour connaître les derniers résultats du PGA tour, dites \"Alexa, demande à Golf Infos les derniers résultats du PGA Tour\". Comment puis-je vous aider?"
HELP_REPROMPT = "Comment puis-je vous aider?"
STOP_MESSAGE = "Merci d'avoir utilisé Golf Infos ! Au revoir."
FALLBACK_MESSAGE = "Golf info ne peut rien pour ça. Il peut seulement vous donner des résultats de golf. Comment puis-je vous aider?"
FALLBACK_REPROMPT = 'Comment puis-je vous aider?'
EXCEPTION_MESSAGE = "Désolé. Je ne peux rien pour ça."


# =========================================================================================================================================
# Editing anything below this line might break your skill.
# =========================================================================================================================================

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_golf_results(tour_slot=None):
    speeches = []
    logger.info('Tour Slot : %s' % tour_slot)
    
    results = requests.get('https://golf.jacoduplessis.co.za/?format=json').json()

    for tour in results['Leaderboards']:

        if tour_slot is not None:
            if tour_slot in ('pga', 'pga tour') and tour['Tour'] != 'PGA Tour':
                continue
            if tour_slot in ('european tour', 'tour européen') and tour['Tour'] != 'European Tour':
                continue
            if tour_slot in ('sunshine', 'sunshine tour') and tour['Tour'] != 'Sunshine Tour':
                continue

        leader_or_winner = 'leader'
        if tour['Round'] == 0:
            current_round = "Tournoi terminé"
            leader_or_winner = 'vainqueur'
        elif tour['Round'] == 1:
            current_round = "1er tour"
        else:
            current_round = "%sème tour" % tour['Round']
        leader = tour['Players'][0]

        speech = '%s. %s. %s. %s est %s à %s.' % (tour['Tour'], tour['Tournament'], current_round, leader['Name'], leader_or_winner, leader['Total'])
        speeches.append(speech)

    return '\n'.join(speeches)

# Built-in Intent Handlers
class GetNewFactHandler(AbstractRequestHandler):
    """Handler for GetNewFact Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("GetNewGolfFactIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In GetNewFactHandler")

        slots = handler_input.request_envelope.request.intent.slots
        tour = slots['tour'].value

        speech = get_golf_results(tour)

        handler_input.response_builder.speak(speech).set_card(SimpleCard(SKILL_NAME, speech)).set_should_end_session(True)
        return handler_input.response_builder.response


class WelcomeHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In WelcomeHandler")

        handler_input.response_builder.speak(WELCOME_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(SKILL_NAME, WELCOME_MESSAGE)).set_should_end_session(False)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        handler_input.response_builder.speak(HELP_MESSAGE).ask(
            HELP_REPROMPT).set_card(SimpleCard(
                SKILL_NAME, HELP_MESSAGE)).set_should_end_session(False)
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        handler_input.response_builder.speak(STOP_MESSAGE).set_should_end_session(True)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.

    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(
            FALLBACK_REPROMPT).set_should_end_session(False)
        return handler_input.response_builder.response


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(
            HELP_REPROMPT).set_should_end_session(False)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(GetNewFactHandler())
sb.add_request_handler(WelcomeHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# TODO: Uncomment the following lines of code for request, response logs.
# sb.add_global_request_interceptor(RequestLogger())
# sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
lambda_handler = sb.lambda_handler()
