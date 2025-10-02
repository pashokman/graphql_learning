import pytest
from testing.generators.user_email_generator import generate_user_email

pytestmark = pytest.mark.user


# def create_and_pare_user_obj(client, query, variables):
#     result = client(query, variables)

#     assert "errors" not in result, f"GraphQL returned errors: {result.get('errors')}"

#     user = result["data"]["createUser"]
#     return user


def test_create_user_without_mandatory_email_field(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """

    result = graphql_client(query)
    error_message = "Variable '$email' of required type 'String!' was not provided."
    assert error_message == result["errors"][0]["message"]


@pytest.mark.xfail
def test_create_user_with_empty_email_field(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """
    variables = {"email": ""}
    result = graphql_client(query, variables)
    error_message = "Variable '$email' of required type 'String!' can't be empty."
    assert error_message == result["errors"][0]["message"]


@pytest.mark.xfail
def test_create_user_with_invalid_plaintext_email(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """
    variables = {"email": "some_string"}
    result = graphql_client(query, variables)
    error_message = "Variable '$email' of required type 'String!' is invalid."
    assert error_message == result["errors"][0]["message"]


@pytest.mark.xfail
def test_create_user_with_invalid_without_dot_email(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """
    variables = {"email": "test@com"}
    result = graphql_client(query, variables)
    error_message = "Variable '$email' of required type 'String!' is invalid."
    assert error_message == result["errors"][0]["message"]


@pytest.mark.xfail
def test_create_user_with_invalid_without_name_email(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """
    variables = {"email": "@domain.com"}
    result = graphql_client(query, variables)
    error_message = "Variable '$email' of required type 'String!' is invalid."
    assert error_message == result["errors"][0]["message"]


@pytest.mark.xfail
def test_create_user_with_the_same_email_is_forbidden(graphql_client):
    query = """
        mutation CreateUser($email: String!) {
        createUser(email: $email) {
            id
            email
            isActive
        }
        }
    """
    variables = {"email": "myname@domain.com"}
    result1 = graphql_client(query, variables)
    result2 = graphql_client(query, variables)
    error_message = "Email already taken"
    assert error_message == result2["errors"][0]["message"]


def test_create_user_with_isactive_field_none(graphql_client):
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
    variables = {"email": email, "isActive": None}

    result = graphql_client(query, variables)
    error_message = "Argument 'isActive' of non-null type 'Boolean!' must not be null."
    assert error_message == result["errors"][0]["message"]
