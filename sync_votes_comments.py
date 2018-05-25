import arrow

from helpers import read_data, write_data, get_settings
import api


settings = get_settings()
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['comment_votes'])
article_map = read_data('article_map')
comment_map = read_data('comment_map')
comment_article_map = read_data('comment_article_map')

for src_comment in comment_map:
    src_article = comment_article_map[src_comment]
    dst_article = article_map[src_article]
    dst_comment = comment_map[src_comment]
    print('Getting votes for comment {}...'.format(src_comment))
    url = '{}/{}/articles/{}/comments/{}/votes.json'.format(settings['src_root'], settings['locale'], src_article,
                                                            src_comment)
    votes = api.get_resource_list(url)
    if not votes:
        print('- no votes found')
        continue
    for vote in votes:
        if last_sync < arrow.get(vote['created_at']):
            print('- adding vote {} to comment {}'.format(vote['id'], dst_comment))
            if vote['value'] == -1:
                url = '{}/articles/{}/comments/{}/down.json'.format(settings['dst_root'], dst_article, dst_comment)
            else:
                url = '{}/articles/{}/comments/{}/up.json'.format(settings['dst_root'], dst_article, dst_comment)
            payload = {'vote': {'user_id': vote['user_id'], 'created_at': vote['created_at']}}
            response = api.post_resource(url, payload, status=200)
            if response is False:
                print('Skipping vote {}'.format(vote['id']))

utc = arrow.utcnow()
sync_dates['comment_votes'] = utc.format()
write_data(sync_dates, 'sync_dates')
