"""
Personalized Restaurant Recommendation Engine — consumer-grade Streamlit UI.
Warm dark theme inspired by modern food discovery apps; backend unchanged.
"""

import html
import logging
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cuisine → banner images (Unsplash, stable IDs — portfolio placeholders)
CUISINE_BANNER_URLS: Dict[str, str] = {
    "italian": "https://images.unsplash.com/photo-1498579150354-977475b0ea0b?w=960&h=480&fit=crop&q=80",
    "indian": "https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=960&h=480&fit=crop&q=80",
    "chinese": "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=960&h=480&fit=crop&q=80",
    "japanese": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=960&h=480&fit=crop&q=80",
    "mexican": "https://images.unsplash.com/photo-1565299585323-38174c871b49?w=960&h=480&fit=crop&q=80",
    "thai": "https://images.unsplash.com/photo-1559314809-0d155014e29e?w=960&h=480&fit=crop&q=80",
    "continental": "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=960&h=480&fit=crop&q=80",
    "american": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=960&h=480&fit=crop&q=80",
    "korean": "https://images.unsplash.com/photo-1498654896293-e815036825ff?w=960&h=480&fit=crop&q=80",
    "french": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=960&h=480&fit=crop&q=80",
    "default": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=960&h=480&fit=crop&q=80",
}


