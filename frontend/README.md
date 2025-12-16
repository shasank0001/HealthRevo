# HealthRevo - React Frontend

A standalone React application for health monitoring and risk prediction. This is the frontend portion that will integrate with a FastAPI backend.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run start
```

## 📁 Project Structure

```
HealthPredict/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── layout/         # Layout components (navbar, etc.)
│   │   └── ui/             # UI components (buttons, cards, etc.)
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility libraries
│   │   ├── api.ts          # Mock API (to be replaced with FastAPI)
│   │   ├── queryClient.ts  # TanStack Query configuration
│   │   └── utils.ts        # Utility functions
│   ├── pages/              # Page components
│   │   ├── doctor/         # Doctor dashboard pages
│   │   ├── patient/        # Patient dashboard pages
│   │   ├── login.tsx       # Login page
│   │   └── not-found.tsx   # 404 page
│   ├── types/              # TypeScript type definitions
│   └── main.tsx            # Application entry point
├── index.html              # HTML template
├── package.json            # Dependencies and scripts
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite build configuration
```

## 🛠 Tech Stack

### Frontend Core
- **React 18.3.1** - UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **Wouter** - Lightweight routing

### UI & Styling
- **TailwindCSS** - Utility-first CSS framework
- **Radix UI** - Headless, accessible components
- **shadcn/ui** - Beautiful component library
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

### State Management
- **TanStack Query** - Server state management
- **React Hook Form** - Form handling
- **Zod** - Schema validation

### Charts & Visualization
- **Recharts** - Chart library for health data visualization

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000/api
```

### API Integration
The app currently uses mock data from `src/lib/api.ts`. To integrate with FastAPI:

1. Update the `API_BASE_URL` in `src/lib/api.ts`
2. Replace mock functions with actual API calls
3. Update types in `src/types/index.ts` to match your backend schema

## 📱 Features

### Patient Features
- **Dashboard**: Overview of health metrics and recent alerts
- **Vitals Entry**: Input and track vital signs (BP, heart rate, etc.)
- **Medications**: Upload prescriptions and track medications
- **AI Assistant**: Chat with AI for health insights and recommendations

### Doctor Features
- **Dashboard**: Patient overview and system statistics
- **Alerts**: Monitor patient alerts and anomalies
- **Prescriptions**: Review and manage patient prescriptions

### Authentication
- Role-based access (patient/doctor/admin)
- Session management
- Protected routes

## 🎨 UI Components

The app uses a comprehensive design system with:
- **Cards** for data display
- **Charts** for health metrics visualization
- **Forms** with validation
- **Modals** and **dialogs**
- **Navigation** and **breadcrumbs**
- **Data tables** with sorting and filtering
- **Chat interface** for AI assistant

## 🔄 Next Steps for FastAPI Integration

1. **Setup FastAPI Backend**:
   ```python
   pip install fastapi uvicorn
   ```

2. **Update API calls**: Replace mock functions in `src/lib/api.ts`

3. **CORS Configuration**: Ensure FastAPI allows requests from `http://localhost:5173`

4. **Authentication**: Implement JWT or session-based auth in FastAPI

5. **Database Integration**: Connect FastAPI to your database (PostgreSQL, etc.)

## 🧪 Development

### Mock Data
The app includes realistic mock data for development:
- Sample patient data
- Vitals history
- Alert notifications
- Chat responses

### Type Safety
All components are fully typed with TypeScript for better development experience and fewer runtime errors.

### Responsive Design
The UI is fully responsive and works on desktop, tablet, and mobile devices.

## 📦 Build Output
- Production build outputs to `dist/`
- Optimized bundles with code splitting
- Static assets for deployment

## 🚀 Deployment
The built application can be deployed to any static hosting service:
- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

---

**Ready for FastAPI integration!** The frontend is completely standalone and can be easily connected to your FastAPI backend by updating the API endpoints in `src/lib/api.ts`.
