import vk_api
from github import Github

KEY_WORDS_PATH = "key_words"
TECHNOLOGIES_PATH = "languages"
COMPANIES_PATH = "companies"

KEY_WORDS = []
TECHNOLOGIES = []
COMPANIES = []


def read_files():
    global KEY_WORDS, TECHNOLOGIES, COMPANIES

    def read(path):
        with open(path) as file:
            return list(filter(len, [line.strip().lower() for line in file]))

    KEY_WORDS = read(KEY_WORDS_PATH)
    TECHNOLOGIES = read(TECHNOLOGIES_PATH)
    COMPANIES = read(COMPANIES_PATH)


read_files()
print("Read data from files")


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
    lang = ""
    try:
        user_info = vk.users.get(user_ids=id, fields='career,universities,site')[0]
        print('Analyzing ' + user_info['first_name'] + ' ' + user_info['last_name'])

        # print(user_info)

        career = []
        if 'career' in user_info:
            career = user_info['career']
            rating += analyze_job(career)

        if 'universities' in user_info:
            rating += analyze_education(user_info['universities'])

        if 'site' in user_info:
            rating += analyze_github(user_info['site'])

        groups = vk.groups.get(user_id=id, filter='groups,publics', extended=1, fields='name')
        rating += analyze_groups(groups)

        print('Got rating ' + str(rating))
        return min(rating, 10)

    except vk_api.exceptions.ApiError as error_msg:
        print(error_msg)
        return 0


def analyze_language(groups, career):
    pass


# gives max of 3
def analyze_groups(groups):
    print(groups)
    for group in groups:
        pass
        # todo:
        # if contains_any()
    pass


# gives max of 3
def analyze_job(career):
    score = 0
    for job in career:
        if 'position' in job and contains_any(job['position'], KEY_WORDS):
            score += 1
        if 'company' in job and contains_any(job['company'], COMPANIES):
            score += 1
        elif 'group_id' in job:
            group = vk.groups.getById(group_id=job['group_id'])
            if 'name' in group and contains_any(group['name'], COMPANIES):
                score += 1
    return min(score, 3)


# gives max of 3
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
def analyze_github(site: str):
    # todo: github api for language
    if site.find('github') != -1:

        Github.get_user()

        return 5
    return 0
