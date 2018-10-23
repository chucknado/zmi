from helpers import read_data, get_settings
import api


settings = get_settings()
src_root = settings['src_root']
locale = settings['locale']
article_map = read_data('article_map')

for src_article in article_map:
    print('Archiving {}...'.format(src_article))

    # DELETE / api / v2 / help_center / articles / {id}.json
    url = '{}/articles/{}.json'.format(src_root, src_article)
    api.delete_resource(url)
