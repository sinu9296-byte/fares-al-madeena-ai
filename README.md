# UAE AI Marketing Manager — Phase 1

A beginner-friendly standalone web-app prototype customised for Fares Al Madeena Cafeteria, a UAE business serving Kerala cuisine, fresh juice, chai, Kannur snacks, mess meals and delivery.

## What works in the free demo
- Business profile form
- Marketing strategy workspace
- Social content draft workspace
- Campaign planner
- Daily content planner
- Food promotion generator
- Local customer growth tracker (manual enquiry/order logging)
- Local SQLite work log
- No API key required to explore the demo

## What requires an API key
Live AI-generated strategies and content use the OpenAI API. API usage may incur charges. The app does not publish posts, send messages, or spend ad money.

## Run on a computer
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Create a virtual environment:
   `python -m venv .venv`
4. Activate it:
   - Windows: `.venv\Scripts\activate`
   - macOS/Linux: `source .venv/bin/activate`
5. Install packages:
   `pip install -r requirements.txt`
6. Start the app:
   `streamlit run app.py`

## Enable live AI
1. Copy `.env.example` to `.env`.
2. Add your own OpenAI API key to `OPENAI_API_KEY`.
3. Keep `.env` private. Never upload it to GitHub or share it in chat.
4. Restart the app.

An API key is not included. The model name can be changed using `OPENAI_MODEL`.

## Free cloud deployment
You can deploy this project through Streamlit Community Cloud by connecting a GitHub repository and selecting `app.py` as the entry point. Check the current hosting terms and limits before deployment.
For live AI, add `OPENAI_API_KEY` under the app's Secrets settings. Do not put the key in source code.

## Important limitations of Phase 1
- This is a prototype, not a finished commercial product.
- Business profile, drafts and manually recorded customer activity are stored in a local SQLite database. Some cloud hosts have ephemeral storage; use a managed database before relying on persistent production records.
- No social account integrations or automatic publishing.
- No advertising spend, customer messaging, or external actions.
- AI outputs must be checked by a human before use.

## Next build milestones
1. Confirm the business name, product/service, audience and offer.
2. Improve the brand profile and UAE market research prompts.
3. Add a secure persistent database.
4. Add platform integrations using official APIs and permissions.
5. Add approval workflows, audit logs and role-based access.
6. Add analytics and scheduled reporting.
