from helpers import read_data, get_settings
import api


settings = get_settings()
article_map = read_data('article_map')

for src_article in article_map:
    dst_article = article_map[src_article]
    print('\nGetting subscriptions for article {}...'.format(src_article))
    url = '{}/articles/{}/subscriptions.json'.format(settings['src_root'], src_article)
    subscriptions = api.get_resource_list(url)
    if not subscriptions:
        print('- no subscriptions found')
        continue
    for sub in subscriptions:
        print('- adding subscription {} to article {}'.format(sub['id'], dst_article))
        url = '{}/articles/{}/subscriptions.json'.format(settings['dst_root'], dst_article)
        payload = {'subscription': {'source_locale': settings['locale'], 'user_id': sub['user_id']}}
        response = api.post_resource(url, payload)
        if response is False:
            print('Skipping subscription {}'.format(sub['id']))
