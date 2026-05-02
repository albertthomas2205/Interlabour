# Inter Labour - Job Board Website

## 📋 Project Overview

**Inter Labour** is a modern, responsive job board and labor recruitment platform designed to connect job seekers, employers, and candidates. The platform facilitates job listings, candidate profiles, employer profiles, and services related to recruitment and employment.

**Status:** Frontend-only static website (HTML/CSS/JavaScript)  
**Version:** 1.0  
**Last Updated:** April 2026

---

## 🎯 Project Description

Inter Labour is a job portal website built using HTML, CSS, and JavaScript with Bootstrap framework. It provides a comprehensive job searching and recruitment experience with multiple layout options and comprehensive pages.

**Primary Purpose:** A job board platform for:
- Job seekers browsing and applying for jobs
- Employers posting job listings and viewing candidates
- Candidates showcasing their profiles
- Information about services and pricing

---

## ✅ Currently Implemented Features

### 1. **Core Pages & Navigation**
- ✅ **Homepage** (index.html)
  - Hero section with search functionality
  - Featured jobs carousel
  - Why choose us section
  - Service overview
  - Company stats/counter
  - Brand logos section

- ✅ **About Us Page** (page-about.html)
  - Company information
  - Mission statement
  - Team overview
  - Company benefits/highlights

- ✅ **Services Page** (page-service.html)
  - Service descriptions
  - Service categories
  - Benefits and features

- ✅ **Contact Page** (page-contact.html)
  - Contact form
  - Leaflet map integration for location
  - Contact information display

- ✅ **Responsive Header/Navigation**
  - Sticky header that follows scroll
  - Desktop navigation menu
  - Mobile hamburger menu with slide-out navigation
  - Mobile search functionality

### 2. **Job Listings & Browsing**
- ✅ Job Grid View (multiple layouts: job-grid.html, job-grid-2.html)
- ✅ Job List View (job-list.html)
- ✅ Job Single Pages (job-single.html, job-single-2.html, job-single-3.html)
  - Multiple job detail page layouts
  - Job description, requirements, qualifications
  - Apply button functionality

### 3. **Employer Management**
- ✅ Employers Grid View (employers-grid.html, employers-grid-2.html)
- ✅ Employers List View (employers-list.html)
- ✅ Employer Single Pages (employers-single.html, employers-single-2.html)
  - Employer profiles
  - Company information
  - Posted jobs list

### 4. **Candidate Management**
- ✅ Candidates Grid View (candidates-grid.html, candidates-grid-2.html)
- ✅ Candidates List View (candidates-list.html)
- ✅ Candidate Single Pages (candidates-single.html, candidates-single-2.html)
  - Candidate profiles
  - Portfolio display
  - Skills showcase

### 5. **Blog Section**
- ✅ Blog Grid View (blog-grid.html, blog-grid-2.html with sidebar)
- ✅ Blog List View (blog-list.html)
- ✅ Blog Single Pages (blog-single.html, blog-single-2.html)
  - Articles/blog posts
  - Blog navigation
  - Related posts section

### 6. **Additional Pages**
- ✅ Pricing Page (page-pricing.html)
  - Pricing plans display
  - Plan features
  - CTA buttons

- ✅ FAQs Page (pages-faqs.html)
  - Frequently asked questions
  - Collapsible accordion

### 7. **Frontend Functionality**
- ✅ **Responsive Design**
  - Mobile-first approach
  - Bootstrap grid system
  - Mobile menu toggle
  - Touch-friendly interface

- ✅ **Interactive Elements**
  - Smooth scroll animations (WOW.js)
  - Sticky sidebar functionality
  - Image gallery/Isotope masonry layout
  - Magnific Popup for image lightbox
  - Select2 dropdown enhancement

- ✅ **Performance Features**
  - Page preloader animation
  - Scroll-to-top button
  - Sticky header on scroll
  - Smooth easing animations
  - Counter animation for statistics

- ✅ **UI/UX Enhancements**
  - Modern color scheme and typography
  - Consistent branding with logo
  - Icon system (Uicons)
  - Bootstrap styling with custom CSS
  - Swiper carousel for featured items

### 8. **Asset Libraries & Plugins**
- ✅ jQuery 3.6.0
- ✅ Bootstrap Bundle (responsive framework)
- ✅ Swiper Bundle (carousel/slider)
- ✅ Magnific Popup (lightbox)
- ✅ Select2 (enhanced dropdown)
- ✅ Perfect Scrollbar (custom scrollbar)
- ✅ Leaflet (mapping)
- ✅ WOW.js (scroll animations)
- ✅ CountUp.js (number animations)
- ✅ Isotope (masonry layout)

