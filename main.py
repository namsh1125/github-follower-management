import os
import requests
from typing import Set

# GitHub API 기본 URL
BASE_URL = "https://api.github.com"


def get_headers(github_token: str) -> dict:
    """
    GitHub API 요청에 사용할 헤더를 생성하는 함수
    :param github_token: GitHub Token
    :return: 헤더 딕셔너리
    """
    return {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }


def get_following(headers: dict) -> Set[str]:
    """
    현재 내가 팔로우하는 사용자 목록을 가져오는 함수
    :return: 내가 팔로우하는 사용자 목록
    """
    following = set()

    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#list-the-people-the-authenticated-user-follows
    url = f"{BASE_URL}/user/following"
    users = get_all_pages(url, headers)

    for user in users:
        following.add(user['login'])

    # print(f"Following: {following}")
    return following


def get_followers(headers: dict) -> Set[str]:
    """
    나를 팔로우하는 사용자 목록을 가져오는 함수
    :return: 나를 팔로우하는 사용자 목록
    """
    followers = set()

    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#list-followers-of-the-authenticated-user
    url = f"{BASE_URL}/user/followers"
    users = get_all_pages(url, headers)

    for user in users:
        followers.add(user['login'])

    # print(f"Followers: {followers}")
    return followers


def get_stargazers(headers: dict) -> Set[str]:
    """
    내가 작업한 모든 리포지토리에서 스타를 준 사용자 목록을 가져오는 함수
    :return: 스타를 준 사용자 목록
    """
    stargazers = set()

    # 나의 모든 리포지토리 목록을 가져오기
    # API 참고: https://docs.github.com/ko/rest/repos/repos?apiVersion=2022-11-28#list-repositories-for-the-authenticated-user
    url = f"{BASE_URL}/user/repos"
    repos = get_all_pages(url, headers)

    # 모든 리포지토리에서 스타를 준 사용자 목록을 가져오기
    for repo in repos:
        stargazers_url = repo['stargazers_url']
        repo_stargazers = get_all_pages(stargazers_url, headers)

        for user in repo_stargazers:
            stargazers.add(user['login'])

    # print(f"Stargazers: {stargazers}")
    return stargazers


def unfollow_user(username: str, headers: dict):
    """
    특정 사용자를 언팔로우하는 함수
    """
    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#unfollow-a-user
    url = f"{BASE_URL}/user/following/{username}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    print(f"Unfollowed: {username}")


def follow_user(username: str, headers: dict):
    """
    특정 사용자를 팔로우하는 함수
    """
    # API 참고: https://docs.github.com/ko/rest/users/followers?apiVersion=2022-11-28#follow-a-user
    url = f"{BASE_URL}/user/following/{username}"
    response = requests.put(url, headers=headers)
    response.raise_for_status()
    print(f"Followed: {username}")


def get_all_pages(url: str, headers: dict) -> list:
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


def follow_users(to_follow: Set[str], headers: dict):
    """
    여러 사용자를 팔로우하는 함수
    :param to_follow: 팔로우할 사용자 목록
    :param headers: API 요청에 사용할 헤더
    :return: None
    """
    successfully_followed = []
    failed_to_follow = []

    for user in to_follow:
        try:
            follow_user(user, headers)
            successfully_followed.append(user)

        except Exception as e:
            failed_to_follow.append(user)
            print(f"사용자 '{user}'를 팔로우하는 중 오류 발생: {e}")

    # 팔로우 결과 출력
    print(f"{len(successfully_followed)}명의 유저를 팔로우했습니다: {', '.join(successfully_followed)}")
    if failed_to_follow:
        print(f"{len(failed_to_follow)}명의 유저를 팔로우하지 못했습니다: {', '.join(failed_to_follow)}")


def unfollow_users(to_unfollow: Set[str], headers: dict):
    """
    여러 사용자를 언팔로우하는 함수
    :param to_unfollow: 언팔로우할 사용자 목록
    :param headers: API 요청에 사용할 헤더
    :return: None
    """
    successfully_unfollowed = []
    failed_to_unfollow = []

    for user in to_unfollow:
        try:
            unfollow_user(user, headers)
            successfully_unfollowed.append(user)

        except Exception as e:
            failed_to_unfollow.append(user)
            print(f"사용자 '{user}'를 언팔로우하는 중 오류 발생: {e}")

    # 언팔로우 결과 출력
    print(f"{len(successfully_unfollowed)}명의 유저를 언팔로우했습니다: {', '.join(successfully_unfollowed)}")
    if failed_to_unfollow:
        print(f"{len(failed_to_unfollow)}명의 유저를 언팔로우하지 못했습니다: {', '.join(failed_to_unfollow)}")


def main():
    # GitHub Token 가져오기
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("환경 변수 'GITHUB_TOKEN'이 설정되지 않았습니다.")

    # Headers 생성
    headers = get_headers(github_token)

    # 팔로잉, 팔로워, 스타를 준 사용자 목록 가져오기
    following = get_following(headers)
    followers = get_followers(headers)
    stargazers = get_stargazers(headers)

    # 팔로우 진행
    to_follow = followers - following  # 상대방이 나를 팔로우하지만, 내가 상대방을 팔로우하지 않는 경우
    follow_users(to_follow, headers)

    # 언팔로우 진행
    to_keep = followers.union(stargazers)  # 나를 팔로우하거나 스타를 준 사용자

    # 참고) 나를 팔로우 하지 않거나 스타를 주지 않은 사용자이지만, 팔로우를 유지하고 싶은 경우 추가하면 됨
    # to_keep.add("username")

    to_unfollow = following - to_keep  # 팔로우를 유지할 사용자를 제외한 모든 사용자
    unfollow_users(to_unfollow, headers)


if __name__ == "__main__":
    main()
