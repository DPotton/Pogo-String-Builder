import os
import sys
import streamlit as st
import pyperclip

st.set_page_config(
    page_title="Pokemon Go Search Builder",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for dark mode styling, thicker buttons & sticky top header
st.markdown("""
<style>
    /* Dark theme alignment for text input fields */
    .stTextInput input {
        background-color: #1e222a !important;
        color: #ffffff !important;
        border: 1px solid #3a3f4d !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus {
        border-color: #ff4b4b !important;
        box-shadow: 0 0 0 1px #ff4b4b !important;
    }

    .stTextInput label {
        color: #e0e0e0 !important;
    }

    /* Thicker, touch-friendly buttons */
    .stButton > button {
        min-height: 3.5rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 0.35rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.15s ease-in-out !important;
    }

    /* Hover effect */
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Make the entire sticky-header container stick to the top on scroll */
    div[data-testid="stVerticalBlock"] > div:has(div.sticky-header-marker) {
        position: sticky;
        top: 2.8rem;
        background-color: var(--background-color, #0e1117);
        z-index: 999;
        padding-top: 0.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(255, 255, 255, 0.1);
    }

    div[data-testid="stExpander"] div[data-testid="stVerticalBlock"] {
        gap: 0.6rem;
    }
</style>
""", unsafe_allow_html=True)

# Master operator definitions (determines concatenation order)
OPERATORS = [
    ("AND (&)", "&"), 
    ("OR (,)", ","), 
    ("NOT (!)", "!"),
    ("Family (+)", "+"), 
    ("Range (-)", "-")
]

# 1. State Initialization
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# Set tracking active toggled operators
if "active_operators" not in st.session_state:
    st.session_state.active_operators = set()

for key, default in [
    ("name_val", ""), ("type_val", ""), ("move_val", ""), 
    ("num_val", ""), ("min_iv", "0"), ("max_iv", "4")
]:
    if key not in st.session_state:
        st.session_state[key] = default

# State modifier helper functions
def add_term(term):
    """Appends selected term followed by all active toggled operators in ordered sequence."""
    if term:
        # Build operator suffix preserving standard defined order (&, ,, !, +, -)
        suffix = "".join([val for _, val in OPERATORS if val in st.session_state.active_operators])
        st.session_state.search_query += f"{term}{suffix}"

def add_iv_stat(stat_type):
    """Generates proper IV range term for Atk/Def/HP based on min/max selection."""
    min_val = st.session_state.min_iv
    max_val = st.session_state.max_iv
    
    # If values are equal, use single number (e.g. 4attack), otherwise range (0-3attack)
    if min_val == max_val:
        iv_term = f"{min_val}{stat_type}"
    else:
        iv_term = f"{min_val}-{max_val}{stat_type}"
        
    add_term(iv_term)

def toggle_operator(op_symbol):
    """Toggles individual operators ON or OFF in the active set."""
    if op_symbol in st.session_state.active_operators:
        st.session_state.active_operators.remove(op_symbol)
    else:
        st.session_state.active_operators.add(op_symbol)

def clear_all():
    st.session_state.search_query = ""

def undo_last():
    if st.session_state.search_query:
        st.session_state.search_query = st.session_state.search_query[:-1]

def copy_to_clipboard():
    """Copies current search query to system clipboard using pyperclip."""
    if st.session_state.search_query:
        pyperclip.copy(st.session_state.search_query)
        st.toast("Copied to clipboard!", icon="📋")
    else:
        st.toast("Search string is empty!", icon="⚠️")

def quit_app():
    """Stops Streamlit script runner and terminates Python backend process."""
    st.toast("Shutting down application...")
    st.stop()
    os._exit(0)

# --- Sidebar for App Controls ---
with st.sidebar:
    st.header("App Controls")
    st.button("Quit App", on_click=quit_app, use_container_width=True, key="btn_quit_sidebar")

# --- App Title Row ---
col_title, col_quit = st.columns([3, 1])
with col_title:
    st.title("Pokemon Go Search Builder")
with col_quit:
    st.button("Quit App", on_click=quit_app, use_container_width=True, key="btn_quit_main")

# --- Sticky Top Container (Search String + Actions) ---
with st.container():
    st.markdown('<div class="sticky-header-marker"></div>', unsafe_allow_html=True)

    # Active Search String Box (Styled for Dark Theme)
    st.text_input(
        "Active Search String",
        key="search_query",
        placeholder="Tap options below or edit string directly..."
    )

    # Action Row: Copy, Clear, and Undo
    col_copy, col_clear, col_undo = st.columns([2, 1, 1])

    with col_copy:
        st.button(
            "Copy to Clipboard", 
            on_click=copy_to_clipboard, 
            type="primary", 
            use_container_width=True, 
            key="btn_copy_pyperclip"
        )

    with col_clear:
        st.button("Clear", on_click=clear_all, use_container_width=True, key="btn_clear_main")
    with col_undo:
        st.button("Undo", on_click=undo_last, use_container_width=True, key="btn_undo_main")

st.markdown("---")

# --- Toggle Operators ---
st.subheader("Operators")
cols_ops = st.columns(3)

for i, (label, val) in enumerate(OPERATORS):
    with cols_ops[i % 3]:
        is_toggled = val in st.session_state.active_operators
        btn_type = "primary" if is_toggled else "secondary"
        display_label = f"✓ {label}" if is_toggled else label
        
        st.button(
            display_label, 
            on_click=toggle_operator, 
            args=(val,), 
            type=btn_type,
            use_container_width=True, 
            key=f"btn_op_{val}"
        )

# --- Touch-Friendly Button Grid Helper ---
def render_button_grid(item_dict_or_list, category_prefix, columns_count=2, prefix="", suffix="", is_dict=False):
    cols = st.columns(columns_count)
    if is_dict:
        items = list(item_dict_or_list.items())
        for i, (label, val) in enumerate(items):
            with cols[i % columns_count]:
                st.button(
                    label, 
                    on_click=add_term, 
                    args=(f"{prefix}{val}{suffix}",), 
                    use_container_width=True,
                    key=f"grid_{category_prefix}_{i}_{val}"
                )
    else:
        for i, val in enumerate(item_dict_or_list):
            with cols[i % columns_count]:
                st.button(
                    str(val).capitalize(), 
                    on_click=add_term, 
                    args=(f"{prefix}{val}{suffix}",), 
                    use_container_width=True,
                    key=f"grid_{category_prefix}_{i}_{val}"
                )

# --- Category Expanders ---
with st.expander("Name / Family", expanded=True):
    st.text_input("Species or Nickname", key="name_val", placeholder="e.g. pikachu")
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.button("Add Name", on_click=lambda: add_term(st.session_state.name_val), use_container_width=True, key="btn_add_name")
    with col_n2:
        st.button("+Family", on_click=lambda: add_term(f"+{st.session_state.name_val}"), use_container_width=True, key="btn_add_family")

with st.expander("Appraisals & IVs"):
    st.caption("Star Ratings")
    render_button_grid(["1*", "2*", "3*", "4*"], "stars", columns_count=2)
    
    st.caption("Individual IV Ranges (0 to 4)")
    c_min, c_max = st.columns(2)
    with c_min:
        st.selectbox("Min IV", ["0", "1", "2", "3", "4"], index=0, key="min_iv")
    with c_max:
        st.selectbox("Max IV", ["0", "1", "2", "3", "4"], index=4, key="max_iv")

    col_iv1, col_iv2, col_iv3 = st.columns(3)
    with col_iv1:
        st.button("Atk", on_click=lambda: add_iv_stat("attack"), use_container_width=True, key="btn_iv_atk")
    with col_iv2:
        st.button("Def", on_click=lambda: add_iv_stat("defense"), use_container_width=True, key="btn_iv_def")
    with col_iv3:
        st.button("HP", on_click=lambda: add_iv_stat("hp"), use_container_width=True, key="btn_iv_hp")

with st.expander("Keywords"):
    keywords = {
        "Shiny": "shiny", "Legendary": "legendary", "Mythical": "mythical",
        "Ultra Beast": "ultra beasts", "Lucky": "lucky", "Traded": "traded",
        "Shadow": "shadow", "Purified": "purified", "Evolve": "evolve",
        "Evolve New": "evolvenew", "Mega Evolve": "megaevolve", "Trade Evolve": "tradeevolve",
        "Gigantamax": "gigantamax", "Dynamax": "dynamax", "Costume": "costume",
        "Defender": "defender", "Hatched": "hatched", "Eggs Only": "eggsonly",
        "Item": "item", "Special Moves": "@special", "Favorite": "favorite",
        "GBL": "gbl", "Snapshot": "snapshot", "Location BG": "locationbackground",
        "Special BG": "specialbackground"
    }
    render_button_grid(keywords, "keywords", columns_count=2, is_dict=True)

with st.expander("Types & Move Counters"):
    st.text_input("Type Name", key="type_val", placeholder="e.g. fire")
    c_t1, c_t2, c_t3 = st.columns(3)
    with c_t1:
        st.button("Type", on_click=lambda: add_term(st.session_state.type_val.lower()), use_container_width=True, key="btn_type_filter")
    with c_t2:
        st.button("Weak (<)", on_click=lambda: add_term(f"<{st.session_state.type_val.lower()}"), use_container_width=True, key="btn_type_weak")
    with c_t3:
        st.button("Counter (>)", on_click=lambda: add_term(f">{st.session_state.type_val.lower()}"), use_container_width=True, key="btn_type_counter")

    st.text_input("Move Name or Type", key="move_val", placeholder="e.g. crunch")
    st.button("Boosted Weather (@weather)", on_click=lambda: add_term("@weather"), use_container_width=True, key="btn_move_weather")
    
    m_cols = st.columns(2)
    with m_cols[0]:
        st.button("Move (@move)", on_click=lambda: add_term(f"@{st.session_state.move_val.lower()}"), use_container_width=True, key="btn_move_any")
    with m_cols[1]:
        st.button("Fast (@1)", on_click=lambda: add_term(f"@1{st.session_state.move_val.lower()}"), use_container_width=True, key="btn_move_fast")
    
    m_cols2 = st.columns(2)
    with m_cols2[0]:
        st.button("Charged 1 (@2)", on_click=lambda: add_term(f"@2{st.session_state.move_val.lower()}"), use_container_width=True, key="btn_move_charge1")
    with m_cols2[1]:
        st.button("Charged 2 (@3)", on_click=lambda: add_term(f"@3{st.session_state.move_val.lower()}"), use_container_width=True, key="btn_move_charge2")

with st.expander("Numerical Ranges"):
    st.caption("Examples: 150, 10-50, -10, 10-")
    st.text_input("Value or Range", key="num_val", placeholder="10-50")
    
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        st.button("CP", on_click=lambda: add_term(f"cp{st.session_state.num_val}"), use_container_width=True, key="btn_num_cp")
        st.button("Age (days)", on_click=lambda: add_term(f"age{st.session_state.num_val}"), use_container_width=True, key="btn_num_age")
        st.button("Distance (km)", on_click=lambda: add_term(f"distance{st.session_state.num_val}"), use_container_width=True, key="btn_num_distance")
    with col_n2:
        st.button("HP", on_click=lambda: add_term(f"hp{st.session_state.num_val}"), use_container_width=True, key="btn_num_hp")
        st.button("Pokedex #", on_click=lambda: add_term(f"{st.session_state.num_val}"), use_container_width=True, key="btn_num_pokedex")
        st.button("Year", on_click=lambda: add_term(f"year{st.session_state.num_val}"), use_container_width=True, key="btn_num_year")

with st.expander("Regions"):
    render_button_grid(
        ["kanto", "johto", "hoenn", "sinnoh", "unova", "alola", "galar", "paldea"],
        "regions",
        columns_count=2
    )

with st.expander("Gender & Size"):
    st.caption("Genders")
    render_button_grid(["male", "female", "genderunknown"], "genders", columns_count=3)
    st.caption("Sizes")
    render_button_grid(["xxs", "xs", "xl", "xxl"], "sizes", columns_count=2)

with st.expander("Raids & Levels"):
    st.caption("Raid Types")
    render_button_grid(["raid", "remoteraid", "megaraid", "exraid", "primalraid"], "raids", columns_count=2)
    
    st.caption("Buddy Levels")
    render_button_grid([f"buddy{i}" for i in range(6)], "buddies", columns_count=3)
    
    st.caption("Mega Levels")
    render_button_grid([f"mega{i}" for i in range(5)], "megas", columns_count=3)