
import streamlit as st
import yfinance as yf
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="MinerviniBot", layout="centered")

st.title("Minervini Stock Analyzer — India Edition")
stock_name = st.text_input("Enter NSE stock symbol (e.g., CDSL.NS)", "CDSL.NS")

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except:
        return None

def check_minervini_criteria(info):
    results = {}

    try:
        results["ROE > 15%"] = info.get("returnOnEquity", 0) * 100 > 15
    except: results["ROE > 15%"] = False

    try:
        results["EPS positive"] = info.get("trailingEps", 0) > 0
    except: results["EPS positive"] = False

    try:
        results["PE < 40"] = info.get("trailingPE", 1000) < 40
    except: results["PE < 40"] = False

    try:
        results["Operating Margin > 15%"] = info.get("operatingMargins", 0) * 100 > 15
    except: results["Operating Margin > 15%"] = False

    try:
        results["5Y Revenue Growth > 10%"] = info.get("revenueGrowth", 0) * 100 > 10
    except: results["5Y Revenue Growth > 10%"] = False

    return results

def summarize_results(results):
    yes = sum(1 for v in results.values() if v)
    if yes == len(results):
        return "YES — Strong Fundamentals"
    elif yes >= len(results) - 1:
        return "PARTIAL YES — Almost There"
    elif yes >= len(results) // 2:
        return "PARTIAL NO — Needs Work"
    else:
        return "NO — Not a Fit"

def generate_pdf(info, results, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Minervini Stock Analysis Report", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Company: {info.get('longName', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Symbol: {info.get('symbol', 'N/A')}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Checklist Results:", ln=True)

    pdf.set_font("Arial", "", 12)
    for key, value in results.items():
        pdf.cell(0, 10, f"{key}: {'✔️' if value else '❌'}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Final Verdict: {summary}", ln=True)

    filename = "Minervini_Report.pdf"
    pdf.output(filename)
    return filename

if stock_name:
    info = get_stock_info(stock_name)
    if info:
        results = check_minervini_criteria(info)
        summary = summarize_results(results)

        st.subheader("Checklist Results")
        for key, value in results.items():
            st.write(f"- {key}: {'✅' if value else '❌'}")

        st.subheader("Final Verdict")
        st.success(summary)

        if st.button("Download Full PDF Report"):
            filename = generate_pdf(info, results, summary)
            with open(filename, "rb") as f:
                st.download_button("Click to Download", f, file_name=filename)
    else:
        st.error("Could not fetch stock data. Make sure the symbol is valid (like TCS.NS, RELIANCE.NS).")
