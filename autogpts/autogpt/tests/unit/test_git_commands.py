import pytest
from git.exc import GitCommandError
from git.repo.base import Repo

from autogpt.agents.agent import Agent
from autogpt.commands.git_operations import GitOperationsComponent
from autogpt.file_storage.base import FileStorage
from autogpt.utils.exceptions import CommandExecutionError


@pytest.fixture
def mock_clone_from(mocker):
    return mocker.patch.object(Repo, "clone_from")


@pytest.fixture
def git_ops_component(agent: Agent):
    return agent.git_ops


def test_clone_auto_gpt_repository(
    git_ops_component: GitOperationsComponent,
    storage: FileStorage,
    mock_clone_from,
    agent: Agent,
):
    mock_clone_from.return_value = None

    repo = "github.com/Significant-Gravitas/Auto-GPT.git"
    scheme = "https://"
    url = scheme + repo
    clone_path = storage.get_path("auto-gpt-repo")

    expected_output = f"Cloned {url} to {clone_path}"

    clone_result = git_ops_component.clone_repository(url, clone_path)

    assert clone_result == expected_output
    mock_clone_from.assert_called_once_with(
        url=f"{scheme}{agent.legacy_config.github_username}:{agent.legacy_config.github_api_key}@{repo}",  # noqa: E501
        to_path=clone_path,
    )


def test_clone_repository_error(
    git_ops_component: GitOperationsComponent,
    storage: FileStorage,
    mock_clone_from,
    agent: Agent,
):
    url = "https://github.com/this-repository/does-not-exist.git"
    clone_path = storage.get_path("does-not-exist")

    mock_clone_from.side_effect = GitCommandError(
        "clone", "fatal: repository not found", ""
    )

    with pytest.raises(CommandExecutionError):
        git_ops_component.clone_repository(url, clone_path)
