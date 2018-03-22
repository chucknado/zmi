import arrow

from helpers import read_data, write_data, get_settings, get_resource_list, post_resource


settings = get_settings()
src_root = settings['src_root']
dst_root = settings['dst_root']
locale = settings['locale']
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['article_votes'])
article_map = read_data('article_map')

for src_article in article_map:
    dst_article = article_map[src_article]
    print('\nGetting votes for article {}...'.format(src_article))
    url = '{}/{}/articles/{}/votes.json'.format(src_root, locale, src_article)
    votes = get_resource_list(url)
    if not votes:
        print('- no votes found')
        continue
    for vote in votes:
        if last_sync < arrow.get(vote['created_at']):
            print('- adding vote {} to article {}'.format(vote['id'], dst_article))
            if vote['value'] == -1:
                url = '{}/articles/{}/down.json'.format(dst_root, dst_article)
            else:
                url = '{}/articles/{}/up.json'.format(dst_root, dst_article)
            payload = {'vote': {'user_id': vote['user_id'], 'created_at': vote['created_at']}}
            post_resource(url, payload, status=200)

utc = arrow.utcnow()
sync_dates['article_votes'] = utc.format()
write_data(sync_dates, 'sync_dates')
