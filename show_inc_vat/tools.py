from odoo.http import request


def is_norwegian_visitor():
    """Return whether the current website visitor is located in Norway (GeoIP)."""
    return bool(request) and request.geoip.country_code == 'NO'
