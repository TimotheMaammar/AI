# NOTE: excerpt from the "Agent Laboratory" project (Samuel Schmidgall, MIT
# License). Illustrative, not standalone runnable: BaseAgent, self.report,
# self.history, self.role_description(), and query_model are not defined in
# this excerpt. No pip install line given here since this isn't published as
# a pip package as far as I know — see
# https://github.com/SamuelSchmidgall/AgentLaboratory

class ProfessorAgent(BaseAgent):
    def __init__(self, model="gpt4omini", notes=None, max_steps=100, openai_api_key=None):
        super().__init__(model, notes, max_steps, openai_api_key)
        self.phases = ["report writing"]

    def generate_readme(self):
        sys_prompt = f"""You are {self.role_description()} \n Here is the written paper \n{self.report}.
Task instructions: Your goal is to integrate all of the knowledge, code, reports, and notes
provided to you and generate a readme.md for a github repository."""

        history_str = "\n".join([_[1] for _ in self.history])
        prompt = (
            f"""History: {history_str}\n{'~' * 10}\n"""
            f"Please produce the readme below in markdown:\n"
        )
        model_resp = query_model(
            model_str=self.model, system_prompt=sys_prompt, prompt=prompt,
            openai_api_key=self.openai_api_key
        )
        return model_resp.replace("```markdown", "")
