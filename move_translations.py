from helpers import read_data, get_settings, package_translation
import api


settings = get_settings()
article_map = read_data('article_map')
locales = ['de', 'es', 'fr', 'ja', 'pt-br']

for article in article_map:
    url = '{}/articles/{}/translations/missing.json'.format(settings['src_root'], article)
    missing_locales = api.get_resource_list(url, list_name='locales', paginate=False)
    for locale in locales:
        if locale in missing_locales:   # if translation missing in src, nothing to move
            continue
        print('Moving {} translation for article {}'.format(locale, article))

        # get translation in src hc
        url = '{}/articles/{}/translations/{}.json'.format(settings['src_root'], article, locale)
        translation = api.get_resource(url)

        # create translation in dest hc
        url = '{}/articles/{}/translations.json'.format(settings['dst_root'], article_map[article])
        payload = package_translation(translation)
        api.post_resource(url, payload)

print('\nFinished moving translations.\n')
