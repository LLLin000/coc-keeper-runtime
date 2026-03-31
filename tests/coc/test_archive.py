"""Tests for archive repository CRUD operations."""

import pytest

from dm_bot.coc.archive import InvestigatorArchiveRepository, InvestigatorArchiveProfile
from dm_bot.characters.models import COCAttributes, COCInvestigatorProfile


class TestArchiveCRUD:
    """Test CRUD operations."""

    @pytest.fixture
    def repo(self):
        """Create fresh repository."""
        return InvestigatorArchiveRepository()

    @pytest.fixture
    def test_profile_data(self):
        """Test profile data."""
        return {
            "user_id": "user1",
            "name": "测试角色",
            "occupation": "医生",
            "age": 35,
            "background": "Test background",
            "portrait_summary": "Test doctor",
            "concept": "Test concept",
            "disposition": "冷静",
            "favored_skills": ["医学", "急救"],
            "generation": {
                "str": 50,
                "con": 50,
                "dex": 50,
                "app": 50,
                "pow": 50,
                "siz": 50,
                "int": 50,
                "edu": 50,
                "luck": 50,
            },
        }

    def test_create_profile(self, repo, test_profile_data):
        """Test profile creation."""
        profile = repo.create_profile(**test_profile_data)

        assert profile.name == "测试角色"
        assert profile.occupation == "医生"
        assert profile.coc.attributes.str == 50

    def test_get_profile(self, repo, test_profile_data):
        """Test profile retrieval."""
        created = repo.create_profile(**test_profile_data)

        retrieved = repo.get_profile("user1", created.profile_id)

        assert retrieved.profile_id == created.profile_id
        assert retrieved.name == created.name

    def test_update_profile(self, repo, test_profile_data):
        """Test profile update."""
        created = repo.create_profile(**test_profile_data)

        updated = repo.update_profile(
            user_id="user1",
            profile_id=created.profile_id,
            name="更新后的名字",
            age=40,
        )

        assert updated.name == "更新后的名字"
        assert updated.age == 40
        assert updated.occupation == "医生"  # Unchanged

    def test_update_read_only_fields(self, repo, test_profile_data):
        """Test that read-only fields cannot be updated."""
        created = repo.create_profile(**test_profile_data)

        with pytest.raises(ValueError, match="read-only"):
            repo.update_profile(
                user_id="user1",
                profile_id=created.profile_id,
                schema_version=99,  # Read-only
            )

    def test_update_coc_stats(self, repo, test_profile_data):
        """Test COC stats update."""
        created = repo.create_profile(**test_profile_data)
        original_san = created.coc.san

        updated = repo.update_coc_stats(
            user_id="user1",
            profile_id=created.profile_id,
            san=original_san + 10,
        )

        assert updated.coc.san == original_san + 10

    def test_update_skills(self, repo, test_profile_data):
        """Test skill update."""
        created = repo.create_profile(**test_profile_data)

        updated = repo.update_skills(
            user_id="user1",
            profile_id=created.profile_id,
            skills={"医学": 60, "急救": 45},
        )

        assert updated.coc.skills["医学"] == 60
        assert updated.coc.skills["急救"] == 45

    def test_list_profiles(self, repo, test_profile_data):
        """Test listing profiles."""
        profile1 = repo.create_profile(**test_profile_data)

        # Archive first before creating second (only one active allowed)
        repo.archive_profile(user_id="user1", profile_id=profile1.profile_id)

        # Create another
        data2 = test_profile_data.copy()
        data2["name"] = "第二个角色"
        repo.create_profile(**data2)

        profiles = repo.list_profiles("user1")

        assert len(profiles) == 2

    def test_delete_profile(self, repo, test_profile_data):
        """Test profile deletion."""
        created = repo.create_profile(**test_profile_data)

        repo.delete_profile(user_id="user1", profile_id=created.profile_id)

        with pytest.raises(KeyError):
            repo.get_profile("user1", created.profile_id)

    def test_archive_profile(self, repo, test_profile_data):
        """Test archiving a profile."""
        created = repo.create_profile(**test_profile_data)

        archived = repo.archive_profile(
            user_id="user1",
            profile_id=created.profile_id,
        )

        assert archived.status == "archived"


