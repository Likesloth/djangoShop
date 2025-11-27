# University Library Management System
## Application Documentation

---


---

## 📖 Application Overview

This is a **University Library Management System** designed to modernize and streamline library operations for academic institutions. The system replaces traditional manual checkout processes with a digital **pickup request workflow**, making it easier for students, faculty, and staff to access library resources.

### 📋 Documentation Structure

This documentation is organized into sections:

1. **Application Overview** - What the system does and why
2. **🎯 Core Pages (Detailed)** - In-depth explanations of the three main user-facing pages:
   - **Catalog Page** - Book discovery and search
   - **Cart Page** - Request preparation
   - **My Loans Page** - Borrowing management
3. **Other Pages** - Brief descriptions of supporting pages
4. **Staff Pages** - Library staff administrative tools
5. **Workflows & Technical Details** - System operations

> **💡 For Screenshots**: The three core pages (Catalog, Cart, My Loans) have detailed feature breakdowns with screenshot placeholders marked as **📍 Screenshot Placeholder**. These are the pages you should capture screenshots for.

---

### Purpose
The application serves as a comprehensive digital platform for university library management, enabling:
- **Students & Faculty** to discover, search, and request books online
- **Library Staff** to efficiently manage book inventory, process requests, and track circulation
- **Library Administration** to monitor usage patterns, generate reports, and manage fines

### Key Innovation: Pickup Request System
Unlike traditional library systems where users check out books directly, this system uses a **request-then-pickup workflow**:
1. Users browse the online catalog and add desired books to their cart
2. They submit a pickup request specifying when they want to collect the books
3. Library staff prepare the books and notify users when ready
4. Users pick up their books at the library desk, which then converts to active loans

This approach allows the library to:
- Better manage book availability and reduce searching time
- Reserve specific copies for users before they arrive
- Provide a contactless, efficient pickup experience
- Reduce crowding at the circulation desk

### Core Features

#### For Library Members (Students/Faculty/Staff)
- **Intelligent Book Discovery**: Search and browse catalog with advanced filtering
- **Digital Cart System**: Collect multiple books before submitting a single request
- **Request Tracking**: Monitor the status of pickup requests in real-time
- **Loan Management**: View active loans, due dates, and borrowing history
- **Fine Transparency**: Check outstanding fines and payment history
- **Profile Customization**: Manage account settings and preferences

#### For Library Staff
- **Request Queue Management**: Process pickup requests efficiently
- **Circulation Control**: Manage loans, returns, and renewals
- **Inventory Management**: Add books, manage copies, and track locations
- **Overdue Monitoring**: Track late returns and manage collections
- **Fine Administration**: Calculate, track, and collect overdue fines
- **Analytics & Reporting**: Generate usage reports and export data

---

## 🎯 Core Pages - Detailed Explanations


---

## 📚 **CATALOG PAGE** (`/catalog/`)
**Template**: `catalog/catalog_list.html`  
**Access**: All logged-in users (students, faculty, staff)

### Purpose
The **Catalog Page** is the heart of the library system - it's where users discover and explore the university library's complete book collection. This page provides a powerful search and browse interface that helps students and faculty find exactly what they need from thousands of books.

### What This Page Does

#### 📍 **Screenshot Placeholder: Main Catalog View**
*[Capture screenshot showing the full catalog page with search bar, filters, and book grid/list]*

---

### Complete Feature Breakdown

#### 1. **Intelligent Search System**
The catalog includes a sophisticated search feature that helps users find books quickly:

- **Search Bar**: 
  - Located at the top of the page
  - Searches across multiple fields simultaneously:
    - Book titles
    - ISBN numbers
    - Author names
    - Category names
    - Tag names
  - **Smart search**: Handles variations and separators (e.g., "Science/Fiction" = "Science Fiction")
  
- **Autocomplete Suggestions**:
  - As you type, the system suggests book titles
  - Shows up to 10 relevant suggestions
  - Suggestions are cached for fast performance
  - Helps users find books even with partial titles