---

## 🚀 Features to Be Added/Updated

### Priority 1: Essential Features (High Priority)
1. **Backend Development**
   - Create REST API (Node.js/Express, Django, or similar)
   - Database design (PostgreSQL/MySQL)
   - User authentication & authorization
   - Job posting/management system
   - Job application tracking
   - User profile management

2. **User Authentication**
   - User registration system
   - Login/Logout functionality
   - Role-based access (Job Seeker, Employer, Admin)
   - Password reset functionality
   - Email verification
   - Remember me functionality

3. **Job Posting System**
   - Admin can post jobs (backend form)
   - Job editing and deletion
   - Job status management (active, closed, archived)
   - Auto-expiry for old jobs
   - Featured job promotion

4. **Job Application System**
   - Apply button fully functional
   - Application tracking
   - Application status updates
   - Resume upload with application
   - Interview scheduling

5. **User Dashboard**
   - Job Seeker Dashboard: Applied jobs, saved jobs, profile
   - Employer Dashboard: Posted jobs, applications, analytics
   - Admin Dashboard: User management, job moderation

### Priority 2: Enhanced Features (Medium Priority)
6. **Advanced Search & Filtering**
   - Filter by location
   - Filter by job category
   - Filter by salary range
   - Search history/saved searches
   - Advanced search filters

7. **User Profile Features**
   - Complete profile setup
   - Resume/CV upload
   - Skills endorsement
   - Portfolio links
   - Work experience timeline
   - Education history

8. **Notifications & Messaging**
   - Email notifications for new jobs
   - In-app notifications
   - Message system between users
   - Application status notifications
   - Job saved/applied alerts

9. **Admin Panel**
   - User management
   - Job moderation
   - Report management
   - Analytics dashboard
   - Content management

10. **Payment Integration** (if applicable)
    - Stripe/PayPal integration
    - Subscription plans
    - Premium job posting
    - Invoice generation

### Priority 3: Nice-to-Have Features (Low Priority)
11. **SEO Optimization**
    - Meta tags for each page
    - Schema markup for jobs
    - Sitemap generation
    - robots.txt optimization
    - URL optimization

12. **Social Features**
    - Social login (Google, LinkedIn, Facebook)
    - Social sharing of job posts
    - Comments on blog/jobs
    - User recommendations

13. **Analytics & Reporting**
    - User analytics
    - Job search analytics
    - Application funnel analysis
    - Export reports to CSV/PDF

14. **Mobile App** (Later Phase)
    - React Native or Flutter mobile app
    - Push notifications
    - Offline functionality
    - Social media integration

15. **Additional Pages**
    - Terms of Service
    - Privacy Policy
    - Cookie Policy
    - Sitemap page

---

## 📁 Project Structure

