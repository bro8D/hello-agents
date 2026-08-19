import httpx

from hello_agents import HelloAgentsLLM


class MyAutoLLM(HelloAgentsLLM):

    def _create_client(self):

        from openai import OpenAI

        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            http_client=httpx.Client(
                trust_env=False
            )
        )