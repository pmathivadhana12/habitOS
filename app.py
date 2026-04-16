import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date, timedelta
import os

from database import (
    init_db, get_habits, add_habit, delete_habit,
    log_habit, get_logs, get_household_logs,
    get_household_members, get_user_household,
    get_streak, create_household, join_household,
    seed_demo_data, get_demo_credentials
)
from auth import (
    show_login_page, show_onboarding_page,
    show_invite_page, check_onboard_or_app
)

init_db()
seed_demo_data()  # Load house_1.csv as demo once

st.set_page_config(page_title="HabitOS", page_icon="⬡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&family=Inter:wght@300;400;500&display=swap');
:root{--bg-base:#080b12;--bg-panel:#0d1117;--bg-card:#111620;--border:#1e2d40;--border-glow:#2a4a6b;--accent-1:#00d4ff;--accent-2:#7b2fff;--accent-3:#ff3c6e;--accent-4:#00ff9d;--text-1:#e8f0f8;--text-2:#8899aa;--text-3:#445566;}
html,body,[class*="css"]{font-family:'Inter',sans-serif;color:var(--text-1);}
.stApp{background-color:var(--bg-base);background-image:radial-gradient(ellipse 80% 50% at 20% 0%,rgba(0,100,255,0.06) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 80% 100%,rgba(123,47,255,0.06) 0%,transparent 60%),url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60'%3E%3Ccircle cx='30' cy='30' r='0.5' fill='%23ffffff08'/%3E%3C/svg%3E");background-attachment:fixed;}
[data-testid="stSidebar"]{background-color:var(--bg-panel) !important;border-right:1px solid var(--border) !important;}
[data-testid="stSidebar"] *{color:var(--text-1) !important;}
h1,h2,h3{font-family:'Syne',sans-serif !important;font-weight:800 !important;}
[data-testid="stMetricValue"]{font-family:'Space Mono',monospace !important;font-size:28px !important;color:var(--accent-1) !important;}
[data-testid="stMetricLabel"]{font-family:'Space Mono',monospace !important;font-size:10px !important;letter-spacing:2px !important;text-transform:uppercase !important;color:var(--text-2) !important;}
.stButton>button{background:linear-gradient(135deg,rgba(0,212,255,0.1),rgba(123,47,255,0.1)) !important;border:1px solid var(--border-glow) !important;color:var(--accent-1) !important;font-family:'Space Mono',monospace !important;font-size:11px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;border-radius:6px !important;}
.stButton>button:hover{background:linear-gradient(135deg,rgba(0,212,255,0.2),rgba(123,47,255,0.2)) !important;border-color:var(--accent-1) !important;box-shadow:0 0 16px rgba(0,212,255,0.2) !important;}
.stTabs [data-baseweb="tab-list"]{background:var(--bg-card) !important;border-radius:10px !important;border:1px solid var(--border) !important;padding:4px !important;}
.stTabs [data-baseweb="tab"]{font-family:'Space Mono',monospace !important;font-size:11px !important;letter-spacing:1.5px !important;text-transform:uppercase !important;color:var(--text-2) !important;border-radius:7px !important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,212,255,0.15),rgba(123,47,255,0.15)) !important;color:var(--accent-1) !important;}
hr{border-color:var(--border) !important;}
::-webkit-scrollbar{width:4px;background:var(--bg-base);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Mono, monospace", color="#8899aa", size=11),
    colorway=["#00d4ff","#7b2fff","#ff3c6e","#00ff9d","#ffbe00","#ff6b35"],
)
PALETTE = ["#00d4ff","#7b2fff","#ff3c6e","#00ff9d","#ffbe00","#ff6b35","#a78bfa","#34d399"]
ICON_OPTIONS = ["🏋️","💧","🌙","💊","🧘","🚶","📚","🥗","🎯","☕","🛌","🏃","🎸","✍️","🧹","🐾"]
UNIT_OPTIONS = ["times","mins","hours","liters","pages","steps","km","reps"]


def section_header(icon, title, subtitle=""):
    sub_html = ""
    if subtitle:
        sub_html = ("<br><span style=\"font-family:Space Mono,monospace;font-size:10px;"
                    "color:#445566;letter-spacing:2px;text-transform:uppercase;\">"
                    + subtitle + "</span>")
    st.markdown(
        "<div style=\"margin:28px 0 18px 0;padding-bottom:14px;border-bottom:1px solid #1e2d40;\">"
        "<span style=\"font-family:Syne,sans-serif;font-weight:800;font-size:20px;color:#e8f0f8;\">"
        + icon + " " + title + "</span>" + sub_html + "</div>",
        unsafe_allow_html=True
    )

def stat_card(label, value, color="#00d4ff"):
    st.markdown(
        "<div style=\"background:#111620;border:1px solid #1e2d40;border-radius:12px;"
        "padding:16px 20px;position:relative;overflow:hidden;margin-bottom:4px;\">"
        "<div style=\"position:absolute;top:0;left:0;right:0;height:2px;"
        "background:linear-gradient(90deg," + color + ",transparent);\"></div>"
        "<div style=\"font-family:Space Mono,monospace;font-size:10px;letter-spacing:2px;"
        "text-transform:uppercase;color:#8899aa;\">" + label + "</div>"
        "<div style=\"font-family:Space Mono,monospace;font-size:24px;font-weight:700;"
        "color:" + color + ";margin-top:6px;\">" + str(value) + "</div>"
        "</div>",
        unsafe_allow_html=True
    )

def habit_bar(icon, name, rate, streak_val):
    bar_color = "#00d4ff" if rate >= 70 else "#ffbe00" if rate >= 40 else "#ff3c6e"
    st.markdown(
        "<div style=\"background:#111620;border:1px solid #1e2d40;border-radius:10px;"
        "padding:14px 18px;margin-bottom:8px;\">"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;\">"
        "<div style=\"font-family:Syne;font-weight:600;font-size:14px;color:#e8f0f8;\">"
        + icon + " " + name + "</div>"
        "<div style=\"display:flex;gap:20px;align-items:center;\">"
        "<span style=\"font-family:Space Mono;font-size:11px;color:#445566;\">🔥 " + str(streak_val) + "d</span>"
        "<span style=\"font-family:Space Mono;font-size:16px;font-weight:700;color:" + bar_color + ";\">" + str(rate) + "%</span>"
        "</div></div>"
        "<div style=\"margin-top:8px;background:#0d1117;border-radius:4px;height:5px;\">"
        "<div style=\"width:" + str(int(rate)) + "%;height:100%;background:" + bar_color + ";border-radius:4px;\"></div>"
        "</div></div>",
        unsafe_allow_html=True
    )

def user_rank_card(name, adherence, streak_val, rank, color):
    medal = ["🥇","🥈","🥉"][rank-1] if rank <= 3 else f"#{rank}"
    st.markdown(
        "<div style=\"background:#111620;border:1px solid #1e2d40;border-radius:12px;"
        "padding:16px 20px;margin-bottom:8px;position:relative;overflow:hidden;\">"
        "<div style=\"position:absolute;top:0;left:0;bottom:0;width:3px;background:" + color + ";border-radius:3px 0 0 3px;\"></div>"
        "<div style=\"display:flex;justify-content:space-between;align-items:center;\">"
        "<div style=\"display:flex;align-items:center;gap:10px;\">"
        "<span style=\"font-size:20px\">" + medal + "</span>"
        "<div><div style=\"font-family:Syne;font-weight:700;font-size:15px;color:#e8f0f8;\">" + name + "</div>"
        "<div style=\"font-family:Space Mono;font-size:10px;color:#445566;\">🔥 " + str(streak_val) + " day streak</div>"
        "</div></div>"
        "<div style=\"font-family:Space Mono;font-size:22px;font-weight:700;color:" + color + ";\">" + str(round(adherence,1)) + "%</div>"
        "</div>"
        "<div style=\"margin-top:10px;background:#0d1117;border-radius:4px;height:4px;\">"
        "<div style=\"width:" + str(int(adherence)) + "%;height:100%;background:" + color + ";border-radius:4px;\"></div>"
        "</div></div>",
        unsafe_allow_html=True
    )

def logs_to_df(logs):
    if not logs: return pd.DataFrame()
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["log_date"])
    return df