```
Inter Labour/
├── index.html                          # Root homepage (simplified version)
├── job-list.html                       # Job listings page
├── job-single.html                     # Job detail page
├── page-about.html                     # About page
├── page-contact.html                   # Contact page
├── page-service.html                   # Services page
│
├── pages/                              # Extended pages with more layouts
│   ├── blog-grid.html                  # Blog grid layout
│   ├── blog-grid-2.html                # Blog grid with sidebar
│   ├── blog-list.html                  # Blog list layout
│   ├── blog-single.html                # Blog post detail
│   ├── blog-single-2.html              # Alternative blog layout
│   ├── candidates-grid.html            # Candidate grid
│   ├── candidates-grid-2.html          # Alternative candidate grid
│   ├── candidates-list.html            # Candidate list
│   ├── candidates-single.html          # Candidate profile
│   ├── candidates-single-2.html        # Alternative candidate profile
│   ├── employers-grid.html             # Employer grid
│   ├── employers-grid-2.html           # Alternative employer grid
│   ├── employers-list.html             # Employer list
│   ├── employers-single.html           # Employer profile
│   ├── employers-single-2.html         # Alternative employer profile
│   ├── index.html                      # Full homepage with hero slider
│   ├── index-3.html                    # Alternative homepage
│   ├── job-grid.html                   # Job grid layout
│   ├── job-grid-2.html                 # Alternative job grid
│   ├── job-list.html                   # Job list layout
│   ├── job-single.html                 # Job detail layout 1
│   ├── job-single-2.html               # Job detail layout 2
│   ├── job-single-3.html               # Job detail layout 3
│   ├── page-about.html                 # About page
│   ├── page-contact.html               # Contact page
│   ├── page-pricing.html               # Pricing page
│   ├── page-service.html               # Services page
│   └── pages-faqs.html                 # FAQ page
│
├── assets/
│   ├── css/
│   │   ├── main.css@v=1.0.css          # Main stylesheet
│   │   ├── plugins/                    # Plugin stylesheets
│   │   │   ├── animate.min.css
│   │   │   ├── magnific-popup.css
│   │   │   ├── perfect-scrollbar.css
│   │   │   ├── select2.min.css
│   │   │   └── swiper-bundle.min.css
│   │   └── vendors/                    # Vendor stylesheets
│   │       ├── bootstrap.min.css
│   │       ├── normalize.css
│   │       └── uicons-regular-rounded.css
│   │
│   ├── js/
│   │   ├── main.js@v=1.0               # Main JavaScript file
│   │   ├── noUISlider.js               # Slider utility
│   │   ├── slider.js                   # Custom slider setup
│   │   ├── plugins/                    # JavaScript plugins
│   │   │   ├── counterup.js
│   │   │   ├── isotope.js
│   │   │   ├── leaflet.js
│   │   │   ├── magnific-popup.js
│   │   │   ├── perfect-scrollbar.min.js
│   │   │   ├── scrollup.js
│   │   │   ├── select2.min.js
│   │   │   ├── swiper-bundle.min.js
│   │   │   ├── waypoints.js
│   │   │   └── wow.js
│   │   └── vendor/                     # Vendor JavaScript
│   │       ├── bootstrap.bundle.min.js
│   │       ├── jquery-3.6.0.min.js
│   │       ├── jquery-migrate-3.3.0.min.js
│   │       └── modernizr-3.6.0.min.js
│   │
│   ├── fonts/
│   │   └── uicons/                     # Icon fonts
│   │
│   └── imgs/
│       ├── avatar/                     # User avatars
│       ├── banner/                     # Banner images
│       ├── blog/                       # Blog post images
│       ├── jobs/
│       │   └── logos/                  # Company logos
│       ├── page/                       # Page-specific images
│       │   ├── about/
│       │   ├── candidates/
│       │   ├── employers/
│       │   ├── faqs/
│       │   ├── homepage3/
│       │   ├── job/
│       │   ├── job-single/
│       │   └── services/
│       ├── slider/                     # Slider images
│       │   ├── logo/
│       │   └── swiper/
│       └── theme/                      # Theme assets
│           ├── icons/
│           ├── SVG/
│           └── favicon.svg
│
└── __MACOSX/                           # macOS backup directory (can be deleted)
```

---

## 🛠️ Technologies Used

### Frontend Stack
- **HTML5** - Semantic markup
- **CSS3** - Modern styling
- **JavaScript (jQuery)** - Interactive functionality
- **Bootstrap 5** - Responsive framework
- **Responsive Design** - Mobile-first approach

### JavaScript Libraries & Plugins
- jQuery 3.6.0
- Swiper Bundle - Carousel/slider functionality
- Magnific Popup - Image lightbox
- Select2 - Enhanced dropdown menus
- Perfect Scrollbar - Custom scrollbar
- WOW.js - Scroll animations
- CountUp.js - Number counter animations
- Isotope - Masonry grid layout
- Leaflet - Interactive maps
- Animate.css - CSS animations

### Design & Icons
- Uicons (UI Connector Icons)
- Bootstrap Icons
- Custom SVG graphics

---

## 💻 How to Run the Project

### Option 1: Direct Browser Navigation (Simplest)
1. Navigate to the project folder: `c:\Users\alber\Desktop\freelance\Inter Labour 2\Inter Labour`
2. Open any `.html` file directly in your web browser by double-clicking
3. Click through the pages using the navigation menu

### Option 2: Local Web Server (Recommended)

#### Using Python (if installed):
```bash
# Navigate to the project directory
cd "c:\Users\alber\Desktop\freelance\Inter Labour 2\Inter Labour"

# Python 3.x
python -m http.server 8000

# Python 2.x (if using older version)
python -m SimpleHTTPServer 8000

# Then open browser: http://localhost:8000
```

