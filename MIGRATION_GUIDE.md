# Django Shop Migration Guide

This guide will help you successfully move your Django Shop project to a new laptop.

## Prerequisites on New Laptop

Before starting, ensure you have the following installed on your new laptop:

- **Python** (version 3.8 or higher)
- **Git** (for cloning the repository)
- **pip** (Python package manager, usually comes with Python)
- **virtualenv** or **venv** (for creating virtual environments)

---

## Step 1: Backup Your Current Project

On your **old laptop**, ensure everything is saved:

1. **Commit all changes to Git** (if using version control):
   ```bash
   cd "e:\work\year 4 ss1\Python web\djangoShop"
   git add .
   git commit -m "Final commit before migration"
   git push origin main
   ```

2. **Export your database** (if you want to keep existing data):
   ```bash
   cd mywebsite
   python manage.py dumpdata > db_backup.json
   ```
   > [!IMPORTANT]
   > This creates a backup of all your database data. Make sure to commit this file or transfer it separately.

3. **Document your environment variables** (if any):
   - Check for any `.env` files
   - Note any secret keys or API credentials
   - Document your `DEBUG`, `ALLOWED_HOSTS`, and database settings

---

## Step 2: Transfer the Project

Choose one of these methods:

### Method A: Using Git (Recommended)

If your project is on GitHub/GitLab/Bitbucket:
```bash
# On new laptop
git clone <your-repository-url>
cd djangoShop
```

### Method B: Direct File Transfer

If not using Git:
- Copy the entire `djangoShop` folder to a USB drive, cloud storage, or network share
- Transfer to your new laptop

---

## Step 3: Set Up Python Virtual Environment

On your **new laptop**:

1. **Navigate to project directory**:
   ```bash
   cd "path/to/djangoShop"
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

   > [!TIP]
   > If you get an execution policy error on Windows PowerShell, run:
   > ```powershell
   > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   > ```

---

## Step 4: Install Dependencies

1. **Upgrade pip** (recommended):
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install project dependencies**:
   
   If you have a `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
   
   If you don't have a `requirements.txt`, install Django and common dependencies:
   ```bash
   pip install django pillow
   ```

   > [!NOTE]
   > If you didn't have a `requirements.txt` on your old laptop, create one now:
   > ```bash
   > pip freeze > requirements.txt
   > ```

---

## Step 5: Configure Database

1. **Navigate to the Django project**:
   ```bash
   cd mywebsite
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Load backed up data** (if you created `db_backup.json` earlier):
   ```bash
   python manage.py loaddata db_backup.json
   ```

4. **Create a superuser** (if starting fresh):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

---

## Step 6: Collect Static Files

1. **Collect all static files**:
   ```bash
   python manage.py collectstatic
   ```
   
   Type `yes` when prompted.

---

## Step 7: Verify the Installation

1. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

2. **Test in browser**:
   - Open `http://127.0.0.1:8000/` in your browser
   - Check that the homepage loads correctly
   - Test login functionality
   - Verify static files (CSS, images) are loading

3. **Access admin panel**:
   - Go to `http://127.0.0.1:8000/admin/`
   - Log in with your superuser credentials
   - Verify data is present

---

## Step 8: Environment Variables & Settings

1. **Check `settings.py`** for any hardcoded paths or settings:
   - Update `BASE_DIR` if needed (should be dynamic)
   - Verify `ALLOWED_HOSTS` includes `'127.0.0.1'` and `'localhost'`
   - Ensure `DEBUG = True` for development

2. **Create `.env` file** (if you use environment variables):
   - Copy your environment variables from the old laptop
   - Never commit sensitive data to Git

3. **Update database settings** if needed:
   - If using SQLite (default), the database file should transfer automatically
   - If using PostgreSQL/MySQL, update connection settings

---

## Common Issues & Solutions

### Issue: "No module named 'django'"
**Solution**: Make sure your virtual environment is activated and Django is installed:
```bash
pip install django
```

### Issue: Static files not loading
**Solution**: Run collectstatic again:
```bash
python manage.py collectstatic --clear
```

### Issue: Database errors
**Solution**: Delete `db.sqlite3` and run migrations from scratch:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Issue: Permission errors on Windows PowerShell
**Solution**: Change execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "Port already in use"
**Solution**: Use a different port:
```bash
python manage.py runserver 8080
```

---

## Quick Start Checklist

Use this checklist to ensure you haven't missed any steps:

- [ ] Install Python on new laptop
- [ ] Install Git (if using version control)
- [ ] Transfer project files
- [ ] Create and activate virtual environment
- [ ] Install dependencies from `requirements.txt`
- [ ] Run database migrations
- [ ] Create superuser account
- [ ] Collect static files
- [ ] Test the application
- [ ] Verify all features work correctly

---

## Additional Recommendations

1. **Create a `requirements.txt`** if you don't have one:
   ```bash
   pip freeze > requirements.txt
   ```

2. **Use version control** (Git):
   - Keeps your code safe
   - Makes moving between machines easy
   - Tracks all changes

3. **Set up a `.gitignore`** file to exclude:
   - `venv/` - virtual environment
   - `*.pyc` - Python compiled files
   - `__pycache__/` - Python cache
   - `db.sqlite3` - database (optional)
   - `.env` - environment variables
   - `/staticfiles/` - collected static files

4. **Document your setup**:
   - Keep notes on any special configurations
   - Document any environment variables needed
   - Note the Python version you're using

---

## Need Help?

- Check Django documentation: https://docs.djangoproject.com/
- Review error messages carefully - they usually point to the issue
- Ensure all file paths are correct for your new laptop's directory structure

Good luck with your migration! 🚀