def adherence_rate(df, col="status"):
    if df.empty: return 0.0
    return round(df[col].mean() * 100, 1)

def calc_streak(logs, habit_id):
    rows = sorted([r for r in logs if r["habit_id"]==habit_id], key=lambda x: x["log_date"], reverse=True)
    count = 0
    for r in rows:
        if r["status"]==1: count += 1
        else: break
    return count

def radar_chart(habits, rates, color="#00d4ff"):
    if not habits: return go.Figure()
    labels = [h["icon"]+" "+h["name"] for h in habits]
    r = rates + [rates[0]]
    theta = labels + [labels[0]]
    cr,cg,cb = int(color[1:3],16),int(color[3:5],16),int(color[5:7],16)
    fig = go.Figure(go.Scatterpolar(r=r,theta=theta,fill="toself",
        line=dict(color=color,width=2),
        fillcolor=f"rgba({cr},{cg},{cb},0.1)",name="Adherence %"))
    fig.update_layout(**PLOTLY_LAYOUT,height=420,
        title=dict(text=""),margin=dict(l=20,r=20,t=10,b=20),
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],gridcolor="#1e2d40",
                tickfont=dict(size=9,color="#445566"),ticksuffix="%"),
            angularaxis=dict(gridcolor="#1e2d40",linecolor="#1e2d40",
                tickfont=dict(family="Space Mono",size=10,color="#8899aa"))))
    return fig