#### Using Node.js (if installed):
```bash
# Install http-server globally (one time)
npm install -g http-server

# Navigate to project directory
cd "c:\Users\alber\Desktop\freelance\Inter Labour 2\Inter Labour"

# Start server
http-server

# View at http://localhost:8080 (or shown in terminal)
```

#### Using VS Code Live Server Extension:
1. Install "Live Server" extension in VS Code
2. Right-click on index.html
3. Select "Open with Live Server"
4. Opens automatically in browser

### Option 3: GitHub Pages (For Online Hosting)
1. Upload the project to GitHub
2. Enable GitHub Pages in repository settings
3. Access via `https://username.github.io/repository-name`

---

## 🎮 User Guide

### Navigation
- **Header Menu**: Click menu items to navigate between pages
- **Mobile Menu**: Click hamburger icon (☰) on mobile devices
- **Scroll to Top**: Click the up arrow icon in bottom-right corner

### Browsing Features
- **Search**: Use search bar in header to find jobs
- **Filters**: Use dropdown filters to narrow down results
- **Grid/List View**: Toggle between different layout views
- **Job Details**: Click on job card to view full details

### Current Limitations (Static Site)
- ❌ Login/Registration - Not functional yet
- ❌ Job Application - Apply buttons don't submit
- ❌ Resume Upload - Not functional
- ❌ Contact Form - Not connected to backend
- ❌ Dynamic Content - All content is hardcoded

---

## 📊 Page Map & Routes

### Main Navigation Structure
```
Home (index.html)
├── About (page-about.html)
├── Services (page-service.html)
├── Jobs (job-list.html)
│   ├── Job Grid (pages/job-grid.html)
│   ├── Job Grid 2 (pages/job-grid-2.html)
│   ├── Job List (pages/job-list.html)
│   ├── Job Details 1 (pages/job-single.html)
│   ├── Job Details 2 (pages/job-single-2.html)
│   └── Job Details 3 (pages/job-single-3.html)
├── Employers (pages/employers-grid.html)
│   ├── Grid View (pages/employers-grid.html)
│   ├── Grid View 2 (pages/employers-grid-2.html)
│   ├── List View (pages/employers-list.html)
│   ├── Profile 1 (pages/employers-single.html)
│   └── Profile 2 (pages/employers-single-2.html)
├── Candidates (pages/candidates-grid.html)
│   ├── Grid View (pages/candidates-grid.html)
│   ├── Grid View 2 (pages/candidates-grid-2.html)
│   ├── List View (pages/candidates-list.html)
│   ├── Profile 1 (pages/candidates-single.html)
│   └── Profile 2 (pages/candidates-single-2.html)
├── Blog (pages/blog-grid.html)
│   ├── Grid View (pages/blog-grid.html)
│   ├── Grid w/ Sidebar (pages/blog-grid-2.html)
│   ├── List View (pages/blog-list.html)
│   ├── Post 1 (pages/blog-single.html)
│   └── Post 2 (pages/blog-single-2.html)
├── Pricing (pages/page-pricing.html)
├── FAQs (pages/pages-faqs.html)
└── Contact (page-contact.html)
```

---

## 🔄 Next Steps & Development Roadmap

### Immediate Next Steps (Week 1-2)
1. [ ] Set up version control (Git)
   - Initialize git repository
   - Create .gitignore file
   - Initial commit of current state

2. [ ] Clean up project structure
   - Remove `__MACOSX` directory
   - Standardize file naming
   - Organize assets better
   - Create minified versions of CSS/JS

3. [ ] Documentation
   - Complete branding documentation
   - Create content guidelines
   - Document color scheme and typography

### Short-term Development (Month 1-2)
4. [ ] Backend Setup
   - Choose framework (Node.js + Express, Python + Django, etc.)
   - Set up database (PostgreSQL recommended)
   - Create project structure for backend

5. [ ] User Authentication
   - User registration endpoint
   - Login/logout functionality
   - JWT or session-based auth
   - Password hashing and security

6. [ ] Database Schema Design
   - Users table (seekers, employers, admin)
   - Jobs table
   - Applications table
   - Candidates profile table
   - Blog posts table

7. [ ] API Development
   - Job CRUD endpoints
   - User CRUD endpoints
   - Application endpoints
   - Authentication endpoints

### Medium-term Development (Month 3-4)
8. [ ] Frontend Integration
   - Connect HTML forms to API
   - Implement login/registration page
   - Create user dashboard
   - Remove hardcoded data

9. [ ] Admin Panel
   - User management
   - Job moderation
   - Analytics dashboard
   - Content management

