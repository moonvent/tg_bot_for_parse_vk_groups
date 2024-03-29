import config
import requests
import sqlite3


def parse_group():
    """
        Парсим вк группы, берем их из БД, и после парсим
    :return:
    """

    connect = sqlite3.connect(database=config.name_of_db)
    cursor = connect.cursor()

    groups = (row[0] for row in cursor.execute('SELECT title_group FROM groups'))
    for group in tuple(groups):
        if group.startswith('-'):
            html_code = requests.get('https://api.vk.com/method/wall.get?owner_id={}&count=2&access_token={}&v=5.120'.format(group, config.vk_token)).text
        else:
            html_code = requests.get('https://api.vk.com/method/wall.get?domain={}&count=2&access_token={}&v=5.120'.format(group, config.vk_token)).text
        dict_of_code = eval(html_code.replace('false', 'False').replace('true', 'True').replace('null', 'None'))
        post = dict_of_code.get('response').get('items')[-1]
        if cursor.execute('SELECT * '  # если такая запись уже публикаовалось - бан
                          'FROM posts '
                          'WHERE posts.id_group = "{}" '
                          '    AND posts.id_post = {}'.format(group, post.get("id"))).fetchall():
            continue
        # else:
        #     cursor.execute('INSERT INTO posts (id_group, id_post) VALUES ("{}", {})'.format(group, post.get("id")))
        #     connect.commit()

        result_dict = {'id': post.get('id'), 'text': post.get('text')}
        attachments = post.get('attachments')
        result_dict['attachments'] = []
        if attachments:
            for attachment in attachments:
                if attachment.get('photo'):
                    result_dict.get('attachments').append(requests.get(
                        max(attachment.get('photo').get('sizes'), key=lambda x: x.get('height')).get('url').replace('\\',
                                                                                                                    '')).content)
                elif attachment.get('link'):
                    result_dict.get('attachments').append(attachment.get('link').get('url'))
                    result_dict['type'] = 'link'
                    result_dict['title'] = attachment.get('link').get('title')

        if not post.get('text') and not post.get('attachments'):
            continue
        yield result_dict
    connect.close()


if __name__ == '__main__':
    print(parse_group())
