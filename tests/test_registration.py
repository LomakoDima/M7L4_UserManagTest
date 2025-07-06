# test_registration.py
import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users, user_choice, main


@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()

def test_user_choice(monkeypatch):
    """Тест выбора действия пользователем."""
    monkeypatch.setattr('builtins.input', lambda _: '1')
    assert user_choice() == '1'

def test_main_register(monkeypatch):
    """Тест сценария регистрации через main()."""
    from registration import registration
    inputs = iter(['2', 'mainuser', 'main@example.com', 'mainpass'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr(registration, 'display_users', lambda: None)

    registration.main()

    # Проверяем, что пользователь действительно добавлен
    assert authenticate_user('mainuser', 'mainpass') is True

def test_main_auth_success(monkeypatch, capsys):
    """Тест успешной авторизации через main()."""
    from registration import registration
    add_user('mainauth', 'auth@example.com', 'pass123')
    inputs = iter(['1', 'mainauth', 'pass123'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    monkeypatch.setattr(registration, 'display_users', lambda: None)

    main()
    captured = capsys.readouterr()
    assert 'авторизация успешна' in captured.out.lower()

def test_main_invalid_input(monkeypatch, capsys):
    """Тест неверного ввода в main()."""
    from registration import registration
    monkeypatch.setattr('builtins.input', lambda _: 'xyz')
    monkeypatch.setattr(registration, 'display_users', lambda: None)

    main()
    captured = capsys.readouterr()
    assert 'неверный ввод' in captured.out.lower()

def test_add_existing_user(setup_database, connection):
    """Тест добавления пользователя с уже существующим логином."""
    add_user('duplicate', 'dup@example.com', 'pass')
    result = add_user('duplicate', 'another@example.com', 'pass123')
    assert result is False, "Добавление пользователя с существующим логином должно вернуть False"

def test_authenticate_success(setup_database):
    """Тест успешной аутентификации пользователя."""
    add_user('authuser', 'auth@example.com', 'secret')
    assert authenticate_user('authuser', 'secret') is True, "Аутентификация должна быть успешной с верными данными"

def test_authenticate_wrong_password(setup_database):
    """Тест аутентификации с неправильным паролем."""
    add_user('wrongpass', 'wrong@example.com', 'correctpass')
    assert authenticate_user('wrongpass', 'wrongpass') is False, "Аутентификация должна провалиться с неправильным паролем"

def test_authenticate_nonexistent_user(setup_database):
    """Тест аутентификации несуществующего пользователя."""
    assert authenticate_user('ghost', 'nope') is False, "Аутентификация несуществующего пользователя должна вернуть False"

def test_display_users_output(capsys, setup_database):
    """Тест отображения списка пользователей (перехват вывода)."""
    add_user('viewuser', 'view@example.com', '123')
    display_users()
    captured = capsys.readouterr()
    assert "Логин: viewuser" in captured.out
    assert "Электронная почта: view@example.com" in captured.out

def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

# Возможные варианты тестов:
"""
Тест добавления пользователя с существующим логином.
Тест успешной аутентификации пользователя.
Тест аутентификации несуществующего пользователя.
Тест аутентификации пользователя с неправильным паролем.
Тест отображения списка пользователей.
"""