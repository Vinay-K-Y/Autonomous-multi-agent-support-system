from ai_core.observability.observability import observability


class AnalyticsService:

    def metrics(self):

        return observability.summary()
        