from ai_core.observability.observability import observability


class WorkflowService:

    def latest_trace(self):

        return observability.get_latest_trace()

    def all_traces(self):

        return observability.get_all_traces()