# OmborxonaCRM

OmborxonaCRM is a warehouse management system built using Django Rest Framework (DRF). This project aims to provide a comprehensive solution for managing warehouse operations, including inventory tracking, order management, and customer relationship management.

## Features

- Inventory Management
- Order Management
- Customer Management
- User Authentication and Authorization
- API Documentation with Swagger
- JWT-based Authentication

## Installation

### Prerequisites

- Python 3.7+
- Django 3.2+
- Django Rest Framework
- PostgreSQL (optional but recommended)

### Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/cbekoder/OmborxonaCRM.git
    cd OmborxonaCRM
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following variables:

    ```plaintext
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=postgres://user:password@localhost:5432/omborxonacrm
    ```

5. **Apply migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

8. **Access the application:**

    Open your browser and go to `http://127.0.0.1:8000`.

## API Documentation

The API documentation is available via Swagger. You can access it at `http://127.0.0.1:8000/`.

## Usage

1. **User Authentication:**

    - Register a new user
    - Obtain JWT token using credentials
    - Use the token for authenticated requests

2. **Manage Inventory:**

    - Add new products
    - Update product details
    - Track inventory levels

3. **Manage Orders:**

    - Create new orders
    - Update order status
    - View order history

4. **Manage Customers:**

    - Add new customers
    - Update customer information
    - View customer interactions

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Django
- Django Rest Framework
- drf-yasg
- djangorestframework-simplejwt

## Contact

For any inquiries, please contact [cbekoder@gmail.com].