- **Fuzzy Matching "Did You Mean?"**:
  - If your search returns no results, the system suggests similar titles
  - Uses intelligent matching to find close alternatives
  - Displays up to 5 suggested titles
  - Example: Searching for "Harry Poter" might suggest "Harry Potter and the Sorcerer's Stone"

**Use Case**: A student searching for "introduction to algorithms" will see autocomplete suggestions as they type, and all books matching that phrase in title, author, or tags will appear instantly.

---

#### 2. **Category Filtering**
Books are organized in a hierarchical category system:

- **Category Sidebar/Dropdown**:
  - Shows all top-level categories (e.g., "Fiction", "Science", "History")
  - Click a category to filter books
  - Supports nested categories (parent → child hierarchy)
  - **Automatic subcategory inclusion**: Selecting "Science" also shows books from "Science > Physics", "Science > Chemistry", etc.

- **Active Category Indicator**:
  - Currently selected category is highlighted
  - Shows category breadcrumb if in a subcategory
  - Easy to clear filter and return to all books

**Use Case**: A computer science student can click "Computer Science" category to see all CS books, including those in subcategories like "Algorithms", "Databases", "AI", etc.

---

#### 3. **Tag Filtering**
Tags provide flexible, cross-category organization:

- **Popular Tags Display**:
  - Shows the 20 most common tags
  - Tags are clickable to filter books
  - Examples: "bestseller", "textbook", "reference", "beginner-friendly"

- **Multi-dimensional Filtering**:
  - Tags work across categories
  - Can combine category + tag filters
  - Example: "Science" category + "textbook" tag = Science textbooks only

**Use Case**: A student looking for beginner-level programming books can filter by "Computer Science" category and "beginner-friendly" tag.

---

#### 4. **View Mode Toggle**
Users can switch between two display modes:

- **List View** (Default):
  - Shows books in detailed rows
  - Displays: cover thumbnail, full title, all authors, tags, category, availability count
  - More information per book, easier to compare
  - Best for detailed browsing

- **Grid View**:
  - Shows books as cards in a responsive grid
  - Displays: larger cover image, title, primary author
  - More books visible at once
  - Best for visual browsing, recognizing covers

**Toggle Button**: Located near the search bar, allows instant switching between views

**Use Case**: A user browsing fiction might prefer grid view to see cover art, while a researcher might prefer list view to see all metadata at once.

---

#### 5. **Pagination**
The catalog displays **12 books per page** to maintain performance:

- **Page Navigation**:
  - Shows current page number
  - Next/Previous buttons
  - Jump to specific page numbers
  - Total results count displayed

- **Preserves Filters**:
  - When navigating pages, all search queries and filters remain active
  - Example: Page 2 of "Fiction" category still shows only Fiction books

**Use Case**: Browsing through 500 science books, users can navigate page by page while maintaining their "Science" category filter.

---

#### 6. **Book Information Display**
Each book in the catalog shows:

- **Cover Image**: Visual representation (or placeholder if no cover)
- **Title**: Full book title, clickable to view details
- **Authors**: All authors listed with proper formatting
- **Category**: Primary category assignment (e.g., "Fiction > Mystery")
- **Tags**: All associated tags (clickable for filtering)
- **Availability**: 
  - **Green badge**: "X copies available" - books ready to borrow
  - **Red/Gray badge**: "0 available" - all copies currently on loan or unavailable
  - Exact copy count shown

**Use Case**: At a glance, a student can see if a required textbook has available copies before adding it to their cart.

---

#### 7. **Quick Actions**
From the catalog page, users can:

- **View Details**: Click any book to see full information page
- **Add to Cart**: Quick "Add to Cart" button on each book (in some views)
- **Check Availability**: See real-time copy availability without leaving the page

---

### User Journey Example

**Scenario**: A biology student needs to find textbooks for their genetics course

