import pytest
import logging
import json
import sys
from langchain_ollama import OllamaLLM
from langchain.llms.base import LLM

# Configure logging for error tracking
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")
LOGGER = logging.getLogger(__name__)

from typing import ClassVar, Optional
from pydantic import BaseModel, Field

class OllamaHandler(BaseModel):
    MODEL_NAME: ClassVar[str] = 'llama3.2'
    model: str = Field(default=MODEL_NAME)
    llm: Optional[OllamaLLM] = None  # تعريف llm كحقل اختياري

    def __init__(self, **data):
        """ تهيئة الكلاس بشكل صحيح مع Pydantic """
        super().__init__(**data)
        object.__setattr__(self, "llm", self.get_llm())  # استخدام object.__setattr__ لتجاوز قيود Pydantic

    def get_llm(self) -> Optional[OllamaLLM]:
        """
        Initializes and returns an instance of OllamaLLM with the appropriate configuration.

        Returns:
            OllamaLLM | None: An instance of the model, or `None` if initialization fails.
        """
        try:
            if not isinstance(self.model, str) or not self.model.strip():
                raise ValueError("Invalid model name provided.")
            
            return OllamaLLM(
                model=self.model,
                system_message="Analyze the text and provide a clear summary in valid JSON format.",
                output_format="json",
                strict_mode=True,
                return_direct=True,
            )
        except Exception as e:
            LOGGER.error(f"Error initializing the model: {e}")
            return None

    def _call(self, prompt: str, stop=None) -> str:
        """
        Implements the LLM API expected by LangChain.
        """
        return self.explain_question_mark(prompt)

    def explain_question_mark(self, question: str) -> str:
        """
        Uses the LLM model to explain the given question.

        Args:
            question (str): The input question to be explained.

        Returns:
            str: The model's response or an error message.
        """
        if self.llm is None:
            return "Error: Model initialization failed."

        try:
            response = self.llm.invoke(question)
            return response
        except Exception as e:
            LOGGER.error(f"Error invoking the model: {e}")
            return f"Error retrieving response: {e}"

    def interactive_mode(self):
        """Interactive console interface for asking questions and receiving responses from the model."""
        print("Willkommen! Geben Sie Ihre Frage ein (oder 'exit' zum Beenden):")

        while True:
            user_input = input("\nIhre Frage: ").strip()

            # Exit condition
            if user_input.lower() in {"exit", "quit"}:
                print("\nProgramm beendet. Auf Wiedersehen!")
                sys.exit(0)

            if not user_input:
                print("⚠ Bitte geben Sie eine gültige Frage ein.")
                continue

            explanation = self.explain_question_mark(user_input)

            print("\nAntwort des Modells:\n")
            try:
                parsed_response = json.loads(explanation) if isinstance(explanation, str) else explanation
                print(json.dumps(parsed_response, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print(explanation)

if __name__ == "__main__":
    handler = OllamaHandler()
    handler.interactive_mode()
