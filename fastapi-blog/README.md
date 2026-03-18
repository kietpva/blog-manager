![][image1]

www.agilityio.com

# FastAPI Practice Plan

## **Mar 11, 2026**

# **OVERVIEW**

This practice project aims to build a RESTful API using FastAPI with PostgreSQL, SQLAlchemy, and Clerk for authentication.

The system provides a user-based blogging platform where:

* Users can create and manage their own posts

* Administrators have full access to manage all posts and users

The project focuses on practicing backend fundamentals including:

* Authentication

* Role-based access control (RBAC)

* Database relationships

* Pagination

* API design

* Unit testing

## **REQUIREMENTS**

The system is a RESTful blogging platform with the following capabilities:

Authentication & Authorization:

* Implement Clerk JWT authentication
* Support Admin and User roles

User Management:

* Users can register and login

* Users have a profile

* Users can update their own profile

* Admin can view all users

* Admin can disable users

Post Management:

* Users can create posts

* Users can update or delete their own posts

* Users can view other users' posts

* Admin can manage all posts

Categories:

* Each post can belong to multiple categories

* Categories are predefined in the database

Pagination:

* Apply pagination for user list and post list

## **RESEARCH RELATED TECHNOLOGIES**

**Clerk Authentication**

Used for authentication and JWT verification.

Research topics:

* JWT verification

* Clerk session tokens

* Extracting clerk\_user\_id from JWT

## **DEVELOPMENT & ESTIMATION**

**EPIC 1 \- Project Setup**

Goal: Initialize the backend environment and core infrastructure.

Task:

* Initialize FastAPI project using uv

* Setup project folder structure

* Configure PostgreSQL database

* Setup SQLAlchemy / SQLModel ORM

* Configure Alembic for database migration

* Setup environment variables using .env

* Integrate Clerk authentication

* Implement JWT verification middleware/dependency

Deliverables:

* Working FastAPI project

* PostgreSQL database connected

* Clerk token verification implemented

**EPIC 2 \- Authentication & Authorization**

Goal: Implement secure authentication and role-based access control.

Features:

* Signup

* Signin

* JWT token verification

* Role-based authorization (Admin / User)

Tasks:

* Integrate Clerk JWT authentication

* Implement authentication dependency

* Implement role-based access control middleware

Deliverables:

* Secure API routes

* Role validation for protected endpoints

**EPIC 3 \- User & Profile Management**

Goal: Implement user management and profile functionality.

Features:

User can:

* Register and login

* View their profile

* Update their profile information

Admin can:

* View user list

* Disable users

Disabled users:

* Cannot login

* Cannot perform any actions

Tasks:

* Create User model

* Create Profile model

* Implement user repository

* Implement profile service

* Implement user APIs

* Implement disable user logic

Deliverables:

* User management APIs

* Profile APIs

**EPIC 4 \- Post Management**

Goal: Implement CRUD operations for posts.

Features:

User can:

* Create posts

* Update their own posts

* Delete their own posts

* View posts from other users

Admin can:

* View all posts

* Update any post

* Delete any post

Tasks:

* Create Post model

* Implement Post repository

* Implement Post service

* Implement CRUD APIs

* Implement ownership validation

* Implement admin override logic

Deliverables:

* Post CRUD APIs

* Ownership validation

**EPIC 5 \- Category System**

Goal: Implement predefined categories for posts.

Features:

* Each post can belong to multiple categories

* Categories are predefined

* Categories are stored and managed in the database

Tasks:

* Create Category model

* Create PostCategory many-to-many relationship table

* Implement migration for predefined categories

* Link categories to posts

Deliverables:

* Category database structure

* Post-category relationship

**EPIC 6 \- Pagination**

Goal: Implement pagination for large datasets.

Apply pagination for:

* Users

* Posts

Tasks:

* Implement pagination utility

* Apply pagination to user list API

* Apply pagination to post list API

Deliverables:

* Pagination query parameters (page, limit)

**EPIC 7 \- Testing & API Documentation**

Goal: Ensure API reliability and documentation.

Tasks:

* Setup Pytest

* Write unit tests for services

* Write tests for authentication logic

* Create Postman collection for API testing

* Verify API documentation using Swagger/OpenAPI

Deliverables:

* Unit tests

* Postman API collection

* Swagger documentation

**Estimation Summary**

| Phase | Task | Estimation |
| :---: | :---: | :---: |
| Project Setup | FastAPI \+ DB \+ Migration | 1.5 days |
| Authentication | Clerk integration | 1 day |
| User Management | Users \+ Profiles | 2 days |
| Post Management | CRUD \+ permissions | 2 days |
| Categories | Relationship \+ migration | 1 day |
| Pagination | Users \+ posts | 1 day |
| Authorization | RBAC | 0.5 days |
| Testing | Pytest | 1.5 days |
| API Testing | Postman | 1.5 days |

Total estimated time: 12 working days

## **DATABASE DESIGN**

**User**

| Field | Type |
| :---: | :---: |
| id | UUID |
| auth\_id | string |
| email | string |
| full_name | string |
| role | enum (admin, user) |
| is\_active | boolean |
| created\_at | datetime |
| updated\_at | datetime |


**Post**

| Field | Type |
| :---: | :---: |
| id | UUID |
| title | string |
| content | text |
| author\_id | UUID |
| created\_at | datetime |
| updated\_at | datetime |

**Category**

| Field | Type |
| :---: | :---: |
| id | UUID |
| name | string |
| description | string |

**Post Category**

| Field | Type |
| :---: | :---: |
| post\_id | UUID |
| category\_id | UUID |

## **API DESIGN**

### **Base URL**

