from helpers import read_data, get_settings, get_resource_list, post_resource


settings = get_settings()
src_root = settings['src_root']
dst_root = settings['dst_root']
locale = settings['locale']
section_map = read_data('section_map')

for section in section_map:
    dst_section = section_map[section]
    print('\nGetting subscriptions for section {}...'.format(section))
    url = '{}/{}/sections/{}/subscriptions.json'.format(src_root, locale, section)
    subscriptions = get_resource_list(url)
    if not subscriptions:
        print('- no subscriptions found')
        continue
    for sub in subscriptions:
        print('- adding subscription {} to section {}'.format(sub['id'], dst_section))
        url = '{}/sections/{}/subscriptions.json'.format(dst_root, dst_section)
        if sub['include_comments'] is True:
            payload = {'subscription': {'source_locale': locale, 'user_id': sub['user_id'],
                                        'include_comments': True}}
        else:
            payload = {'subscription': {'source_locale': locale, 'user_id': sub['user_id']}}
        post_resource(url, payload)
