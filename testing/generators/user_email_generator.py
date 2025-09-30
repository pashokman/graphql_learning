from faker import Faker

fake = Faker()


def generate_user_email():
    return fake.email()
