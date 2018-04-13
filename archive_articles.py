from helpers import read_data, get_settings, put_resource


settings = get_settings()
src_root = settings['src_root']
src_archive = settings['src_archive']
locale = settings['locale']
article_map = read_data('article_map')

for src_article in article_map:
    print('Archiving {}...'.format(src_article))
    url = '{}/{}/articles/{}.json'.format(src_root, locale, src_article)
    payload = {'article': {'section_id': int(src_archive)}}
    put_resource(url, payload)
