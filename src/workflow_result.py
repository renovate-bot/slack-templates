"""Offer WorkflowResult class."""
from collections.abc import Sequence

from .slack_notification import SlackNotification


class WorkflowResult(SlackNotification):
    """Subclass SlackNotification for the result of a GitHub Actions workflow.

    Public Instance Methods:
    set_slack_message(): Set SLACK_MESSAGE env var for result of CI workflow.

    Overrides:
    get_message(): Return a message reporting the result of a CI workflow.
    """

    def __init__(self, token: str, job_results: Sequence[str]):
        """Construct a SlackNotification for the result of a CI workflow.

        token: the token to use to authenticate to the GitHub API. Obtain from
        '${{ github.token }}' in the workflow.
        job_results: the results of the jobs in the workflow. Obtain from
        "${{ join(needs.*.result, ' ') }}" or '${{ job.status }}' in the workflow.
        Alternatively, pass a single custom result.
        """
        super().__init__(token)
        self._job_results = job_results

    def get_message(self) -> str:
        """Return the result of a GitHub Actions workflow.

        Handle workflows triggered by a pull_request or push event.
        """
        workflow_link = self.get_workflow_link()
        workflow_result = self._get_workflow_result()
        event_info = self.get_event_info()
        actor = self.get_actor()
        return f"{workflow_link} *{workflow_result}* for {event_info} by {actor}."

    def _get_workflow_result(self) -> str:
        """Return a single workflow result summarizing the job results."""
        if len(self._job_results) == 1:
            return self._job_results[0]
        if all(result == "skipped" for result in self._job_results):
            return "skipped"
        if all(result in ("success", "skipped") for result in self._job_results):
            return "success"

        # The workflow was unsuccessful; return the most severe result present.
        for result in ("failure", "cancelled"):
            if result in self._job_results:
                return result

        return " ".join(self._job_results)