def heatmap_chart(df, habits):
    if df.empty or not habits: return go.Figure()
    habit_names=[h["icon"]+" "+h["name"] for h in habits]
    habit_ids=[h["id"] for h in habits]
    dates=sorted(df["date"].dt.date.unique())
    date_labels=[d.strftime("%b %d") for d in dates]
    z=[]
    for hid in habit_ids:
        row=[]
        for d in dates:
            sub=df[(df["habit_id"]==hid)&(df["date"].dt.date==d)]
            row.append(float(sub["status"].iloc[0]) if not sub.empty else float("nan"))
        z.append(row)
    fig=go.Figure(go.Heatmap(z=z,x=date_labels,y=habit_names,
        colorscale=[[0,"#1a0a0a"],[0.5,"#2a1a4a"],[1,"#00d4ff"]],
        zmin=0,zmax=1,showscale=False,xgap=2,ygap=4,
        hovertemplate="%{y}<br>%{x}<br>%{z:.0%}<extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT,height=220,
        yaxis=dict(tickfont=dict(size=11),gridcolor="#1e2d40"),
        xaxis=dict(gridcolor="#1e2d40"),
        margin=dict(l=10,r=10,t=20,b=30))
    return fig

def gauge_chart(value, label, color="#00d4ff"):
    fig=go.Figure(go.Indicator(mode="gauge+number",value=value,
        number=dict(suffix="%",font=dict(family="Space Mono",color=color,size=26)),
        gauge=dict(axis=dict(range=[0,100],tickfont=dict(size=8,color="#445566")),
            bar=dict(color=color,thickness=0.6),bgcolor="rgba(0,0,0,0)",bordercolor="#1e2d40",
            steps=[dict(range=[0,40],color="rgba(255,60,110,0.08)"),
                   dict(range=[40,70],color="rgba(255,190,0,0.06)"),
                   dict(range=[70,100],color="rgba(0,255,157,0.06)")])))
    fig.update_layout(**{**PLOTLY_LAYOUT,"height":240,
        "title":dict(text=label,x=0.5,font=dict(family="Space Mono",size=11,color="#8899aa")),
        "margin":dict(l=10,r=10,t=50,b=10)})
    return fig

def line_chart(df, user_col="user_name"):
    if df.empty: return go.Figure()
    daily=df.groupby(["date",user_col])["status"].mean().mul(100).reset_index()
    fig=go.Figure()
    for i,u in enumerate(daily[user_col].unique()):
        color=PALETTE[i%len(PALETTE)]
        ud=daily[daily[user_col]==u].sort_values("date")
        fig.add_trace(go.Scatter(x=ud["date"],y=ud["status"],name=u,mode="lines+markers",
            line=dict(color=color,width=2),marker=dict(size=5,color=color),
            hovertemplate=f"<b>{u}</b><br>%{{x|%b %d}}<br>%{{y:.1f}}%<extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT,height=300,
        yaxis=dict(title="Adherence %",range=[0,105],gridcolor="#1e2d40"),
        xaxis=dict(gridcolor="#1e2d40"),
        legend=dict(orientation="h",y=-0.2,bgcolor="rgba(13,17,23,0.8)",bordercolor="#1e2d40",borderwidth=1),
        margin=dict(l=10,r=10,t=20,b=10))
    return fig

def radar_overlay(members_data):
    fig=go.Figure()
    for m in members_data:
        labels=[h["icon"]+" "+h["name"] for h in m["habits"]]
        if not labels: continue
        r=m["rates"]+[m["rates"][0]]
        theta=labels+[labels[0]]
        c=m["color"]
        cr,cg,cb=int(c[1:3],16),int(c[3:5],16),int(c[5:7],16)
        fig.add_trace(go.Scatterpolar(r=r,theta=theta,fill="toself",name=m["name"],
            line=dict(color=c,width=2),fillcolor=f"rgba({cr},{cg},{cb},0.06)"))
    fig.update_layout(**PLOTLY_LAYOUT,height=480,title=dict(text=""),
        margin=dict(l=20,r=20,t=10,b=60),
        polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,range=[0,100],gridcolor="#1e2d40",
                tickfont=dict(size=9,color="#445566"),ticksuffix="%"),
            angularaxis=dict(gridcolor="#1e2d40",linecolor="#1e2d40",
                tickfont=dict(family="Space Mono",size=10,color="#8899aa"))),
        legend=dict(orientation="h",y=-0.1,bgcolor="rgba(13,17,23,0.8)",bordercolor="#1e2d40",borderwidth=1))
    return fig


