import requests
from typing import Set

# GitHub 개인 액세스 토큰 설정
GITHUB_TOKEN = "{YOUR_GITHUB_TOKEN}"
GITHUB_USERNAME = "{YOUR_GITHUB_USERNAME}"

# GitHub API 기본 URL
BASE_URL = "https://api.github.com"

# API 요청에 사용할 헤더
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


def get_following() -> Set[str]:
    """
    현재 내가 팔로우하는 사용자 목록을 가져오는 함수
    :return: 내가 팔로우하는 사용자 목록
    """
    following = set()

    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#list-the-people-the-authenticated-user-follows
    url = f"{BASE_URL}/user/following"
    users = get_all_pages(url)

    for user in users:
        following.add(user['login'])

    print(f"Following: {following}")
    return following


def get_followers() -> Set[str]:
    """
    나를 팔로우하는 사용자의 목록을 가져오는 함수
    :return: 나를 팔로우하는 사용자 목록
    """
    followers = set()

    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#list-followers-of-the-authenticated-user
    url = f"{BASE_URL}/user/followers"
    users = get_all_pages(url)

    for user in users:
        followers.add(user['login'])

    print(f"Followers: {followers}")
    return followers


def get_stargazers() -> Set[str]:
    """
    내가 작업한 모든 리포지토리에서 스타를 준 사용자 목록을 가져오는 함수
    :return: 스타를 준 사용자 목록
    """
    stargazers = set()

    # 나의 모든 리포지토리 목록을 가져오기
    # API 참고: https://docs.github.com/ko/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-the-authenticated-user
    url = f"{BASE_URL}/user/repos"
    repos = get_all_pages(url)

    # 모든 리포지토리에서 스타를 준 사용자 목록을 가져오기
    for repo in repos:
        stargazers_url = repo['stargazers_url']
        repo_stargazers = get_all_pages(stargazers_url)

        for user in repo_stargazers:
            stargazers.add(user['login'])

    print(f"Stargazers: {stargazers}")
    return stargazers


def unfollow_user(username: str):
    """
    특정 사용자를 언팔로우하는 함수
    """
    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#unfollow-a-user
    url = f"{BASE_URL}/user/following/{username}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    print(f"Unfollowed: {username}")


def follow_user(username: str):
    """
    특정 사용자를 팔로우하는 함수
    """
    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#follow-a-user
    url = f"{BASE_URL}/user/following/{username}"
    response = requests.put(url, headers=headers)
    response.raise_for_status()
    print(f"Followed: {username}")


def get_all_pages(url: str) -> list:
    """
    주어진 URL에서 모든 페이지의 결과를 가져오는 함수
    """
    results = []
    page = 1
    while True:
        response = requests.get(f"{url}?page={page}&per_page=100", headers=headers)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        results.extend(data)
        page += 1

    return results


def main():
    following = get_following()
    followers = get_followers()
    stargazers = get_stargazers()

    # 팔로우 진행
    to_follow = followers - following  # 상대방이 나를 팔로우하지만, 내가 상대방을 팔로우하지 않는 경우
    for user in to_follow:
        follow_user(user)

    # 언팔로우 진행
    to_keep = followers.union(stargazers)  # 나를 팔로우하거나 스타를 준 사용자

    # 참고) 나를 팔로우 하지 않거나 스타를 주지 않은 사용자이지만, 팔로우를 유지하고 싶은 경우 추가하면 됨
    # to_keep.add("username")

    to_unfollow = [user for user in following if user not in to_keep]
    for user in to_unfollow:
        unfollow_user(user)


if __name__ == "__main__":
    main()
