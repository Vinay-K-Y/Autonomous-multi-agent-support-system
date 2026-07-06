from functools import wraps

from ai_core.observability.tracer import WorkflowTracer


def traced(agent_name: str):

    def wrapper(func):

        @wraps(func)
        async def inner(state):

            tracer = getattr(state, "_tracer", None)

            if tracer is None:

                tracer = WorkflowTracer()

                state._tracer = tracer

            tracer.start_agent(agent_name)

            try:

                result = await func(state)

                tracer.finish_agent()

                result.trace = tracer.workflow

                return result

            except Exception as e:

                tracer.fail_agent(e)

                raise

        return inner

    return wrapper