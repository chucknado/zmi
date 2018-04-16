from helpers import read_data, get_settings, get_resource_list, post_resource


settings = get_settings()
src_root = settings['src_root']
dst_root = settings['dst_root']
locale = settings['locale']
article_map = read_data('article_map')

for src_article in article_map:
    dst_article = article_map[src_article]
    print('\nGetting subscriptions for article {}...'.format(src_article))
    url = '{}/articles/{}/subscriptions.json'.format(src_root, src_article)
    subscriptions = get_resource_list(url)
    if not subscriptions:
        print('- no subscriptions found')
        continue
    for sub in subscriptions:
        print('- adding subscription {} to article {}'.format(sub['id'], dst_article))
        url = '{}/articles/{}/subscriptions.json'.format(dst_root, dst_article)
        payload = {'subscription': {'source_locale': locale, 'user_id': sub['user_id']}}
        post_resource(url, payload)
