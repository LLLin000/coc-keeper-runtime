"""SCEN-04: Chaos lobby stress test with 5 concurrent users.

Integration tests for concurrent user lobby flow covering:
- 5 concurrent users bind/join/ready without race conditions
- No duplicate members under concurrent load
- All reach SCENE_ROUND_OPEN
- Phase transitions correct under load
"""

from __future__ import annotations

import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

from dm_bot.orchestrator.session_store import SessionStore, SessionPhase


@pytest.fixture
def chaos_store() -> SessionStore:
    return SessionStore()


def _bind_and_join(channel_id: str, user_id: str, store: SessionStore) -> str:
    if user_id == "owner":
        store.bind_campaign(
            campaign_id="chaos-c1",
            channel_id=channel_id,
            guild_id="g1",
            owner_id=user_id,
        )
    else:
        store.join_campaign(channel_id=channel_id, user_id=user_id)
    return user_id


def test_five_concurrent_users_bind_join_ready(chaos_store: SessionStore) -> None:
    """5 concurrent users bind/join/ready without race conditions."""
    store = chaos_store
    channel_id = "chaos-ch1"
    store.bind_campaign(
        campaign_id="chaos-c1",
        channel_id=channel_id,
        guild_id="g1",
        owner_id="owner",
    )
    users = ["p1", "p2", "p3", "p4"]

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(_bind_and_join, channel_id, uid, store) for uid in users
        ]
        results = [f.result() for f in as_completed(futures)]

    session = store.get_by_channel(channel_id)
    assert len(session.member_ids) == 5
    assert len(set(session.member_ids)) == 5

    session.transition_to(SessionPhase.AWAITING_READY)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(session.set_player_ready, uid, True)
            for uid in ["owner"] + users
        ]
        [f.result() for f in as_completed(futures)]

    assert all(session.player_ready.values())


def test_no_duplicate_members_under_concurrent_load(chaos_store: SessionStore) -> None:
    """Run concurrent join 5 times - never any duplicate member_ids."""
    for attempt in range(5):
        store = SessionStore()
        channel_id = f"stress-ch{attempt}"
        store.bind_campaign(
            campaign_id=f"c{attempt}",
            channel_id=channel_id,
            guild_id="g1",
            owner_id="owner",
        )

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(
                    store.join_campaign, channel_id=channel_id, user_id=f"p{i}"
                )
                for i in range(4)
            ]
            [f.result() for f in as_completed(futures)]

        session = store.get_by_channel(channel_id)
        assert len(session.member_ids) == len(set(session.member_ids)), (
            f"Duplicates on attempt {attempt}"
        )


def test_all_reach_scene_round_open(chaos_store: SessionStore) -> None:
    """All 5 users ready → transition to SCENE_ROUND_OPEN."""
    store = chaos_store
    channel_id = "chaos-ch2"
    store.bind_campaign(
        campaign_id="c2", channel_id=channel_id, guild_id="g1", owner_id="owner"
    )
    users = ["p1", "p2", "p3", "p4"]

    for uid in users:
        store.join_campaign(channel_id=channel_id, user_id=uid)

    session = store.get_by_channel(channel_id)
    session.transition_to(SessionPhase.AWAITING_READY)
    all_users = ["owner"] + users

    for uid in all_users:
        session.set_player_ready(uid, True)

    session.admin_started = True
    if session.can_start_session():
        session.transition_to(SessionPhase.SCENE_ROUND_OPEN)

    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN


def test_phase_transitions_correct_under_load(chaos_store: SessionStore) -> None:
    """Phase transitions work correctly under concurrent user load."""
    store = chaos_store
    channel_id = "chaos-ch3"

    store.bind_campaign(
        campaign_id="c3", channel_id=channel_id, guild_id="g1", owner_id="owner"
    )
    users = ["p1", "p2", "p3", "p4"]

    for uid in users:
        store.join_campaign(channel_id=channel_id, user_id=uid)

    session = store.get_by_channel(channel_id)

    all_users = ["owner"] + users
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(session.set_player_ready, uid, True) for uid in all_users
        ]
        [f.result() for f in as_completed(futures)]

    session.admin_started = True
    assert session.can_start_session()

    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN

    session.transition_to(SessionPhase.SCENE_ROUND_RESOLVING)
    assert session.session_phase == SessionPhase.SCENE_ROUND_RESOLVING

    session.transition_to(SessionPhase.SCENE_ROUND_OPEN)
    assert session.session_phase == SessionPhase.SCENE_ROUND_OPEN