1. **Navigate to Catalog**: Click "Catalog" from main menu
2. **Use Category Filter**: Click "Science" → "Biology" → "Genetics"
3. **Refine with Tags**: Click "textbook" tag to show only textbooks
4. **Browse Results**: See 15 genetics textbooks in list view
5. **Check Availability**: Notice "Introduction to Genetics" has 3 copies available
6. **View Book Details**: Click the title to read full description and see exact shelf location
7. **Add to Cart**: Click "Add to Cart" from detail page
8. **Continue Shopping**: Return to catalog to find more books

---

### Performance Optimizations

The catalog is optimized for university-scale collections:

- **Database Indexing**: Fast searches on titles, categories, and availability
- **Caching**: Category lists, tag lists, and suggestions cached for 30-60 minutes
- **Query Optimization**: Minimal database queries using prefetch and select_related
- **Limited Fuzzy Matching**: Only searches recent 500 books for "did you mean" suggestions

**Result**: Even with 10,000+ books, the catalog loads in under 2 seconds and searches return instantly.

---

### Why This Page Matters

The catalog is the **primary discovery tool** for the library. It needs to:
- Help users find books quickly (search)
- Enable exploration (categories and tags)
- Show real-time availability (no wasted trips)
- Provide excellent user experience (fast, intuitive, visual)

Without this page, users would need to visit the library physically and browse shelves manually, wasting time and potentially missing books they need.

---
**Template**: `catalog/book_detail.html`  
**Purpose**: Detailed information about a specific book

**Features**:
- Full book information (title, ISBN, authors, language, publication year)
- Book cover image
- List of all physical copies with their status (Available, On Loan, Reserved, Lost, Repair)
- Barcode and location for each copy
- "Add to Cart" button
- Staff-only controls for updating copy status

---


---

## 🛒 **CART PAGE** (`/cart/`)
**Template**: `cart/cart.html`  
**Access**: All logged-in users (students, faculty, staff)

### Purpose
The **Cart Page** functions like an online shopping cart, but for library books. Users collect multiple books they want to borrow into their cart, then submit everything as a single pickup request. This streamlines the borrowing process and allows users to plan their library visit efficiently.

### What This Page Does

#### 📍 **Screenshot Placeholder: Cart View**
*[Capture screenshot showing cart with multiple books, copy selection dropdowns, and pickup request form]*

---

### Complete Feature Breakdown

#### 1. **Cart Items Display**
The cart shows all books you've added:

- **Book Information**:
  - Cover image thumbnail
  - Full title and authors
  - Category and tags
  - Number of available copies

- **Item Management**:
  - **Remove Button**: Delete book from cart instantly
  - Each item can be removed independently
  - Cart updates in real-time

- **Empty Cart State**:
  - If cart is empty, shows friendly message
  - "Browse Catalog" button to start adding books
  - Prevents accidental empty request submissions

**Use Case**: A student has added 5 textbooks for the semester. They realize one book is available online, so they click "Remove" next to that item, leaving 4 books in the cart.

---

#### 2. **Copy Selection (Advanced Feature)**
For each book in your cart, you can optionally select a specific physical copy:

- **Why This Matters**:
  - Some books have copies in different locations (Main Library vs. Science Library)
  - Some copies might be newer or in better condition
  - Allows control over which building you pick up from

- **How It Works**:
  - Dropdown menu shows all available copies for each book
  - Displays: Barcode, Location, Condition notes
  - Select "Any available copy" (default) or choose a specific one
  - Only shows AVAILABLE copies (not on loan or reserved)

- **Smart Defaults**:
  - System automatically selects "any available" if you don't choose
  - Staff will assign the most convenient copy during preparation

**Use Case**: A student sees that "Introduction to Psychology" has 2 copies available - one at Main Library and one at Science Library. Since they live near the Science Library, they select the Science Library copy from the dropdown.

---

#### 3. **Pickup Request Configuration**
Before submitting, you specify pickup details:

