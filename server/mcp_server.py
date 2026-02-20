import requests
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FinSightMCP")

@mcp.tool()
def get_financial_context() -> str:
    context_parts = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        res = requests.get(url, timeout=5)
        data = res.json()
        ils_rate = data["rates"].get("ILS", 0)
        eur_rate = data["rates"].get("EUR", 0)
        
        if ils_rate and eur_rate:
            eur_to_ils = ils_rate / eur_rate
            context_parts.append(f"Live Exchange Rates: 1 USD = {ils_rate:.2f} ILS | 1 EUR = {eur_to_ils:.2f} ILS")
    except:
        pass

    try:
        crypto_url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        c_res = requests.get(crypto_url, timeout=5, headers=headers)
        c_data = c_res.json()
        btc_price = c_data["bpi"]["USD"]["rate"]
        context_parts.append(f"Live Crypto: Bitcoin (BTC) = ${btc_price}")
    except:
        pass

    try:
        rss_url = "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC,^IXIC"
        r_res = requests.get(rss_url, timeout=5, headers=headers)
        root = ET.fromstring(r_res.content)
        headlines = []
        for item in root.findall('./channel/item')[:3]:
            title = item.find('title').text
            if title:
                headlines.append(f"- {title}")
        
        if headlines:
            context_parts.append("Latest Market Headlines:\n" + "\n".join(headlines))
    except:
        pass

    if not context_parts:
        return "Market data is currently unavailable. Assume normal market conditions."
        
    return "\n\n".join(context_parts)

@mcp.tool()
def calculate_investment_forecast(principal: float, monthly_contribution: float, annual_interest_rate: float, years: int) -> str:
    months = years * 12
    monthly_rate = (annual_interest_rate / 100) / 12
    future_value = principal
    
    for _ in range(months):
        future_value += monthly_contribution
        future_value *= (1 + monthly_rate)
        
    total_invested = principal + (monthly_contribution * months)
    profit = future_value - total_invested
    
    return f"Forecast for {years} years:\nTotal Invested: {total_invested:,.2f} ILS\nEstimated Value: {future_value:,.2f} ILS\nEstimated Profit: {profit:,.2f} ILS"

if __name__ == "__main__":
    mcp.run(transport='stdio')