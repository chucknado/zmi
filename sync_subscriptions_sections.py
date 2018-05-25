from helpers import read_data, get_settings
import api


settings = get_settings()
section_map = read_data('section_map')

for section in section_map:
    dst_section = section_map[section]
    print('\nGetting subscriptions for section {}...'.format(section))
    url = '{}/{}/sections/{}/subscriptions.json'.format(settings['src_root'], settings['locale'], section)
    subscriptions = api.get_resource_list(url)
    if not subscriptions:
        print('- no subscriptions found')
        continue
    for sub in subscriptions:
        print('- adding subscription {} to section {}'.format(sub['id'], dst_section))
        url = '{}/sections/{}/subscriptions.json'.format(settings['dst_root'], dst_section)
        if sub['include_comments'] is True:
            payload = {'subscription': {'source_locale': settings['locale'], 'user_id': sub['user_id'],
                                        'include_comments': True}}
        else:
            payload = {'subscription': {'source_locale': settings['locale'], 'user_id': sub['user_id']}}
        response = api.post_resource(url, payload)
        if response is False:
            print('Skipping subscription {}'.format(sub['id']))
