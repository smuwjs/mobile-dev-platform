import { StrictMode } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import { Layout } from './components/layout'
import DashboardPage from './pages/dashboard'
import ProjectsPage from './pages/projects'
import ProjectDetailPage from './pages/projects/[id]'
import TasksPage from './pages/tasks'
import CostsPage from './pages/costs'
import LoginPage from './pages/login'

function App() {
  return (
    <StrictMode>
      <BrowserRouter>
        <Routes>
          <Route path="/dev/login" element={<LoginPage />} />
          <Route path="/dev/" element={<Layout><DashboardPage /></Layout>} />
          <Route path="/dev/projects" element={<Layout><ProjectsPage /></Layout>} />
          <Route path="/dev/projects/:id" element={<Layout><ProjectDetailPage /></Layout>} />
          <Route path="/dev/tasks" element={<Layout><TasksPage /></Layout>} />
          <Route path="/dev/costs" element={<Layout><CostsPage /></Layout>} />
        </Routes>
      </BrowserRouter>
    </StrictMode>
  )
}

export default App