class TestArchivePersistence:
    """Test persistence operations."""

    @pytest.fixture
    def repo(self):
        """Create fresh repository."""
        return InvestigatorArchiveRepository()

    def test_export_import_state(self):
        """Test state export and import."""
        repo = InvestigatorArchiveRepository()

        # Create profile
        repo.create_profile(
            user_id="user1",
            name="Test",
            occupation="Doctor",
            age=30,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["医学"],
            generation={
                "str": 50,
                "con": 50,
                "dex": 50,
                "app": 50,
                "pow": 50,
                "siz": 50,
                "int": 50,
                "edu": 50,
                "luck": 50,
            },
        )

        # Export
        state = repo.export_state()

        # Import to new repo
        new_repo = InvestigatorArchiveRepository()
        new_repo.import_state(state)

        # Verify
        profiles = new_repo.list_profiles("user1")
        assert len(profiles) == 1
        assert profiles[0].name == "Test"


class TestArchiveRepositoryWithPersistence:
    """Test archive repository with persistence store."""

    def test_save_and_load_profile(self):
        """Test saving and loading a profile."""
        import uuid
        from dm_bot.persistence.store import PersistenceStore
        from dm_bot.coc.archive import InvestigatorArchiveRepository

        # Use unique shared memory URI to isolate tests
        uri = f"file:mem{uuid.uuid4().hex}?mode=memory&cache=shared"
        store = PersistenceStore(uri)

        # Create repo with persistence
        repo = InvestigatorArchiveRepository(persistence_store=store)

        # Create profile
        profile = repo.create_profile(
            user_id="user1",
            name="Persisted User",
            occupation="Detective",
            age=40,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["侦查"],
            generation={
                "str": 50,
                "con": 50,
                "dex": 50,
                "app": 50,
                "pow": 50,
                "siz": 50,
                "int": 50,
                "edu": 50,
                "luck": 50,
            },
        )

        # Save to persistence
        repo.save_to_persistence("user1", profile.profile_id)

        # Create new repo and load
        new_repo = InvestigatorArchiveRepository(persistence_store=store)
        loaded = new_repo.load_from_persistence("user1")

        assert len(loaded) == 1
        assert loaded[0].name == "Persisted User"

    def test_persist_all(self):
        """Test persisting all profiles."""
        import uuid
        from dm_bot.persistence.store import PersistenceStore
        from dm_bot.coc.archive import InvestigatorArchiveRepository

        # Use unique shared memory URI to isolate tests
        uri = f"file:mem{uuid.uuid4().hex}?mode=memory&cache=shared"
        store = PersistenceStore(uri)

        repo = InvestigatorArchiveRepository(persistence_store=store)

        # Create two profiles (archive first before second for same user)
        profile1 = repo.create_profile(
            user_id="user1",
            name="User One",
            occupation="Doctor",
            age=30,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["医学"],
            generation={
                "str": 50,
                "con": 50,
                "dex": 50,
                "app": 50,
                "pow": 50,
                "siz": 50,
                "int": 50,
                "edu": 50,
                "luck": 50,
            },
        )
        repo.archive_profile(user_id="user1", profile_id=profile1.profile_id)

        repo.create_profile(
            user_id="user2",
            name="User Two",
            occupation="Detective",
            age=35,
            background="Test",
            portrait_summary="Test",
            concept="Test",
            disposition="冷静",
            favored_skills=["侦查"],
            generation={
                "str": 50,
                "con": 50,
                "dex": 50,
                "app": 50,
                "pow": 50,
                "siz": 50,
                "int": 50,
                "edu": 50,
                "luck": 50,
            },
        )

        # Persist all
        repo.persist_all()

        # Verify via store directly
        profiles_user1 = store.load_user_profiles("user1")
        profiles_user2 = store.load_user_profiles("user2")

        assert len(profiles_user1) == 1
        assert len(profiles_user2) == 1
        assert profiles_user1[0]["name"] == "User One"
        assert profiles_user2[0]["name"] == "User Two"