def manage_habits_page():
    user=st.session_state.user
    section_header("⚙", "Manage Habits", "Add, view or remove your habits")
    habits=get_habits(user["id"])
    if habits:
        st.markdown("<div style='font-family:Space Mono;font-size:10px;color:#445566;letter-spacing:2px;margin-bottom:8px;'>YOUR HABITS</div>",unsafe_allow_html=True)
        for h in habits:
            c1,c2=st.columns([7,1])
            with c1:
                st.markdown(
                    "<div style='background:#111620;border:1px solid #1e2d40;border-radius:8px;padding:12px 16px;display:flex;justify-content:space-between;'>"
                    "<span style='font-family:Syne;font-weight:600;color:#e8f0f8;'>" + h["icon"]+" "+h["name"] + "</span>"
                    "<span style='font-family:Space Mono;font-size:10px;color:#445566;'>Target: " + str(h["target"])+" "+h["unit"] + "</span>"
                    "</div>",unsafe_allow_html=True)
            with c2:
                if st.button("🗑", key=f"del_{h['id']}"):
                    delete_habit(h["id"],user["id"]); st.rerun()
    st.markdown("<br>",unsafe_allow_html=True)
    section_header("➕", "Add New Habit")
    with st.form("add_habit_form"):
        c1,c2=st.columns(2)
        with c1:
            new_name=st.text_input("Habit Name",placeholder="e.g. Meditation")
            new_target=st.number_input("Daily Target",min_value=0.1,value=1.0,step=0.5)
        with c2:
            new_icon=st.selectbox("Icon",ICON_OPTIONS)
            new_unit=st.selectbox("Unit",UNIT_OPTIONS)
        new_type=st.radio("Type",["binary (done/not done)","quantity (track amount)"],horizontal=True)
        if st.form_submit_button("⬡ ADD HABIT",use_container_width=True):
            if not new_name: st.error("Enter a habit name.")
            else:
                htype="binary" if "binary" in new_type else "quantity"
                add_habit(user["id"],new_name,new_icon,new_unit,new_target,htype)
                st.success(f"Added {new_icon} {new_name}!"); st.rerun()


