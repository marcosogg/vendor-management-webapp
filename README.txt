# Vendor Management WebApp

## Overview

The Vendor Management WebApp is a comprehensive solution for managing vendor relationships, tracking spend, and assessing risks. It provides a user-friendly interface for procurement teams to efficiently manage their vendor ecosystem.

## Features

- Vendor profile management
- Spend tracking and analysis
- Risk assessment and scoring
- Data import capabilities
- Interactive dashboard with various visualizations
- RESTful API for integration with other systems

## Technology Stack

- Backend: Django 5.0.7
- Frontend: HTML, Tailwind CSS
- Database: PostgreSQL (production), SQLite (development)
- Additional libraries: Chart.js, DataTables

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/vendor-management-webapp.git
   cd vendor-management-webapp
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in the necessary environment variables

5. Run migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Access the application at `http://localhost:8000`

## Testing

To run tests:

```
pytest
```

## Contributing

We welcome contributions to the Vendor Management WebApp! Please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Write tests for your changes
4. Ensure all tests pass and code meets style guidelines
5. Submit a pull request with a clear description of your changes

Please refer to our [Contribution Guidelines](CONTRIBUTING.md) for more detailed information.

## Documentation

- [API Documentation](docs/API.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please file an issue on the GitHub repository or contact our support team at support@vendormanagement.com.