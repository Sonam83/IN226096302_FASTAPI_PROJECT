# IN226096302_FASTAPI_PROJECT

# **Project Overview**

Movie Ticket Booking System using FastAPI(CineStar Booking API)  is a backend system that simulates a real-world movie ticket booking platform. It allows users to browse movies, book tickets, manage seat availability, and perform advanced operations like search, filtering, sorting, and pagination.

This project demonstrates RESTful API design, data validation, business logic implementation, and multi-step workflows.


# **Features**


- Core Functionalities

- Browse all movies

- View movie details by ID

- Book movie tickets

- Track bookings and revenue

- Manage seat availability

# **Advanced Functionalities**


🔍 Keyword-based search

🔃 Sorting (price, duration, seats, etc.)

📄 Pagination for large datasets

🔗 Combined browsing (search + filter + sort + pagination)

# **Multi-Step Workflow :**


Seat Hold - Confirm Booking - Release Seats
Prevents overbooking and ensures data consistency

# **Concepts Implemented**


🔹 **1. GET APIs**

- Home route (/)

- List all movies (/movies)

- Get movie by ID (/movies/{movie_id})

- Summary endpoint (/movies/summary)

- View all bookings (/bookings)

🔹 **2. POST + Pydantic**

- Request body validation using BaseModel

- Field constraints:

  min_length, gt, le

- Proper error handling for invalid inputs

🔹**3. Helper Functions**

- Reusable logic implemented using:

- find_movie() to fetch movie by ID

- calculate_ticket_cost() to pricing logic with seat types & promo codes

- filter_movies_logic() to filtering with query params

✔ Used Query() parameters

✔ Applied is not None conditions for filtering

🔹**4. CRUD Operations**

- POST - Create movie

- PUT - Update movie

- DELETE - Delete movie

Handled:

✅ 201 Created
❌ 404 Not Found
❌ Duplicate entries
❌ Prevent delete if bookings exist

🔹 **5. Multi-Step Workflow**

- Implemented connected endpoints:

- POST /seat-hold - Hold seats temporarily

- POST /seat-confirm/{hold_id} to Confirm booking

- DELETE /seat-release/{hold_id} to Release held seats

✔ Ensures real-world booking flow

✔ Maintains seat consistency

🔹 **6. Advanced APIs** 

🔍 /movies/search - keyword search

🔃 /movies/sort - sorting

📄 /movies/page - pagination

🔥 /movies/browse - combined endpoint

**✔ Also implemented for bookings:**

- Search

- Sort

- Pagination

# **Tech Stack**


- FastAPI

- Python

- Pydantic

- Uvicorn

▶️**How to Run the Project**


# Install dependencies
pip install fastapi uvicorn

# Run the server
uvicorn main:app --reload

# **API Documentation (Swagger UI)**
Open in browser:

http://127.0.0.1:8000/docs

# **Key Learnings**
- Designing RESTful APIs

- Implementing real-world business logic

- Data validation using Pydantic

- Handling edge cases (availability, duplicates)

- Building scalable API structure

- Multi-step workflow design