10. [ ] Advanced Features
    - Email notifications
    - Search optimization
    - Wishlist/saved jobs
    - User ratings/reviews

### Long-term Development (Month 5+)
11. [ ] Mobile App
    - React Native app
    - Push notifications
    - Offline support

12. [ ] Payment System
    - Subscription plans
    - Payment gateway integration
    - Invoice generation

13. [ ] SEO & Performance
    - SEO optimization
    - Performance tuning
    - Caching strategies

14. [ ] Deployment
    - Choose hosting (AWS, Digital Ocean, Heroku)
    - Set up CI/CD pipeline
    - Configure domain
    - Set up SSL certificate

---

## 📋 Development Recommendations

### Best Practices to Follow
1. **Version Control**
   - Use Git for version management
   - Create meaningful commit messages
   - Use branches for features

2. **Code Organization**
   - Separate concerns (HTML, CSS, JS)
   - Use modular JavaScript
   - Keep CSS organized with comments

3. **Security**
   - Implement input validation
   - Use HTTPS
   - Sanitize user inputs
   - Implement rate limiting
   - Use environment variables for sensitive data

4. **Performance**
   - Minify CSS and JavaScript
   - Optimize images
   - Implement lazy loading
   - Use CDN for static assets
   - Implement caching

5. **Testing**
   - Unit tests for functions
   - Integration tests for API
   - End-to-end testing
   - Cross-browser testing

6. **Documentation**
   - Keep README updated
   - Document API endpoints
   - Add code comments
   - Create developer guide

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue: Page won't load**
- Solution: Make sure you're using a local server (not file://)
- Check browser console for errors (F12)

**Issue: Styling broken**
- Solution: Check that all CSS files are loaded in browser Network tab
- Clear browser cache (Ctrl+Shift+Delete)

**Issue: JavaScript not working**
- Solution: Check that jQuery and Bootstrap are loaded before custom scripts
- Check browser console for JavaScript errors

**Issue: Images not showing**
- Solution: Verify image paths are correct
- Check that image files exist in assets/imgs folder

---

## 📝 File Modification Notes

- **CSS Files:** Modify `assets/css/main.css@v=1.0.css` for styling
- **JavaScript:** Modify `assets/js/main.js@v=1.0` for interactivity
- **HTML Pages:** Modify individual `.html` files for content changes
- **Images:** Replace images in `assets/imgs/` folders

---

## 🔐 Security Considerations

This is currently a **static website** with no backend security concerns. When adding backend features:
- Never store passwords in plain text
- Implement CSRF protection
- Use HTTPS only
- Sanitize all user inputs
- Implement proper authentication
- Set proper CORS headers
- Use parameterized queries (prevent SQL injection)

---

## 📊 Performance Metrics

Current optimizations:
- ✅ Responsive design reduces data transfer
- ✅ Minified plugin files
- ✅ CSS bundled in main file
- ✅ jQuery-based for browser compatibility

Potential improvements:
- [ ] Implement lazy loading for images
- [ ] Minify custom CSS/JS
- [ ] Use WebP image format
- [ ] Implement service workers (PWA)
- [ ] Use modern JavaScript framework

---

## 📄 License & Credits

**Project:** Inter Labour Job Board  
**Created:** 2026  
**Template Based On:** JobHub HTML Template  
**License:** [To be defined]

### Credits
- Bootstrap Framework
- jQuery
- Swiper Carousel
- Magnific Popup
- Icons by Uicons
- Other open-source libraries

---

## 🎯 Quick Checklist for Next Meeting/Review

- [ ] Review project structure and features
- [ ] Decide on backend technology stack
- [ ] Define user roles and permissions
- [ ] Plan database schema
- [ ] Create wireframes for admin dashboard
- [ ] Set up development environment
- [ ] Create deployment plan
- [ ] Allocate budget for hosting/services

---

## 📞 Contact & Support

For questions or updates to this README:
- Update this file as project evolves
- Keep documentation current
- Add new sections as features are added

---

**Last Updated:** April 27, 2026  
**Status:** Frontend Complete - Ready for Backend Development  
**Version:** 1.0

---

## Summary

**Inter Labour** is a comprehensive job board website with a complete frontend implementation. The platform is ready for backend development and integration with a database. The current static pages showcase all the necessary functionality needed for a modern job portal. The next major step is backend API development and database implementation to make the application fully functional.

For detailed technical specifications, feature documentation, or development questions, refer to the relevant sections above.