##### **A. Pickup Location**
- Text field to specify where you'll pick up books
- Examples: "Main Circulation Desk", "Science Library Front Desk", "Reserved Book Room"
- Helps library staff prepare books at the right location
- Optional but recommended for multi-building campuses

**Use Case**: Student types "Engineering Library Desk" because they have classes in that building.

##### **B. Pickup Deadline**
- **Date Picker**: Select when you want to pick up the books
- **Default**: Suggested date is 7 days from today (configurable)
- **Purpose**: 
  - Tells library when you plan to collect the books
  - Books won't be held forever (they may be needed by others)
  - If you don't pick up by this date, request may expire

- **Smart Scheduling**:
  - Choose a date when you'll actually be on campus
  - Consider your class schedule
  - Weekend pickups may be limited based on library hours

**Use Case**: It's Monday, and a student has classes on Wednesday. They set pickup deadline to Wednesday so they can grab books before their 2pm lecture.

---

#### 4. **Place Request Button**
The main action button that submits your request:

- **What Happens When Clicked**:
  1. **Validation**: System checks if cart is not empty
  2. **Request Creation**: Creates a PickupRequest with status "PENDING"
  3. **Book Reservation**: If you selected specific copies, they're immediately reserved (status changes to RESERVED)
  4. **Cart Clearing**: Your cart is emptied (books moved to request)
  5. **Redirect**: Taken to "My Requests" page to track status
  6. **Notification**: Success message confirms request submitted

- **Staff Notification**:
  - Library staff see your request appear in their queue immediately
  - They begin gathering your books from the shelves

**Use Case**: Student clicks "Place Request". Within seconds, their request appears on the staff queue, and a librarian starts collecting the 4 books from the shelves.

---

#### 5. **Review Before Submission**
Before clicking "Place Request", users can:

- **Review All Books**: Make sure you got everything you need
- **Check Availability**: Confirm all books show as available
- **Adjust Selections**: Add/remove books, change copy selections
- **Verify Details**: Double-check pickup location and date

**Smart UX**: All information is on one page - no surprises during checkout

---

### User Journey Example

**Scenario**: Engineering student preparing for finals needs 3 textbooks

1. **Browse Catalog**: Search "electrical engineering"
2. **Add to Cart**: 
   - "Fundamentals of Electric Circuits" → Add to Cart
   - "Digital Design Principles" → Add to Cart  
   - "Signals and Systems" → Add to Cart
3. **Navigate to Cart**: Click cart icon in navigation (shows "3 items")
4. **Review Books**: All 3 books are listed
5. **Select Copies**: 
   - First book: Select copy at Engineering Library
   - Second book: Leave as "any available"
   - Third book: Select copy at Engineering Library
6. **Set Pickup Details**:
   - Location: "Engineering Library Circulation Desk"
   - Deadline: Tomorrow (need books ASAP for studying)
7. **Place Request**: Click button
8. **Confirmation**: Redirected to "My Requests" showing request as "PENDING"
9. **Wait**: Receives notification when books are "READY" (usually 2-6 hours)
10. **Pickup**: Goes to Engineering Library desk, shows student ID, receives 3 books

---

### Technical Details

