import os
import sqlite3
from datetime import date
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.getenv("DATABASE_PATH", "marketing_manager.db")

st.set_page_config(page_title="UAE AI Marketing Manager", page_icon="📈", layout="wide")

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT, task_type TEXT, title TEXT, details TEXT, status TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS profile (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        business_name TEXT, business_type TEXT, audience TEXT,
        offer TEXT, tone TEXT, channels TEXT,
        location TEXT DEFAULT 'Al Jurf, Ajman, near Lucky Center, UAE',
        delivery TEXT DEFAULT 'Yes',
        priority TEXT DEFAULT 'All services equally'
    )""")
    # Safely add new columns to databases created by an earlier prototype.
    existing = {row[1] for row in conn.execute("PRAGMA table_info(profile)").fetchall()}
    for col, definition in [
        ("location", "TEXT DEFAULT 'Al Jurf, Ajman, near Lucky Center, UAE'"),
        ("delivery", "TEXT DEFAULT 'Yes'"),
        ("priority", "TEXT DEFAULT 'All services equally'")
    ]:
        if col not in existing:
            conn.execute(f"ALTER TABLE profile ADD COLUMN {col} {definition}")
    conn.execute("""CREATE TABLE IF NOT EXISTS customer_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        activity_date TEXT, customer_label TEXT, channel TEXT,
        activity_type TEXT, service TEXT, value_aed REAL DEFAULT 0, notes TEXT
    )""")
    conn.commit()
    return conn

conn = db()

def get_profile():
    row = conn.execute("SELECT business_name,business_type,audience,offer,tone,channels FROM profile WHERE id=1").fetchone()
    if row:
        return dict(zip(["business_name","business_type","audience","offer","tone","channels"], row))
    return {"business_name":"Fares Al Madeena Cafeteria","business_type":"Kerala cuisine, fresh juice, chai, Kannur snacks, mess service and food delivery","audience":"Kerala food lovers, UAE residents, nearby workers and families","offer":"Kerala cuisine, fresh juices, chai, Kannur snacks, mess meals and delivery. Prices, menu and delivery areas to be confirmed.","tone":"Traditional","channels":"Instagram, Facebook, TikTok, WhatsApp (manual enquiries)"}

def save_profile(p):
    conn.execute("""INSERT INTO profile(id,business_name,business_type,audience,offer,tone,channels,location,delivery,priority)
    VALUES(1,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
    business_name=excluded.business_name,business_type=excluded.business_type,
    audience=excluded.audience,offer=excluded.offer,tone=excluded.tone,channels=excluded.channels,
    location=excluded.location,delivery=excluded.delivery,priority=excluded.priority""",
    (p["business_name"],p["business_type"],p["audience"],p["offer"],p["tone"],p["channels"],
     p["location"],p["delivery"],p["priority"]))
    conn.commit()

def add_task(task_type, title, details):
    conn.execute("INSERT INTO tasks(created_at,task_type,title,details,status) VALUES(?,?,?,?,?)",
                 (date.today().isoformat(), task_type, title, details, "Draft"))
    conn.commit()

def ai_response(prompt):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None, "Demo mode: add an OpenAI API key in your deployment secrets to enable live AI. No API call was made."
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            instructions=("You are a careful UAE-focused marketing manager. "
                          "Use AED where relevant. Do not invent market statistics, prices, "
                          "or legal claims. Clearly label assumptions. Draft content only; "
                          "never claim to publish, spend money, or contact customers."),
            input=prompt
        )
        return response.output_text, None
    except Exception as e:
        return None, f"AI request failed: {e}"

profile = get_profile()

with st.sidebar:
    st.title("📈 Marketing Manager")
    st.caption("Your UAE business marketing workspace")
    page = st.radio("Workspace", ["Overview", "Business Profile", "Marketing Strategy",
                                  "Content Studio", "Daily Content Planner", "Promotion Generator",
                                  "Campaign Planner", "Customer Growth Tracker", "Reports"])
    st.divider()
    st.caption("Phase 1 prototype • AED • UAE")

st.title("UAE AI Marketing Manager")
st.caption("A human-approved marketing workspace for your business.")

if page == "Overview":
    tasks = conn.execute("SELECT created_at,task_type,title,status FROM tasks ORDER BY id DESC").fetchall()
    a,b,c = st.columns(3)
    a.metric("Saved drafts", len(tasks))
    b.metric("Awaiting approval", sum(1 for t in tasks if t[3] == "Awaiting approval"))
    c.metric("Published", 0)
    st.subheader("Welcome")
    st.write(f"Business: **{profile['business_name']}**")
    st.write(f"Location: **{profile['location']}** · Delivery: **{profile['delivery']}**")
    st.info("The workspace is configured for local marketing in Al Jurf, Ajman. Complete the business profile with confirmed menu, prices and delivery terms before creating public promotions.")
    st.subheader("Recent work")
    if tasks:
        st.dataframe([{"Date":t[0],"Type":t[1],"Title":t[2],"Status":t[3]} for t in tasks],
                     use_container_width=True, hide_index=True)
    else:
        st.write("No drafts yet. Create your first strategy or social post.")
    st.warning("This prototype does not publish posts, send messages, or spend advertising money.")

elif page == "Business Profile":
    st.subheader("Tell the AI about your business")
    st.write("You haven't supplied your business name or product yet. Add only information you are comfortable storing.")
    with st.form("profile_form"):
        business_name = st.text_input("Business name", profile["business_name"])
        business_type = st.text_input("What do you sell or provide?", profile["business_type"],
                                      placeholder="Example: Kerala tea and snacks")
        audience = st.text_input("Who are your ideal customers?", profile["audience"],
                                 placeholder="Example: UAE residents who enjoy South Indian food")
        offer = st.text_area("Main product, service or offer", profile["offer"])
        tone = st.selectbox("Brand voice", ["Professional and friendly", "Premium", "Playful", "Traditional", "Bold"],
                             index=["Professional and friendly", "Premium", "Playful", "Traditional", "Bold"].index(profile["tone"])
                             if profile["tone"] in ["Professional and friendly", "Premium", "Playful", "Traditional", "Bold"] else 0)
        channels = st.text_input("Marketing channels", profile["channels"])
        location = st.text_input("Business location", profile["location"])
        delivery = st.selectbox("Delivery availability", ["Yes", "No", "Through delivery platforms"],
                                index=["Yes", "No", "Through delivery platforms"].index(profile["delivery"])
                                if profile["delivery"] in ["Yes", "No", "Through delivery platforms"] else 0)
        priority = st.selectbox("Marketing priority", ["All services equally", "Kerala food and snacks",
                                  "Chai and fresh juice", "Mess service", "Food delivery"],
                                index=["All services equally", "Kerala food and snacks",
                                       "Chai and fresh juice", "Mess service", "Food delivery"].index(profile["priority"])
                                if profile["priority"] in ["All services equally", "Kerala food and snacks",
                                  "Chai and fresh juice", "Mess service", "Food delivery"] else 0)
        saved = st.form_submit_button("Save business profile", type="primary")
        if saved:
            save_profile({"business_name":business_name,"business_type":business_type,
                          "audience":audience,"offer":offer,"tone":tone,"channels":channels,
                          "location":location,"delivery":delivery,"priority":priority})
            st.success("Business profile saved.")
            st.rerun()

elif page == "Marketing Strategy":
    st.subheader("Create a marketing strategy")
    goal = st.selectbox("Main goal", ["Build brand awareness", "Get more enquiries", "Increase sales",
                                      "Launch a product", "Grow social media"])
    period = st.selectbox("Planning period", ["7 days", "30 days", "90 days"])
    budget = st.number_input("Marketing budget (AED)", min_value=0, value=0, step=50)
    extra = st.text_area("Additional context", placeholder="Tell the AI about your current situation...")
    if st.button("Generate strategy", type="primary"):
        prompt = f"""Create a practical {period} marketing strategy for this UAE business.
Business: {profile['business_name']}
Location: {profile['location']}
Delivery: {profile['delivery']}
Marketing priority: {profile['priority']}
Type: {profile['business_type']}
Audience: {profile['audience']}
Offer: {profile['offer']}
Channels: {profile['channels']}
Brand voice: {profile['tone']}
Goal: {goal}
Budget: AED {budget}
Context: {extra}
Include objectives, audience assumptions, channel plan, weekly actions, content ideas,
KPIs and a realistic zero-cost option. Do not invent market data."""
        result, error = ai_response(prompt)
        if result:
            st.markdown(result)
            add_task("Strategy", f"{period} plan: {goal}", result)
        else:
            st.warning(error)
            st.markdown("**Demo preview — suggested structure**")
            st.markdown(f"""1. **Goal:** {goal}
2. **Audience:** {profile['audience']}
3. **Channels:** {profile['channels']}
4. **Budget:** AED {budget}
5. **First action:** Define one clear offer and create three helpful posts.
6. **Measure:** Enquiries, qualified leads, conversions and cost per lead.
7. **Next step:** Complete the business profile and enable live AI when ready.""")

elif page == "Content Studio":
    st.subheader("Social media content studio")
    platform = st.selectbox("Platform", ["Instagram", "Facebook", "TikTok", "LinkedIn"])
    content_type = st.selectbox("Content format", ["Post", "Reel / short video", "Story", "Carousel"])
    topic = st.text_area("What should the content be about?", placeholder="Example: Introduce our best-selling product")
    language = st.selectbox("Language", ["English", "Hindi", "Malayalam"])
    if st.button("Create content draft", type="primary", disabled=not topic.strip()):
        prompt = f"""Create a {content_type} for {platform} in {language}.
Business: {profile['business_name']} ({profile['business_type']})
Audience: {profile['audience']}
Offer: {profile['offer']}
Brand voice: {profile['tone']}
Topic: {topic}
Give a hook, main copy or scene-by-scene script, call to action, and relevant hashtags.
Avoid unsupported claims and do not imply the content has been published."""
        result, error = ai_response(prompt)
        if result:
            st.markdown(result)
            add_task("Content", f"{platform} {content_type}: {topic[:60]}", result)
        else:
            st.warning(error)
            st.markdown(f"""**Demo content brief**
- Platform: {platform}
- Format: {content_type}
- Language: {language}
- Topic: {topic}
- Hook idea: Start with a customer problem or a surprising product benefit.
- Call to action: Invite people to ask a question or learn more.
- Status: Draft only""")


elif page == "Daily Content Planner":
    st.subheader("Daily content planner")
    st.write(f"Plan content for customers around **{profile['location']}**.")
    with st.form("daily_plan"):
        plan_date = st.date_input("Content date", value=date.today())
        channel = st.selectbox("Channel", ["Instagram", "Facebook", "TikTok", "WhatsApp status"])
        service = st.selectbox("Service to feature", ["Kerala cuisine", "Fresh juice", "Chai",
                               "Kannur snacks", "Mess service", "Delivery", "Mixed menu"])
        language = st.selectbox("Language", ["English", "Malayalam", "Hindi"])
        objective = st.selectbox("Post objective", ["Awareness", "Enquiries", "Orders", "Repeat customers"])
        submit_plan = st.form_submit_button("Create daily content plan", type="primary")
    if submit_plan:
        prompt = f"""Create a practical one-day content plan for Fares Al Madeena Cafeteria.
Date: {plan_date}; Location: {profile['location']}; Channel: {channel};
Feature: {service}; Language: {language}; Objective: {objective}.
Business offers Kerala cuisine, fresh juice, chai, Kannur snacks, mess service and delivery.
Give a suggested posting concept, opening hook, caption/script, CTA, visual shot list,
and a simple way to measure results. Do not invent prices, specific menu items, timings or offers."""
        result, error = ai_response(prompt)
        if result:
            st.markdown(result)
            add_task("Daily content", f"{plan_date} · {channel} · {service}", result)
        else:
            st.warning(error)
            st.markdown(f"""**Demo plan**
- Date: {plan_date}
- Channel: {channel}
- Featured service: {service}
- Language: {language}
- Objective: {objective}
- Hook: "Looking for a taste of Kerala in Ajman?"
- Visual: Show the real featured item, its preparation and final serving.
- CTA: "Visit us in Al Jurf, Ajman, near Lucky Center. Message us to ask about delivery."
- Status: Draft only. Confirm item availability and delivery details before publishing.""")

elif page == "Promotion Generator":
    st.subheader("Food promotion generator")
    with st.form("promo_form"):
        promo_service = st.selectbox("What are you promoting?", ["Kerala cuisine", "Fresh juice", "Chai",
                                     "Kannur snacks", "Mess service", "Delivery", "All services"])
        promo_goal = st.selectbox("Promotion goal", ["Increase visits", "Increase delivery enquiries",
                                  "Attract mess customers", "Introduce the cafeteria", "Promote a special item"])
        promo_channel = st.selectbox("Where will you promote it?", ["Instagram Reel", "Instagram post",
                                      "Facebook post", "WhatsApp status", "Flyer concept"])
        promo_language = st.selectbox("Promotion language", ["English", "Malayalam", "Hindi"])
        promo_details = st.text_area("Confirmed item/price/offer details (optional)",
                                     placeholder="Only enter details that are confirmed by the business.")
        promo_submit = st.form_submit_button("Generate promotion", type="primary")
    if promo_submit:
        prompt = f"""Create a promotion for Fares Al Madeena Cafeteria in Al Jurf, Ajman, near Lucky Center.
Service: {promo_service}; Goal: {promo_goal}; Format: {promo_channel};
Language: {promo_language}; Confirmed details supplied: {promo_details or 'None'}.
Include headline, copy/script, visual direction and CTA.
Do not invent discounts, prices, menu details, availability, operating hours or delivery areas.
If details are missing, use a general invitation and mark what needs confirmation."""
        result, error = ai_response(prompt)
        if result:
            st.markdown(result)
            add_task("Promotion", f"{promo_service} · {promo_goal}", result)
        else:
            st.warning(error)
            st.markdown(f"""**Demo promotion draft**
**Headline:** A little taste of Kerala in Al Jurf!
**Copy:** Discover Kerala cuisine, fresh juice, chai and Kannur snacks at Fares Al Madeena Cafeteria, near Lucky Center, Ajman. Ask us about our mess service and delivery.
**CTA:** Visit us or message the cafeteria for current menu and delivery details.
**Format:** {promo_channel} · {promo_language}
**Before publishing:** Confirm the featured items, current prices and delivery terms.""")

elif page == "Customer Growth Tracker":
    st.subheader("Customer growth tracker")
    st.write("Record customer enquiries and orders manually. Avoid entering sensitive personal information.")
    with st.form("activity_form"):
        activity_date = st.date_input("Date", value=date.today())
        customer_label = st.text_input("Customer label (optional)", placeholder="Use initials or a non-identifying label")
        activity_channel = st.selectbox("How did they find you?", ["Walk-in", "Instagram", "Facebook",
                                         "TikTok", "WhatsApp", "Phone", "Delivery platform", "Other"])
        activity_type = st.selectbox("Activity", ["Enquiry", "Order", "Repeat order", "Mess service enquiry"])
        activity_service = st.selectbox("Service", ["Kerala cuisine", "Fresh juice", "Chai",
                                         "Kannur snacks", "Mess service", "Delivery", "Multiple"])
        order_value = st.number_input("Order value (AED, if applicable)", min_value=0.0, value=0.0, step=5.0)
        activity_notes = st.text_area("Notes (optional)", placeholder="No card details or sensitive customer data.")
        activity_submit = st.form_submit_button("Save customer activity", type="primary")
    if activity_submit:
        conn.execute("""INSERT INTO customer_activity(activity_date,customer_label,channel,activity_type,service,value_aed,notes)
                        VALUES(?,?,?,?,?,?,?)""",
                     (activity_date.isoformat(), customer_label, activity_channel, activity_type,
                      activity_service, order_value, activity_notes))
        conn.commit()
        st.success("Activity saved.")
    rows = conn.execute("""SELECT activity_date,channel,activity_type,service,value_aed
                           FROM customer_activity ORDER BY id DESC LIMIT 100""").fetchall()
    if rows:
        st.subheader("Recent customer activity")
        st.dataframe([{"Date":r[0],"Channel":r[1],"Activity":r[2],"Service":r[3],"Value (AED)":r[4]}
                      for r in rows], use_container_width=True, hide_index=True)
        total_orders = sum(1 for r in rows if r[2] in ("Order", "Repeat order"))
        total_enquiries = sum(1 for r in rows if r[2] in ("Enquiry", "Mess service enquiry"))
        revenue = sum(float(r[4] or 0) for r in rows if r[2] in ("Order", "Repeat order"))
        m1,m2,m3 = st.columns(3)
        m1.metric("Recorded enquiries", total_enquiries)
        m2.metric("Recorded orders", total_orders)
        m3.metric("Recorded order value", f"AED {revenue:.2f}")
    else:
        st.info("Your recorded enquiries and orders will appear here.")

elif page == "Campaign Planner":
    st.subheader("Campaign planner")
    with st.form("campaign"):
        title = st.text_input("Campaign name", placeholder="Example: UAE National Day promotion")
        objective = st.text_input("Campaign objective", placeholder="Example: Generate enquiries")
        start = st.date_input("Proposed start date", value=date.today())
        end = st.date_input("Proposed end date", value=date.today())
        budget = st.number_input("Proposed budget (AED)", min_value=0, value=0, step=50)
        notes = st.text_area("Campaign notes")
        submit = st.form_submit_button("Save campaign draft")
        if submit:
            add_task("Campaign", title or "Untitled campaign",
                     f"Objective: {objective}\nStart: {start}\nEnd: {end}\nBudget: AED {budget}\nNotes: {notes}")
            st.success("Campaign draft saved. No ads have been launched and no money has been spent.")

elif page == "Reports":
    st.subheader("Marketing work log")
    rows = conn.execute("SELECT created_at,task_type,title,details,status FROM tasks ORDER BY id DESC").fetchall()
    if rows:
        for created, kind, title, details, status in rows:
            with st.expander(f"{created} · {kind} · {title} · {status}"):
                st.write(details)
                if st.button("Mark as awaiting approval", key=f"approve_{created}_{title}"):
                    conn.execute("UPDATE tasks SET status='Awaiting approval' WHERE created_at=? AND title=?",
                                 (created,title))
                    conn.commit()
                    st.rerun()
    else:
        st.info("Your saved strategies, content and campaign drafts will appear here.")

st.divider()
st.caption("Prototype only. Review all AI-generated claims and content before using them in public.")
