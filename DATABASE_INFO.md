# Database Configuration

## Current Setup: SQLite

The project is currently configured to use **SQLite** database for development.

### SQLite Database

- **Database File**: `db.sqlite3` (in project root)
- **Status**: ✅ Created and migrations applied
- **Size**: ~580KB (will grow as data is added)

### Advantages of SQLite for Development

- ✅ No setup required - works out of the box
- ✅ No separate database server needed
- ✅ Perfect for development and testing
- ✅ Easy to backup (just copy the file)
- ✅ Fast for small to medium datasets

### Switching to PostgreSQL (For Production)

If you want to use PostgreSQL instead:

1. **Uncomment PostgreSQL configuration** in `backend/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
           'NAME': config('DB_NAME', default='hrms_db'),
           'USER': config('DB_USER', default='postgres'),
           'PASSWORD': config('DB_PASSWORD', default='postgres'),
           'HOST': config('DB_HOST', default='localhost'),
           'PORT': config('DB_PORT', default='5432'),
       }
   }
   ```

2. **Comment out SQLite configuration**

3. **Update `.env` file** with PostgreSQL credentials

4. **Create PostgreSQL database**:
   ```bash
   createdb hrms_db
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

### Database Management

#### View Database (SQLite)
```bash
# Using sqlite3 command line
sqlite3 db.sqlite3

# Or use Django shell
python manage.py shell
```

#### Backup Database (SQLite)
```bash
# Simply copy the file
cp db.sqlite3 db.sqlite3.backup
```

#### Reset Database (SQLite)
```bash
# Delete database and recreate
rm db.sqlite3
python manage.py migrate
```

### Current Database Status

✅ **Migrations Applied**: All migrations have been successfully applied
✅ **Database Created**: `db.sqlite3` file exists
✅ **Ready to Use**: Database is ready for development

### Next Steps

1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

2. Access admin panel:
   - URL: http://localhost:8001/admin/
   - Login with superuser credentials

3. Start using the application!
