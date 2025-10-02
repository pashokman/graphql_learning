# graphql_learning
Here I will be learning how to interact and test GraphQL API.


# Set up and run
1. Create virtual environment:
```
python -m venv venv
```
2. Activate virtual environment:
```
.\venv\Scripts\activate
```
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Run API:
```
uvicorn app.main:app --reload
```
5. To open local API documentation, visit:
```
http://127.0.0.1:8000/graphql
```
6. To run the testing, open new terminal and run the command:
```
pytest
```

# Example queries
1. Get all API data:
```
query {
  allUsers {
    id
    email
    isActive
    houses {
      id
      title
    }
    garages {
      id
      title
    }
    cars {
      id
      model
    }
    driverLicense {
      id
      number
    }
  }
}
```

2. Get all users:
```
query {
  allUsers {
    id
    email
	}
}
```

3. Create new user and get id, email and isActive fields as a result value:
```
mutation {
  createUser(email:"firstuser@mail.com") {
    id
    email
    isActive
  }
}
```

4. Create a new house owned by user created earlier and return new house object with house_id=id, title, owner with id, email fields and list of garages:
```
mutation {
  createHouse(title:"Main House", ownerId: 1) {
    id
    title
    owner {
      id
      email
    }
    garages {
      id
      title
      owner {
        id
        email
      }
    }
  }
}
```

5. Create a new garage owned by user created earlier and related to house created earlier, return new garage object with garage_id=id, title, owner object (with id and email fields), house object (with id and title fields), cars list (with cars objects with id and model fields):
```
mutation {
	createGarage(
    title: "First garage in main house", 
    ownerId: 1, 
    houseId: 1) {
			id
    	title
    	owner {
        id
        email
      }
    	house {
        id
        title
      }
    	cars {
        id
        model
      }
  }
}
```

6. To get all all houses, garages and cars of user with id = 1:
```
query {
  user(id:1){
    email
    houses{
      id
      title
      garages {
        id
        title
        cars {
          id
          model
        }
      }
    }
  }
}
```

7. To get few same type objects we should assign names for each object (like Alex and Bod for user objects):
```
query {
  Alex: user(id: 1){
    id,
    email
  }
  Bob: user(id: 2){
    id,
    email,
    isActive
  }
}
```

8. To change alias of the result object field we should (response will return `user_id: 1`):
```
query {
  Alex: user(id: 1){
    user_id: id,
    email
  }
}
```

9. To get few same type objects with the same fields in compact form we should use fragment:
```
query {
  Alex: user(id: 1){
    ...UserInfo
  }
  Bob: user(id: 2){
		...UserInfo
  }
}

fragment UserInfo on UserType {
  id,
  email,
  isActive
}
```

10. To use a variable we should use `$` sign:
```
query getUserByID ($id: Int!) {
  user (id: $id) {
    email,
    isActive
  }
}
```
We also should assign `id` variable in Variables section:
```
{
  "id": 1
}
```