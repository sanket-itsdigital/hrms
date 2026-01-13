# Server Information

## ✅ Django Server Running on Port 8001

The Django development server has been started on port **8001**.

### Access URLs

- **Admin Panel**: http://localhost:8001/admin/
- **API Swagger Documentation**: http://localhost:8001/swagger/
- **API ReDoc Documentation**: http://localhost:8001/redoc/
- **API JSON Schema**: http://localhost:8001/api/swagger.json

### Server Management

#### Start Server
```bash
# Method 1: Direct command
python manage.py runserver 8001

# Method 2: Using helper script (macOS/Linux)
./runserver.sh

# Method 3: Using helper script (Windows)
runserver.bat
```

#### Stop Server
Press `Ctrl+C` in the terminal where the server is running, or:
```bash
# Find and kill the process
lsof -ti:8001 | xargs kill
# Or
pkill -f "manage.py runserver 8001"
```

#### Check Server Status
```bash
# Check if port 8001 is in use
lsof -i:8001

# Or check process
ps aux | grep "manage.py runserver"
```

### Important Notes

1. **Database Setup Required**: Before the server can fully function, you need to:
   - Set up PostgreSQL database
   - Update `.env` file with database credentials
   - Run migrations: `python manage.py migrate`
   - Create superuser: `python manage.py createsuperuser`

2. **Current Status**: The server is running but may show database connection errors until PostgreSQL is configured.

3. **Default Port**: If you want to use the default port 8000, simply run:
   ```bash
   python manage.py runserver
   ```

### Troubleshooting

#### Port Already in Use
If port 8001 is already in use, you can:
- Use a different port: `python manage.py runserver 8002`
- Kill the process using port 8001: `lsof -ti:8001 | xargs kill`

#### Database Connection Errors
If you see database connection errors:
1. Ensure PostgreSQL is installed and running
2. Create the database: `createdb hrms_db`
3. Update `.env` with correct database credentials
4. Run migrations: `python manage.py migrate`

#### Static Files Not Loading
If static files aren't loading:
```bash
python manage.py collectstatic
```

### Next Steps

1. Set up PostgreSQL database
2. Configure `.env` file with database credentials
3. Run migrations
4. Create superuser
5. Access admin panel at http://localhost:8001/admin/
