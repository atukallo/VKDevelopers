import collections

import vk_api

import analyzis

import pandas as pd

vk = None
default_user = ('125376958', 'Alexander', 'Tukallo')

SCORE_THRESHOLD = 3  # score is given from 0 to 10. If score >= threshold => is programmer


# Method returns pair: (rating : int, language : str),
#   where rating is an int in a range [0; 10]
#   depicting assurance, that a user is a programmer
#   language is user's favourite programming language if any, else ""
def get_score(id):
    return analyzis.analyze_user(id, vk), "c++"


def walk_and_store(start=default_user, limit=5, lang=""):
    programmers = pd.DataFrame(columns=('id', 'first_name', 'last_name', 'rank', 'language', 'link'))
    visited_ids = set()
    to_visit = collections.deque()
    to_visit.append(start)

    # starting bfs
    while len(to_visit) != 0:
        # logging:
        # if len(visited_ids) % 5 == 0:
        #     print('Visited ' + str(len(visited_ids)) + ' guys')

        cur_user = to_visit.popleft()  # (id, first_name, last_name)
        visited_ids.add(cur_user[0])

        # try to get friends to learn if the account was deleted
        try:
            friends = vk.friends.get(user_id=cur_user[0], fields='first_name,last_name')
        except vk_api.exceptions.ApiError as error_msg:
            continue

        score = get_score(cur_user[0])
        if score[0] >= SCORE_THRESHOLD:
            link = 'https://vk.com/id' + str(cur_user[0])
            programmers.loc[len(programmers)] = [*cur_user, *score, link]

        if len(programmers) >= limit:
            break

        for friend in friends['items']:
            friend = (friend['id'], friend['first_name'], friend['last_name'])
            if friend[0] not in visited_ids:
                to_visit.append(friend)

    # bfs is finished, time to save programmers we found
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
