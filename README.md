# HHA Medicine - Medical Billing KPI Dashboard 🏥

A professional medical billing analytics dashboard for healthcare organizations to track Key Performance Indicators (KPIs) and optimize revenue cycle management.

## 📂 Project Structure (Easy to Understand)

```
HHAMedicine-Dashboard/
│
├── 📁 01_Frontend_Website/     ← The website you see in browser
│   ├── index.html              ← Main webpage
│   └── (other web files)       ← Styles and scripts
│
├── 📁 02_Backend_Server/       ← The brain that provides data
│   ├── main_server.py          ← Main server program
│   ├── requirements.txt        ← List of needed software
│   └── (other server files)    ← Supporting files
│
├── 📁 03_Documentation/        ← Help and guides
│   └── (documentation files)   ← User guides and help
│
├── 📁 04_Setup_Scripts/        ← One-click start buttons
│   └── START_DASHBOARD.bat     ← Double-click to start!
│
└── README.md                   ← You are reading this!
```

## 🚀 Super Easy Start Guide (No Coding Required!)

### Option 1: One-Click Start (Easiest)
1. Go to the `04_Setup_Scripts` folder
2. Double-click on `START_DASHBOARD.bat`
3. The dashboard will open automatically in your browser!

### Option 2: View Dashboard Only
1. Go to the `01_Frontend_Website` folder
2. Double-click on `index.html`
3. The dashboard opens in your browser (without live data)

## 💡 What This Dashboard Does

This dashboard helps medical billing teams to:
- 📊 Track revenue in real-time
- 📋 Monitor claims processing
- 👥 View patient statistics
- 📈 Analyze performance metrics
- 💰 Optimize billing operations
- 🎯 Identify improvement areas

## 📊 Key Features

### Revenue Tracking
- Total revenue
- Monthly/Daily revenue
- Growth percentage
- Collection rates

### Claims Management
- Total claims processed
- Pending claims
- Denial rates
- Approval percentages

### Patient Analytics
- Total patient count
- New patient acquisition
- Patient satisfaction scores
- Active patient tracking

### Performance Metrics
- Days in AR (Accounts Receivable)
- First pass resolution rate
- Net collection rate
- Department-wise performance

## 🖥️ System Requirements

- **For Users:** Any modern web browser (Chrome, Firefox, Edge, Safari)
- **For Server:** Python 3.8 or higher (automatically handled by setup script)

## 🔧 For Developers

### Manual Installation
```bash
# 1. Navigate to backend folder
cd 02_Backend_Server

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python main_server.py
```

### API Endpoints
- `http://localhost:5010/` - API information
- `http://localhost:5010/api/kpi` - All KPI metrics
- `http://localhost:5010/api/revenue` - Revenue data
- `http://localhost:5010/api/claims` - Claims data
- `http://localhost:5010/api/patients` - Patient data
- `http://localhost:5010/api/performance` - Performance metrics
- `http://localhost:5010/health` - Health check

## 🌐 Live Demo

Visit: https://medicalbillingkpi.z13.web.core.windows.net/

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- 📱 Smartphones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktop computers

## 🔒 Security

- Secure API endpoints
- CORS protection
- Data encryption
- User authentication (optional)

## 📈 Dashboard Screenshots

The dashboard includes:
1. **Main Overview** - Complete KPI summary
2. **Revenue Analytics** - Detailed revenue breakdown
3. **Claims Tracker** - Real-time claims monitoring
4. **Performance Metrics** - Department and provider performance
5. **Payer Mix Analysis** - Insurance distribution

## 🆘 Troubleshooting

### Dashboard won't start?
1. Make sure Python is installed
2. Run the START_DASHBOARD.bat file as administrator
3. Check if port 5010 is available

### No data showing?
1. Ensure the backend server is running
2. Check your internet connection
3. Refresh the browser (F5)

## 📞 Support

- **Organization:** HHA Medicine
- **Developer:** Akhil Reddy Danda
- **Email:** support@hhamedicine.com
- **Website:** https://hhamedicine.com

## 🚀 Deployment

### Deploy to Azure
```bash
# Frontend
az storage blob upload-batch --account-name <storage> --destination '$web' --source ./01_Frontend_Website

# Backend
az containerapp create --name hha-dashboard --resource-group <rg> --image <docker-image>
```

## 📄 License

Copyright © 2024 HHA Medicine. All rights reserved.

## 🎯 Future Enhancements

- [ ] Real-time notifications
- [ ] Advanced predictive analytics
- [ ] AI-powered insights
- [ ] Integration with EHR systems
- [ ] Automated reporting
- [ ] Multi-facility support

---

**Note:** This is a professional medical billing dashboard. For production use, ensure proper security configurations and HIPAA compliance.