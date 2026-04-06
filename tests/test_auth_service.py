import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from app.services.auth_service import register_user, login
from app.schemas.auth import RegisterRequest, LoginRequest


@pytest.mark.asyncio
async def test_register_duplicate_email():
    db = AsyncMock()
    email_service = MagicMock()

    existing_user = MagicMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)

    db.execute = AsyncMock(return_value=mock_result)

    payload = RegisterRequest(
        email="test@gmail.com",
        username="testuser",
        password="password123",
        role="submitter",
    )

    with pytest.raises(HTTPException) as exc:
        await register_user(db, payload, email_service)

    assert exc.value.status_code == 400
    assert "email" in exc.value.detail.lower()

    db.flush.assert_not_called()
    db.commit.assert_not_called()

    email_service.send_verification_code.assert_not_called()


@pytest.mark.asyncio
async def test_register_duplicate_username():
    db = AsyncMock()
    email_service = MagicMock()

    existing_username = MagicMock()

    mock_no_result = MagicMock()
    mock_no_result.scalar_one_or_none = MagicMock(return_value=None)

    mock_username_result = MagicMock()
    mock_username_result.scalar_one_or_none = MagicMock(return_value=existing_username)

    db.execute = AsyncMock(side_effect=[mock_no_result, mock_username_result])

    payload = RegisterRequest(
        email="test@gmail.com",
        username="testusername",
        password="testpassword",
        role="submitter",
    )

    with pytest.raises(HTTPException) as exc:
        await register_user(db, payload, email_service)

    assert exc.value.status_code == 400
    assert "username" in exc.value.detail.lower()

    db.flush.assert_not_called()
    db.commit.assert_not_called()

    email_service.send_verification_code.assert_not_called()


@pytest.mark.asyncio
async def test_register_user_success():
    db = AsyncMock()
    email_service = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)

    db.execute = AsyncMock(return_value=mock_result)

    payload = RegisterRequest(
        email="test@gmail.com",
        username="username123",
        password="password123",
        role="submitter",
    )

    with patch(
        "app.services.auth_service.create_verification_code",
        new_callable=AsyncMock,
        return_value="123456",
    ):
        result = await register_user(db, payload, email_service)

    assert (
        result["message"] == "Account created. Check your email for a verification code"
    )
    db.flush.assert_called_once()
    db.commit.assert_called_once()
    email_service.send_verification_code.assert_called_once()


@pytest.mark.asyncio
async def test_login_user_unauthorized():
    db = AsyncMock()
    email_service = MagicMock()
    existing_user = MagicMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_user)

    db.execute = AsyncMock(return_value=mock_result)

    payload = LoginRequest(email="test@gmail.com", password="password123")

    with patch("app.services.auth_service.verify_password", return_value=False):
        with patch("app.utils.security.create_access_token") as mock_access:
            with patch("app.utils.security.create_refresh_token") as mock_refresh:
                with pytest.raises(HTTPException) as exc:
                    await login(db, payload, email_service)

    assert exc.value.status_code == 401

    db.commit.assert_not_called()
    mock_access.assert_not_called()
    mock_refresh.assert_not_called()
