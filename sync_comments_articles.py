import arrow

from helpers import read_data, write_data, get_settings, package_comment, get_resource_list, \
    post_resource, put_resource


settings = get_settings()
src_root = settings['src_root']
dst_root = settings['dst_root']
locale = settings['locale']
sync_dates = read_data('sync_dates')
last_sync = arrow.get(sync_dates['comments'])
article_map = read_data('article_map')
comment_map = read_data('comment_map')
comment_article_map = read_data('comment_article_map')

for src_article in article_map:
    dst_article = article_map[src_article]
    print('\nGetting comments in article {}...'.format(src_article))
    url = '{}/{}/articles/{}/comments.json'.format(src_root, locale, src_article)
    comments = get_resource_list(url)
    if not comments:
        print('- no comments found')
        continue
    for src_comment in comments:
        if last_sync < arrow.get(src_comment['created_at']):
            print('- adding new comment {} to article {}'.format(src_comment['id'], dst_article))
            url = '{}/articles/{}/comments.json'.format(dst_root, dst_article)
            payload = package_comment(src_comment)
            new_comment = post_resource(url, payload)
            comment_map[str(src_comment['id'])] = new_comment['id']
            comment_article_map[str(src_comment['id'])] = src_article
            continue
        if last_sync < arrow.get(src_comment['updated_at']):
            print('- updating comment {} in article {}'.format(src_comment['id'], dst_article))
            dst_comment = comment_map[str(src_comment['id'])]
            url = '{}/articles/{}/comments/{}.json'.format(dst_root, dst_article, dst_comment)
            payload = package_comment(src_comment, put=True)
            put_resource(url, payload)
            continue
        print('- comment {} is up to date'.format(src_comment['id']))

utc = arrow.utcnow()
sync_dates['comments'] = utc.format()
write_data(sync_dates, 'sync_dates')
write_data(comment_map, 'comment_map')
write_data(comment_article_map, 'comment_article_map')
