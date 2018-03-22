from YamJam import yamjam


def get_auth():
    return '{}/token'.format(yamjam()['ZEN_USER']), yamjam()['ZEN_API_TOKEN']
