# Studio Booking Management App

## Description

This portfolio project is a comprehensive web application designed for managing studio bookings. It features a robust backend built with Django and showcases my skills in backend development. The application includes functionalities such as user authentication, studio management, booking scheduling, and payment processing.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [License](#license)
- [Contact](#contact)
- [Authors](#authors)

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL
- Django 5.0

### Backend Setup

1. Clone the repository:

    ```bash
    git clone https://github.com/Mathewkoech/studio-booking-management.git
    cd studio-booking-management
    ```

2. Create and activate a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install backend dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory and add the necessary environment variables. For example:

    ```env
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    DEBUG=True
    ```

5. Apply database migrations:

    ```bash
    python manage.py migrate
    ```

6. Run the development server:

    ```bash
    python manage.py runserver
    ```

## Features

- **User Authentication**: Secure login and registration using Django Allauth.
- **Studio Management**: Admin interface for managing studio details, including availability, pricing, and amenities.
- **Booking Scheduling**: Users can view available slots and book studios based on their needs.
- **Payment Processing**: Seamless payment integration for secure transactions.
- **User Dashboard**: Users can view their booking history and manage upcoming reservations.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

If you have any questions or feedback, feel free to reach out to me at [mathewkoech55@gmail.com](mailto:mathewkoech55@gmail.com).

## Authors

- Mathew K. (mathekoech55@gmail.com)
- Debay C. (omolpeter@gmail.com)
