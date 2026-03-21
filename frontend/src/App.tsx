import { StrictMode } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import { Layout } from './components/layout'
import DashboardPage from './pages/dashboard'
import ProjectsPage from './pages/projects'
import ProjectDetailPage from './pages/projects/[id]'
import TasksPage from './pages/tasks'
import TaskBoardPage from './pages/task-board'
import CostsPage from './pages/costs'
import RequirementsPage from './pages/requirements'
import EstimationPage from './pages/estimation'
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
          <Route path="/dev/task-board" element={<Layout><TaskBoardPage /></Layout>} />
          <Route path="/dev/costs" element={<Layout><CostsPage /></Layout>} />
          <Route path="/dev/requirements" element={<Layout><RequirementsPage /></Layout>} />
          <Route path="/dev/estimation" element={<Layout><EstimationPage /></Layout>} />
        </Routes>
      </BrowserRouter>
    </StrictMode>
  )
}

export default App
