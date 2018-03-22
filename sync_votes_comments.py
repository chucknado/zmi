import arrow

from helpers import read_data, write_data, get_settings, get_resource_list, post_resource


settings = get_settings()
src_root = settings['src_root']
dst_root = settings['dst_root']
locale = settings['locale']
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
    url = '{}/{}/articles/{}/comments/{}/votes.json'.format(src_root, locale, src_article, src_comment)
    votes = get_resource_list(url)
    if not votes:
        print('- no votes found')
        continue
    for vote in votes:
        if last_sync < arrow.get(vote['created_at']):
            print('- adding vote {} to comment {}'.format(vote['id'], dst_comment))
            if vote['value'] == -1:
                url = '{}/articles/{}/comments/{}/down.json'.format(dst_root, dst_article, dst_comment)
            else:
                url = '{}/articles/{}/comments/{}/up.json'.format(dst_root, dst_article, dst_comment)
            payload = {'vote': {'user_id': vote['user_id'], 'created_at': vote['created_at']}}
            post_resource(url, payload, status=200)

utc = arrow.utcnow()
sync_dates['comment_votes'] = utc.format()
write_data(sync_dates, 'sync_dates')
