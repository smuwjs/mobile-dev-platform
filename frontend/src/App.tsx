import { StrictMode } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import { Layout } from './components/layout'
import DashboardPage from './pages/dashboard'
import ProjectsPage from './pages/projects'
import ProjectDetailPage from './pages/projects/[id]'
import TasksPage from './pages/tasks'
import TaskBoardPage from './pages/task-board'
import CostsPage from './pages/costs'
import RequirementsPage from './pages/requirements'
import LoginPage from './pages/login'

function App() {
  return (
    <StrictMode>
      <BrowserRouter basename="/dev">
        <Routes>
          <Route path="/" element={<Navigate to="/projects" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<Layout><DashboardPage /></Layout>} />
          <Route path="/projects" element={<Layout><ProjectsPage /></Layout>} />
          <Route path="/projects/:id" element={<Layout><ProjectDetailPage /></Layout>} />
          <Route path="/tasks" element={<Layout><TasksPage /></Layout>} />
          <Route path="/task-board" element={<Layout><TaskBoardPage /></Layout>} />
          <Route path="/costs" element={<Layout><CostsPage /></Layout>} />
          <Route path="/requirements" element={<Layout><RequirementsPage /></Layout>} />
        </Routes>
      </BrowserRouter>
    </StrictMode>
  )
}

export default App
