import arrow

from helpers import read_data, write_data, get_settings
import api


settings = get_settings()
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['article_votes'])
article_map = read_data('article_map')

for src_article in article_map:
    dst_article = article_map[src_article]
    print('\nGetting votes for article {}...'.format(src_article))
    url = '{}/{}/articles/{}/votes.json'.format(settings['src_root'], settings['locale'], src_article)
    votes = api.get_resource_list(url)
    if not votes:
        print('- no votes found')
        continue
    for vote in votes:
        if last_sync < arrow.get(vote['created_at']):
            print('- adding vote {} to article {}'.format(vote['id'], dst_article))
            if vote['value'] == -1:
                url = '{}/articles/{}/down.json'.format(settings['dst_root'], dst_article)
            else:
                url = '{}/articles/{}/up.json'.format(settings['dst_root'], dst_article)
            payload = {'vote': {'user_id': vote['user_id'], 'created_at': vote['created_at']}}
            response = api.post_resource(url, payload, status=200)
            if response is False:
                print('Skipping vote {}'.format(vote['id']))

utc = arrow.utcnow()
sync_dates['article_votes'] = utc.format()
write_data(sync_dates, 'sync_dates')
