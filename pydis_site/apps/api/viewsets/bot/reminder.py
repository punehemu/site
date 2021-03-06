from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    UpdateModelMixin
)
from rest_framework.viewsets import GenericViewSet

from pydis_site.apps.api.models.bot.reminder import Reminder
from pydis_site.apps.api.serializers import ReminderSerializer


class ReminderViewSet(
    CreateModelMixin, ListModelMixin, DestroyModelMixin, UpdateModelMixin, GenericViewSet
):
    """
    View providing CRUD access to reminders.

    ## Routes
    ### GET /bot/reminders
    Returns all reminders in the database.

    #### Response format
    >>> [
    ...     {
    ...         'active': True,
    ...         'author': 1020103901030,
    ...         'content': "Make dinner",
    ...         'expiration': '5018-11-20T15:52:00Z',
    ...         'id': 11
    ...     },
    ...     ...
    ... ]

    #### Status codes
    - 200: returned on success

    ### POST /bot/reminders
    Create a new reminder.

    #### Request body
    >>> {
    ...     'author': int,
    ...     'content': str,
    ...     'expiration': str  # ISO-formatted datetime
    ... }

    #### Status codes
    - 201: returned on success
    - 400: if the body format is invalid
    - 404: if no user with the given ID could be found

    ### DELETE /bot/reminders/<id:int>
    Delete the reminder with the given `id`.

    #### Status codes
    - 204: returned on success
    - 404: if a reminder with the given `id` does not exist

    ## Authentication
    Requires an API token.
    """

    serializer_class = ReminderSerializer
    queryset = Reminder.objects.prefetch_related('author')
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('active', 'author__id')
