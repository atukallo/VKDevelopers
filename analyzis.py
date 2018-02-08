import vk_api
from github import Github

KEY_WORDS_PATH = "key_words"
LANGUAGES_PATH = "languages"
COMPANIES_PATH = "companies"
GROUPS_PATH = "groups"

KEY_WORDS = []
LANGUAGES = []
COMPANIES = []
GROUPS = []


def read_files():
    global KEY_WORDS, LANGUAGES, COMPANIES, GROUPS

    def read(path):
        with open(path) as file:
            return list(filter(len, [line.strip().lower() for line in file]))

    KEY_WORDS = read(KEY_WORDS_PATH)
    LANGUAGES = read(LANGUAGES_PATH)
    COMPANIES = read(COMPANIES_PATH)
    GROUPS = read(GROUPS_PATH)


read_files()
print("Read utils from files")
g = Github(login_or_token="a30aaccea5624f96d8650542b7a86f56b66c6b1a")
print("Authorized with public key to github")


def contains_any(substring: str, strings: list):
    substring = substring.lower()
    for s in strings:
        if substring.find(s) != -1:
            return True
    return False


vk = None


def analyze_user(id, vkk):
    global vk
    vk = vkk

    rating = 0
    lang = '-'

    lang_stats = {}
    for l in LANGUAGES:
        lang_stats[l] = 0

    try:
        user_info = vk.users.get(user_ids=id, fields='career,universities,site')[0]
        print('Analyzing ' + user_info['first_name'] + ' ' + user_info['last_name'] +
              ' query answer: ' + str(user_info))

        if 'career' in user_info:
            career = user_info['career']
            rating += analyze_job(career, lang_stats)

        if 'universities' in user_info:
            rating += analyze_education(user_info['universities'])

        if 'site' in user_info:
            rating += analyze_github(user_info['site'], lang_stats)

        try:
            groups = vk.groups.get(user_id=id, filter='groups,publics', extended=1, fields='name')
            rating += analyze_groups(groups, lang_stats)
        except vk_api.exceptions.ApiError as error_msg:
            pass  # access to groups denied

        print('Got rating ' + str(rating) + ' with stats: ' + str(lang_stats))

        # let's find most popular language
        m = 0
        for l in lang_stats:
            val = lang_stats[l]
            if val > m:
                lang = l
                m = val

        return min(rating, 10), lang

    except vk_api.exceptions.ApiError as error_msg:
        print(error_msg)
        return rating, lang


# gives max of 3
def analyze_groups(groups, lang_stats):
    rating = 0
    # print('Groups: ' + str(groups))
    for group in groups['items']:
        group_name = group['name'].lower()
        if contains_any(group_name, GROUPS):
            rating += 1
        for l in LANGUAGES:
            if group_name.find(l) != -1:
                lang_stats[l] += 1
    return min(rating, 3)


# gives max of 3
def analyze_job(career, lang_stats):
    score = 0
    for job in career:
        if 'position' in job and contains_any(job['position'], KEY_WORDS):
            score += 1
            # let's analyze some technologies:
            for l in LANGUAGES:
                if job['position'].find(l) != -1:
                    lang_stats[l] += 1

        if 'company' in job and contains_any(job['company'], COMPANIES):
            score += 1
        elif 'group_id' in job:
            group = vk.groups.getById(group_id=job['group_id'])
            if 'name' in group and contains_any(group['name'], COMPANIES):
                score += 1
    return min(score, 3)  # gives max of 3


def analyze_education(education):
    score = 0
    for uni in education:
        if 'chair_name' in uni and contains_any(uni['chair_name'], KEY_WORDS) or \
                                'faculty_name' in uni and contains_any(uni['faculty_name'], KEY_WORDS):
            if score == 0:
                score += 2
            else:
                score += 1
    return min(score, 3)


# gives 5 if present. Person with a github is definitely a programmer!
def analyze_github(site: str, lang_stats: dict):
    if site.find('github') == -1:
        return 0

    # let's try to parse the user's name
    login = site.replace('https:', '').replace('github', '').replace('/', '') \
        .replace('.', '').replace('com', '').replace('io', '')
    print('Loading github repos for login: ' + login)
    # learn favourite language from github repos
    try:
        for r in g.get_user(login).get_repos():
            l = r.language.lower()
            if l in lang_stats:
                lang_stats[l] += 1
            else:
                print('Language ' + l + ' is ignored')
    except Exception as e:
        # print(e)
        pass
    return 5  # return score of 5 for rating
