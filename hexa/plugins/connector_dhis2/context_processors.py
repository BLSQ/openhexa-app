from hexa.plugins.connector_dhis2.models import Extract


def current_extract(request):
    if request.session.get("connector_dhis2_current_extract") is not None:
        try:
            return {
                "current_extract": Extract.objects.filter_for_user(request.user).get(
                    id=request.session.get("connector_dhis2_current_extract")
                )
            }
        except Extract.DoesNotExist:
            pass

    return {}
