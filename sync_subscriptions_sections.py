import arrow

from helpers import read_data, write_data, get_settings, get_resource_list, post_resource


settings = get_settings()
src_root = settings['src_root']
dst_root = settings['dst_root']
locale = settings['locale']
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['subscriptions_sections'])
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
        if last_sync < arrow.get(sub['created_at']):
            print('- adding subscription {} to section {}'.format(sub['id'], dst_section))
            url = '{}/sections/{}/subscriptions.json'.format(dst_root, dst_section)
            if sub['include_comments'] is True:
                payload = {"subscription": {"source_locale": locale, "user_id": sub['user_id'],
                                            "include_comments": True}}
            else:
                payload = {"subscription": {"source_locale": locale, "user_id": sub['user_id']}}
            post_resource(url, payload)
        else:
            print('- subscription {} is up to date'.format(sub['id']))

utc = arrow.utcnow()
sync_dates['subscriptions_sections'] = utc.format()
write_data(sync_dates, 'sync_dates')