class PolishedAIRestaurantApp:
    """Streamlit UI for personalized restaurant recommendations."""

    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.setup_page_config()
        self.setup_polished_css()

    @staticmethod
    def _budget_label_to_api_value(label: str) -> str | None:
        mapping = {
            "Budget Friendly": "low",
            "Moderate": "medium",
            "Premium": "high",
            "Fine Dining": "high",
        }
        return mapping.get(label)

    @staticmethod
    def _parse_highlights_meta(highlights: List[Any]) -> Tuple[Optional[str], Optional[str]]:
        cuisine_val: Optional[str] = None
        rating_val: Optional[str] = None
        for h in highlights or []:
            s = str(h).strip()
            low = s.lower()
            if low.startswith("cuisine:"):
                cuisine_val = s.split(":", 1)[1].strip() or None
            elif low.startswith("rating:"):
                rating_val = s.split(":", 1)[1].strip() or None
        return cuisine_val, rating_val

    @staticmethod
    def _banner_url_for_cuisine(cuisine_key: Optional[str]) -> str:
        if not cuisine_key:
            return CUISINE_BANNER_URLS["default"]
        key = cuisine_key.strip().lower()
        return CUISINE_BANNER_URLS.get(key, CUISINE_BANNER_URLS["default"])

    def setup_page_config(self):
        st.set_page_config(
            page_title="AI Restaurant Recommendation System",
            page_icon="🍽️",
            layout="centered",
            initial_sidebar_state="collapsed",
            menu_items={
                "Get Help": None,
                "Report a bug": "https://github.com/janvip08/Milestone-1-Zomato/issues",
                "About": "Personalized Restaurant Recommendation Engine",
            },
        )

    def setup_polished_css(self):
        st.markdown(
            """
            <style>
            :root {
                --bg-deep: #0F1115;
                --bg-elevated: #161A22;
                --card: #1B2230;
                --card-border: rgba(255, 255, 255, 0.08);
                --text: #FFFFFF;
                --text-muted: #EAEAEA;
                --text-soft: #B8BCC8;
                --accent: #E23744;
                --accent-2: #FF5A5F;
                --accent-3: #FF7A59;
            }

            .stApp {
                background: linear-gradient(180deg, var(--bg-deep) 0%, var(--bg-elevated) 45%, var(--bg-deep) 100%);
                background-attachment: fixed;
                color: var(--text);
            }

            .stSidebar, [data-testid="stSidebar"],
            .stMainMenu, .stHeader, .stToolbar,
            [data-testid="stHeader"], [data-testid="stToolbar"],
            .stDeployButton, [data-testid="stDeployButton"],
            .css-1lcbmhc, .css-1outcr7 {
                display: none !important;
            }

            .main .block-container {
                background: var(--bg-elevated);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 1.75rem 2rem 2.25rem;
                margin: 1.25rem auto 2rem auto !important;
                max-width: 720px !important;
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
            }

            /* Hero */
            .hero-wrap {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
                margin: 0 0 1.5rem 0;
                padding: 0.25rem 0 0.5rem;
            }
            .hero-kicker {
                font-size: 0.75rem;
                font-weight: 700;
                letter-spacing: 0.12em;
                text-transform: uppercase;
                color: var(--accent-2);
                margin: 0 0 0.5rem;
                text-align: center;
            }
            .hero-title {
                font-size: 1.85rem;
                font-weight: 800;
                color: var(--text);
                margin: 0 0 0.5rem;
                line-height: 1.2;
                text-align: center;
            }
            .hero-sub {
                font-size: 1rem;
                color: var(--text-muted);
                margin: 0;
                max-width: 34rem;
                line-height: 1.5;
                text-align: center;
            }
            .hero-trust {
                font-size: 0.85rem;
                color: var(--text-soft);
                margin: 0.75rem 0 0;
                max-width: 32rem;
                text-align: center;
            }

            /* Labels */
            .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label,
            div[data-testid="stSelectbox"] label, div[data-testid="stTextInput"] label,
            div[data-testid="stTextArea"] label, div[data-testid="stSlider"] label {
                color: var(--text) !important;
                font-weight: 600 !important;
                font-size: 0.9rem !important;
                opacity: 1 !important;
            }

            .stTextInput > div > div > input,
            .stSelectbox > div > div > select,
            .stTextArea > div > div > textarea {
                background: var(--card) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 12px !important;
                color: #FFFFFF !important;
                font-size: 15px !important;
                padding: 14px 16px !important;
            }
            .stTextInput input::placeholder,
            .stTextArea textarea::placeholder {
                color: #EAEAEA !important;
                opacity: 1 !important;
            }
            .stTextInput > div > div > input:focus,
            .stSelectbox > div > div > select:focus,
            .stTextArea > div > div > textarea:focus {
                border-color: rgba(226, 55, 68, 0.55) !important;
                box-shadow: 0 0 0 2px rgba(226, 55, 68, 0.2) !important;
                outline: none !important;
            }

            .stSlider > div > div > div {
                background: var(--card) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 12px !important;
                padding: 12px 14px !important;
            }

            /* Button Text Visibility Globals */
            .stButton button,
            .stButton button *,
            .stButton button span,
            .stButton button div,
            .stButton button p {
                color: #FFFFFF !important;
                opacity: 1 !important;
                visibility: visible !important;
                -webkit-text-fill-color: #FFFFFF !important;
                mix-blend-mode: normal !important;
            }

            /* All Secondary Buttons (Budget chips) */
            button[kind="secondary"] {
                background: var(--card) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 999px !important;
                font-weight: 600 !important;
                font-size: 0.8rem !important;
                padding: 0.55rem 0.5rem !important;
                text-transform: none !important;
                box-shadow: none !important;
            }
            button[kind="secondary"]:hover {
                border-color: rgba(226, 55, 68, 0.45) !important;
                background: #242b3b !important;
                transform: translateY(-1px);
            }

            /* All Primary Buttons (Main CTA & Selected Budget) */
            button[kind="primary"] {
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-3) 100%) !important;
                border: none !important;
                border-radius: 14px !important;
                font-weight: 700 !important;
                font-size: 1rem !important;
                padding: 0.85rem 1.25rem !important;
                text-transform: none !important;
                box-shadow: 0 8px 24px rgba(226, 55, 68, 0.28) !important;
            }
            button[kind="primary"]:hover {
                box-shadow: 0 10px 28px rgba(226, 55, 68, 0.38) !important;
                transform: translateY(-1px);
            }

            /* Fix budget chips shape when selected (inside columns) */
            [data-testid="stColumn"] button[kind="primary"] {
                border-radius: 999px !important;
                font-size: 0.8rem !important;
                padding: 0.55rem 0.5rem !important;
                font-weight: 600 !important;
                box-shadow: none !important;
            }

            /* Section title for results */
            .results-heading {
                font-size: 1.25rem;
                font-weight: 800;
                color: var(--text);
                margin: 1.25rem 0 0.75rem;
                text-align: center;
            }

            /* Food cards (single injected block) */
            .food-card {
                background: var(--card);
                border: 1px solid var(--card-border);
                border-radius: 16px;
                overflow: hidden;
                margin-bottom: 1.25rem;
                box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
            }
            .food-card__media {
                position: relative;
                height: 160px;
                background: #12151c;
            }
            .food-card__media img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
            }
            .food-card__body { padding: 1rem 1.15rem 1.2rem; }
            .food-card__title {
                font-size: 1.35rem;
                font-weight: 800;
                color: var(--text);
                margin: 0 0 0.65rem;
                line-height: 1.25;
            }
            .food-card__chips {
                display: flex;
                flex-wrap: wrap;
                gap: 0.45rem;
                align-items: center;
                margin-bottom: 0.85rem;
            }
            .chip {
                display: inline-flex;
                align-items: center;
                padding: 0.35rem 0.65rem;
                border-radius: 999px;
                font-size: 0.78rem;
                font-weight: 700;
                border: 1px solid var(--card-border);
                background: rgba(255,255,255,0.04);
                color: var(--text-muted);
            }
            .chip--match {
                background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
                color: #fff;
                border: none;
            }
            .chip--accent { color: var(--text); border-color: rgba(226,55,68,0.35); }
            .food-card__section-title {
                font-size: 0.8rem;
                font-weight: 800;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: var(--accent-2);
                margin: 0.85rem 0 0.35rem;
            }
            .food-card__list {
                margin: 0;
                padding-left: 1.1rem;
                color: var(--text-muted);
                font-size: 0.9rem;
                line-height: 1.55;
            }
            .food-card__list li { margin: 0.2rem 0; }

            .loading-box {
                text-align: center;
                padding: 2rem 1rem;
                color: var(--text-soft);
            }
            .loading-box .spinner {
                width: 44px;
                height: 44px;
                border: 3px solid rgba(255,255,255,0.12);
                border-top-color: var(--accent);
                border-radius: 50%;
                margin: 0 auto 1rem;
                animation: spin 0.85s linear infinite;
            }
            @keyframes spin { to { transform: rotate(360deg); } }

            .empty-box {
                text-align: center;
                padding: 2.5rem 1rem;
                color: var(--text-soft);
                background: var(--card);
                border-radius: 16px;
                border: 1px solid var(--card-border);
            }

            @media (max-width: 600px) {
                .hero-title { font-size: 1.5rem; }
                .food-card__media { height: 140px; }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def render_ai_header(self):
        st.markdown(
            """<div class="hero-wrap">
<p class="hero-kicker">Personalized picks</p>
<h1 class="hero-title">AI Restaurant Recommendation System</h1>
<p class="hero-sub">Discover restaurants tailored to your taste with AI-powered ranking and preference matching.</p>
<p class="hero-trust">Tell us where you are, what you crave, and your budget — we surface spots worth your time.</p>
</div>""",
            unsafe_allow_html=True,
        )

    def render_budget_selector(self) -> str:
        st.markdown("**Budget**")
        options = ["Budget Friendly", "Moderate", "Premium", "Fine Dining"]
        state_key = "polished_budget_choice"
        if state_key not in st.session_state:
            st.session_state[state_key] = "Moderate"

        cols = st.columns(4)
        for i, option in enumerate(options):
            with cols[i]:
                is_sel = st.session_state[state_key] == option
                clicked = st.button(
                    option,
                    key=f"{state_key}_{option}",
                    use_container_width=True,
                    type="primary" if is_sel else "secondary",
                )
                if clicked:
                    st.session_state[state_key] = option
        return str(st.session_state[state_key])

    def get_user_preferences(self) -> Dict[str, Any]:
        preferences: Dict[str, Any] = {}
        st.markdown("**Where & what**")
        col1, col2 = st.columns(2)
        with col1:
            preferences["location"] = st.text_input(
                "City / area",
                placeholder="e.g. Indiranagar, Koramangala",
                help="Neighborhood or area name",
            )
        with col2:
            cuisine_options = [
                "",
                "Italian",
                "Indian",
                "Chinese",
                "Japanese",
                "Mexican",
                "Thai",
                "Continental",
                "American",
                "Korean",
                "French",
            ]
            preferences["cuisine"] = st.selectbox(
                "Cuisine",
                options=cuisine_options,
                index=0,
                help="Optional cuisine filter",
            )

        preferences["budget_label"] = self.render_budget_selector()

        preferences["min_rating"] = st.slider(
            "Minimum rating",
            min_value=1.0,
            max_value=5.0,
            value=4.0,
            step=0.5,
        )
        preferences["additional_constraints"] = st.text_area(
            "Extras (optional)",
            placeholder="Outdoor seating, date night, kid-friendly…",
            help="Anything else we should weigh",
        )
        preferences["top_n"] = st.selectbox(
            "How many picks?",
            options=[3, 5, 8, 10],
            index=1,
        )
        return preferences

    def render_cta_button(self) -> bool:
        return st.button(
            "Find my perfect restaurant",
            key="cta_main",
            type="primary",
            use_container_width=True,
            help="Get recommendations from your AI system",
        )

    def get_recommendations(self, preferences: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """POST /recommend — unchanged contract."""
        try:
            budget_api_value = self._budget_label_to_api_value(str(preferences.get("budget_label", "")))
            payload = {
                "preferences": {
                    "location": preferences.get("location", ""),
                    "cuisine": preferences.get("cuisine", ""),
                    "budget": budget_api_value,
                    "min_rating": preferences.get("min_rating", 4.0),
                    "additional_constraints": preferences.get("additional_constraints", ""),
                    "top_n": preferences.get("top_n", 5),
                },
                "max_recommendations": preferences.get("top_n", 5),
                "response_type": "recommendation",
                "include_explanations": True,
            }
            response = requests.post(
                f"{self.api_base_url}/recommend",
                json=payload,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: {str(e)}")
            return None
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            return None

    def render_recommendation_card(self, recommendation: Dict[str, Any], index: int) -> None:
        """One HTML block per card; all dynamic text escaped — no raw markup leakage."""
        rank = recommendation.get("rank", index)
        name_raw = str(recommendation.get("restaurant_name", "") or "").strip()
        name = html.escape(name_raw or "Restaurant")

        match_score = recommendation.get("match_score")
        match_pct: Optional[str] = None
        if isinstance(match_score, (int, float)):
            match_pct = f"{float(match_score) * 100:.1f}%"

        price_indication = recommendation.get("price_indication")
        best_for = recommendation.get("best_for")
        reasons = [str(r) for r in (recommendation.get("reasons") or []) if r]
        highlights = [str(h) for h in (recommendation.get("highlights") or []) if h]

        parsed_cuisine, parsed_rating = self._parse_highlights_meta(highlights)
        cuisine_chip = recommendation.get("cuisine") or parsed_cuisine
        rating_chip = recommendation.get("rating")
        if rating_chip is None and parsed_rating:
            rating_chip = parsed_rating
        if cuisine_chip is not None:
            cuisine_chip = str(cuisine_chip).strip() or None
        if rating_chip is not None:
            rating_chip = str(rating_chip).strip() or None

        has_body = bool(
            name_raw
            or match_pct
            or price_indication
            or best_for
            or reasons
            or highlights
            or cuisine_chip
            or rating_chip
        )
        if not has_body:
            return

        banner_key = None
        if cuisine_chip:
            banner_key = cuisine_chip.split()[0] if cuisine_chip else None
        elif recommendation.get("cuisine"):
            banner_key = str(recommendation.get("cuisine")).split()[0]
        img_url = self._banner_url_for_cuisine(banner_key)
        alt = html.escape((name_raw or "Restaurant")[:80])

        chips: List[str] = []
        if match_pct:
            chips.append(f'<span class="chip chip--match">{html.escape(match_pct)} match</span>')
        if cuisine_chip:
            chips.append(f'<span class="chip chip--accent">🍽 {html.escape(cuisine_chip)}</span>')
        if price_indication:
            chips.append(f'<span class="chip">{html.escape(str(price_indication))}</span>')
        if rating_chip is not None:
            chips.append(f'<span class="chip">⭐ {html.escape(str(rating_chip))}</span>')
        if best_for:
            chips.append(f'<span class="chip">{html.escape(str(best_for))}</span>')
        chips.append(f'<span class="chip">#{html.escape(str(rank))}</span>')

        reasons_html = ""
        if reasons:
            lis = "".join(f"<li>{html.escape(r)}</li>" for r in reasons)
            reasons_html = f'<p class="food-card__section-title">Why this restaurant?</p><ul class="food-card__list">{lis}</ul>'

        highlights_html = ""
        if highlights:
            lis = "".join(f"<li>{html.escape(h)}</li>" for h in highlights)
            highlights_html = f'<p class="food-card__section-title">Highlights</p><ul class="food-card__list">{lis}</ul>'

        card_html = f"""<article class="food-card">
<div class="food-card__media">
<img src="{html.escape(img_url)}" alt="{alt}" loading="lazy" referrerpolicy="no-referrer" />
</div>
<div class="food-card__body">
<h2 class="food-card__title">{name}</h2>
<div class="food-card__chips">{"".join(chips)}</div>
{reasons_html}
{highlights_html}
</div>
</article>"""
        st.markdown(card_html, unsafe_allow_html=True)

    def render_loading_state(self):
        st.markdown(
            """
            <div class="loading-box">
                <div class="spinner"></div>
                <p><strong>Finding restaurants…</strong></p>
                <p style="font-size:0.9rem;margin:0;">Matching your preferences to the best picks.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_empty_state(self):
        st.markdown(
            """
            <div class="empty-box">
                <p style="font-size:2rem;margin:0 0 0.5rem;">🍽️</p>
                <p><strong>No matches yet</strong></p>
                <p style="font-size:0.9rem;margin:0;">Try a broader area, different cuisine, or relaxed filters.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def run(self):
        self.render_ai_header()
        preferences = self.get_user_preferences()

        if self.render_cta_button():
            self.render_loading_state()
            recommendations = self.get_recommendations(preferences)

            if recommendations:
                st.markdown("---")
                st.markdown('<p class="results-heading">Your picks</p>', unsafe_allow_html=True)
                recs = recommendations.get("recommendations") or []
                if recs:
                    for i, rec in enumerate(recs):
                        self.render_recommendation_card(rec, i + 1)
                else:
                    self.render_empty_state()
                if recommendations.get("summary"):
                    st.markdown("---")
                    st.markdown(f"**Summary** · {recommendations['summary']}")
            else:
                st.error("Could not load recommendations. Check the API and try again.")


if __name__ == "__main__":
    PolishedAIRestaurantApp().run()
