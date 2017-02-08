from rest_framework.renderers import BaseRenderer


class ClusterKeyRenderer(BaseRenderer):
    """ Simple plain text renderer for ClusterKey model.

    Returns data in the following format: key: value
    For non existent elements returns an empty string
    """

    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data and 'key' in data and 'value' in data:
            return "%s: %s" % (data['key'], data['value'])
        return ""
