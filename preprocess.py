import collections

import pandas as pd
import vk_api

import analysis

vk = None
tukallo_id = '125376958'

SCORE_THRESHOLD = 4  # score is given from 0 to 10. If score >= threshold => user is a programmer


def get_score(id):
    """
    :param id: user_id to get_score for
    :return: (rating: ing, lang_stat: dict), where rating is an int in a range [0; 10]
            depicting assurance, that a user is a programmer,
            lang_stat is user's statistics about programming languages from LANGUAGES
    """
    return analysis.analyze_user(id, vk)


def get_max(d: dict):
    maxx = 0
    ans = "-"
    for key in d:
        val = d[key]
        if val > maxx:
            ans = key
            maxx = val
    return ans


def walk_and_store(start_id=tukallo_id, lang="", limit=100):
    programmers = pd.DataFrame(columns=('id', 'first_name', 'last_name', 'rank', 'language', 'link'))

    start = vk.users.get(user_ids=start_id)[0]
    start_user = (start_id, start['first_name'], start['last_name'])

    observed_users = set()
    observed_users.add(start_user)

    to_visit = collections.deque()
    to_visit.append(start_user)

    # starting bfs
    while len(to_visit) != 0:
        cur_user = to_visit.popleft()  # (id, first_name, last_name)

        # try to get friends to learn if the account was deleted
        try:
            friends = vk.friends.get(user_id=cur_user[0], fields='first_name,last_name')
        except vk_api.exceptions.ApiError as error_msg:
            continue

        # analyze user
        score = get_score(cur_user[0])

        link = 'https://vk.com/id' + str(cur_user[0])
        best_lang = get_max(score[1])
        if lang == '':
            if score[0] >= SCORE_THRESHOLD:
                programmers.loc[len(programmers)] = [*cur_user, score[0], best_lang, link]
        elif score[1][lang] > 0:
            programmers.loc[len(programmers)] = [*cur_user, score[0], lang, link]

        if len(programmers) >= limit:
            break

        for friend in friends['items']:
            friend_t = (friend['id'], friend['first_name'], friend['last_name'])
            if friend_t not in observed_users:
                if friend_t[1] == 'Tukallo':
                    print('fucking shit!')
                to_visit.append(friend_t)
                observed_users.add(friend_t)

    # bfs is finished, time to save programmers we found
    programmers = programmers.sort_values(by=['rank'], ascending=False)
    programmers.to_csv('processed/' + start_user[1] + start_user[2] + str(limit) + lang + ".csv")


def get_developers(vk_id=tukallo_id, lang='', limit=10):
    """
    Method finds all the developers in a specified programming language close to specified user_id
    :param vk_id: user to start search from
    :param lang: language to filter developers with. If lang == '', then all the developers are reported
            without filtering by language
    :param limit: number of developers to report
    :return: output is written to console & csv file
    """
    login, password = "alex.tukallo@gmail.com", ""
    vk_session = vk_api.VkApi(login=login)

    try:
        vk_session.auth()
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return

    print("authorized")

    global vk
    vk = vk_session.get_api()

    walk_and_store(vk_id, lang, limit)


if __name__ == '__main__':
    # get all the developers in all the programming languages:
    get_developers(limit=40)  # Tukallo
    get_developers(vk_id='53448', limit=40)  # Andrey Novoselsky
    get_developers(vk_id='33251758', limit=5)  # Yuriy Tikhonov

    # get all the developers for a specific programming language:
    get_developers(lang='python', limit=10)  # Tukallo
    get_developers(vk_id='53448', lang='java', limit=10)  # Andrey Novoselsky
    get_developers(vk_id='225270855', lang='php', limit=1)  # Ivan Revin
