import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ── Generate dataset ──────────────────────────────────────────────────────────
np.random.seed(42)
n = 200
data = {
    "CustomerID": [f"CUST{str(i).zfill(4)}" for i in range(1, n+1)],
    "Age": np.random.randint(18, 65, n).tolist(),
    "Gender": np.random.choice(["Male", "Female"], n).tolist(),
    "Subscription_Plan": np.random.choice(["Basic","Standard","Premium"], n, p=[0.4,0.35,0.25]).tolist(),
    "Monthly_Charges": np.round(np.random.uniform(10, 100, n), 2).tolist(),
    "Tenure_Months": np.random.randint(1, 60, n).tolist(),
    "Login_Frequency_PerMonth": np.random.randint(0, 30, n).tolist(),
    "Support_Contacts": np.random.randint(0, 10, n).tolist(),
    "Last_Login_Days_Ago": np.random.randint(1, 90, n).tolist(),
    "Payment_Delay": np.random.choice(["Yes","No"], n, p=[0.3,0.7]).tolist(),
}
df = pd.DataFrame(data)
churn = []
for _, row in df.iterrows():
    score = 0
    if row["Login_Frequency_PerMonth"] < 5: score += 2
    if row["Last_Login_Days_Ago"] > 14: score += 2
    if row["Support_Contacts"] > 5: score += 1
    if row["Payment_Delay"] == "Yes": score += 2
    if row["Tenure_Months"] < 6: score += 1
    if row["Subscription_Plan"] == "Basic": score += 1
    churn.append("Yes" if score >= 4 else "No")
df["Churned"] = churn

# ── App ───────────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)
app.title = "Customer Churn Dashboard"

PLANS = ["All"] + sorted(df["Subscription_Plan"].unique().tolist())

app.layout = html.Div(style={"fontFamily": "Segoe UI, sans-serif", "backgroundColor": "#f0f2f5", "minHeight": "100vh", "padding": "20px"}, children=[

    # ── Header ────────────────────────────────────────────────────────────────
    html.Div(style={"backgroundColor": "#1a1a2e", "borderRadius": "12px", "padding": "24px 32px", "marginBottom": "24px"}, children=[
        html.H1("📊 Customer Churn Analytics Dashboard", style={"color": "white", "margin": 0, "fontSize": "26px"}),
        html.P("VirtualWorks Lab Internship — Interactive Insights for Retention Strategy",
               style={"color": "#a0a0c0", "margin": "6px 0 0 0", "fontSize": "14px"}),
    ]),

    # ── Filter ────────────────────────────────────────────────────────────────
    html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "16px 24px", "marginBottom": "24px",
                    "display": "flex", "alignItems": "center", "gap": "20px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"}, children=[
        html.Label("Filter by Subscription Plan:", style={"fontWeight": "600", "color": "#333"}),
        dcc.Dropdown(id="plan-filter", options=[{"label": p, "value": p} for p in PLANS],
                     value="All", clearable=False,
                     style={"width": "220px", "fontSize": "14px"}),
    ]),

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    html.Div(id="kpi-cards", style={"display": "grid", "gridTemplateColumns": "repeat(4, 1fr)", "gap": "16px", "marginBottom": "24px"}),

    # ── Row 1 Charts ──────────────────────────────────────────────────────────
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}, children=[
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "16px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"}, children=[dcc.Graph(id="churn-pie")]),
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "16px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"}, children=[dcc.Graph(id="plan-bar")]),
    ]),

    # ── Row 2 Charts ──────────────────────────────────────────────────────────
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px", "marginBottom": "16px"}, children=[
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "16px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"}, children=[dcc.Graph(id="payment-bar")]),
        html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "16px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)"}, children=[dcc.Graph(id="login-box")]),
    ]),

    # ── Row 3 Chart ───────────────────────────────────────────────────────────
    html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "16px", "boxShadow": "0 2px 8px rgba(0,0,0,0.06)", "marginBottom": "16px"}, children=[
        dcc.Graph(id="tenure-hist")
    ]),
])

# ── Callbacks ─────────────────────────────────────────────────────────────────
@app.callback(
    Output("kpi-cards", "children"),
    Output("churn-pie", "figure"),
    Output("plan-bar", "figure"),
    Output("payment-bar", "figure"),
    Output("login-box", "figure"),
    Output("tenure-hist", "figure"),
    Input("plan-filter", "value"),
)
def update_all(plan):
    dff = df if plan == "All" else df[df["Subscription_Plan"] == plan]

    total = len(dff)
    churned = (dff["Churned"] == "Yes").sum()
    churn_rate = round(churned / total * 100, 1)
    avg_tenure = round(dff["Tenure_Months"].mean(), 1)
    avg_login = round(dff["Login_Frequency_PerMonth"].mean(), 1)

    def kpi(title, value, color, icon):
        return html.Div(style={"backgroundColor": "white", "borderRadius": "12px", "padding": "20px 24px",
                               "boxShadow": "0 2px 8px rgba(0,0,0,0.06)", "borderLeft": f"5px solid {color}"}, children=[
            html.P(f"{icon} {title}", style={"margin": "0 0 8px 0", "color": "#666", "fontSize": "13px", "fontWeight": "600"}),
            html.H2(str(value), style={"margin": 0, "color": color, "fontSize": "28px"}),
        ])

    cards = [
        kpi("Total Customers", total, "#3498db", "👥"),
        kpi("Churned", churned, "#e74c3c", "🚪"),
        kpi("Churn Rate", f"{churn_rate}%", "#e67e22", "📉"),
        kpi("Avg Tenure (months)", avg_tenure, "#2ecc71", "📅"),
    ]

    # Pie
    pie = px.pie(dff, names="Churned", title="Churn Distribution",
                 color="Churned", color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"},
                 hole=0.4)
    pie.update_layout(margin=dict(t=40, b=10), height=300)

    # Plan bar
    plan_data = dff.groupby(["Subscription_Plan", "Churned"]).size().reset_index(name="Count")
    plan_bar = px.bar(plan_data, x="Subscription_Plan", y="Count", color="Churned",
                      title="Churn by Subscription Plan", barmode="group",
                      color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"})
    plan_bar.update_layout(margin=dict(t=40, b=10), height=300)

    # Payment bar
    pay_data = dff.groupby(["Payment_Delay", "Churned"]).size().reset_index(name="Count")
    pay_bar = px.bar(pay_data, x="Payment_Delay", y="Count", color="Churned",
                     title="Churn by Payment Delay", barmode="group",
                     color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"})
    pay_bar.update_layout(margin=dict(t=40, b=10), height=300)

    # Login boxplot
    login_box = px.box(dff, x="Churned", y="Login_Frequency_PerMonth",
                       title="Login Frequency vs Churn",
                       color="Churned", color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"})
    login_box.update_layout(margin=dict(t=40, b=10), height=300)

    # Tenure histogram
    tenure_hist = px.histogram(dff, x="Tenure_Months", color="Churned",
                               title="Tenure Distribution by Churn Status",
                               nbins=20, barmode="overlay", opacity=0.7,
                               color_discrete_map={"Yes": "#e74c3c", "No": "#2ecc71"})
    tenure_hist.update_layout(margin=dict(t=40, b=10), height=320)

    return cards, pie, plan_bar, pay_bar, login_box, tenure_hist

if __name__ == "__main__":
    app.run(debug=True, port=8050)
