from run_ollama import OllamaHandler
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
import yfinance as yf

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="langchain")



# Initialize the intelligent agent using Ollama
handler = OllamaHandler()
#print("Handler Object:", handler)

#if hasattr(handler, "llm"):
    #print("Handler LLM:", handler.llm)


def get_stock_price(ticker: str):
    """
    Fetch the current closing price of a given stock using Yahoo Finance.
    
    :param ticker: The stock ticker symbol (e.g., 'AAPL', 'MSFT').
    :return: The current stock price or an error message.
    """
    ticker = ticker.strip().upper().replace("'", "").replace('"', "")

    stock = yf.Ticker(ticker)

    if stock.info.get("regularMarketPrice") is None:
        return f" Stock {ticker} is unavailable or might have been removed from Yahoo Finance."

    history = stock.history(period="1d")

    if history.empty:
        return f" No available data for {ticker}. The market might be closed or insufficient data exists."

    price = history["Close"].iloc[-1]
    return f"The current price of {ticker} is {price:.2f} USD."


# Create a tool within LangChain using `get_stock_price`
stock_tool = Tool(
    name="StockPrice",
    func=get_stock_price,
    description="Fetches the current stock price using Yahoo Finance.",
    return_direct=True
)

#print("Available Tools:", stock_tool.name)

# Initialize the agent with the stock price tool
agent = initialize_agent(
    tools=[stock_tool],
    llm=handler.llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    allowed_tools=["StockPrice"],  # Ensure the name matches exactly
    handle_parsing_errors=True
)

#print("Available Tools:", [tool.name for tool in agent.tools])

if __name__ == "__main__":
    while True:
        try:
            company_symbol = input("Enter stock symbol (e.g., MSFT, AAPL, TSLA or 'exit' to quit): ").strip().upper()
            
            if company_symbol in ["EXIT", "Q", "QUIT"]:  
                print("Exiting program. Goodbye!")
                break

            response = agent.invoke(f"What is the current stock price of {company_symbol}?")
            print(f"The current price of {company_symbol} is {response['output']}")

        except KeyboardInterrupt:  
            print("\nUser interrupted the program. Exiting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
