import pytest
from testing.generators.user_email_generator import generate_user_email

pytestmark = pytest.mark.user


def create_and_pare_user_obj(client, query, variables):
    result = client(query, variables)

    assert "errors" not in result, f"GraphQL returned errors: {result.get('errors')}"

    user = result["data"]["createUser"]
    return user


def test_create_user_with_valid_credentials_return_all_fields(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert isinstance(user["id"], int), "id must be an integer"
    assert user["email"] == email
    assert user["isActive"] is True


def test_create_user_with_valid_credentials_return_only_id(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert isinstance(user["id"], int), "id must be an integer"
    assert "email" not in user
    assert "isActive" not in user


def test_create_user_with_valid_credentials_return_only_email(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            email
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert "id" not in user
    assert user["email"] == email
    assert "isActive" not in user


def test_create_user_with_valid_credentials_return_only_isActive(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            isActive
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert "id" not in user
    assert "email" not in user
    assert user["isActive"] == True


def test_create_user_with_valid_credentials_return_id_email(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert isinstance(user["id"], int), "id must be an integer"
    assert user["email"] == email
    assert "isActive" not in user


def test_create_user_with_valid_credentials_return_id_isActive(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            isActive
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert isinstance(user["id"], int), "id must be an integer"
    assert "email" not in user
    assert user["isActive"] == True


def test_create_user_with_valid_credentials_return_email_isActive(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            email
            isActive
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert "id" not in user
    assert user["email"] == email
    assert user["isActive"] == True


def test_create_user_with_valid_credentials_isactive_false_return_all_fields(graphql_client):
    query = """
        mutation CreateUser($email: String!, $isActive: Boolean) {
        createUser(email: $email, isActive: $isActive) {
            id
            email
            isActive
        }
        }
    """
    email = generate_user_email()
    variables = {"email": email, "isActive": False}

    user = create_and_pare_user_obj(graphql_client, query, variables)

    assert isinstance(user["id"], int), "id must be an integer"
    assert user["email"] == email
    assert user["isActive"] == False
