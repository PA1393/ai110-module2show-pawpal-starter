import streamlit as st
from datetime import date

from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session-state bootstrap ────────────────────────────────────────────────────
# Streamlit reruns the whole script on every interaction.
# We store the Owner in st.session_state so it survives across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = None


# ── Sidebar: owner setup ───────────────────────────────────────────────────────
with st.sidebar:
    st.header("👤 Owner Setup")
    owner_name = st.text_input("Your name", value="Jordan")
    owner_email = st.text_input("Email", value="jordan@example.com")
    budget = st.number_input(
        "Daily time budget (min)", min_value=15, max_value=480, value=120, step=15
    )

    if st.button("Save owner", use_container_width=True):
        st.session_state.owner = Owner(
            name=owner_name,
            email=owner_email,
            available_minutes_per_day=int(budget),
        )
        st.success(f"Owner '{owner_name}' saved!")

    if st.session_state.owner:
        o = st.session_state.owner
        st.caption(f"Active: **{o.name}** | Budget: {o.available_minutes_per_day} min")


# ── Guard: require an owner before anything else ───────────────────────────────
if st.session_state.owner is None:
    st.title("🐾 PawPal+")
    st.info("Fill in your name and click **Save owner** in the sidebar to get started.")
    st.stop()

owner: Owner = st.session_state.owner

st.title(f"🐾 PawPal+  —  {owner.name}'s Dashboard")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_pets, tab_tasks, tab_schedule = st.tabs(["🐶 Pets", "📋 Tasks", "📅 Schedule"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Pets
# ══════════════════════════════════════════════════════════════════════════════
with tab_pets:
    st.subheader("Add a pet")

    with st.form("add_pet_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            pet_name = st.text_input("Name", value="Mochi")
        with col2:
            species = st.selectbox("Species", ["dog", "cat", "other"])
        with col3:
            age = st.number_input("Age (years)", min_value=0, max_value=30, value=2)
        with col4:
            breed = st.text_input("Breed", value="unknown")

        submitted = st.form_submit_button("Add pet", use_container_width=True)
        if submitted:
            # Guard: no duplicate names
            existing_names = [p.name for p in owner.get_pets()]
            if pet_name in existing_names:
                st.warning(f"A pet named '{pet_name}' already exists.")
            else:
                owner.add_pet(Pet(name=pet_name, species=species, age=int(age), breed=breed))
                st.success(f"Added {pet_name} the {breed} {species}!")

    st.divider()
    st.subheader("Your pets")

    pets = owner.get_pets()
    if not pets:
        st.info("No pets yet. Add one above.")
    else:
        for pet in pets:
            col_info, col_remove = st.columns([5, 1])
            with col_info:
                st.markdown(
                    f"**{pet.name}** — {pet.breed} {pet.species}, age {pet.age}  "
                    f"| {len(pet.get_tasks())} task(s)"
                )
            with col_remove:
                if st.button("Remove", key=f"remove_pet_{pet.name}"):
                    owner.remove_pet(pet.name)
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Tasks
# ══════════════════════════════════════════════════════════════════════════════
with tab_tasks:
    pets = owner.get_pets()

    if not pets:
        st.info("Add a pet first (see the Pets tab) before adding tasks.")
    else:
        st.subheader("Add a task")

        with st.form("add_task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                target_pet_name = st.selectbox(
                    "Assign to pet", [p.name for p in pets]
                )
                task_title = st.text_input("Task title", value="Morning walk")
                task_type = st.selectbox(
                    "Type",
                    ["walk", "feeding", "medication", "appointment", "grooming", "enrichment"],
                )
            with col2:
                duration = st.number_input(
                    "Duration (min)", min_value=1, max_value=240, value=20
                )
                priority = st.selectbox("Priority", ["high", "medium", "low"])
                pref_hour = st.slider("Preferred start time (hour)", 5, 22, 8)
                preferred_time = f"{pref_hour:02d}:00"
                is_recurring = st.checkbox("Recurring?", value=False)
                recurrence = st.selectbox(
                    "Recurrence", ["daily", "weekly", "as_needed"], disabled=not is_recurring
                )

            submitted = st.form_submit_button("Add task", use_container_width=True)
            if submitted:
                target_pet = next(p for p in pets if p.name == target_pet_name)
                target_pet.add_task(
                    Task(
                        title=task_title,
                        duration_minutes=int(duration),
                        priority=priority,
                        task_type=task_type,
                        is_recurring=is_recurring,
                        recurrence_interval=recurrence if is_recurring else "as_needed",
                        preferred_time=preferred_time,
                    )
                )
                st.success(f"Added '{task_title}' to {target_pet_name}!")

        st.divider()
        st.subheader("Current tasks by pet")

        for pet in pets:
            tasks = pet.get_tasks()
            with st.expander(f"{pet.name}  ({len(tasks)} task(s))", expanded=True):
                if not tasks:
                    st.caption("No tasks yet.")
                else:
                    for task in tasks:
                        col_info, col_done, col_remove = st.columns([5, 1, 1])
                        with col_info:
                            status = "~~" if task.completed else ""
                            st.markdown(
                                f"{status}**{task.title}**{status}  "
                                f"— {task.duration_minutes} min | {task.priority} | {task.task_type}"
                            )
                        with col_done:
                            if not task.completed:
                                if st.button("Done", key=f"done_{pet.name}_{task.title}"):
                                    next_task = task.mark_complete()
                                    if next_task is not None:
                                        pet.add_task(next_task)
                                    st.rerun()
                        with col_remove:
                            if st.button("✕", key=f"del_{pet.name}_{task.title}"):
                                pet.remove_task(task.title)
                                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Schedule
# ══════════════════════════════════════════════════════════════════════════════
with tab_schedule:
    pets = owner.get_pets()

    if not pets:
        st.info("Add at least one pet with tasks before generating a schedule.")
    else:
        col_date, col_time, col_btn = st.columns([2, 2, 1])
        with col_date:
            sched_date = st.date_input("Schedule date", value=date.today())
        with col_time:
            start_hour = st.slider("Start time (hour)", min_value=5, max_value=12, value=8)
            start_time_str = f"{start_hour:02d}:00"
        with col_btn:
            st.write("")  # vertical spacing
            st.write("")
            run = st.button("Generate schedule", use_container_width=True, type="primary")

        if run:
            scheduler = Scheduler(
                owner=owner,
                date=str(sched_date),
                start_time=start_time_str,
            )

            st.divider()
            all_empty = True

            for pet in pets:
                schedule = scheduler.generate_schedule(pet)
                if not schedule:
                    continue
                all_empty = False

                st.subheader(f"🐾 {pet.name}")

                # Table view
                rows = [s.to_dict() for s in schedule]
                st.dataframe(
                    rows,
                    column_order=["start_time", "end_time", "title", "duration_minutes", "priority", "task_type"],
                    hide_index=True,
                    use_container_width=True,
                )

                # Plain-English explanation
                with st.expander("Plan explanation"):
                    st.text(scheduler.explain_plan(schedule))

                # Conflict report
                conflicts = scheduler.detect_conflicts(schedule)
                if conflicts:
                    st.warning(f"{len(conflicts)} conflict(s) detected:")
                    for a, b in conflicts:
                        st.write(f"- **{a.task.title}** overlaps **{b.task.title}**")
                else:
                    st.success("No scheduling conflicts.")

            if all_empty:
                st.warning("No tasks fit within the available time budget for any pet.")
