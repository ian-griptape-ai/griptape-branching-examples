from griptape.artifacts import InfoArtifact
from griptape.structures import Workflow
from griptape.tasks import BranchTask, PromptTask
from griptape.utils import StructureVisualizer

from rich.pretty import pprint


def on_run(task: BranchTask) -> InfoArtifact:
    if "ESCALATE" in task.input.value:
        return InfoArtifact("send_escalation_email")
    else:
        return InfoArtifact("create_legal_ticket")


workflow = Workflow(
    conversation_memory_strategy="per_task",
    tasks=[
        PromptTask(
            [
                "Prompt to parse notice message '{{ args[0] }}'",
            ],
            child_ids=["check_escalation_status"],
            id="parse_notice_message",
        ),
        PromptTask(
            [
                "Prompt to check escalation status. Output only either ESCALATE or DO_NOT_ESCALATE: '{{ args[0] }}'",
            ],
            child_ids=["branch"],
            id="check_escalation_status",
        ),
        BranchTask(
            "{{ parents_output_text }}",
            on_run=on_run,
            id="branch",
            child_ids=["send_escalation_email", "create_legal_ticket"],
        ),
        PromptTask(
            "Prompt to send escalation email",
            id="send_escalation_email",
            child_ids=["create_legal_ticket"],
        ),
        PromptTask(
            "Prompt to create legal ticket",
            id="create_legal_ticket",
        ),
    ],
)

print(StructureVisualizer(workflow).to_url())

workflow.run("Test input")

print("OUTPUT")
for task in workflow.tasks:
    if task.output != None:
        pprint(task.output.value)


# workflow.run("The hotel was awful. There were bugs in my bed")
