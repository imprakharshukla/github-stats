import asyncio
import os
import re
import json

import aiohttp

from github_stats import Stats


################################################################################
# Helper Functions
################################################################################


def generate_output_folder() -> None:
    """
    Create the output folder if it does not already exist
    """
    if not os.path.isdir("generated"):
        os.mkdir("generated")


################################################################################
# Individual JSON Generation Functions
################################################################################


async def generate_overview(s: Stats) -> None:
    """
    Generate summary statistics in JSON format
    :param s: Represents user's GitHub statistics
    """
    output = {
        "name": await s.name,
        "stars": await s.stargazers,
        "forks": await s.forks,
        "contributions": await s.total_contributions,
        "lines_changed": sum(await s.lines_changed),
        "views": await s.views,
        "repos": len(await s.repos),
    }

    generate_output_folder()
    with open("generated/overview.json", "w") as f:
        json.dump(output, f, indent=4)


async def generate_languages(s: Stats) -> None:
    """
    Generate summary languages used in JSON format
    :param s: Represents user's GitHub statistics
    """
    output = await s.languages

    generate_output_folder()
    with open("generated/languages.json", "w") as f:
        json.dump(output, f, indent=4)


################################################################################
# Main Function
################################################################################


async def main() -> None:
    """
    Generate all JSON files
    """
    access_token = os.getenv("ACCESS_TOKEN")
    if not access_token:
        # access_token = os.getenv("GITHUB_TOKEN")
        raise Exception("A personal access token is required to proceed!")
    user = os.getenv("GITHUB_ACTOR")
    if user is None:
        raise RuntimeError("Environment variable GITHUB_ACTOR must be set.")
    exclude_repos = os.getenv("EXCLUDED")
    excluded_repos = (
        {x.strip() for x in exclude_repos.split(",")} if exclude_repos else None
    )
    exclude_langs = os.getenv("EXCLUDED_LANGS")
    excluded_langs = (
        {x.strip() for x in exclude_langs.split(",")} if exclude_langs else None
    )
    # Convert a truthy value to a Boolean
    raw_ignore_forked_repos = os.getenv("EXCLUDE_FORKED_REPOS")
    ignore_forked_repos = (
            not not raw_ignore_forked_repos
            and raw_ignore_forked_repos.strip().lower() != "false"
    )
    async with aiohttp.ClientSession() as session:
        s = Stats(
            user,
            access_token,
            session,
            exclude_repos=excluded_repos,
            exclude_langs=excluded_langs,
            ignore_forked_repos=ignore_forked_repos,
        )
        await asyncio.gather(generate_languages(s), generate_overview(s))


if __name__ == "__main__":
    asyncio.run(main())
