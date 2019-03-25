# -*- coding: utf-8 -*-
def formalize_request(website, lang, criteria):
    """Formalize request.

    :param lang:
    :param criteria:
    :return: url with params
    """
    if(not website.endswith('/')):
        website += '/'
    return '%s%s/?criteria=%s' % (website, lang, criteria)