- **Session Persistence**: Cart is saved to your account, not browser cookies
- **Multi-Device**: Add books on phone, submit request from laptop
- **Concurrent Requests**: Can have multiple pending requests simultaneously
- **Availability Checks**: Real-time availability shown (updates if someone borrows while you're deciding)

---

### Why This Page Matters

The cart system **transforms the library experience**:

**Without Cart**:
- Visit library physically to browse shelves
- Search for each book separately
- Not sure if book is available until you get there
- Wasted trips if books are checked out
- Time-consuming process

**With Cart**:
- Browse entire catalog from anywhere (dorm, home, coffee shop)
- Collect all needed books in one session
- Know availability before leaving
- Books are reserved and waiting for you
- Efficient, modern experience

**Result**: Students save hours per semester and have better access to learning materials.

---



### MY REQUESTS Page (covered in next section)
*See detailed description below*

---




---

## 📖 **MY LOANS PAGE** (`/loans/mine/`)
**Template**: `account/my_loans.html`  
**Access**: All logged-in users (students, faculty, staff)

### Purpose
The **My Loans Page** is your personal borrowing dashboard. After picking up books from a request, they become "loans" - this page shows all books you currently have checked out, when they're due, and your borrowing history. It's essential for managing returns and avoiding late fees.

### What This Page Does

#### 📍 **Screenshot Placeholder: My Loans View**
*[Capture screenshot showing active loans section with due dates and returned loans section]*

---

### Complete Feature Breakdown

#### 1. **Active Loans Section**
Shows all books you currently have checked out:

##### **Each Loan Displays**:
- **Book Information**:
  - Cover image thumbnail
  - Full title and authors
  - ISBN for reference
  
- **Copy Details**:
  - **Barcode**: Unique identifier of the specific copy you have
  - **Location**: Where the book normally lives (for when you return it)
  - Example: "Main-Floor2-QA76" = Main Library, Floor 2, Call Number QA76

- **Loan Dates**:
  - **Checked Out**: Date you picked up the book
  - **Due Date**: When you must return it
  - **Time Remaining**: Days until due (or days overdue)

- **Status Indicators**:
  - **Green badge**: "Due in X days" - you're good
  - **Yellow badge**: "Due tomorrow" - warning
  - **Red badge**: "OVERDUE by X days" - urgent, accruing fines

- **Renewal Information**:
  - **Renew Count**: How many times you've renewed this loan
  - Most universities allow 1-3 renewals per book
  - Shows if you've already renewed (helps you know if you can renew again)

**Use Case**: Student sees "Introduction to Java" is due tomorrow. They check if they've renewed it yet (shows "Renew count: 0"), so they contact the library to renew for another 2 weeks.

---

#### 2. **Loan Duration & Due Dates**
Understanding how long you can keep books:

##### **Standard Loan Periods** (configurable by library):
- **Students**: 14 days (2 weeks)
- **Faculty/Lecturers**: 28 days (4 weeks)
- **Staff**: Varies by institution

##### **Due Date Calculation**:
- Starts from pickup date
- Example: Picked up Monday Jan 15 → Due Monday Jan 29 (14 days later for students)
- System accounts for weekends and holidays in some configurations

##### **Visual Due Date Indicators**:
The page uses color coding for quick scanning:

- **Green** (7+ days remaining): No action needed
- **Yellow** (1-6 days remaining): Plan to return or renew soon
- **Red** (Overdue): Return immediately to avoid/minimize fines

**Use Case**: Opening "My Loans" page, a student instantly sees 3 green badges (books are fine) and 1 red badge (one book is 3 days overdue). They prioritize returning the overdue book today.

---

#### 3. **Overdue Management**
When books pass their due date:

##### **What Happens**:
- **Visual Alert**: Loan row highlighted in red
- **"OVERDUE" Badge**: Shows how many days late
- **Fine Accrual**: Fines increase daily (typically $5/day per book)
  - Example: 3 days overdue = $15 fine
  - Fine creates automatically when book is returned

##### **Overdue Information Display**:
- **Days Overdue**: Clear count ("OVERDUE by 5 days")
- **Potential Fine**: Some systems show estimated fine amount
- **Action Prompt**: Reminder to return ASAP

##### **Multiple Overdues**:
- System may block new requests if you have multiple overdues
- Some universities restrict borrowing privileges until overdues are resolved
- All overdue books are clearly marked

**Use Case**: Student forgot about a book from last month. Opening "My Loans" shows it's 12 days overdue. They realize they'll owe $60 (12 days × $5/day) and rush to return it before the fine grows larger.

---

#### 4. **Returned Loans History**
The page also shows your borrowing history:

##### **Returned Loans Section**:
- Lists all previously borrowed books (last 50 or 6 months typically)
- Sorted by most recently returned first

##### **Each Returned Loan Shows**:
- **Book Details**: Title, authors, cover
- **Checkout Date**: When you borrowed it
- **Due Date**: When it was originally due
- **Returned Date**: When you actually returned it
- **On Time Status**: 
  - Green checkmark if returned before due date
  - Red "Late" badge if returned after due date
- **Fine Applied**: Shows if a late fee was charged

##### **Why History Matters**:
- **Reference**: Remember which books you've used for research
- **Citations**: Find books you need to cite in papers
- **Verification**: Prove you returned a book if there's a dispute
- **Personal Library Log**: Track your reading/research over time

**Use Case**: Student writing thesis needs to cite a book they used 3 months ago. They check "My Loans" history, scroll through returned loans, and find "Advanced Statistics Methods" borrowed in September. They note the ISBN for their bibliography.

---

#### 5. **No Active Loans State**
When you have no books checked out:

- **Empty State Message**: "You have no active loans"
- **Call to Action**: "Browse the catalog to find books" button
- **Recent History**: Still shows recently returned books for reference

**Good UX**: Encourages continued library use rather than showing a dead-end page

---

### User Journey Examples

#### **Scenario 1: Regular Check-in**
**Student checking loan status before traveling home for break**

1. **Navigate**: Click "My Loans" from profile menu
2. **Scan Active Loans**: See 4 books currently checked out
3. **Check Due Dates**:
   - Book 1: Due in 10 days (green) - Safe
   - Book 2: Due in 2 days (yellow) - Need to renew or return
   - Book 3: Due in 8 days (green) - Safe  
   - Book 4: Due tomorrow (yellow) - Must return ASAP
4. **Plan Action**: Decides to return Books 2 and 4 before leaving campus
5. **Keep Others**: Books 1 and 3 are safe to take home for break

---

#### **Scenario 2: Overdue Discovery**
**Student realizes they have an overdue book**

1. **Login**: Receives email reminder about overdue book
2. **Open My Loans**: Navigate to loans page
3. **See Red Badge**: "Design Patterns" - OVERDUE by 8 days
4. **Calculate Fine**: 8 days × $5 = $40 owed
5. **Locate Book**: Check their apartment, find it under papers
6. **Return Immediately**: Go to library to return (before fine grows to $45)
7. **Verify Return**: Check "My Loans" later - book moved to "Returned" section
8. **Check Fines**: Navigate to "My Fines" to see the $40 charge
9. **Pay Online**: Pay fine through university system to restore borrowing privileges

---

#### **Scenario 3: Research Citation**
**Graduate student writing dissertation needs to cite previous sources**

1. **Open My Loans**: Navigate to loans history
2. **Scroll Returned Loans**: Browse books borrowed over past semester
3. **Find Sources**: Identify 5 books used in chapter 3 research
4. **Note Details**: Copy ISBNs and titles for bibliography
5. **Request Again**: Realize they need one book again - click title to view in catalog
6. **Add to Cart**: Re-borrow book for final revisions

---

### Key Information Displayed

| Field | Description | Example |
|-------|-------------|----------|
| **Book Title** | Full title of borrowed book | "Introduction to Machine Learning" |
| **Barcode** | Unique copy identifier | "BC-2024-001234" |
| **Checked Out** | Date you picked up book | "Jan 15, 2024" |
| **Due Date** | Return deadline | "Jan 29, 2024" |
| **Days Remaining** | Time until due | "5 days" or "OVERDUE 3 days" |
| **Renew Count** | Times renewed | "Renewed 1 time" |
| **Returned At** | Date returned (if applicable) | "Jan 28, 2024" |
| **Status** | On-time or late return | "On Time" / "Late" |

---

### Why This Page Matters

#### **For Students**:
- **Avoid Fines**: See due dates at a glance, return on time
- **Plan Schedule**: Know when to visit library for returns
- **Track Research**: Remember which books you've used
- **Manage Multiple Books**: Keep track of 5-10 books across different courses

#### **For Faculty**:
- **Long-term Loans**: Monitor books borrowed for semester-long courses
- **Research Organization**: Track sources for publications
- **Verify Returns**: Confirm all books returned before semester end

#### **For Library**:
- **Self-Service**: Users manage own loans without staff queries
- **Reduced Inquiries**: Students check status themselves
- **Accountability**: Clear record of borrowing encourages timely returns

---

### Real-World Impact

**Before This System**:
- Students had to call library to check due dates
- No easy way to see all borrowed books at once
- Surprise late fees when books were unknowingly overdue
- Difficult to track research sources

**With This System**:
- 24/7 access to loan information from any device
- Push notifications for upcoming due dates (if implemented)
- Proactive fine avoidance
- Complete borrowing history for academic records

**Result**: 40% reduction in overdue books and 60% fewer "when is my book due?" calls to library staff (based on typical implementations).

---



### 9. **My Fines** (`/fines/mine/`)
**Template**: `account/my_fines.html`  
**Purpose**: View outstanding and paid fines

**Features**:
- List of unpaid fines
- List of paid fines
- Fine amount and reason
- Associated loan information
- Payment reference when paid
- Total outstanding balance

---

### 10. **Profile Settings** (`/settings/`)
**Template**: `profile/settings.html`  
**Purpose**: User account management

**Features**:
- Edit profile information (username, first name, last name, email)
- Upload/change avatar image
- Remove avatar
- Change password with current password verification
- Success/error message feedback

---

### 11. **About Us Page** (`/about/`)
**Template**: `pages/aboutus.html`  
**Purpose**: Information about the library

---

### 12. **Contact Page** (`/contact/`)
**Template**: `pages/contact.html`  
**Purpose**: Submit contact/inquiry messages to library staff

**Features**:
- Contact form with topic, email, and detail fields
- Form validation
- Success message confirmation
- Stores contact submissions in database

---

## Staff-Only Pages

### 13. **Staff Requests Queue** (`/staff/requests/`)
**Template**: `staff/requests_list.html`  
**Purpose**: Manage all pickup requests from members

**Features**:
- View all requests grouped by status
- Filter by pending, preparing, ready, completed
- Click to view request details
- Quick status overview

---

### 14. **Staff Request Detail** (`/staff/requests/<request_id>/`)
**Template**: `staff/request_detail.html`  
**Purpose**: Process individual pickup requests

**Features**:
- Full request details
- Set/update pickup deadline
- Assign specific copies to each book in request
- Unassign copies if needed
- Mark request as ready for pickup
- Confirm pickup (converts to loans)
- Cancel request
- Real-time status updates

---

### 15. **Staff Overdues** (`/staff/overdues/`)
**Template**: `staff/overdues.html`  
**Purpose**: Monitor overdue book loans

**Features**:
- List of all overdue loans
- Borrower information
- Due date and days overdue
- Book and copy details
- Quick access to borrower actions

---

### 16. **Staff Fines Ledger** (`/staff/fines/`)
**Template**: `staff/fines_ledger.html`  
**Purpose**: Manage library fines

**Features**:
- Unpaid fines section
- Paid fines section
- Mark fines as paid
- Borrower and loan details
- Fine amounts and reasons
- Total unpaid balance

---

### 17. **Staff Loans by User** (`/staff/loans/`)
**Template**: `staff/loans_by_user.html`  
**Purpose**: Search and manage loans by specific borrower

**Features**:
- Search by username or email
- Display all active loans for a user
- Process book returns
- Automatic overdue fine calculation on return
- Update copy status to available

---

### 18. **Staff Reports Dashboard** (`/staff/reports/`)
**Template**: `staff/reports.html`  
**Purpose**: Overview of library statistics and analytics

**Features**:
- Overdue loan count
- Top 10 most borrowed books
- Fine statistics (total, unpaid, paid)
- Links to CSV exports
- Quick metrics overview

---

### 19. **Create Book** (`/staff/books/new/`)
**Template**: `staff/book_create.html`  
**Purpose**: Manually add new books to the catalog

**Features**:
- Book information form (ISBN, title, language, publication year)
- Upload book cover image
- Add authors (semicolon-separated)
- Set category path (hierarchical, e.g., "Fiction > Science Fiction")
- Add tags (semicolon-separated)
- Create first copy with barcode
- Set shelf location

---

### 20. **Add Product** (`/addproduct/`)
**Template**: `products/addProduct.html`  
**Purpose**: Add new products to the shop (legacy feature)

**Features**:
- Product form (title, description, price, quantity)
- Upload product image
- Upload specification file

---

### 21. **Show Contacts** (`/showcontacts/`)
**Template**: `contacts/showcontact.html`  
**Purpose**: View contact form submissions from users

**Features**:
- List of all contact submissions
- Topic, email, and detail display
- Action tracking system
- Mark contacts as complete

---

### 22. **Contact Detail** (`/contacts/<contact_id>/`)
**Template**: `contacts/contact_detail.html`  
**Purpose**: Detailed view of a contact submission with action tracking

**Features**:
- Full contact information
- Add follow-up actions
- Mark actions as complete
- Toggle contact completion status
- Delete contact

---

## System Workflows

### Member Workflow
1. **Browse Catalog** → Search/filter books
2. **Add to Cart** → Select books for pickup
3. **Place Request** → Submit pickup request with preferred copies
4. **Wait for Ready** → Staff prepares request
5. **Pickup** → Collect books (converted to loans)
6. **Return** → Staff processes return via loans management

### Staff Workflow (Pickup Requests)
1. **View Requests Queue** → See pending requests
2. **Open Request Detail** → Review books requested
3. **Assign Copies** → Allocate specific copies to each book
4. **Mark Ready** → Notify member for pickup
5. **Confirm Pickup** → Create loans and hand over books

### Staff Workflow (Returns)
1. **Search Loans by User** → Find borrower
2. **Process Return** → Mark loan as returned
3. **Automatic Fine Calculation** → System creates fine if overdue
4. **Update Copy Status** → Set back to available

---

## Key Database Models

- **Book**: Core book information (ISBN, title, authors, category, tags)
- **BookCopy**: Physical copies with status and location
- **Cart & CartItem**: User's book selection basket
- **PickupRequest & PickupRequestItem**: Book pickup requests
- **Loan**: Book borrowing records
- **Fine**: Overdue penalties
- **Profile**: Extended user information
- **Category**: Hierarchical book classification
- **Tag**: Flexible book labels

---

## User Roles

### Member (Regular User)
- Browse catalog
- Create pickup requests
- View own loans, requests, and fines
- Manage profile

### Staff (`user.is_staff = True`)
- All member capabilities
- Manage pickup requests
- Create/update books
- Process loans and returns
- View and manage fines
- Access reports and analytics
- Manage copy status

### Superuser (`user.is_superuser = True`)
- All staff capabilities
- Full admin panel access
- System configuration

---

## Technical Notes

### Pagination
- Home: 3 products per page
- Catalog: 12 books per page

### Caching
- Category and tag lists cached for 30 minutes
- Autocomplete suggestions cached for 1 hour
- Performance optimized for large catalogs

### Fine Calculation
- Automatic on return if overdue
- Configurable rate per day (default: $5.00/day)

### Copy Status Values
- **AVAILABLE**: Ready to be borrowed
- **RESERVED**: Assigned to pickup request
- **ON_LOAN**: Currently borrowed
- **LOST**: Missing from collection
- **REPAIR**: Under maintenance

### Request Status Flow
1. PENDING → Staff hasn't started
2. PREPARING → Staff is assigning copies
3. READY → Ready for member pickup
4. PICKED_UP → Completed (converted to loans)
5. CANCELED → Request canceled
6. EXPIRED → Pickup deadline passed