| /api/v1 |
| :---- |

### **Standard Response Format**

**Object Response**

```json
{
  "data": {}
}
```

**Array Response**

```json
{
  "data": []
}
```

**Paginated Response**

```json
{
  "data": [],
  "meta": {
    "pagination": {
      "total": 100,
      "limit": 10,
      "offset": 0,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

### **Error Response Format**

```json
{
  "error": {
    "code": "post_not_found",
    "message": "Post does not exist"
  }
}
```

### **Response Codes**

| Code | Meaning |
| :---: | :---: |
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 405 | Internal server error |

### **User APIs**

**Get Profile**

GET /profile

```json
# Response
# 200 SUCCESS

{
  "data": {
    "id": "uuid",
    "email": "user@gmail.com",
    "role": "user",
    "is_active": true,
    "full_name": "John Doe",
    "created_at": "2026-03-12T10:00:00"
  }
}
```

Response Codes:

* 200 success
* 401 unauthorized

Error Codes:

* unauthorized

**Update Profile**

PATCH /profile

```json
# Request
{
  "full_name": "John Doe"
}
```

```json
# Response
{
  "data": {
    "message": "Profile updated"
  }
}
```

Response Codes:

* 200 success
* 400 invalid\_request
* 401 unauthorized

Error Codes

* invalid\_profile\_data
* unauthorized

### **User(Admin)**

**Get Users**

GET /users?limit=1\&offset=0

```json
# Response
{
  "data": [
    {
      "id": "uuid",
      "email": "user@gmail.com",
      "role": "user",
      "is_active": true,
      "created_at": "2026-03-12T10:00:00"
    }
  ],
  "meta": {
    "pagination": {
      "total": 20,
      "limit": 1,
      "offset": 0,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

Response Codes:

* 200 success
* 401 unauthorized
* 403 forbidden

Error Codes

* unauthorized
* permission\_denied

**Disable User**

PATCH /users/{user\_id}/disable

```json
# Response
{
  "data": {
    "message": "User disabled"
  }
}
```

Response Codes:

* 200 success
* 403 forbidden
* 404 user\_not\_found

Error Codes:

* user\_not\_found
* permission\_denied

### **Post APIs**

**Create Post**

POST /posts

```json
# Request
{
  "title": "FastAPI Tutorial",
  "content": "Learn FastAPI step by step",
  "category_ids": [
    "uuid-category-1",
    "uuid-category-2"
  ]
}
```

```json
# Response
{
  "data": {
    "id": "uuid",
    "title": "FastAPI Tutorial",
    "content": "Learn FastAPI step by step",
    "author_id": "uuid",
    "created_at": "2026-03-12T10:00:00"
  }
}
```

Response Codes:

* 200 created
* 400 invalid\_request
* 401 unauthorized

Error Codes

* invalid\_post\_data
* unauthorized

**Get Posts**

GET /posts?limit=10\&offset=0

```json
# Response
{
  "data": [
    {
      "id": "uuid",
      "title": "FastAPI Tutorial",
      "author": {
        "id": "uuid",
        "email": "user@gmail.com"
      },
      "categories": [
        {
          "id": "uuid",
          "name": "Technology"
        }
      ],
      "created_at": "2026-03-12T10:00:00"
    }
  ],
  "meta": {
    "pagination": {
      "total": 100,
      "limit": 10,
      "offset": 0,
      "hasNext": true,
      "hasPrev": false
    }
  }
}
```

Response Codes:

* 200 success

**Get Post Details**

GET /posts/{post\_id}

```json
# Response
{
  "data": {
    "id": "uuid",
    "title": "FastAPI Tutorial",
    "content": "Full post content",
    "author": {
      "id": "uuid",
      "email": "user@gmail.com"
    },
    "categories": [
      {
        "id": "uuid",
        "name": "Technology"
      }
    ],
    "created_at": "2026-03-12T10:00:00"
  }
}
```

Response Codes

* 200 success
* 404 post\_not\_found

Error Codes

* post\_not\_found

**Update Post**

PUT /posts/{post\_id}

```json
# Request
{
  "title": "Updated title",
  "content": "Updated content",
  "category_ids": [
    "uuid-category-1"
  ]
}
```

```json
# Response
{
  "data": {
    "message": "Post updated"
  }
}
```

Response Codes

* 200 success
* 403 forbidden
* 404 post\_not\_found

Error Codes

* permission\_denied
* post\_not\_found

**Delete Post**

DELETE /posts/{post\_id}

```json
# Response
{
  "data": {
    "message": "Post deleted"
  }
}
```

Response Codes:

* 200 success
* 403 forbidden
* 404 post\_not\_found

ErrorCodes

* permission\_denied
* post\_not\_found

### **Category APIs**

**Get Categories**

GET /categories

```json
# Response
{
  "data": [
    {
      "id": "uuid",
      "name": "Technology",
      "description": "Tech related posts"
    },
    {
      "id": "uuid",
      "name": "Business",
      "description": "Business topics"
    }
  ]
}
```

Response Codes

* 200 success

### **HTTP Status Codes**

| Code | Meaning |
| :---: | :---: |
| 200 | success |
| 201 | created |
| 400 | bad request |
| 401 | unauthorized |
| 403 | forbidden |
| 404 | not found |
| 500 | internal error |

## **TESTING**

Testing methods:

**Unit Testing**

Using Pytest

Test coverage:

* User service

* Post service
  Authentication dependency

* Authorization logic

**API Testing**

Using Postman

Test scenarios:

* Authentication

* User management

* Post CRUD

* Role permissions

* Pagination

[image1]: <data:image/png;base64,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>
