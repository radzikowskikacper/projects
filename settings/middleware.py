from django import http
import traceback
import logging
import time
import re


# Instantiating loggers
logger = logging.getLogger('projects_helper')
request_logger = logging.getLogger('django.request')


class StandardExceptionMiddleware(object):

    # Log exceptions different form 404, together with traceback
    def process_exception(self, request, exception):
        """Describes way of processing exceptions - handles 404 errors in the standard way, logs other"""
        if isinstance(exception, http.Http404):  # pass, standard handling of 404 errors will take place later
            pass
        else:
            logger.error(str(exception) + '\n' + str(traceback.format_exc()))
        return None



MAX_BODY_LENGTH = 800  # log no more that this many chars of request.body


class LoggingMiddleware(object):

    SKIPPED_URLS_REGEXP = [
        '^/$',
        '^/i18n/',
        '^/about/$',
        '^/admin',
        '^/login/$',
        '^/logout',
        '^/logged_out',
        '^/select_course',
        '^/(lecturers|students)/[A-Za-z]+/projects/$',
        '^/(lecturers|students)/[A-Za-z]+/projects/\d+/$',
        '^/(lecturers|students)/[A-Za-z]+/projects/search[/?]?',
        '^/(lecturers|students)/[A-Za-z]+/teams/$',
        '^/(lecturers|students)/profile/',
    ]

    # Log: requests method, request path, response code, username. Requests with less imporant path are skipped.
    def process_response(self, request, response):
        log_time = time.strftime("%d/%b/%Y %H:%M:%S")

        for url_reg in self.SKIPPED_URLS_REGEXP:
            if (re.match(url_reg, request.get_full_path())):
                return response

        user = ''
        if hasattr(request, 'user'):
            user = str(request.user) # will be AnonymousUser if request has no user attr
        params = ''
        if request.body:
            params = '- params: ' + self.chunked_to_max(self.cut_csrf_token(request.body))

        request_logger.info("[{}] \"{} {}\" {} user: {} {}".format(log_time, request.method, request.get_full_path(), response.status_code, user, params))
        return response

    def cut_csrf_token(self, msg):
        splitted = re.split('(csrfmiddlewaretoken=[A-za-z\d]+[&]?)', str(msg))
        if splitted:
            return str(splitted[0] + splitted[2])[2:-1]
        else:
            return str(msg)

    def chunked_to_max(self, msg):
        if (len(msg) > MAX_BODY_LENGTH):
            return "{}\n...".format(msg[0:MAX_BODY_LENGTH])
        else:
            return msg