def log_habits_page():
    user=st.session_state.user
    habits=get_habits(user["id"])
    section_header("📝", "Log Habits", date.today().strftime("%A, %B %d"))
    if not habits:
        st.info("No habits yet! Go to Manage Habits to add some."); return
    log_date=st.date_input("Log date",value=date.today())
    st.markdown("<br>",unsafe_allow_html=True)
    with st.form("log_form"):
        entries={}
        for h in habits:
            st.markdown("<div style='font-family:Syne;font-weight:600;font-size:14px;color:#e8f0f8;margin:12px 0 6px 0;'>"+h["icon"]+" "+h["name"]+"</div>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1: done=st.radio("Status",["✅ Done","❌ Missed"],key=f"s_{h['id']}",horizontal=True,label_visibility="collapsed")
            with c2: val=st.number_input(f"Value",min_value=0.0,value=float(h["target"]),step=0.5,key=f"v_{h['id']}",label_visibility="collapsed")
            entries[h["id"]]={"status":1 if "Done" in done else 0,"value":val}
        if st.form_submit_button("⬡ SAVE ALL LOGS",use_container_width=True):
            for hid,e in entries.items():
                log_habit(user["id"],hid,str(log_date),e["status"],e["value"])
            st.success(f"Logged {len(entries)} habits for {log_date}!"); st.rerun()


def individual_dashboard():
    user=st.session_state.user
    habits=get_habits(user["id"])
    logs=get_logs(user["id"],days=30)
    df=logs_to_df(logs)
    total_adh=adherence_rate(df) if not df.empty else 0.0
    days_tracked=df["date"].nunique() if not df.empty else 0
    max_streak=max([calc_streak(logs,h["id"]) for h in habits],default=0) if habits else 0
    best_habit_name="—"
    if not df.empty and habits:
        rmap={h["id"]:adherence_rate(df[df["habit_id"]==h["id"]]) for h in habits}
        bh=next((h for h in habits if h["id"]==max(rmap,key=rmap.get)),None)
        if bh: best_habit_name=bh["icon"]+" "+bh["name"]
    st.markdown(
        "<div style='background:linear-gradient(135deg,rgba(0,0,0,0),rgba(0,212,255,0.06));border:1px solid #1e2d40;border-radius:16px;padding:28px 32px;margin-bottom:24px;position:relative;overflow:hidden;'>"
        "<div style='font-family:Space Mono;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#445566;'>INDIVIDUAL DASHBOARD</div>"
        "<div style='font-family:Syne,sans-serif;font-weight:800;font-size:36px;color:#00d4ff;margin:6px 0 4px 0;'>"+user["name"]+"</div>"
        "<div style='font-family:Space Mono;font-size:12px;color:#8899aa;'>"+str(days_tracked)+" days tracked · Best: "+best_habit_name+"</div>"
        "</div>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: stat_card("Adherence (30d)",f"{total_adh}%")
    with c2: stat_card("Best Streak",f"{max_streak}d","#00ff9d")
    with c3: stat_card("Days Tracked",str(days_tracked),"#ffbe00")
    with c4: stat_card("Active Habits",str(len(habits)),"#7b2fff")
    st.markdown("<br>",unsafe_allow_html=True)
    if not habits:
        st.info("No habits yet! Use Manage Habits in the sidebar."); return
    tab1,tab2=st.tabs(["OVERVIEW","HABIT BREAKDOWN"])
    with tab1:
        if not df.empty:
            section_header("▸","Habit Radar","Adherence across all habits")
            rates=[adherence_rate(df[df["habit_id"]==h["id"]]) for h in habits]
            st.plotly_chart(radar_chart(habits,rates,"#00d4ff"),use_container_width=True)
            section_header("▸","Habit Heatmap","Daily completion grid")
            st.plotly_chart(heatmap_chart(df,habits),use_container_width=True)
            section_header("▸","Per-Habit Gauges")
            cols=st.columns(min(len(habits),4))
            for i,h in enumerate(habits):
                rate=adherence_rate(df[df["habit_id"]==h["id"]])
                gc="#00d4ff" if rate>=70 else "#ffbe00" if rate>=40 else "#ff3c6e"
                with cols[i%4]: st.plotly_chart(gauge_chart(rate,h["icon"]+" "+h["name"],gc),use_container_width=True)
        else:
            st.info("No logs yet for this period. Start logging!")
    with tab2:
        section_header("▸","Habit Breakdown")
        if not df.empty:
            for h in habits:
                rate=adherence_rate(df[df["habit_id"]==h["id"]])
                st_val=calc_streak(logs,h["id"])
                habit_bar(h["icon"],h["name"],rate,st_val)
            section_header("▸","Daily Trend")
            df["user_name"]=user["name"]
            st.plotly_chart(line_chart(df,"user_name"),use_container_width=True)
        else:
            st.info("No logs yet.")


def household_dashboard():
    user=st.session_state.user
    hh=st.session_state.get("household") or get_user_household(user["id"])
    if not hh:
        st.warning("You're not in a household yet.")
        c1,c2=st.columns(2)
        with c1:
            hname=st.text_input("Create household",placeholder="Household name")
            if st.button("Create",key="cr_hh"):
                r=create_household(hname,user["id"])
                if r["ok"]: st.session_state.household=r["household"]; st.rerun()
        with c2:
            code=st.text_input("Join household",placeholder="Invite code")
            if st.button("Join",key="j_hh"):
                r=join_household(code,user["id"])
                if r["ok"]: st.session_state.household=r["household"]; st.rerun()
        return
    members=get_household_members(hh["id"])
    logs=get_household_logs(hh["id"],days=30)
    df=logs_to_df(logs)
    house_adh=adherence_rate(df) if not df.empty else 0.0
    total_days=df["date"].nunique() if not df.empty else 0
    best_member="—"
    if not df.empty and "uid" in df.columns:
        bm_id=df.groupby("uid")["status"].mean().idxmax()
        bm=next((m for m in members if m["id"]==bm_id),None)
        if bm: best_member=bm["name"]
    member_spans=" · ".join("<span style='color:"+PALETTE[i%len(PALETTE)]+";'>"+m["name"]+"</span>" for i,m in enumerate(members))
    st.markdown(
        "<div style='background:linear-gradient(135deg,rgba(0,212,255,0.04),rgba(123,47,255,0.08));border:1px solid #1e2d40;border-radius:16px;padding:28px 32px;margin-bottom:24px;position:relative;overflow:hidden;'>"
        "<div style='font-family:Space Mono;font-size:10px;letter-spacing:3px;text-transform:uppercase;color:#445566;'>HOUSEHOLD · "+hh["name"].upper()+"</div>"
        "<div style='font-family:Syne,sans-serif;font-weight:800;font-size:28px;color:#e8f0f8;margin:6px 0 4px 0;'>"+member_spans+"</div>"
        "<div style='font-family:Space Mono;font-size:12px;color:#8899aa;'>"+str(total_days)+" days tracked · Top: "+best_member+"</div>"
        "</div>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: stat_card("House Adherence",f"{house_adh}%")
    with c2: stat_card("Members",str(len(members)),"#7b2fff")
    with c3: stat_card("Days Tracked",str(total_days),"#ffbe00")
    with c4: stat_card("Top Performer",best_member,"#00ff9d")
    with st.expander("🔗 Invite Code — share with members"):
        st.markdown("<div style='font-family:Space Mono;font-size:28px;font-weight:700;color:#00d4ff;text-align:center;letter-spacing:6px;padding:12px;'>"+hh["invite_code"]+"</div>",unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    tab1,tab2=st.tabs(["LEADERBOARD","TRENDS & RADAR"])
    with tab1:
        section_header("▸","Leaderboard","Ranked by overall adherence")
        if not df.empty and "uid" in df.columns:
            ranked=df.groupby("uid")["status"].mean().mul(100).sort_values(ascending=False)
            for rank,(uid,adh) in enumerate(ranked.items(),1):
                m=next((x for x in members if x["id"]==uid),None)
                if not m: continue
                color=PALETTE[(rank-1)%len(PALETTE)]
                mlogs=[l for l in logs if l["uid"]==uid]
                hm=get_habits(uid)
                max_st=max([calc_streak(mlogs,h["id"]) for h in hm],default=0) if hm else 0
                user_rank_card(m["name"],adh,max_st,rank,color)
            section_header("▸","Adherence Gauges")
            cols=st.columns(len(members))
            for i,m in enumerate(members):
                color=PALETTE[i%len(PALETTE)]
                mdf=df[df["uid"]==m["id"]] if "uid" in df.columns else pd.DataFrame()
                rate=adherence_rate(mdf)
                with cols[i]: st.plotly_chart(gauge_chart(rate,m["name"],color),use_container_width=True)
            if "habit_name" in df.columns:
                section_header("▸","Habit Performance Matrix")
                pivot=df.groupby(["user_name","habit_name"])["status"].mean().mul(100).round(1).unstack(fill_value=0)
                def cc(val):
                    if val>=70: return "background-color:#0d2b1a;color:#00ff9d"
                    elif val>=40: return "background-color:#2b2200;color:#ffbe00"
                    return "background-color:#2b0a0a;color:#ff3c6e"
                st.dataframe(pivot.style.map(cc).format("{:.1f}%"),use_container_width=True)
        else:
            st.info("No household logs yet.")
    with tab2:
        if not df.empty and "user_name" in df.columns:
            section_header("▸","Daily Adherence Trends")
            st.plotly_chart(line_chart(df,"user_name"),use_container_width=True)
            section_header("▸","Radar Overlay","All members on one chart")
            mdata=[]
            for i,m in enumerate(members):
                mdf=df[df["uid"]==m["id"]]
                hm=get_habits(m["id"])
                if not hm: continue
                rates=[adherence_rate(mdf[mdf["habit_id"]==h["id"]]) for h in hm]
                mdata.append({"name":m["name"],"habits":hm,"rates":rates,"color":PALETTE[i%len(PALETTE)]})
            if mdata: st.plotly_chart(radar_overlay(mdata),use_container_width=True)
            section_header("▸","Individual Heatmaps")
            cols=st.columns(len(members))
            for i,m in enumerate(members):
                mdf=df[df["uid"]==m["id"]]
                hm=get_habits(m["id"])
                with cols[i]:
                    st.markdown("<div style='font-family:Syne;font-weight:700;font-size:13px;color:"+PALETTE[i%len(PALETTE)]+";text-align:center;margin-bottom:6px;'>"+m["name"]+"</div>",unsafe_allow_html=True)
                    if not mdf.empty and hm: st.plotly_chart(heatmap_chart(mdf,hm),use_container_width=True)
                    else: st.caption("No data yet")
        else:
            st.info("No household logs yet.")


def settings_page():
    user=st.session_state.user
    hh=st.session_state.get("household") or get_user_household(user["id"])
    section_header("⚙","Settings","Account & Household")
    st.markdown("<div style='background:#111620;border:1px solid #1e2d40;border-radius:10px;padding:16px 20px;margin-bottom:16px;'><div style='font-family:Syne;font-size:16px;color:#e8f0f8;font-weight:700;'>"+user["name"]+"</div><div style='font-family:Space Mono;font-size:11px;color:#445566;margin-top:4px;'>"+user["email"]+"</div></div>",unsafe_allow_html=True)
    if hh:
        st.markdown("<div style='background:#111620;border:1px solid #1e2d40;border-radius:10px;padding:16px 20px;margin-bottom:16px;'><div style='font-family:Syne;font-size:15px;color:#e8f0f8;font-weight:700;'>🏠 "+hh["name"]+"</div><div style='font-family:Space Mono;font-size:20px;color:#00d4ff;font-weight:700;letter-spacing:4px;margin-top:8px;'>"+hh["invite_code"]+"</div><div style='font-family:Space Mono;font-size:10px;color:#445566;margin-top:4px;'>INVITE CODE — share with members</div></div>",unsafe_allow_html=True)
    else:
        st.info("Not in a household. Join or create one from the Household Dashboard.")
    st.markdown("<br>",unsafe_allow_html=True)
    if st.button("🚪 Sign Out", use_container_width=True, key="settings_signout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.page = "login"
        st.rerun()


def main():
    if "page" not in st.session_state:
        st.session_state.page = "login"

    page = st.session_state.page

    # ── Auth pages — render nothing else until fully resolved ──
    if page == "login":
        show_login_page()
        return
    if page == "onboarding":
        show_onboarding_page()
        return
    if page == "show_invite":
        show_invite_page()
        return
    if page == "onboard_check":
        check_onboard_or_app()
        return

    # ── Loading screen — shown briefly between demo click and app render ──
    if page == "loading":
        st.markdown("""
        <div style="position:fixed;top:0;left:0;right:0;bottom:0;
                    background:#080b12;z-index:9999;
                    display:flex;flex-direction:column;
                    align-items:center;justify-content:center;">
            <div style="font-family:Syne,sans-serif;font-weight:800;
                        font-size:36px;color:#e8f0f8;margin-bottom:8px;">
                ⬡ HabitOS
            </div>
            <div style="font-family:Space Mono,monospace;font-size:11px;
                        letter-spacing:3px;text-transform:uppercase;color:#445566;">
                Loading dashboard...
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Immediately switch to app on next rerun
        st.session_state.page = "app"
        st.rerun()
        return

    # ── Guard: must have a user in session ──
    user = st.session_state.get("user")
    if not user:
        st.session_state.page = "login"
        st.rerun()
        return

    # ── Pre-set nav from session if coming from demo login ──
    if "nav" not in st.session_state:
        st.session_state.nav = "🧍 Individual Dashboard"

    with st.sidebar:
        st.markdown("<div style='padding:20px 0 8px 0;'><div style='font-family:Syne,sans-serif;font-weight:800;font-size:22px;color:#e8f0f8;'>⬡ HabitOS</div><div style='font-family:Space Mono;font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#445566;margin-top:2px;'>Health Analytics v2.0</div></div>",unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e2d40;margin:12px 0;'>",unsafe_allow_html=True)
        st.markdown("<div style='font-family:Space Mono;font-size:10px;color:#445566;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px;'>SIGNED IN AS</div><div style='font-family:Syne;font-weight:700;font-size:14px;color:#00d4ff;'>"+user["name"]+"</div>",unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e2d40;margin:12px 0;'>",unsafe_allow_html=True)
        nav_options = ["🧍 Individual Dashboard","🏠 Household Dashboard","📝 Log Habits","⚙ Manage Habits","🔧 Settings"]
        # Use index to pre-select correct page (e.g. from demo login)
        current_nav = st.session_state.get("nav", nav_options[0])
        nav_index = nav_options.index(current_nav) if current_nav in nav_options else 0
        nav = st.radio("", nav_options, index=nav_index,
                       label_visibility="collapsed", key="nav")
        st.markdown("<hr style='border-color:#1e2d40;margin:16px 0;'>",unsafe_allow_html=True)
        habits=get_habits(user["id"])
        logs=get_logs(user["id"],days=7)
        df_q=logs_to_df(logs)
        adh7=adherence_rate(df_q)
        st.markdown("<div style='font-family:Space Mono;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#445566;margin-bottom:8px;'>7-DAY STATS</div><div style='background:#111620;border:1px solid #1e2d40;border-radius:8px;padding:12px;'><div style='display:flex;justify-content:space-between;margin-bottom:6px;'><span style='font-family:Space Mono;font-size:10px;color:#8899aa;'>Adherence</span><span style='font-family:Space Mono;font-size:11px;color:#00d4ff;font-weight:700;'>"+str(adh7)+"%</span></div><div style='display:flex;justify-content:space-between;'><span style='font-family:Space Mono;font-size:10px;color:#8899aa;'>Active habits</span><span style='font-family:Space Mono;font-size:11px;color:#7b2fff;font-weight:700;'>"+str(len(habits))+"</span></div></div>",unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#1e2d40;margin:16px 0;'>",unsafe_allow_html=True)
        # Demo badge if viewing demo
        is_demo = st.session_state.get("user",{}).get("email","").endswith("@demo.habitos")
        if is_demo:
            st.markdown(
                "<div style='background:rgba(255,190,0,0.08);border:1px solid rgba(255,190,0,0.3);"
                "border-radius:8px;padding:8px 12px;margin-bottom:12px;text-align:center;'>"
                "<span style='font-family:Space Mono;font-size:10px;color:#ffbe00;letter-spacing:2px;'>👁 DEMO MODE</span>"
                "</div>",
                unsafe_allow_html=True
            )
        if st.button("🚪 Sign Out", use_container_width=True, key="sidebar_signout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.session_state["page"] = "login"
            st.rerun()

    if "Individual" in nav: individual_dashboard()
    elif "Household" in nav: household_dashboard()
    elif "Log Habits" in nav: log_habits_page()
    elif "Manage Habits" in nav: manage_habits_page()
    elif "Settings" in nav: settings_page()

if __name__=="__main__":
    main()
