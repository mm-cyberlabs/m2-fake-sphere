from transformers import pipeline

# Initialize local text generation model (ensure 'distilgpt2' is downloaded locally)
local_generator = pipeline('text-generation', model='distilgpt2')


class AiAgentPrecision:
    """
    Uses a local text generation model (distilgpt2) to decide the best Faker method
    based on the business name and description.
    """

    def __init__(self, business_name, datatype, description):
        self.bus_name = business_name
        self.datatype = datatype
        self.desc = description

    def decide(self):
        """
        TODO: This need refinement and a specific trained LLM on Faker Library.
        """
        prompt = (
            f"Given the business attribute '{self.bus_name}' with description '{self.desc}', "
            f"which Faker method best generates realistic synthetic data? "
            f"Return only the best method name."
        )

        response = local_generator(prompt, max_new_tokens=30, truncation=True, num_return_sequences=1)
        return response[0]['generated_text']


if __name__ == '__main__':
    resp = AiAgentPrecision('full_name', 'string', 'Full name of a user.')
    print(resp.decide())
