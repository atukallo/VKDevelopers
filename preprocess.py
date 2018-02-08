import collections

import pandas as pd
import vk_api

import analyzis

vk = None
default_user = ('125376958', 'Alexander', 'Tukallo')

SCORE_THRESHOLD = 3  # score is given from 0 to 10. If score >= threshold => user is a programmer


def get_score(id):
    """
    :param id: user_id to get_score for
    :return: (rating: ing, language: str), where rating is an int in a range [0; 10]
            depicting assurance, that a user is a programmer,
            language is user's favourite programming language if any, else "-"
    """
    return analyzis.analyze_user(id, vk)


def walk_and_store(start=default_user, limit=50, lang=""):
    programmers = pd.DataFrame(columns=('id', 'first_name', 'last_name', 'rank', 'language', 'link'))

    observed_users = set()
    observed_users.add(start)

    to_visit = collections.deque()
    to_visit.append(start)

    # starting bfs
    while len(to_visit) != 0:
        # logging:
        # if len(observed_users) % 5 == 0:
        #     print('Visited ' + str(len(observed_users)) + ' guys')

        cur_user = to_visit.popleft()  # (id, first_name, last_name)

        # try to get friends to learn if the account was deleted
        try:
            friends = vk.friends.get(user_id=cur_user[0], fields='first_name,last_name')
        except vk_api.exceptions.ApiError as error_msg:
            continue

        score = get_score(cur_user[0])
        if score[0] >= SCORE_THRESHOLD and (lang == '' or lang == score[1]):
            link = 'https://vk.com/id' + str(cur_user[0])
            programmers.loc[len(programmers)] = [*cur_user, *score, link]
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
    print('All in all analyzed ' + str(len(observed_users)) + ' guys')
    programmers = programmers.sort_values(by=['rank'], ascending=False)
    programmers.to_csv(start[1] + start[2] + str(limit) + lang + ".csv")


def main():
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

    walk_and_store()


if __name__ == '__main__':
    main()
